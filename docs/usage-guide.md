# Usage Guide

## Install

IntelliCrawl requires Python 3.11 or newer.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

The base install supports deterministic demo mode:

```sh
intellicrawl demo
```

## Live Configuration

Install the optional provider dependencies and create a local environment file:

```sh
python -m pip install -e ".[live]"
cp .env.example .env
```

Required variables:

```text
FIRECRAWL_API_KEY=fc-your-key
OPENAI_API_KEY=sk-your-key
```

Optional controls:

| Variable | Default | Constraint |
| --- | ---: | --- |
| `INTELLICRAWL_OPENAI_MODEL` | `gpt-5.4-mini` | non-empty model name |
| `INTELLICRAWL_CACHE_TTL` | `86400` | zero or more seconds |
| `INTELLICRAWL_TIMEOUT` | `60` | positive seconds |
| `INTELLICRAWL_MAX_TOOLS` | `4` | 1 through 6 |
| `INTELLICRAWL_CONCURRENCY` | `3` | 1 through 8 |
| `INTELLICRAWL_CACHE_DIR` | platform user cache | writable local path |

`LiveSettings` validates these values before constructing any provider. API keys are omitted from its representation.

## Research

```sh
intellicrawl research "authentication providers for a B2B SaaS"
```

Queries are whitespace-normalized and must contain 3 to 180 characters. The same validation applies to every invocation path.

Bypass cached source results when freshness matters:

```sh
intellicrawl research "serverless Postgres" --no-cache
```

## Output Formats

| Format | Command | Intended use |
| --- | --- | --- |
| Terminal | `--format table` | interactive inspection |
| Markdown | `--format markdown` | notes and decision records |
| JSON | `--format json` | typed downstream processing |
| CSV | `--format csv` | spreadsheet comparison |

Without `--output`, non-table formats write only machine-readable data to standard output:

```sh
intellicrawl demo --format json | jq '.tools[].name'
```

Write any format to disk:

```sh
intellicrawl research "observability platforms" \
  --format json \
  --output reports/observability.json
```

Parent directories are created automatically. The destination is replaced atomically after a complete write.

## Exit Codes

| Code | Meaning |
| ---: | --- |
| `0` | report completed, including reports marked partial |
| `2` | invalid configuration, invalid input, or research failure |
| `130` | interrupted by the user |

Warnings inside a report identify incomplete profiles or unavailable synthesis without discarding valid results.

## Reproduce The Public Report Artifacts

```sh
python -m pip install -e ".[dev]"
python scripts/build_demo_artifacts.py
```

Generated report examples live in `examples/`. The README demonstration in `docs/media/` is a real macOS Terminal capture of `intellicrawl demo`, retained separately from deterministic report generation so the project never presents a drawn terminal as runtime evidence.
