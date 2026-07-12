"""Optional Firecrawl and OpenAI integrations for live research."""

from __future__ import annotations

import asyncio
from typing import TypeVar

from pydantic import BaseModel

from intellicrawl.models import (
    Recommendation,
    SourceDocument,
    ToolAnalysis,
    ToolReport,
    ToolSelection,
)
from intellicrawl.pipeline import ResearchPipeline
from intellicrawl.prompts import (
    SYSTEM_GUARD,
    analysis_prompt,
    recommendation_prompt,
    selection_prompt,
)
from intellicrawl.providers import FirecrawlSearchProvider, ProviderError
from intellicrawl.settings import LiveSettings

ModelT = TypeVar("ModelT", bound=BaseModel)


class OpenAIAnalysisProvider:
    """Structured OpenAI analysis with explicit source-evidence prompts."""

    def __init__(self, model: object, *, model_name: str, timeout_seconds: float = 60) -> None:
        self.model = model
        self._model_name = model_name
        self.timeout_seconds = timeout_seconds

    @property
    def model_name(self) -> str:
        return self._model_name

    async def _structured(self, schema: type[ModelT], prompt: str) -> ModelT:
        structured = self.model.with_structured_output(schema, method="json_schema")
        try:
            result = await asyncio.wait_for(
                structured.ainvoke([("system", SYSTEM_GUARD), ("human", prompt)]),
                timeout=self.timeout_seconds,
            )
        except TimeoutError as error:
            raise ProviderError("OpenAI analysis timed out") from error
        except Exception as error:
            raise ProviderError(f"OpenAI analysis failed: {error}") from error
        return schema.model_validate(result)

    async def select_tools(
        self,
        query: str,
        sources: list[SourceDocument],
        *,
        limit: int,
    ) -> ToolSelection:
        return await self._structured(ToolSelection, selection_prompt(query, sources, limit))

    async def analyze_tool(
        self,
        tool_name: str,
        sources: list[SourceDocument],
    ) -> ToolAnalysis:
        return await self._structured(ToolAnalysis, analysis_prompt(tool_name, sources))

    async def recommend(self, query: str, tools: list[ToolReport]) -> Recommendation:
        return await self._structured(Recommendation, recommendation_prompt(query, tools))


def build_live_pipeline(
    settings: LiveSettings,
    *,
    use_cache: bool = True,
) -> ResearchPipeline:
    """Construct live providers lazily so demo mode needs no API dependencies."""

    try:
        from diskcache import Cache
        from firecrawl import Firecrawl
        from langchain_openai import ChatOpenAI
    except ImportError as error:  # pragma: no cover - depends on optional installation
        raise RuntimeError('live research requires: pip install -e ".[live]"') from error

    cache = None
    if use_cache:
        settings.cache_dir.mkdir(parents=True, exist_ok=True)
        cache = Cache(str(settings.cache_dir), size_limit=512 * 1024 * 1024)
    search = FirecrawlSearchProvider(
        Firecrawl(api_key=settings.firecrawl_api_key),
        cache=cache,
        timeout_seconds=settings.request_timeout_seconds,
        cache_ttl_seconds=settings.cache_ttl_seconds,
        concurrency=settings.concurrency,
    )
    model = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        timeout=settings.request_timeout_seconds,
        max_retries=2,
    )
    analyzer = OpenAIAnalysisProvider(
        model,
        model_name=settings.openai_model,
        timeout_seconds=settings.request_timeout_seconds,
    )
    return ResearchPipeline(
        search,
        analyzer,
        mode="live",
        max_tools=settings.max_tools,
        concurrency=settings.concurrency,
    )
