# Contributing to IntelliCrawl

Thanks for helping improve IntelliCrawl. This project values clear agent behavior, reproducible examples, safe API-key handling, and honest documentation.

## Development Setup

```sh
git clone https://github.com/ethanvillalovoz/intellicrawl.git
cd intellicrawl
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-ci.txt
```

For live advanced-agent runs:

```sh
pip install -r advanced-agent/requirements.txt
cp advanced-agent/.env.example advanced-agent/.env
```

Add your own local API keys to `.env`. Do not commit real keys or generated cache files.

## Before Opening A Pull Request

Run:

```sh
PYTHONPATH=advanced-agent pytest tests
python -m compileall advanced-agent simple-agent tests
```

For changes that affect Firecrawl/OpenAI behavior, also run a manual live query and include:

- Query used
- Output mode
- Relevant logs or sanitized output
- Any API/provider errors

## Contribution Guidelines

- Keep pull requests focused and small.
- Preserve the existing CLI contract unless the PR clearly explains a user-facing change.
- Mock external services in tests instead of calling live APIs in CI.
- Update docs when commands, environment variables, output formats, or workflow behavior changes.
- Avoid committing `.env`, API responses, cache directories, private scraped content, or generated exports.

## Reporting Issues

Use the bug report template and include the agent path (`advanced-agent` or `simple-agent`), command, Python version, OS, dependency versions, and any relevant sanitized error output.

## Code Of Conduct

Please follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
