# FAQ

## Which agent should I use?

Use `advanced-agent/` for the polished developer-tool comparison workflow. Use `simple-agent/` for lower-level MCP experimentation.

## Why does CI not call Firecrawl or OpenAI?

Live API calls would make CI slower, more expensive, and dependent on external service availability. CI validates deterministic models, prompt helpers, and syntax. Live integration tests should be run manually with API keys.

## Where is cached scraped data stored?

The advanced agent uses `.firecrawl_cache/` through `diskcache`. Cache directories are ignored by git because they can contain generated scraped content.

## Why does the CLI reject some characters in interactive mode?

Interactive mode includes a conservative query validator to keep terminal input simple and reduce accidental shell-like or markup-heavy input. Single-query mode currently passes the query directly.

## Can I export output to a file?

Yes. Use `--output-file` with any output format:

```sh
python main.py "vector databases" --output markdown --output-file results.md
```

For batch JSON, the output file is a valid JSON list.
