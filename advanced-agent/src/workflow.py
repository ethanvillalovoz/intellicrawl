import logging
import asyncio
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .models import ResearchState, CompanyInfo, CompanyAnalysis
from .firecrawl_service import FirecrawlService
from .prompts import DeveloperToolsPrompts
from .logging_config import setup_logging

# Set up logging for the workflow
setup_logging()
logger = logging.getLogger(__name__)

class Workflow:
    """
    Async Workflow class orchestrates the research process using Firecrawl and LLM.

    Steps:
        1. Extract relevant developer tools from articles.
        2. Research each tool/company for details.
        3. Analyze and summarize findings.
    """

    def __init__(self):
        """
        Initialize the Workflow with Firecrawl service, LLM, and prompt templates.
        Builds the workflow graph for orchestrating research steps.
        """
        self.firecrawl = FirecrawlService()  # Firecrawl API service
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)  # LLM for analysis
        self.prompts = DeveloperToolsPrompts()  # Prompt templates
        self.workflow = self._build_workflow()  # Build the workflow graph

    def _build_workflow(self):
        """
        Build the workflow graph for research steps using StateGraph.

        Returns:
            StateGraph: Compiled workflow graph.
        """
        graph = StateGraph(ResearchState)
        # Register workflow steps as nodes
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)
        graph.set_entry_point("extract_tools")  # Entry point
        # Define step transitions
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)
        return graph.compile()

    async def _extract_tools_step(self, state: ResearchState) -> Dict[str, Any]:
        """
        Step 1: Search for articles and extract developer tool names asynchronously.

        Args:
            state (ResearchState): Current research state.

        Returns:
            Dict[str, Any]: Dictionary with extracted tool names.
        """
        logger.info(f"Finding articles about: {state.query}")

        # Build article search query
        article_query = f"{state.query} tools comparison best alternatives"
        # Search for companies/tools using Firecrawl (cached)
        search_results = await self.firecrawl.search_companies_async(article_query, num_results=3)

        # Aggregate scraped content from search results for LLM context
        all_content = ""
        for result in search_results.data:
            url = result.get("url", "")
            scraped = await self.firecrawl.scrape_company_pages_async(url)
            if scraped:
                all_content += scraped.markdown[:1500] + "\n\n"

        # Prepare LLM messages for tool extraction
        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(state.query, all_content))
        ]

        # Invoke LLM to extract tool names asynchronously
        try:
            response = await self.llm.ainvoke(messages)
            tool_names = [
                name.strip()
                for name in response.content.strip().split("\n")
                if name.strip()
            ]
            logger.info(f"Extracted tools: {', '.join(tool_names[:5])}")
            return {"extracted_tools": tool_names}
        except Exception as e:
            logger.exception("Error extracting tools")
            return {"extracted_tools": []}

    async def _analyze_company_content(self, company_name: str, content: str) -> CompanyAnalysis:
        """
        Analyze scraped company content using LLM and structured output asynchronously.

        Args:
            company_name (str): Name of the company/tool.
            content (str): Scraped website content.

        Returns:
            CompanyAnalysis: Structured analysis result.
        """
        structured_llm = self.llm.with_structured_output(CompanyAnalysis)
        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_analysis_user(company_name, content))
        ]
        try:
            analysis = await structured_llm.ainvoke(messages)
            return analysis
        except Exception as e:
            logger.exception(f"Error analyzing company content for {company_name}")
            # Return default analysis if LLM fails
            return CompanyAnalysis(
                pricing_model="Unknown",
                is_open_source=None,
                tech_stack=[],
                description="Analysis failed",
                api_available=None,
                language_support=[],
                integration_capabilities=[],
            )

    async def _research_step(self, state: ResearchState) -> Dict[str, Any]:
        """
        Step 2: Research each extracted tool/company for details asynchronously.

        Args:
            state (ResearchState): Current research state.

        Returns:
            Dict[str, Any]: Dictionary with list of CompanyInfo objects.
        """
        extracted_tools = getattr(state, "extracted_tools", [])

        # Fallback to direct search if no tools extracted
        if not extracted_tools:
            logger.warning("No extracted tools found, falling back to direct search")
            search_results = await self.firecrawl.search_companies_async(state.query, num_results=4)
            tool_names = [
                result.get("metadata", {}).get("title", "Unknown")
                for result in search_results.data
            ]
        else:
            tool_names = extracted_tools[:4]

        logger.info(f"Researching specific tools: {', '.join(tool_names)}")

        companies = []
        for tool_name in tool_names:
            # Search for official site and scrape details asynchronously
            tool_search_results = await self.firecrawl.search_companies_async(tool_name + " official site", num_results=1)

            if tool_search_results:
                result = tool_search_results.data[0]
                url = result.get("url", "")

                # Create CompanyInfo object with initial data
                company = CompanyInfo(
                    name=tool_name,
                    description=result.get("markdown", ""),
                    website=url,
                    tech_stack=[],
                    competitors=[]
                )

                # Scrape company page for more details
                scraped = await self.firecrawl.scrape_company_pages_async(url)
                if scraped:
                    content = scraped.markdown
                    analysis = await self._analyze_company_content(company.name, content)

                    # Populate company info with analysis results
                    company.pricing_model = analysis.pricing_model
                    company.is_open_source = analysis.is_open_source
                    company.tech_stack = analysis.tech_stack
                    company.description = analysis.description
                    company.api_available = analysis.api_available
                    company.language_support = analysis.language_support
                    company.integration_capabilities = analysis.integration_capabilities

                companies.append(company)

        return {"companies": companies}

    async def _analyze_step(self, state: ResearchState) -> Dict[str, Any]:
        """
        Step 3: Generate recommendations based on researched companies asynchronously.

        Args:
            state (ResearchState): Current research state.

        Returns:
            Dict[str, Any]: Dictionary with analysis/recommendation string.
        """
        logger.info("Generating recommendations")

        # Serialize company data for LLM input
        company_data = ", ".join([
            company.json() for company in state.companies
        ])

        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(content=self.prompts.recommendations_user(state.query, company_data))
        ]

        try:
            response = await self.llm.ainvoke(messages)
            return {"analysis": response.content}
        except Exception as e:
            logger.exception("Error generating recommendations")
            return {"analysis": "Analysis failed due to an error."}

    async def run(self, query: str) -> ResearchState:
        """
        Run the async workflow for a given user query.

        Args:
            query (str): The user's research query.

        Returns:
            ResearchState: Final research state with all results.
        """
        initial_state = ResearchState(query=query)
        try:
            # Run the workflow graph asynchronously
            final_state = await self.workflow.ainvoke(initial_state)
            return ResearchState(**final_state)
        except Exception as e:
            logger.critical(f"Workflow failed for query '{query}': {e}")
            return ResearchState(query=query)