"""LangGraph orchestration for source-backed tool research."""

from __future__ import annotations

import asyncio
import re
from collections.abc import Callable
from datetime import date
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from intellicrawl.contracts import AnalysisProvider, SearchProvider
from intellicrawl.models import (
    EvidenceField,
    Recommendation,
    ResearchReport,
    SourceCitation,
    SourceDocument,
    ToolReport,
)


class ResearchError(RuntimeError):
    """Raised when a report cannot be produced without inventing evidence."""


class PipelineState(TypedDict, total=False):
    query: str
    discovery_sources: list[SourceDocument]
    tool_names: list[str]
    tools: list[ToolReport]
    recommendation: Recommendation
    warnings: list[str]


def normalize_query(query: str) -> str:
    """Normalize whitespace and reject empty, huge, or control-character queries."""

    normalized = re.sub(r"\s+", " ", query).strip()
    if not 3 <= len(normalized) <= 180:
        raise ValueError("query must contain between 3 and 180 characters")
    if any(ord(character) < 32 for character in normalized):
        raise ValueError("query cannot contain control characters")
    return normalized


def _deduplicate_names(names: list[str], limit: int) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for name in names:
        cleaned = re.sub(r"\s+", " ", name).strip(" -\t\n")
        key = cleaned.casefold()
        if not cleaned or key in seen:
            continue
        seen.add(key)
        output.append(cleaned[:100])
        if len(output) == limit:
            break
    return output


class ResearchPipeline:
    """Discover, profile, and compare tools through replaceable providers."""

    def __init__(
        self,
        search: SearchProvider,
        analyzer: AnalysisProvider,
        *,
        mode: Literal["demo", "live"],
        max_tools: int = 4,
        sources_per_tool: int = 3,
        concurrency: int = 3,
        today: Callable[[], date] = date.today,
    ) -> None:
        if not 1 <= max_tools <= 6:
            raise ValueError("max_tools must be between 1 and 6")
        if not 1 <= sources_per_tool <= 6:
            raise ValueError("sources_per_tool must be between 1 and 6")
        if concurrency <= 0:
            raise ValueError("concurrency must be positive")
        self.search = search
        self.analyzer = analyzer
        self.mode = mode
        self.max_tools = max_tools
        self.sources_per_tool = sources_per_tool
        self._semaphore = asyncio.Semaphore(concurrency)
        self._today = today
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(PipelineState)
        graph.add_node("discover", self._discover_step)
        graph.add_node("research", self._research_step)
        graph.add_node("recommend", self._recommend_step)
        graph.add_edge(START, "discover")
        graph.add_edge("discover", "research")
        graph.add_edge("research", "recommend")
        graph.add_edge("recommend", END)
        return graph.compile()

    async def _discover_step(self, state: PipelineState) -> dict[str, object]:
        query = state["query"]
        sources = await self.search.search(
            f"{query} developer tools comparison official documentation",
            limit=max(self.max_tools, 4),
        )
        if not sources:
            raise ResearchError("discovery returned no usable public sources")
        selection = await self.analyzer.select_tools(query, sources, limit=self.max_tools)
        names = _deduplicate_names(selection.names, self.max_tools)
        if not names:
            raise ResearchError("analysis returned no specific tool names")
        return {"discovery_sources": sources, "tool_names": names}

    async def _research_one(self, tool_name: str) -> tuple[ToolReport | None, str | None]:
        async with self._semaphore:
            try:
                sources = await self.search.search(
                    f"{tool_name} official documentation pricing API GitHub",
                    limit=self.sources_per_tool,
                )
                if not sources:
                    return None, f"{tool_name}: no usable source pages"
                analysis = await self.analyzer.analyze_tool(tool_name, sources)
                known = {source.source_id for source in sources}
                evidence = [
                    item for item in analysis.evidence if set(item.source_ids).issubset(known)
                ]
                covered = {item.field for item in evidence}
                required: set[EvidenceField] = {
                    "description",
                    "pricing_model",
                    "is_open_source",
                    "api_available",
                }
                complete = required.issubset(covered)
                warning = None if complete else f"{tool_name}: some fields lack source evidence"
                report = ToolReport(
                    name=tool_name,
                    website=sources[0].url,
                    description=analysis.description,
                    pricing_model=analysis.pricing_model,
                    is_open_source=analysis.is_open_source,
                    tech_stack=analysis.tech_stack,
                    api_available=analysis.api_available,
                    language_support=analysis.language_support,
                    integrations=analysis.integrations,
                    evidence=evidence,
                    sources=[SourceCitation.from_document(source) for source in sources],
                    status="complete" if complete else "partial",
                )
                return report, warning
            except Exception as error:
                return None, f"{tool_name}: {type(error).__name__}: {error}"

    async def _research_step(self, state: PipelineState) -> dict[str, object]:
        results = await asyncio.gather(*(self._research_one(name) for name in state["tool_names"]))
        tools = [tool for tool, _ in results if tool is not None]
        warnings = list(state.get("warnings", []))
        warnings.extend(warning for _, warning in results if warning)
        if not tools:
            raise ResearchError("none of the discovered tools could be sourced and analyzed")
        return {"tools": tools, "warnings": warnings}

    async def _recommend_step(self, state: PipelineState) -> dict[str, object]:
        warnings = list(state.get("warnings", []))
        try:
            recommendation = await self.analyzer.recommend(state["query"], state["tools"])
        except Exception as error:
            warnings.append(f"recommendation unavailable: {type(error).__name__}: {error}")
            recommendation = Recommendation(
                summary=(
                    "No recommendation was generated. Compare the source-backed profiles above "
                    "against your own requirements."
                ),
                best_for=[],
            )
        return {"recommendation": recommendation, "warnings": warnings}

    async def run(self, query: str) -> ResearchReport:
        normalized = normalize_query(query)
        state = await self.graph.ainvoke({"query": normalized, "warnings": []})
        warnings = state.get("warnings", [])
        return ResearchReport(
            query=normalized,
            mode=self.mode,
            snapshot_date=self._today(),
            status="partial" if warnings else "complete",
            model=self.analyzer.model_name,
            tools=state["tools"],
            recommendation=state["recommendation"],
            warnings=warnings,
        )
