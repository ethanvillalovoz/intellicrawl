"""Provider contracts used by the pipeline and deterministic demo."""

from __future__ import annotations

from typing import Protocol

from intellicrawl.models import (
    Recommendation,
    SourceDocument,
    ToolAnalysis,
    ToolReport,
    ToolSelection,
)


class SearchProvider(Protocol):
    async def search(self, query: str, *, limit: int) -> list[SourceDocument]: ...


class AnalysisProvider(Protocol):
    @property
    def model_name(self) -> str: ...

    async def select_tools(
        self,
        query: str,
        sources: list[SourceDocument],
        *,
        limit: int,
    ) -> ToolSelection: ...

    async def analyze_tool(
        self,
        tool_name: str,
        sources: list[SourceDocument],
    ) -> ToolAnalysis: ...

    async def recommend(self, query: str, tools: list[ToolReport]) -> Recommendation: ...
