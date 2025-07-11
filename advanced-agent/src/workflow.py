import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .models import ResearchState, CompanyInfo, CompanyAnalysis
from .firecrawl_service import FirecrawlService
from .prompts import DeveloperToolsPrompts
from .logging_config import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

class Workflow:
    """
    Workflow class orchestrates the research process using Firecrawl and LLM.
    Steps:
        1. Extract relevant developer tools from articles.
        2. Research each tool/company for details.
        3. Analyze and summarize findings.
    """

    def __init__(self):
        # Initialize Firecrawl API service, LLM, and prompt templates
        self.firecrawl = FirecrawlService()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        self.prompts = DeveloperToolsPrompts()
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        """
        Build the workflow graph for research steps.
        """
        graph = StateGraph(ResearchState)
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)
        graph.set_entry_point("extract_tools")
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)
        return graph.compile()

    def _extract_tools_step(self, state: ResearchState) -> Dict[str, Any]:
        logger.info(f"Finding articles about: {state.query}")

        # Formulate search query for articles
        article_query = f"{state.query} tools comparison best alternatives"
        search_results = self.firecrawl.search_companies(article_query, num_results=3)

        # Aggregate scraped content from search results
        all_content = ""
        for result in search_results.data:
            url = result.get("url", "")
            scraped = self.firecrawl.scrape_company_pages(url)
            if scraped:
                all_content += scraped.markdown[:1500] + "\n\n"

        # Prepare LLM messages for tool extraction
        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(state.query, all_content))
        ]

        # Invoke LLM to extract tool names
        try:
            response = self.llm.invoke(messages)
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

    def _analyze_company_content(self, company_name: str, content: str) -> CompanyAnalysis:
        """
        Analyze scraped company content using LLM and structured output.
        """
        structured_llm = self.llm.with_structured_output(CompanyAnalysis)

        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_analysis_user(company_name, content))
        ]

        try:
            analysis = structured_llm.invoke(messages)
            return analysis
        except Exception as e:
            logger.exception(f"Error analyzing company content for {company_name}")
            return CompanyAnalysis(
                pricing_model="Unknown",
                is_open_source=None,
                tech_stack=[],
                description="Analysis failed",
                api_available=None,
                language_support=[],
                integration_capabilities=[],
            )

    def _research_step(self, state: ResearchState) -> Dict[str, Any]:
        """
        Step 2: Research each extracted tool/company for details.
        """
        extracted_tools = getattr(state, "extracted_tools", [])

        # Fallback to direct search if no tools extracted
        if not extracted_tools:
            logger.warning("No extracted tools found, falling back to direct search")
            search_results = self.firecrawl.search_companies(state.query, num_results=4)
            tool_names = [
                result.get("metadata", {}).get("title", "Unknown")
                for result in search_results.data
            ]
        else:
            tool_names = extracted_tools[:4]

        logger.info(f"Researching specific tools: {', '.join(tool_names)}")

        companies = []
        for tool_name in tool_names:
            # Search for official site and scrape details
            tool_search_results = self.firecrawl.search_companies(tool_name + " official site", num_results=1)

            if tool_search_results:
                result = tool_search_results.data[0]
                url = result.get("url", "")

                company = CompanyInfo(
                    name=tool_name,
                    description=result.get("markdown", ""),
                    website=url,
                    tech_stack=[],
                    competitors=[]
                )

                scraped = self.firecrawl.scrape_company_pages(url)
                if scraped:
                    content = scraped.markdown
                    analysis = self._analyze_company_content(company.name, content)

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

    def _analyze_step(self, state: ResearchState) -> Dict[str, Any]:
        """
        Step 3: Generate recommendations based on researched companies.
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
            response = self.llm.invoke(messages)
            return {"analysis": response.content}
        except Exception as e:
            logger.exception("Error generating recommendations")
            return {"analysis": "Analysis failed due to an error."}

    def run(self, query: str) -> ResearchState:
        """
        Run the workflow for a given user query.
        Returns the final research state.
        """
        initial_state = ResearchState(query=query)
        try:
            final_state = self.workflow.invoke(initial_state)
            return ResearchState(**final_state)
        except Exception as e:
            logger.critical(f"Workflow failed for query '{query}': {e}")
            return ResearchState(query=query)