"""Validated live-provider configuration."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_cache_path


def _integer(environment: Mapping[str, str], name: str, default: int) -> int:
    raw = environment.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer") from error


@dataclass(frozen=True, repr=False)
class LiveSettings:
    firecrawl_api_key: str
    openai_api_key: str
    openai_model: str
    cache_dir: Path
    cache_ttl_seconds: int
    request_timeout_seconds: int
    max_tools: int
    concurrency: int

    @classmethod
    def from_environment(
        cls,
        environment: Mapping[str, str] | None = None,
    ) -> LiveSettings:
        values = os.environ if environment is None else environment
        firecrawl_key = values.get("FIRECRAWL_API_KEY", "").strip()
        openai_key = values.get("OPENAI_API_KEY", "").strip()
        missing = [
            name
            for name, value in (
                ("FIRECRAWL_API_KEY", firecrawl_key),
                ("OPENAI_API_KEY", openai_key),
            )
            if not value
        ]
        if missing:
            raise ValueError("missing required environment variables: " + ", ".join(missing))

        settings = cls(
            firecrawl_api_key=firecrawl_key,
            openai_api_key=openai_key,
            openai_model=values.get("INTELLICRAWL_OPENAI_MODEL", "gpt-5.4-mini").strip(),
            cache_dir=Path(
                values.get("INTELLICRAWL_CACHE_DIR", str(user_cache_path("intellicrawl")))
            ).expanduser(),
            cache_ttl_seconds=_integer(values, "INTELLICRAWL_CACHE_TTL", 86_400),
            request_timeout_seconds=_integer(values, "INTELLICRAWL_TIMEOUT", 60),
            max_tools=_integer(values, "INTELLICRAWL_MAX_TOOLS", 4),
            concurrency=_integer(values, "INTELLICRAWL_CONCURRENCY", 3),
        )
        if not settings.openai_model:
            raise ValueError("INTELLICRAWL_OPENAI_MODEL cannot be empty")
        if settings.cache_ttl_seconds < 0:
            raise ValueError("INTELLICRAWL_CACHE_TTL cannot be negative")
        if settings.request_timeout_seconds <= 0:
            raise ValueError("INTELLICRAWL_TIMEOUT must be positive")
        if not 1 <= settings.max_tools <= 6:
            raise ValueError("INTELLICRAWL_MAX_TOOLS must be between 1 and 6")
        if not 1 <= settings.concurrency <= 8:
            raise ValueError("INTELLICRAWL_CONCURRENCY must be between 1 and 8")
        return settings
