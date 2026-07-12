# Security Policy

## Supported Version

Security fixes target the latest release and the `main` branch.

## Report A Vulnerability

Use GitHub's private vulnerability reporting for this repository when available. Otherwise contact the maintainer through the email listed on [ethanvillalovoz.com](https://ethanvillalovoz.com/). Do not put credentials, exploit payloads, private source content, or sensitive logs in a public issue.

Include affected versions, reproduction steps, impact, and a minimal sanitized example. You can expect an initial response within seven days.

## Trust Boundaries

Live mode sends a user query to Firecrawl and sends public source content to OpenAI for structured analysis. Review the providers' current data and retention policies before submitting sensitive information. IntelliCrawl is designed for public developer-tool research, not confidential documents.

Web content is untrusted input. Prompts tell the model to ignore instructions embedded in source text, but prompt injection defenses are not absolute. Inspect citations and avoid treating generated recommendations as executable instructions.

## Local Data

Never commit:

- `.env` files or API keys
- provider caches or raw API responses
- private source content
- unsanitized reports or logs

The local TTL cache may contain scraped page bodies. Restrict its filesystem access and delete it when no longer needed. API keys are excluded from `LiveSettings` representations.

## Defensive Behavior

- Source URLs must be public HTTP(S) URLs without embedded credentials.
- Provider calls have bounded timeouts and concurrency.
- Full scraped content is excluded from report serialization.
- Evidence IDs must resolve to the report's source list.
- CSV exports prefix formula-like cells before spreadsheet use.
- File exports use atomic replacement.

These controls reduce common risks but do not turn IntelliCrawl into a sandboxed browser or a security decision engine.
