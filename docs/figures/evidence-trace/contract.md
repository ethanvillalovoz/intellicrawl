# Figure contract: IntelliCrawl system architecture

## Communication job

This figure should let a technical reviewer reconstruct how IntelliCrawl swaps deterministic and live providers without changing its orchestration, then follows one typed LangGraph from discovery through parallel research, recommendation, and serialization.

## Figure form

A left-to-right system architecture: provider assemblies implement two narrow interfaces; the shared graph executes `discover -> research -> recommend`; a strict `ResearchReport` crosses the public boundary into four renderers. Validation and degraded-run behavior sit beneath the execution path rather than inside a UI screenshot.

## Visual encoding

The figure uses a warm editorial palette: green and orange distinguish provider assemblies, forest marks the shared graph, plum marks synthesis, and ochre marks the typed output. Every role is also named, so the architecture remains legible without color.

## Supported claim

Demo and live assemblies implement the same search and analysis contracts. The maintained graph discovers and deduplicates one to six tools, profiles them concurrently, rejects unknown source IDs, preserves partial results as warnings, synthesizes a recommendation with a neutral fallback, and serializes a strict report whose scraped bodies remain private.

## Evidence used

- `src/intellicrawl/pipeline.py` for graph stages, fan-out, source-ID filtering, partial profiles, and recommendation fallback.
- `src/intellicrawl/contracts.py` for the replaceable search and analysis interfaces.
- `src/intellicrawl/demo.py`, `src/intellicrawl/live.py`, and `src/intellicrawl/providers.py` for deterministic and live assemblies, caching, and bounded provider behavior.
- `src/intellicrawl/models.py` and `src/intellicrawl/renderers.py` for strict report schemas and terminal, Markdown, JSON, and CSV outputs.

## Evidence boundary

- The figure documents maintained control flow; it is not evidence from a live crawl or a current market assessment.
- It does not evaluate recommendation quality, retrieval quality, latency, cost, or factual correctness.
- Live mode sends public-web content to Firecrawl and OpenAI and requires a fresh user-owned run.
- Source validation establishes reference integrity inside the report; it does not independently verify every source statement.

## Scope rule

Only branches and boundaries verified in maintained source are shown. No benchmark values, provider outcomes, or inferred infrastructure are introduced.

## Delivery formats

- Editable source: `editable/intellicrawl-evidence-trace.pptx`
- README export: `exports/intellicrawl-evidence-trace.svg`
- Review export: `exports/intellicrawl-evidence-trace.png`
- Print/preflight export: `exports/intellicrawl-evidence-trace.pdf`
