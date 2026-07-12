from intellicrawl.demo import TOOL_SOURCES
from intellicrawl.prompts import (
    SYSTEM_GUARD,
    analysis_prompt,
    recommendation_prompt,
    selection_prompt,
    source_context,
)


def test_source_context_is_bounded_and_identified() -> None:
    source = TOOL_SOURCES["weaviate"][0].model_copy(update={"content": "x" * 10_000})
    context = source_context([source], per_source_chars=100)
    assert 'id="S1"' in context
    assert "x" * 101 not in context


def test_prompts_treat_sources_as_evidence() -> None:
    sources = TOOL_SOURCES["weaviate"]
    selection = selection_prompt("vector databases", sources, 3)
    analysis = analysis_prompt("Weaviate", sources)
    assert "at most 3" in selection
    assert "Allowed source IDs: S1, S2" in analysis
    assert "untrusted external data" in SYSTEM_GUARD


async def test_recommendation_prompt_uses_validated_profiles() -> None:
    from intellicrawl.demo import create_demo_report

    report = await create_demo_report()
    prompt = recommendation_prompt(report.query, report.tools)
    assert "Weaviate" in prompt
    assert "Do not introduce new facts" in prompt
