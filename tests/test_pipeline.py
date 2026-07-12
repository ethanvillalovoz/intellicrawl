from datetime import date

import pytest

from intellicrawl.demo import build_demo_pipeline
from intellicrawl.models import (
    FieldEvidence,
    Recommendation,
    SourceDocument,
    ToolAnalysis,
    ToolSelection,
)
from intellicrawl.pipeline import ResearchError, ResearchPipeline, normalize_query


@pytest.mark.asyncio
async def test_demo_runs_through_complete_graph() -> None:
    report = await build_demo_pipeline().run("  vector   databases for production RAG ")
    assert report.query == "vector databases for production RAG"
    assert report.status == "complete"
    assert [tool.name for tool in report.tools] == ["Weaviate", "Pinecone", "Qdrant"]
    assert report.source_count == 6
    assert all(tool.evidence for tool in report.tools)


@pytest.mark.parametrize("query", ("", "ab", "x" * 181, "abc\x01def"))
def test_query_validation_is_consistent(query: str) -> None:
    with pytest.raises(ValueError):
        normalize_query(query)


class EmptySearch:
    async def search(self, query: str, *, limit: int):
        return []


class MinimalAnalyzer:
    @property
    def model_name(self) -> str:
        return "test"

    async def select_tools(self, query, sources, *, limit):
        return ToolSelection(names=["ExampleDB"])

    async def analyze_tool(self, tool_name, sources):
        return ToolAnalysis(
            description="Example",
            pricing_model="unknown",
            is_open_source="unknown",
            api_available="unknown",
            evidence=[FieldEvidence(field="description", source_ids=["S1"], note="Only one field")],
        )

    async def recommend(self, query, tools):
        return Recommendation(summary="Compare the evidence.")


@pytest.mark.asyncio
async def test_empty_discovery_is_a_hard_failure() -> None:
    pipeline = ResearchPipeline(EmptySearch(), MinimalAnalyzer(), mode="live")
    with pytest.raises(ResearchError, match="no usable"):
        await pipeline.run("example databases")


class PartialSearch:
    async def search(self, query: str, *, limit: int):
        if "comparison" in query:
            return [
                SourceDocument(
                    source_id="S1",
                    title="Discovery",
                    url="https://example.com/discovery",
                )
            ]
        return [
            SourceDocument(
                source_id="S1",
                title="Docs",
                url="https://example.com/docs",
            )
        ]


@pytest.mark.asyncio
async def test_missing_field_evidence_yields_a_partial_report() -> None:
    pipeline = ResearchPipeline(
        PartialSearch(),
        MinimalAnalyzer(),
        mode="live",
        today=lambda: date(2026, 1, 1),
    )
    report = await pipeline.run("example databases")
    assert report.status == "partial"
    assert report.tools[0].status == "partial"
    assert "lack source evidence" in report.warnings[0]


class FailingRecommendationAnalyzer(MinimalAnalyzer):
    async def analyze_tool(self, tool_name, sources):
        analysis = await super().analyze_tool(tool_name, sources)
        analysis.evidence.extend(
            [
                FieldEvidence(field="pricing_model", source_ids=["S1"], note="Docs"),
                FieldEvidence(field="is_open_source", source_ids=["S1"], note="Docs"),
                FieldEvidence(field="api_available", source_ids=["S1"], note="Docs"),
            ]
        )
        return analysis

    async def recommend(self, query, tools):
        raise RuntimeError("model unavailable")


@pytest.mark.asyncio
async def test_recommendation_failure_preserves_sourced_profiles() -> None:
    pipeline = ResearchPipeline(PartialSearch(), FailingRecommendationAnalyzer(), mode="live")
    report = await pipeline.run("example databases")
    assert report.status == "partial"
    assert report.tools[0].status == "complete"
    assert "No recommendation was generated" in report.recommendation.summary


@pytest.mark.parametrize(
    "kwargs",
    (
        {"max_tools": 0},
        {"sources_per_tool": 7},
        {"concurrency": 0},
    ),
)
def test_pipeline_rejects_invalid_bounds(kwargs) -> None:
    with pytest.raises(ValueError):
        ResearchPipeline(PartialSearch(), MinimalAnalyzer(), mode="demo", **kwargs)
