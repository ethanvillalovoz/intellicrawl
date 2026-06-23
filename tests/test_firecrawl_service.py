import pytest

from src.firecrawl_service import FirecrawlService


def test_firecrawl_service_requires_api_key(monkeypatch):
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)

    with pytest.raises(ValueError, match="FIRECRAWL_API_KEY"):
        FirecrawlService()
