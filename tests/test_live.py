import asyncio

import pytest

from intellicrawl.demo import TOOL_SOURCES
from intellicrawl.live import OpenAIAnalysisProvider
from intellicrawl.models import Recommendation, ToolAnalysis, ToolSelection
from intellicrawl.providers import ProviderError


class FakeRunnable:
    def __init__(self, value=None, error=None, delay=0) -> None:
        self.value = value
        self.error = error
        self.delay = delay

    async def ainvoke(self, messages):
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.error:
            raise self.error
        return self.value


class FakeModel:
    def __init__(self, values) -> None:
        self.values = values
        self.calls = []

    def with_structured_output(self, schema, method):
        self.calls.append((schema, method))
        return FakeRunnable(self.values[schema])


@pytest.mark.asyncio
async def test_openai_provider_requests_native_structured_outputs() -> None:
    analysis = ToolAnalysis(
        description="Example",
        pricing_model="unknown",
        is_open_source="unknown",
        api_available="unknown",
        evidence=[{"field": "description", "source_ids": ["S1"], "note": "Docs"}],
    )
    model = FakeModel(
        {
            ToolSelection: {"names": ["ExampleDB"]},
            ToolAnalysis: analysis,
            Recommendation: {"summary": "Compare it.", "best_for": []},
        }
    )
    provider = OpenAIAnalysisProvider(model, model_name="test-model")
    sources = TOOL_SOURCES["weaviate"]

    assert (await provider.select_tools("query", sources, limit=1)).names == ["ExampleDB"]
    assert (await provider.analyze_tool("ExampleDB", sources)).description == "Example"
    assert (await provider.recommend("query", [])).summary == "Compare it."
    assert provider.model_name == "test-model"
    assert all(method == "json_schema" for _, method in model.calls)


@pytest.mark.asyncio
async def test_openai_provider_wraps_failure_and_timeout() -> None:
    class BrokenModel:
        def __init__(self, runnable) -> None:
            self.runnable = runnable

        def with_structured_output(self, schema, method):
            return self.runnable

    source = TOOL_SOURCES["weaviate"]
    failed = OpenAIAnalysisProvider(
        BrokenModel(FakeRunnable(error=OSError("offline"))),
        model_name="test",
    )
    with pytest.raises(ProviderError, match="failed"):
        await failed.select_tools("query", source, limit=1)

    timed = OpenAIAnalysisProvider(
        BrokenModel(FakeRunnable(value={"names": ["x"]}, delay=0.05)),
        model_name="test",
        timeout_seconds=0.001,
    )
    with pytest.raises(ProviderError, match="timed out"):
        await timed.select_tools("query", source, limit=1)
