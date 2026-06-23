# Usage Guide

## Environment Variables

The advanced agent requires:

```text
FIRECRAWL_API_KEY=your_firecrawl_api_key
OPENAI_API_KEY=your_openai_api_key
```

Create the local file from the example:

```sh
cp advanced-agent/.env.example advanced-agent/.env
```

## Interactive Mode

```sh
cd advanced-agent
python main.py
```

Enter a developer-tool category when prompted, such as:

```text
vector databases
serverless Postgres
developer observability platforms
```

Type `quit` or `exit` to stop.

## Single Query Mode

```sh
cd advanced-agent
python main.py "authentication platforms" --output markdown
```

## Batch Mode

Create a local `queries.txt` file:

```text
vector databases
CI/CD platforms
serverless hosting
```

Then run:

```sh
cd advanced-agent
python main.py --batch queries.txt --output csv
```

## Output Formats

- `text`: colorized terminal output
- `markdown`: structured notes suitable for docs
- `json`: structured agent state
- `csv`: spreadsheet-friendly table

## Simple Agent

The simple agent requires Node.js/npm because it launches Firecrawl MCP through `npx`.

```sh
cd simple-agent
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Use this path when experimenting directly with Firecrawl MCP tools.
