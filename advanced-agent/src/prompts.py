class DeveloperToolsPrompts:
    """
    Collection of prompt templates for analyzing developer tools and technologies.
    Includes system and user prompts for extraction, analysis, and recommendations.
    """

    # -----------------------------------------------------------
    # Tool Extraction Prompts
    # -----------------------------------------------------------

    # System prompt for tool extraction
    TOOL_EXTRACTION_SYSTEM = (
        "You are a tech researcher. Extract specific tool, library, platform, or service names from articles.\n"
        "Focus on actual products/tools that developers can use, not general concepts or features."
    )

    @staticmethod
    def tool_extraction_user(query: str, content: str) -> str:
        """
        User prompt for extracting tool/service names from article content.
        Returns a formatted string with extraction instructions and example.
        """
        return (
            f"Query: {query}\n"
            f"Article Content: {content}\n\n"
            "Extract a list of specific tool/service names mentioned in this content that are relevant to "
            f"\"{query}\".\n\n"
            "Rules:\n"
            "- Only include actual product names, not generic terms\n"
            "- Focus on tools developers can directly use/implement\n"
            "- Include both open source and commercial options\n"
            "- Limit to the 5 most relevant tools\n"
            "- Return just the tool names, one per line, no descriptions\n\n"
            "Example format:\n"
            "Supabase\n"
            "PlanetScale\n"
            "Railway\n"
            "Appwrite\n"
            "Nhost"
        )

    # -----------------------------------------------------------
    # Company/Tool Analysis Prompts
    # -----------------------------------------------------------

    # System prompt for company/tool analysis
    TOOL_ANALYSIS_SYSTEM = (
        "You are analyzing developer tools and programming technologies.\n"
        "Focus on extracting information relevant to programmers and software developers.\n"
        "Pay special attention to programming languages, frameworks, APIs, SDKs, and development workflows."
    )

    @staticmethod
    def tool_analysis_user(company_name: str, content: str) -> str:
        """
        User prompt for analyzing a company/tool from website content.
        Returns a formatted string with analysis instructions and required fields.
        """
        return (
            f"Company/Tool: {company_name}\n"
            f"Website Content: {content[:2500]}\n\n"
            "Analyze this content from a developer's perspective and provide:\n"
            "- pricing_model: One of \"Free\", \"Freemium\", \"Paid\", \"Enterprise\", or \"Unknown\"\n"
            "- is_open_source: true if open source, false if proprietary, null if unclear\n"
            "- tech_stack: List of programming languages, frameworks, databases, APIs, or technologies supported/used\n"
            "- description: Brief 1-sentence description focusing on what this tool does for developers\n"
            "- api_available: true if REST API, GraphQL, SDK, or programmatic access is mentioned\n"
            "- language_support: List of programming languages explicitly supported (e.g., Python, JavaScript, Go, etc.)\n"
            "- integration_capabilities: List of tools/platforms it integrates with (e.g., GitHub, VS Code, Docker, AWS, etc.)\n\n"
            "Focus on developer-relevant features like APIs, SDKs, language support, integrations, and development workflows."
        )

    # -----------------------------------------------------------
    # Recommendation Prompts
    # -----------------------------------------------------------

    # System prompt for recommendations
    RECOMMENDATIONS_SYSTEM = (
        "You are a senior software engineer providing quick, concise tech recommendations.\n"
        "Keep responses brief and actionable - maximum 3-4 sentences total."
    )

    @staticmethod
    def recommendations_user(query: str, company_data: str) -> str:
        """
        User prompt for generating developer tool recommendations.
        Returns a formatted string with recommendation instructions.
        """
        return (
            f"Developer Query: {query}\n"
            f"Tools/Technologies Analyzed: {company_data}\n\n"
            "Provide a brief recommendation (3-4 sentences max) covering:\n"
            "- Which tool is best and why\n"
            "- Key cost/pricing consideration\n"
            "- Main technical advantage\n\n"
            "Be concise and direct - no long explanations needed."
        )