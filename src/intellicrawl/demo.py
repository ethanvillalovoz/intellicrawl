"""Deterministic no-key providers for documentation, tests, and product evaluation."""

from __future__ import annotations

from datetime import date

from intellicrawl.models import (
    FieldEvidence,
    Recommendation,
    SourceDocument,
    ToolAnalysis,
    ToolReport,
    ToolSelection,
)
from intellicrawl.pipeline import ResearchPipeline

SNAPSHOT_DATE = date(2026, 7, 11)


def _source(source_id: str, title: str, url: str, content: str) -> SourceDocument:
    return SourceDocument(
        source_id=source_id,
        title=title,
        url=url,
        excerpt=content[:240],
        content=content,
    )


DISCOVERY = [
    _source(
        "S1",
        "Vector database documentation index",
        "https://weaviate.io/developers/weaviate",
        "A comparison snapshot covering Weaviate, Pinecone, and Qdrant for vector search.",
    )
]


TOOL_SOURCES = {
    "weaviate": [
        _source(
            "S1",
            "Weaviate documentation",
            "https://weaviate.io/developers/weaviate",
            "Weaviate documents vector search, APIs, and client libraries.",
        ),
        _source(
            "S2",
            "Weaviate pricing",
            "https://weaviate.io/pricing",
            "Weaviate publishes cloud pricing and a free path for evaluation.",
        ),
    ],
    "pinecone": [
        _source(
            "S1",
            "Pinecone documentation",
            "https://docs.pinecone.io",
            "Pinecone documents a managed vector database, API, and SDKs.",
        ),
        _source(
            "S2",
            "Pinecone pricing",
            "https://www.pinecone.io/pricing",
            "Pinecone publishes usage-based plans and a starter tier.",
        ),
    ],
    "qdrant": [
        _source(
            "S1",
            "Qdrant documentation",
            "https://qdrant.tech/documentation",
            "Qdrant documents its open-source vector search engine, API, and clients.",
        ),
        _source(
            "S2",
            "Qdrant cloud pricing",
            "https://qdrant.tech/pricing",
            "Qdrant publishes managed cloud plans and a free cluster option.",
        ),
    ],
}


ANALYSES = {
    "weaviate": ToolAnalysis(
        description="Open-source vector database with managed cloud and a broad client ecosystem.",
        pricing_model="freemium",
        is_open_source="yes",
        tech_stack=["vector search", "GraphQL", "REST"],
        api_available="yes",
        language_support=["Python", "TypeScript", "Go", "Java"],
        integrations=["OpenAI", "Hugging Face", "LangChain"],
        evidence=[
            FieldEvidence(field="description", source_ids=["S1"], note="Product documentation"),
            FieldEvidence(field="pricing_model", source_ids=["S2"], note="Published pricing"),
            FieldEvidence(field="is_open_source", source_ids=["S1"], note="Documentation"),
            FieldEvidence(field="api_available", source_ids=["S1"], note="API documentation"),
            FieldEvidence(field="language_support", source_ids=["S1"], note="Client docs"),
            FieldEvidence(field="integrations", source_ids=["S1"], note="Integration docs"),
        ],
    ),
    "pinecone": ToolAnalysis(
        description="Managed vector database focused on hosted retrieval infrastructure.",
        pricing_model="freemium",
        is_open_source="no",
        tech_stack=["vector search", "serverless"],
        api_available="yes",
        language_support=["Python", "TypeScript", "Java", "Go"],
        integrations=["OpenAI", "LangChain", "LlamaIndex"],
        evidence=[
            FieldEvidence(field="description", source_ids=["S1"], note="Product documentation"),
            FieldEvidence(field="pricing_model", source_ids=["S2"], note="Published pricing"),
            FieldEvidence(field="is_open_source", source_ids=["S1"], note="Hosted product docs"),
            FieldEvidence(field="api_available", source_ids=["S1"], note="API documentation"),
            FieldEvidence(field="language_support", source_ids=["S1"], note="SDK docs"),
            FieldEvidence(field="integrations", source_ids=["S1"], note="Integration docs"),
        ],
    ),
    "qdrant": ToolAnalysis(
        description="Open-source vector search engine available self-hosted or as a managed cloud.",
        pricing_model="freemium",
        is_open_source="yes",
        tech_stack=["Rust", "vector search", "REST", "gRPC"],
        api_available="yes",
        language_support=["Python", "TypeScript", "Rust", "Go"],
        integrations=["LangChain", "LlamaIndex", "OpenAI"],
        evidence=[
            FieldEvidence(field="description", source_ids=["S1"], note="Product documentation"),
            FieldEvidence(field="pricing_model", source_ids=["S2"], note="Published pricing"),
            FieldEvidence(field="is_open_source", source_ids=["S1"], note="Documentation"),
            FieldEvidence(field="api_available", source_ids=["S1"], note="API documentation"),
            FieldEvidence(field="language_support", source_ids=["S1"], note="Client docs"),
            FieldEvidence(field="integrations", source_ids=["S1"], note="Integration docs"),
        ],
    ),
}


class DemoSearchProvider:
    async def search(self, query: str, *, limit: int) -> list[SourceDocument]:
        lowered = query.casefold()
        for name, sources in TOOL_SOURCES.items():
            if name in lowered:
                return sources[:limit]
        return DISCOVERY[:limit]


class DemoAnalysisProvider:
    @property
    def model_name(self) -> str:
        return "deterministic-fixture"

    async def select_tools(
        self,
        query: str,
        sources: list[SourceDocument],
        *,
        limit: int,
    ) -> ToolSelection:
        return ToolSelection(names=["Weaviate", "Pinecone", "Qdrant"][:limit])

    async def analyze_tool(
        self,
        tool_name: str,
        sources: list[SourceDocument],
    ) -> ToolAnalysis:
        return ANALYSES[tool_name.casefold()]

    async def recommend(self, query: str, tools: list[ToolReport]) -> Recommendation:
        return Recommendation(
            summary=(
                "Choose Pinecone when a fully managed path is the priority. Choose Weaviate or "
                "Qdrant when open-source deployment flexibility matters; compare their operational "
                "models and client ecosystems against your workload before committing."
            ),
            best_for=[
                "Pinecone: managed operations",
                "Weaviate: integrated open-source platform",
                "Qdrant: self-hosted control",
            ],
        )


def build_demo_pipeline() -> ResearchPipeline:
    return ResearchPipeline(
        DemoSearchProvider(),
        DemoAnalysisProvider(),
        mode="demo",
        max_tools=3,
        sources_per_tool=2,
        today=lambda: SNAPSHOT_DATE,
    )


async def create_demo_report():
    return await build_demo_pipeline().run("vector databases for production RAG")
