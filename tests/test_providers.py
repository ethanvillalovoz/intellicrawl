import time
from types import SimpleNamespace

import pytest

from intellicrawl.providers import (
    FirecrawlSearchProvider,
    ProviderError,
    validate_public_url,
)


@pytest.mark.parametrize(
    "url",
    (
        "file:///etc/passwd",
        "https://localhost/admin",
        "https://127.0.0.1/private",
        "https://10.0.0.1/private",
        "https://user:pass@example.com",
    ),
)
def test_private_or_unsafe_urls_are_rejected(url: str) -> None:
    with pytest.raises(ValueError):
        validate_public_url(url)


def test_public_urls_are_accepted() -> None:
    assert validate_public_url("https://docs.example.com/path") == "https://docs.example.com/path"


class FakeClient:
    def __init__(self) -> None:
        self.search_calls = 0
        self.scrape_calls = 0

    def search(self, query, **kwargs):
        self.search_calls += 1
        return SimpleNamespace(
            web=[
                SimpleNamespace(
                    title="Example docs",
                    url="https://example.com/docs",
                    description="Official documentation",
                    markdown="",
                ),
                {"title": "Duplicate", "url": "https://example.com/docs"},
                {"title": "Local", "url": "https://localhost/private"},
            ]
        )

    def scrape(self, url, **kwargs):
        self.scrape_calls += 1
        return SimpleNamespace(markdown="# Example\nValidated source body.")


@pytest.mark.asyncio
async def test_provider_normalizes_hydrates_deduplicates_and_caches() -> None:
    client = FakeClient()
    cache = {}
    provider = FirecrawlSearchProvider(client, cache=cache)

    first = await provider.search("example database", limit=3)
    second = await provider.search("example database", limit=3)

    assert len(first) == 1
    assert first[0].source_id == "S1"
    assert first[0].content.startswith("# Example")
    assert second[0].content == first[0].content
    assert client.search_calls == 1
    assert client.scrape_calls == 1


@pytest.mark.asyncio
async def test_provider_supports_nested_dictionary_response() -> None:
    class DictClient(FakeClient):
        def search(self, query, **kwargs):
            return {
                "data": {
                    "web": [
                        {
                            "metadata": {
                                "title": "Dictionary docs",
                                "sourceURL": "https://example.org/docs",
                            },
                            "markdown": "Body",
                        }
                    ]
                }
            }

    documents = await FirecrawlSearchProvider(DictClient()).search("query", limit=1)
    assert documents[0].title == "Dictionary docs"
    assert documents[0].content == "Body"


@pytest.mark.asyncio
async def test_provider_wraps_errors_and_timeouts() -> None:
    class BrokenClient:
        def search(self, query, **kwargs):
            raise OSError("offline")

    with pytest.raises(ProviderError, match="failed"):
        await FirecrawlSearchProvider(BrokenClient()).search("query", limit=1)

    class SlowClient:
        def search(self, query, **kwargs):
            time.sleep(0.05)
            return {"data": {"web": []}}

    with pytest.raises(ProviderError, match="timed out"):
        await FirecrawlSearchProvider(SlowClient(), timeout_seconds=0.001).search("query", limit=1)


@pytest.mark.parametrize(
    "kwargs",
    (
        {"timeout_seconds": 0},
        {"cache_ttl_seconds": -1},
        {"concurrency": 0},
    ),
)
def test_provider_rejects_invalid_bounds(kwargs) -> None:
    with pytest.raises(ValueError):
        FirecrawlSearchProvider(FakeClient(), **kwargs)


@pytest.mark.asyncio
async def test_search_validates_query_and_limit() -> None:
    provider = FirecrawlSearchProvider(FakeClient())
    with pytest.raises(ValueError, match="empty"):
        await provider.search(" ", limit=1)
    with pytest.raises(ValueError, match="between"):
        await provider.search("query", limit=11)
