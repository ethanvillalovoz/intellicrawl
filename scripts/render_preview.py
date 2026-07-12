"""Render the animated README preview from the deterministic report artifact."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib.font_manager as font_manager
from PIL import Image, ImageDraw, ImageFont

from intellicrawl.models import ResearchReport

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1200, 675
BACKGROUND = "#f4f4f2"
PANEL = "#ffffff"
INK = "#171717"
MUTED = "#6b6b67"
LINE = "#d8d8d4"
BLUE = "#2563eb"
GREEN = "#138a62"
CORAL = "#d95d45"
FONT_PATH = font_manager.findfont("DejaVu Sans")


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size=size)


def base_scene(kicker: str, title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.text((70, 52), kicker.upper(), fill=MUTED, font=font(18))
    draw.text((70, 86), title, fill=INK, font=font(42))
    draw.text((70, 145), subtitle, fill=MUTED, font=font(21))
    return image, draw


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    draw.rounded_rectangle(box, radius=8, fill=PANEL, outline=LINE, width=2)


def pipeline_scene(progress: int) -> Image.Image:
    image, draw = base_scene(
        "IntelliCrawl",
        "vector databases for production RAG",
        "A comparison is only useful when every claim can be inspected.",
    )
    stages = (
        ("01", "Discover", "Search public sources"),
        ("02", "Profile", "Normalize tool claims"),
        ("03", "Compare", "Preserve source evidence"),
    )
    for index, (number, title, detail) in enumerate(stages):
        x = 70 + index * 374
        panel(draw, (x, 236, x + 330, 466))
        active = index <= progress
        color = (BLUE, GREEN, CORAL)[index] if active else "#b8b8b2"
        draw.rounded_rectangle((x + 28, 270, x + 76, 318), radius=7, fill=color)
        draw.text((x + 40, 282), number, fill="#ffffff", font=font(15))
        draw.text((x + 28, 346), title, fill=INK if active else MUTED, font=font(28))
        draw.text((x + 28, 392), detail, fill=MUTED, font=font(18))
        if index < 2:
            draw.line((x + 330, 351, x + 374, 351), fill=LINE, width=3)
    draw.text((70, 535), "LIVE", fill=GREEN, font=font(17))
    draw.text((130, 535), "Firecrawl + OpenAI", fill=INK, font=font(17))
    draw.text((390, 535), "DEMO", fill=BLUE, font=font(17))
    draw.text((460, 535), "same pipeline, no API keys", fill=INK, font=font(17))
    return image


def source_scene(report: ResearchReport) -> Image.Image:
    image, draw = base_scene(
        "Source collection",
        f"{report.source_count} sources / {len(report.tools)} tool profiles",
        "Scraped content stays private; citations remain in every exported report.",
    )
    colors = (BLUE, GREEN, CORAL)
    for index, tool in enumerate(report.tools):
        x = 70 + index * 374
        panel(draw, (x, 232, x + 330, 516))
        draw.text((x + 26, 266), tool.name, fill=INK, font=font(29))
        for line_index, line in enumerate(textwrap.wrap(tool.description, width=32)[:3]):
            draw.text((x + 26, 309 + line_index * 22), line, fill=MUTED, font=font(16))
        for source_index, source in enumerate(tool.sources):
            y = 390 + source_index * 58
            draw.rounded_rectangle((x + 26, y, x + 64, y + 38), radius=5, fill=colors[index])
            draw.text((x + 35, y + 9), source.source_id, fill="#ffffff", font=font(14))
            title = source.title[:27]
            draw.text((x + 78, y + 8), title, fill=INK, font=font(16))
    return image


def comparison_scene(report: ResearchReport) -> Image.Image:
    image, draw = base_scene(
        "Normalized comparison",
        "Decisions without the terminal noise",
        "Unknown stays unknown; partial evidence is visible instead of silently filled in.",
    )
    panel(draw, (70, 222, 1128, 548))
    columns = (70, 350, 560, 760, 950)
    headers = ("Tool", "Pricing", "Open source", "API", "Sources")
    for x, header in zip(columns, headers, strict=True):
        draw.text((x + 24, 254), header, fill=MUTED, font=font(17))
    draw.line((94, 296, 1104, 296), fill=LINE, width=2)
    for row, tool in enumerate(report.tools):
        y = 330 + row * 66
        draw.text((94, y), tool.name, fill=INK, font=font(23))
        draw.text((374, y + 2), tool.pricing_model, fill=INK, font=font(19))
        draw.text((584, y + 2), tool.is_open_source.title(), fill=INK, font=font(19))
        draw.text((784, y + 2), tool.api_available.title(), fill=INK, font=font(19))
        draw.text(
            (974, y + 2), str(len(tool.sources)), fill=(BLUE, GREEN, CORAL)[row], font=font(21)
        )
        if row < len(report.tools) - 1:
            draw.line((94, y + 48, 1104, y + 48), fill="#ecece8", width=1)
    return image


def recommendation_scene(report: ResearchReport) -> Image.Image:
    image, draw = base_scene(
        "Recommendation",
        "Derived from the validated profiles",
        "The report keeps the decision brief and the evidence close.",
    )
    panel(draw, (70, 224, 1128, 520))
    lines = (
        "Choose Pinecone when a fully managed path is the priority.",
        "Choose Weaviate or Qdrant when deployment flexibility matters.",
        "Compare operations and client ecosystems against the workload.",
    )
    for index, line in enumerate(lines):
        y = 272 + index * 58
        draw.rounded_rectangle((100, y, 110, y + 31), radius=3, fill=(BLUE, GREEN, CORAL)[index])
        draw.text((134, y - 2), line, fill=INK, font=font(22))
    draw.text((100, 456), "Snapshot", fill=MUTED, font=font(17))
    draw.text((190, 456), report.snapshot_date.isoformat(), fill=INK, font=font(17))
    draw.text((370, 456), "Status", fill=MUTED, font=font(17))
    draw.text((432, 456), report.status, fill=GREEN, font=font(17))
    draw.text((570, 456), "Export", fill=MUTED, font=font(17))
    draw.text((632, 456), "Markdown / JSON / CSV", fill=INK, font=font(17))
    return image


def main() -> None:
    payload = json.loads((ROOT / "examples" / "demo-report.json").read_text())
    report = ResearchReport.model_validate(payload)
    scenes = [
        pipeline_scene(0),
        pipeline_scene(1),
        pipeline_scene(2),
        source_scene(report),
        comparison_scene(report),
        recommendation_scene(report),
    ]
    output = ROOT / "docs" / "media" / "intellicrawl-preview.webp"
    output.parent.mkdir(parents=True, exist_ok=True)
    scenes[0].save(
        output,
        save_all=True,
        append_images=scenes[1:],
        duration=[800, 650, 650, 1_600, 1_600, 1_800],
        loop=0,
        quality=82,
        method=6,
    )


if __name__ == "__main__":
    main()
