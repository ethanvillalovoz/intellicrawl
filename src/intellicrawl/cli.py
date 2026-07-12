"""Scriptable command-line interface for demo and live research modes."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from rich.console import Console

from intellicrawl import __version__
from intellicrawl.demo import create_demo_report
from intellicrawl.live import build_live_pipeline
from intellicrawl.pipeline import ResearchError
from intellicrawl.renderers import render_report, render_terminal, write_output
from intellicrawl.settings import LiveSettings


def _add_output_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--format",
        choices=("table", "markdown", "json", "csv"),
        default="table",
        dest="output_format",
    )
    parser.add_argument("--output", type=Path, help="atomically write the result to this path")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="intellicrawl",
        description="Source-backed developer-tool research.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    demo = commands.add_parser("demo", help="run the deterministic no-key walkthrough")
    _add_output_arguments(demo)

    research = commands.add_parser("research", help="run live Firecrawl and OpenAI research")
    research.add_argument("query", help="developer-tool category or comparison question")
    research.add_argument("--no-cache", action="store_true", help="disable the local source cache")
    _add_output_arguments(research)
    return parser


async def _run(args: argparse.Namespace):
    if args.command == "demo":
        return await create_demo_report()

    try:
        from dotenv import load_dotenv
    except ImportError as error:
        raise RuntimeError('live research requires: pip install -e ".[live]"') from error
    load_dotenv()
    settings = LiveSettings.from_environment()
    pipeline = build_live_pipeline(settings, use_cache=not args.no_cache)
    return await pipeline.run(args.query)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    console = Console()
    error_console = Console(stderr=True)
    try:
        report = asyncio.run(_run(args))
        if args.output:
            content = render_report(report, args.output_format)
            destination = write_output(args.output, content)
            console.print(f"Saved {args.output_format} report to {destination}")
        elif args.output_format == "table":
            render_terminal(report, console)
        else:
            sys.stdout.write(render_report(report, args.output_format))
        return 0
    except (ResearchError, RuntimeError, ValueError) as error:
        error_console.print(f"intellicrawl: {error}")
        return 2
    except KeyboardInterrupt:
        error_console.print("intellicrawl: interrupted")
        return 130


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
