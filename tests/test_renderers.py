import csv
import io
import json
from datetime import date

from intellicrawl.demo import create_demo_report
from intellicrawl.models import Recommendation, ResearchReport
from intellicrawl.renderers import (
    render_csv,
    render_json,
    render_markdown,
    render_report,
    render_terminal,
    write_output,
)


async def test_all_renderers_emit_inspectable_sources() -> None:
    report = await create_demo_report()
    markdown = render_markdown(report)
    payload = json.loads(render_json(report))
    rows = list(csv.DictReader(io.StringIO(render_csv(report))))
    terminal = render_terminal(report)

    assert "[S1]" in markdown
    assert "https://weaviate.io" in markdown
    assert "content" not in payload["tools"][0]["sources"][0]
    assert len(rows) == 3
    assert rows[0]["sources"].startswith("https://")
    assert "6 sources" in terminal
    assert "Recommendation" in terminal


async def test_render_dispatch_and_invalid_format() -> None:
    report = await create_demo_report()
    assert render_report(report, "json").startswith("{")
    assert render_report(report, "markdown").startswith("#")
    assert render_report(report, "csv").startswith("query,")
    assert "INTELLICRAWL" in render_report(report, "table")

    try:
        render_report(report, "xml")
    except ValueError as error:
        assert "unsupported" in str(error)
    else:
        raise AssertionError("invalid renderer did not fail")


async def test_csv_neutralizes_spreadsheet_formulas() -> None:
    report = await create_demo_report()
    dangerous_tool = report.tools[0].model_copy(update={"name": '=HYPERLINK("bad")'})
    changed = report.model_copy(update={"query": "+SUM(1,1)", "tools": [dangerous_tool]})
    row = next(csv.DictReader(io.StringIO(render_csv(changed))))
    assert row["query"].startswith("'")
    assert row["tool"].startswith("'")


def test_atomic_output_replaces_existing_file(tmp_path) -> None:
    path = tmp_path / "nested" / "report.md"
    path.parent.mkdir()
    path.write_text("old")
    assert write_output(path, "new\n") == path
    assert path.read_text() == "new\n"
    assert not list(path.parent.glob("*.tmp"))


async def test_markdown_escapes_untrusted_labels() -> None:
    report = await create_demo_report()
    tool = report.tools[0].model_copy(update={"name": "Tool | [unsafe]"})
    changed = ResearchReport(
        query="safe query",
        mode="demo",
        snapshot_date=date(2026, 7, 11),
        status="complete",
        model="fixture",
        tools=[tool],
        recommendation=Recommendation(summary="Use <evidence>.", best_for=[]),
    )
    markdown = render_markdown(changed)
    assert "Tool \\| \\[unsafe\\]" in markdown
    assert "&lt;evidence&gt;" in markdown
