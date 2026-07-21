# Figure contract: IntelliCrawl evidence trace

## Communication job

This figure should allow a skeptical technical reviewer to conclude that IntelliCrawl preserves field-level source traceability across parallel tool profiles because it shows the complete dated demo report, validated source IDs, failure semantics, and export boundary under the committed deterministic configuration.

## Figure form

A left-to-right provenance graph: one research question fans into three parallel profile lanes, each lane displays the local `S1`/`S2` mapping for all six normalized fields, and the validated profiles converge into one report with four export views. The terminal interface is intentionally omitted so field-to-source structure remains dominant.

## Supported claim

The `2026-07-11` deterministic fixture compares three tools through the maintained LangGraph pipeline. Each committed profile contains six normalized evidence fields backed by two validated source IDs; the complete fixture contains six public citations and no warnings. The same pipeline preserves partial profiles and explicit warnings when evidence or providers fail.

## Evidence used

- `examples/demo-report.json` for the query, snapshot date, tool profiles, source counts, evidence fields, recommendation, status, and warnings.
- `src/intellicrawl/pipeline.py` for concurrency, source-ID filtering, partial-profile behavior, neutral recommendation fallback, and graph state transitions.
- `src/intellicrawl/demo.py` for the deterministic provider assembly.
- `src/intellicrawl/renderers.py` for table, Markdown, JSON, and CSV output behavior.

## Evidence boundary

- The displayed comparison is a dated deterministic fixture, not a live crawl or current market assessment.
- The figure does not evaluate recommendation quality, retrieval quality, latency, cost, or factual correctness.
- Live mode sends public-web content to Firecrawl and OpenAI and requires a fresh user-owned run.
- Source validation establishes reference integrity inside the report; it does not independently verify every source statement.

## Selection rule

The figure uses the complete committed demo report. All three tool profiles, all six evidence fields per profile, the six-source total, the recommendation boundary, and the empty warning set are represented; no tool or failure state was selected after viewing outcomes.

## Delivery formats

- Editable source: `editable/intellicrawl-evidence-trace.pptx`
- README export: `exports/intellicrawl-evidence-trace.svg`
- Review export: `exports/intellicrawl-evidence-trace.png`
- Print/preflight export: `exports/intellicrawl-evidence-trace.pdf`
