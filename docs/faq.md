# FAQ

## Can I evaluate IntelliCrawl without API keys?

Yes. `intellicrawl demo` runs a dated, deterministic comparison through the same graph and report models as live mode. It does not call external services.

## Are demo results current recommendations?

No. They are a reproducible snapshot used to demonstrate behavior and test exports. Run live research and inspect the cited source pages for a current decision.

## Why is a report marked partial?

A profile becomes partial when a required field lacks valid source evidence. The overall report is partial when it contains a warning, such as a failed tool profile or unavailable recommendation. IntelliCrawl keeps valid evidence instead of hiding the entire run.

## Why does a value say unknown?

The available sources did not support a confident normalized value. Unknown is an intentional result, not a parsing failure.

## Where is scraped content stored?

Live mode uses a bounded local `diskcache` directory under the operating system's user cache path unless `INTELLICRAWL_CACHE_DIR` overrides it. That cache may contain public page content and should still be treated as private local data.

## Does the exported report contain scraped pages?

No. Reports contain normalized claims, evidence notes, titles, and public URLs. Full scraped content is excluded from public serialization.

## Why does CI avoid live API calls?

Provider calls cost money, vary with external availability, and are not reproducible. CI tests the adapters, orchestration, failure behavior, and deterministic providers without credentials.

## How do I force fresh source retrieval?

Use `intellicrawl research "your query" --no-cache`. You can also set `INTELLICRAWL_CACHE_TTL=0` to disable cache writes.

## Can I use another search or analysis provider?

Yes. Implement the `SearchProvider` or `AnalysisProvider` protocol in `contracts.py`, then assemble it with `ResearchPipeline`. The graph does not depend directly on Firecrawl or OpenAI.

## Is this a hosted recommendation service?

No. IntelliCrawl is a local research CLI. Review citations before using its output for procurement, security, financial, or other consequential decisions.
