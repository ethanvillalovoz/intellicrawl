"""Normalized, cached access to the Firecrawl Python SDK."""

from __future__ import annotations

import asyncio
import hashlib
import ipaddress
import json
from collections.abc import Mapping, MutableMapping
from typing import Any
from urllib.parse import urlparse

from intellicrawl.models import SourceDocument


class ProviderError(RuntimeError):
    """Raised when an external provider cannot return validated data."""


def validate_public_url(url: str) -> str:
    """Accept public HTTP(S) URLs and reject obvious local/private targets."""

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("source URL must use http or https")
    hostname = parsed.hostname.casefold().rstrip(".")
    if parsed.username or parsed.password:
        raise ValueError("source URL cannot include credentials")
    if hostname == "localhost" or hostname.endswith(".local"):
        raise ValueError("source URL cannot target a local hostname")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        if not address.is_global:
            raise ValueError("source URL cannot target a private or reserved address")
    return url


def _field(value: object, name: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _search_items(response: object) -> list[object]:
    direct = _field(response, "web")
    if direct is not None:
        return list(direct)
    data = _field(response, "data")
    if isinstance(data, list):
        return data
    web = _field(data, "web")
    return list(web or [])


def _normalized_document(item: object, source_id: str) -> SourceDocument | None:
    metadata = _field(item, "metadata", {}) or {}
    raw_url = (
        _field(item, "url")
        or _field(metadata, "source_url")
        or _field(metadata, "sourceURL")
        or _field(metadata, "url")
    )
    if not raw_url:
        return None
    try:
        url = validate_public_url(str(raw_url))
    except ValueError:
        return None
    title = _field(item, "title") or _field(metadata, "title") or urlparse(url).hostname
    markdown = _field(item, "markdown", "") or ""
    description = _field(item, "description") or _field(metadata, "description") or ""
    excerpt = " ".join(str(description or markdown[:600]).split())[:600]
    return SourceDocument(
        source_id=source_id,
        title=str(title or "Untitled source"),
        url=url,
        excerpt=excerpt,
        content=str(markdown),
    )


class FirecrawlSearchProvider:
    """Firecrawl search adapter with normalization, timeout, and TTL caching."""

    def __init__(
        self,
        client: object,
        *,
        cache: MutableMapping[str, object] | object | None = None,
        timeout_seconds: float = 60,
        cache_ttl_seconds: int = 86_400,
        concurrency: int = 3,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if cache_ttl_seconds < 0:
            raise ValueError("cache_ttl_seconds cannot be negative")
        if concurrency <= 0:
            raise ValueError("concurrency must be positive")
        self.client = client
        self.cache = cache
        self.timeout_seconds = timeout_seconds
        self.cache_ttl_seconds = cache_ttl_seconds
        self._semaphore = asyncio.Semaphore(concurrency)

    def _cache_key(self, query: str, limit: int) -> str:
        payload = json.dumps({"query": query, "limit": limit}, sort_keys=True)
        return "search:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _cache_get(self, key: str) -> list[SourceDocument] | None:
        if self.cache is None:
            return None
        value = self.cache.get(key)  # type: ignore[union-attr]
        if value is None:
            return None
        return [SourceDocument.model_validate(item) for item in value]

    def _cache_set(self, key: str, documents: list[SourceDocument]) -> None:
        if self.cache is None or self.cache_ttl_seconds == 0:
            return
        value = [
            {**document.model_dump(mode="json"), "content": document.content}
            for document in documents
        ]
        setter = getattr(self.cache, "set", None)
        if callable(setter):
            setter(key, value, expire=self.cache_ttl_seconds)
        else:
            assert isinstance(self.cache, MutableMapping)
            self.cache[key] = value

    async def _call(self, function, *args, **kwargs):
        async with self._semaphore:
            try:
                return await asyncio.wait_for(
                    asyncio.to_thread(function, *args, **kwargs),
                    timeout=self.timeout_seconds,
                )
            except TimeoutError as error:
                raise ProviderError("Firecrawl request timed out") from error
            except Exception as error:
                raise ProviderError(f"Firecrawl request failed: {error}") from error

    async def _scrape_missing_content(self, document: SourceDocument) -> SourceDocument:
        if document.content:
            return document
        response = await self._call(
            self.client.scrape,
            str(document.url),
            formats=["markdown"],
            only_main_content=True,
            remove_base64_images=True,
            block_ads=True,
        )
        markdown = _field(response, "markdown", "") or ""
        if not markdown:
            return document
        return document.model_copy(
            update={
                "content": str(markdown),
                "excerpt": document.excerpt or " ".join(str(markdown)[:600].split()),
            }
        )

    async def search(self, query: str, *, limit: int) -> list[SourceDocument]:
        if not query.strip():
            raise ValueError("search query cannot be empty")
        if not 1 <= limit <= 10:
            raise ValueError("search limit must be between 1 and 10")
        key = self._cache_key(query, limit)
        cached = self._cache_get(key)
        if cached is not None:
            return cached

        response = await self._call(
            self.client.search,
            query,
            limit=limit,
            scrape_options={"formats": ["markdown"], "onlyMainContent": True},
        )
        documents: list[SourceDocument] = []
        seen_urls: set[str] = set()
        for item in _search_items(response):
            document = _normalized_document(item, f"S{len(documents) + 1}")
            if document is None or str(document.url) in seen_urls:
                continue
            seen_urls.add(str(document.url))
            documents.append(document)
            if len(documents) == limit:
                break
        hydrated = await asyncio.gather(
            *(self._scrape_missing_content(document) for document in documents)
        )
        self._cache_set(key, list(hydrated))
        return list(hydrated)
