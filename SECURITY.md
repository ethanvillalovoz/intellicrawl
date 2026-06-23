# Security Policy

## Supported Scope

IntelliCrawl is a portfolio/research project that calls external APIs. Security reports should focus on API-key handling, dependency issues, unsafe file handling, cache leakage, prompt/data exposure, or behavior that could surprise users running the CLI locally.

## Secrets

Do not commit `.env` files, API keys, Firecrawl caches, OpenAI request/response logs, scraped private content, or generated output that contains sensitive data. The repository includes `.env.example` files only.

## External Services

The advanced agent sends user queries and scraped web content to OpenAI for analysis and uses Firecrawl for search/scraping. Users should avoid submitting private or confidential information unless they understand the external service policies involved.

## Reporting

Open a GitHub issue with reproduction steps, affected files, dependency versions, and any relevant logs. Do not include secrets or private scraped data in public issues.
