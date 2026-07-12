"""Terminal and file renderers for validated research reports."""

from __future__ import annotations

import csv
import io
import json
import os
import tempfile
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from intellicrawl.models import Availability, ResearchReport, ToolReport


def _availability(value: Availability) -> str:
    return {"yes": "Yes", "no": "No", "unknown": "Unknown"}[value]


def _markdown(value: object) -> str:
    text = str(value)
    for source, replacement in (
        ("\\", "\\\\"),
        ("|", "\\|"),
        ("[", "\\["),
        ("]", "\\]"),
        ("<", "&lt;"),
        (">", "&gt;"),
    ):
        text = text.replace(source, replacement)
    return text


def _csv_cell(value: object) -> str:
    text = str(value)
    if text.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + text
    return text


def render_json(report: ResearchReport) -> str:
    return json.dumps(report.model_dump(mode="json"), indent=2) + "\n"


def _citations(tool: ToolReport, field: str) -> str:
    ids: list[str] = []
    for evidence in tool.evidence:
        if evidence.field == field:
            ids.extend(evidence.source_ids)
    return " ".join(f"[{source_id}]" for source_id in dict.fromkeys(ids))


def render_markdown(report: ResearchReport) -> str:
    lines = [
        f"# {_markdown(report.query)}",
        "",
        (
            f"**Mode:** {_markdown(report.mode)}  "
            f"**Snapshot:** {report.snapshot_date.isoformat()}  "
            f"**Status:** {_markdown(report.status)}"
        ),
        "",
        "| Tool | Pricing | Open source | API | Sources |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for tool in report.tools:
        lines.append(
            "| "
            + " | ".join(
                (
                    _markdown(tool.name),
                    _markdown(tool.pricing_model),
                    _availability(tool.is_open_source),
                    _availability(tool.api_available),
                    str(len(tool.sources)),
                )
            )
            + " |"
        )

    for tool in report.tools:
        lines.extend(
            [
                "",
                f"## {_markdown(tool.name)}",
                "",
                f"{_markdown(tool.description)} {_citations(tool, 'description')}".rstrip(),
                "",
                f"- **Website:** {tool.website}",
                (
                    f"- **Pricing:** {_markdown(tool.pricing_model)} "
                    f"{_citations(tool, 'pricing_model')}"
                ).rstrip(),
                (
                    f"- **Open source:** {_availability(tool.is_open_source)} "
                    f"{_citations(tool, 'is_open_source')}"
                ).rstrip(),
                (
                    f"- **API:** {_availability(tool.api_available)} "
                    f"{_citations(tool, 'api_available')}"
                ).rstrip(),
                f"- **Languages:** {_markdown(', '.join(tool.language_support) or 'Unknown')}",
                f"- **Integrations:** {_markdown(', '.join(tool.integrations) or 'Unknown')}",
                "",
                "**Sources**",
                "",
            ]
        )
        for source in tool.sources:
            lines.append(f"- [{source.source_id}] [{_markdown(source.title)}]({source.url})")

    lines.extend(["", "## Recommendation", "", _markdown(report.recommendation.summary)])
    if report.recommendation.best_for:
        lines.extend(["", "**Best fit**", ""])
        lines.extend(f"- {_markdown(item)}" for item in report.recommendation.best_for)
    if report.warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {_markdown(warning)}" for warning in report.warnings)
    return "\n".join(lines).rstrip() + "\n"


def render_csv(report: ResearchReport) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        (
            "query",
            "tool",
            "website",
            "pricing",
            "open_source",
            "api",
            "languages",
            "integrations",
            "description",
            "sources",
            "status",
        )
    )
    for tool in report.tools:
        writer.writerow(
            tuple(
                _csv_cell(value)
                for value in (
                    report.query,
                    tool.name,
                    tool.website,
                    tool.pricing_model,
                    tool.is_open_source,
                    tool.api_available,
                    ", ".join(tool.language_support),
                    ", ".join(tool.integrations),
                    tool.description,
                    " ".join(str(source.url) for source in tool.sources),
                    tool.status,
                )
            )
        )
    return output.getvalue()


def render_terminal(report: ResearchReport, console: Console | None = None) -> str:
    target = console or Console(record=True, width=120, color_system=None)
    target.print(Text("INTELLICRAWL / SOURCE-BACKED DEVELOPER TOOL RESEARCH", style="dim"))
    target.print(Text(report.query, style="bold"))
    target.print(
        Text(
            f"{report.mode} mode  /  {report.snapshot_date.isoformat()}  /  "
            f"{report.source_count} sources",
            style="dim",
        )
    )
    target.print()

    table = Table(show_header=True, header_style="bold", box=None, pad_edge=False)
    table.add_column("Tool", min_width=16)
    table.add_column("Pricing", min_width=11)
    table.add_column("Open", min_width=8)
    table.add_column("API", min_width=8)
    table.add_column("Evidence", justify="right")
    for tool in report.tools:
        table.add_row(
            Text(tool.name),
            Text(tool.pricing_model),
            Text(_availability(tool.is_open_source)),
            Text(_availability(tool.api_available)),
            Text(str(len(tool.sources))),
        )
    target.print(table)
    target.print()

    for tool in report.tools:
        target.print(Text(tool.name, style="bold"), Text(f"  {tool.website}", style="dim"))
        target.print(Text(tool.description))
        source_line = "  ".join(f"[{source.source_id}] {source.title}" for source in tool.sources)
        target.print(Text(source_line, style="dim"))
        target.print()

    target.print(
        Panel(Text(report.recommendation.summary), title="Recommendation", border_style="blue")
    )
    if report.warnings:
        target.print(Text("Warnings", style="bold yellow"))
        for warning in report.warnings:
            target.print(Text(f"- {warning}", style="yellow"))
    if console is not None:
        return ""
    return target.export_text()


def render_report(report: ResearchReport, output_format: str) -> str:
    if output_format == "json":
        return render_json(report)
    if output_format == "markdown":
        return render_markdown(report)
    if output_format == "csv":
        return render_csv(report)
    if output_format == "table":
        return render_terminal(report)
    raise ValueError(f"unsupported output format: {output_format}")


def write_output(path: str | Path, content: str) -> Path:
    """Atomically replace an export so interrupted runs do not leave partial files."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
        text=True,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, destination)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise
    return destination
