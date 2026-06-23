# Changelog

## Unreleased

## [1.1.0] - 2026-06-23

- Added `--output-file` support for text, Markdown, JSON, and CSV output.
- Added sanitized Markdown, JSON, and CSV examples.
- Added deterministic rendering/output tests and kept CI free of live Firecrawl/OpenAI calls.
- Lazily import the live workflow so output rendering can be tested without external agent dependencies.

## [1.0.0] - 2026-06-23

- Rewrote the public README around the actual advanced/simple agent structure.
- Replaced automatic release-on-push workflow with deterministic CI.
- Added lightweight tests, CI dependencies, architecture docs, usage guide, FAQ, security policy, and code of conduct.
- Removed generated Firecrawl cache files from version control.
- Hardened Pydantic model defaults and Firecrawl async wrappers without changing the public CLI workflow.
