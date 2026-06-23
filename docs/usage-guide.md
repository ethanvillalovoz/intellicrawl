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

To write the rendered result directly to disk:

```sh
python main.py "authentication platforms" --output markdown --output-file ../exports/auth-platforms.md
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

Batch output can also be written to a single file:

```sh
python main.py --batch queries.txt --output json --output-file ../exports/research-batch.json
```

## Output Formats

- `text`: colorized terminal output
- `markdown`: structured notes suitable for docs
- `json`: structured agent state
- `csv`: spreadsheet-friendly table

Use `--output-file` with any format. For batch JSON, IntelliCrawl writes a valid JSON list where each item contains the query and result. For batch CSV, IntelliCrawl writes a single table with a `Query` column.

## Example Outputs

- [Markdown sample](../examples/sample-output.md)
- [JSON sample](../examples/sample-output.json)
- [CSV sample](../examples/sample-output.csv)

## Simple Agent

The simple agent requires Node.js/npm because it launches Firecrawl MCP through `npx`.

```sh
cd simple-agent
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Use this path when experimenting directly with Firecrawl MCP tools.
