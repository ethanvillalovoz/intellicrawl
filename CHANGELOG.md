# Changelog

All notable changes to IntelliCrawl are documented here.

## [Unreleased]

## [2.0.0] - 2026-07-11

### Added

- One installable `intellicrawl` package and CLI.
- Deterministic no-key demo that exercises the production graph.
- Field-level evidence records and strict source-reference validation.
- Atomic Markdown, JSON, and CSV exports with committed examples.
- Animated, reproducible README preview.
- Provider, pipeline, CLI, renderer, prompt, settings, and model tests with a 90% coverage gate.

### Changed

- Replaced the split advanced/simple prototypes with one LangGraph pipeline and replaceable provider contracts.
- Updated the live integration to the current Firecrawl Python SDK and OpenAI structured output.
- Made query validation, timeouts, concurrency, partial-result behavior, and error exit codes consistent.
- Rebuilt documentation, automation, and contributor guidance around the new architecture.

### Security

- Reject obvious local, private, reserved, and credential-bearing source URLs.
- Keep full scraped content out of serialized reports.
- Treat source text as untrusted prompt data.
- Neutralize spreadsheet formulas in CSV exports.

### Migration

The old `advanced-agent/main.py` and `simple-agent/main.py` entry points were removed. Install the package and use `intellicrawl demo` or `intellicrawl research` instead.

## [1.1.0] - 2026-06-23

- Added file exports and sanitized examples to the original advanced agent.
- Added deterministic rendering tests.

## [1.0.0] - 2026-06-23

- Added baseline CI, documentation, tests, cache hygiene, and security guidance to the original two-agent repository.

[Unreleased]: https://github.com/ethanvillalovoz/intellicrawl/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/ethanvillalovoz/intellicrawl/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/ethanvillalovoz/intellicrawl/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/ethanvillalovoz/intellicrawl/releases/tag/v1.0.0
