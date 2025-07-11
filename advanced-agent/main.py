import logging
import argparse
from dotenv import load_dotenv
from src.workflow import Workflow
from src.logging_config import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


def main():
    """
    Main entry point for the Developer Tools Research Agent.
    Handles user input, runs the research workflow, and displays results.
    """
    parser = argparse.ArgumentParser(
        description="Developer Tools Research Agent: Analyze and compare developer tools using LLMs and Firecrawl."
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Developer tools query (e.g., 'vector database', 'CI/CD platform'). If omitted, enters interactive mode."
    )
    parser.add_argument(
        "--batch",
        type=str,
        help="Path to a file containing queries (one per line) for batch processing."
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format for results."
    )
    args = parser.parse_args()

    workflow = Workflow()
    logger.info("Developer Tools Research Agent started")

    def display_result(result, query):
        print(f"\n📊 Results for: {query}")
        print("=" * 60)
        for i, company in enumerate(result.companies, 1):
            print(f"\n{i}. 🏢 {company.name}")
            print(f"   🌐 Website: {company.website}")
            print(f"   💰 Pricing: {company.pricing_model}")
            print(f"   📖 Open Source: {company.is_open_source}")
            if company.tech_stack:
                print(f"   🛠️  Tech Stack: {', '.join(company.tech_stack[:5])}")
            if company.language_support:
                print(f"   💻 Language Support: {', '.join(company.language_support[:5])}")
            if company.api_available is not None:
                api_status = "✅ Available" if company.api_available else "❌ Not Available"
                print(f"   🔌 API: {api_status}")
            if company.integration_capabilities:
                print(f"   🔗 Integrations: {', '.join(company.integration_capabilities[:4])}")
            if company.description and company.description != "Analysis failed":
                print(f"   📝 Description: {company.description}")
            print()
        if result.analysis:
            print("Developer Recommendations: ")
            print("-" * 40)
            print(result.analysis)

    if args.batch:
        # Batch mode: read queries from file
        try:
            with open(args.batch, "r") as f:
                queries = [line.strip() for line in f if line.strip()]
            for query in queries:
                result = workflow.run(query)
                if args.output == "json":
                    print(result.json())
                else:
                    display_result(result, query)
        except Exception as e:
            logger.critical(f"Batch processing failed: {e}")
            print("Batch processing failed. See logs for details.")
    elif args.query:
        # Single query mode
        result = workflow.run(args.query)
        if args.output == "json":
            print(result.json())
        else:
            display_result(result, args.query)
    else:
        # Interactive mode
        print("Developer Tools Research Agent (interactive mode)")
        while True:
            try:
                query = input("\n🔍 Developer Tools Query: ").strip()
                if query.lower() in {"quit", "exit"}:
                    logger.info("User exited the agent.")
                    break
                if query:
                    result = workflow.run(query)
                    display_result(result, query)
            except Exception as e:
                logger.critical(f"Fatal error in main loop: {e}")
                print("A fatal error occurred. Please check the logs for details.")
                break


if __name__ == "__main__":
    main()