# IntelliCrawl system-architecture figure

This directory contains the public architecture overview and the code evidence used to construct it.

| File | Purpose |
| --- | --- |
| `contract.md` | Communication job, architecture scope, and evidence boundary |
| `provenance.json` | Input and output checksums plus source revision |
| `editable/intellicrawl-evidence-trace.pptx` | Editable composition |
| `exports/intellicrawl-evidence-trace.svg` | README-ready vector export |
| `exports/intellicrawl-evidence-trace.png` | Raster review export |
| `exports/intellicrawl-evidence-trace.pdf` | Print/preflight artifact |
| `preflight/` | PowerPoint, final-size, grayscale, and PDF checks |

The diagram traces the deterministic and live provider assemblies through their shared interfaces, LangGraph stages, typed report, renderers, and failure boundaries. It describes maintained code paths; it is not a live benchmark or a current tool comparison.
