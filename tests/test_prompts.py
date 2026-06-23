from src.prompts import DeveloperToolsPrompts


def test_tool_extraction_prompt_includes_query_and_content():
    prompt = DeveloperToolsPrompts.tool_extraction_user(
        "vector databases",
        "The article compares Pinecone and Weaviate.",
    )

    assert "vector databases" in prompt
    assert "Pinecone and Weaviate" in prompt
    assert "Return just the tool names" in prompt


def test_analysis_prompt_truncates_long_content():
    content = "x" * 3000
    prompt = DeveloperToolsPrompts.tool_analysis_user("ExampleTool", content)
    prompt_content = prompt.split("Website Content: ", 1)[1].split("\n\n", 1)[0]

    assert "Company/Tool: ExampleTool" in prompt
    assert prompt_content == "x" * 2500


def test_recommendations_prompt_is_concise():
    prompt = DeveloperToolsPrompts.recommendations_user(
        "serverless hosting",
        "Vercel, Netlify",
    )

    assert "3-4 sentences max" in prompt
    assert "serverless hosting" in prompt
