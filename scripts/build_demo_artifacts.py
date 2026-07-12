"""Regenerate deterministic example exports from the no-key demo pipeline."""

from __future__ import annotations

import asyncio
from pathlib import Path

from intellicrawl.demo import create_demo_report
from intellicrawl.renderers import render_csv, render_json, render_markdown, write_output

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    report = asyncio.run(create_demo_report())
    examples = ROOT / "examples"
    write_output(examples / "demo-report.json", render_json(report))
    write_output(examples / "demo-report.md", render_markdown(report))
    write_output(examples / "demo-report.csv", render_csv(report))


if __name__ == "__main__":
    main()
