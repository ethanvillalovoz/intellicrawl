import json

from main import render_batch_results, render_result, write_output_file
from src.models import CompanyInfo, ResearchState


def sample_state():
    return ResearchState(
        query="vector databases",
        companies=[
            CompanyInfo(
                name="Weaviate",
                description="Open-source vector database for semantic search and retrieval-augmented generation.",
                website="https://weaviate.io",
                pricing_model="Freemium",
                is_open_source=True,
                tech_stack=["Python", "Go", "GraphQL"],
                api_available=True,
                language_support=["Python", "JavaScript", "Go"],
                integration_capabilities=["OpenAI", "Hugging Face", "LangChain"],
            )
        ],
        analysis="Use Weaviate when you want an open-source vector database with strong developer integrations.",
    )


def test_render_markdown_result():
    output = render_result(sample_state(), "vector databases", "markdown", colorize=False)

    assert "# Results for: vector databases" in output
    assert "## 1. Weaviate" in output
    assert "- **Pricing:** Freemium" in output
    assert "### Developer Recommendations" in output


def test_render_json_result_is_valid_json():
    output = render_result(sample_state(), "vector databases", "json", colorize=False)
    payload = json.loads(output)

    assert payload["query"] == "vector databases"
    assert payload["companies"][0]["name"] == "Weaviate"


def test_render_batch_json_result_is_valid_json_array():
    output = render_batch_results(
        [("vector databases", sample_state())],
        "json",
        colorize=False,
    )
    payload = json.loads(output)

    assert payload[0]["query"] == "vector databases"
    assert payload[0]["result"]["companies"][0]["name"] == "Weaviate"


def test_render_batch_csv_includes_query_column():
    output = render_batch_results(
        [("vector databases", sample_state())],
        "csv",
        colorize=False,
    )

    assert output.startswith("Query,Name,Website")
    assert "vector databases,Weaviate,https://weaviate.io" in output


def test_write_output_file_creates_parent_directories(tmp_path):
    output_file = tmp_path / "exports" / "result.md"

    write_output_file(output_file, "# Example\n")

    assert output_file.read_text(encoding="utf-8") == "# Example\n"
