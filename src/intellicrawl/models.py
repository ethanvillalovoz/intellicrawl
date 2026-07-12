"""Validated public and internal research models."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

PricingModel = Literal["free", "freemium", "paid", "enterprise", "unknown"]
Availability = Literal["yes", "no", "unknown"]
ReportStatus = Literal["complete", "partial"]
EvidenceField = Literal[
    "description",
    "pricing_model",
    "is_open_source",
    "api_available",
    "language_support",
    "integrations",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class SourceDocument(StrictModel):
    """A normalized source; full content is kept out of serialized reports."""

    source_id: str = Field(pattern=r"^S[1-9][0-9]*$")
    title: str = Field(min_length=1, max_length=240)
    url: HttpUrl
    excerpt: str = Field(default="", max_length=600)
    content: str = Field(default="", exclude=True, repr=False)


class SourceCitation(StrictModel):
    source_id: str = Field(pattern=r"^S[1-9][0-9]*$")
    title: str = Field(min_length=1, max_length=240)
    url: HttpUrl

    @classmethod
    def from_document(cls, document: SourceDocument) -> SourceCitation:
        return cls(source_id=document.source_id, title=document.title, url=document.url)


class FieldEvidence(StrictModel):
    """Links one normalized field to the source records that support it."""

    field: EvidenceField
    source_ids: list[str] = Field(min_length=1, max_length=4)
    note: str = Field(min_length=1, max_length=240)


class ToolSelection(StrictModel):
    names: list[str] = Field(min_length=1, max_length=6)


class ToolAnalysis(StrictModel):
    description: str = Field(min_length=1, max_length=500)
    pricing_model: PricingModel
    is_open_source: Availability
    tech_stack: list[str] = Field(default_factory=list, max_length=8)
    api_available: Availability
    language_support: list[str] = Field(default_factory=list, max_length=8)
    integrations: list[str] = Field(default_factory=list, max_length=8)
    evidence: list[FieldEvidence] = Field(min_length=1, max_length=12)


class Recommendation(StrictModel):
    summary: str = Field(min_length=1, max_length=900)
    best_for: list[str] = Field(default_factory=list, max_length=4)


class ToolReport(StrictModel):
    name: str = Field(min_length=1, max_length=100)
    website: HttpUrl
    description: str = Field(min_length=1, max_length=500)
    pricing_model: PricingModel
    is_open_source: Availability
    tech_stack: list[str] = Field(default_factory=list, max_length=8)
    api_available: Availability
    language_support: list[str] = Field(default_factory=list, max_length=8)
    integrations: list[str] = Field(default_factory=list, max_length=8)
    evidence: list[FieldEvidence] = Field(default_factory=list, max_length=12)
    sources: list[SourceCitation] = Field(min_length=1, max_length=6)
    status: ReportStatus = "complete"

    @model_validator(mode="after")
    def evidence_must_reference_known_sources(self) -> ToolReport:
        known = {source.source_id for source in self.sources}
        referenced = {source_id for item in self.evidence for source_id in item.source_ids}
        unknown = referenced - known
        if unknown:
            raise ValueError(f"evidence references unknown sources: {sorted(unknown)}")
        return self


class ResearchReport(StrictModel):
    query: str = Field(min_length=3, max_length=180)
    mode: Literal["demo", "live"]
    snapshot_date: date
    status: ReportStatus
    model: str
    tools: list[ToolReport] = Field(min_length=1, max_length=6)
    recommendation: Recommendation
    warnings: list[str] = Field(default_factory=list, max_length=20)

    @property
    def source_count(self) -> int:
        return sum(len(tool.sources) for tool in self.tools)
