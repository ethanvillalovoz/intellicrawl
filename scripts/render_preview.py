"""Render the deterministic CLI output as a terminal capture."""

from __future__ import annotations

import io
import json
from pathlib import Path

import matplotlib.font_manager as font_manager
from PIL import Image, ImageDraw, ImageFont
from rich.console import Console

from intellicrawl.models import ResearchReport
from intellicrawl.renderers import render_terminal

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "media" / "intellicrawl-evidence.png"
WIDTH, HEIGHT = 1440, 900
MONO_PATH = font_manager.findfont("DejaVu Sans Mono")


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(MONO_PATH, size=size)


def main() -> None:
    payload = json.loads((ROOT / "examples" / "demo-report.json").read_text())
    report = ResearchReport.model_validate(payload)
    stream = io.StringIO()
    console = Console(record=True, width=112, color_system=None, file=stream)
    render_terminal(report, console)
    terminal_output = console.export_text().rstrip()

    canvas = Image.new("RGB", (WIDTH, HEIGHT), "#0d1117")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, WIDTH, 50), fill="#161b22")
    for x, color in ((22, "#ff5f57"), (48, "#febc2e"), (74, "#28c840")):
        draw.ellipse((x, 18, x + 13, 31), fill=color)
    draw.text((112, 15), "intellicrawl — demo", fill="#8b949e", font=font(15))

    draw.text((28, 78), "$", fill="#58a6ff", font=font(18))
    draw.text((52, 78), "intellicrawl demo --format table", fill="#e6edf3", font=font(18))
    draw.line((28, 116, WIDTH - 28, 116), fill="#30363d", width=1)
    draw.multiline_text(
        (28, 142),
        terminal_output,
        fill="#d7dde5",
        font=font(17),
        spacing=8,
    )
    draw.text(
        (28, HEIGHT - 34),
        "deterministic demo  ·  six source records  ·  no API keys",
        fill="#8b949e",
        font=font(14),
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT, optimize=True)
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
