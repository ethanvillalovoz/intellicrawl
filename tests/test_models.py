from datetime import date

import pytest
from pydantic import ValidationError

from intellicrawl.models import (
    FieldEvidence,
    Recommendation,
    ResearchReport,
    SourceCitation,
    SourceDocument,
    ToolReport,
)


def sample_tool(**updates) -> ToolReport:
    values = {
        "name": "ExampleDB",
        "website": "https://example.com/docs",
        "description": "A source-backed example database.",
        "pricing_model": "freemium",
        "is_open_source": "yes",
        "tech_stack": ["Python"],
        "api_available": "yes",
        "language_support": ["Python"],
        "integrations": ["Example Cloud"],
        "evidence": [FieldEvidence(field="description", source_ids=["S1"], note="Official docs")],
        "sources": [
            SourceCitation(
                source_id="S1",
                title="Example docs",
                url="https://example.com/docs",
            )
        ],
    }
    values.update(updates)
    return ToolReport(**values)


def test_source_content_is_private_in_serialized_reports() -> None:
    document = SourceDocument(
        source_id="S1",
        title="Docs",
        url="https://example.com",
        content="private scraped body",
    )
    assert document.content == "private scraped body"
    assert "content" not in document.model_dump()
    assert SourceCitation.from_document(document).source_id == "S1"


def test_tool_rejects_evidence_for_unknown_source() -> None:
    with pytest.raises(ValidationError, match="unknown sources"):
        sample_tool(
            evidence=[FieldEvidence(field="description", source_ids=["S2"], note="Missing source")]
        )


def test_report_counts_sources_and_forbids_extra_fields() -> None:
    report = ResearchReport(
        query="example databases",
        mode="demo",
        snapshot_date=date(2026, 7, 11),
        status="complete",
        model="fixture",
        tools=[sample_tool()],
        recommendation=Recommendation(summary="Use the evidence.", best_for=[]),
    )
    assert report.source_count == 1
    with pytest.raises(ValidationError):
        ResearchReport(**report.model_dump(), surprise=True)
