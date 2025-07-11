import logging
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
    workflow = Workflow()
    logger.info("Developer Tools Research Agent started")
    print("Developer Tools Research Agent")

    while True:
        try:
            # Prompt user for a developer tools query
            query = input("\n🔍 Developer Tools Query: ").strip()
            if query.lower() in {"quit", "exit"}:
                logger.info("User exited the agent.")
                break

            if query:
                # Run the research workflow for the user's query
                result = workflow.run(query)
                print(f"\n📊 Results for: {query}")
                print("=" * 60)

                # Display information for each researched company/tool
                for i, company in enumerate(result.companies, 1):
                    print(f"\n{i}. 🏢 {company.name}")
                    print(f"   🌐 Website: {company.website}")
                    print(f"   💰 Pricing: {company.pricing_model}")
                    print(f"   📖 Open Source: {company.is_open_source}")

                    # Show tech stack if available
                    if company.tech_stack:
                        print(f"   🛠️  Tech Stack: {', '.join(company.tech_stack[:5])}")

                    # Show supported programming languages if available
                    if company.language_support:
                        print(
                            f"   💻 Language Support: {', '.join(company.language_support[:5])}"
                        )

                    # Show API availability status
                    if company.api_available is not None:
                        api_status = (
                            "✅ Available" if company.api_available else "❌ Not Available"
                        )
                        print(f"   🔌 API: {api_status}")

                    # Show integration capabilities if available
                    if company.integration_capabilities:
                        print(
                            f"   🔗 Integrations: {', '.join(company.integration_capabilities[:4])}"
                        )

                    # Show company/tool description if available and valid
                    if company.description and company.description != "Analysis failed":
                        print(f"   📝 Description: {company.description}")

                    print()  # Blank line for readability

                # Display developer recommendations if available
                if result.analysis:
                    print("Developer Recommendations: ")
                    print("-" * 40)
                    print(result.analysis)
        except Exception as e:
            logger.critical(f"Fatal error in main loop: {e}")
            print("A fatal error occurred. Please check the logs for details.")
            break


if __name__ == "__main__":
    main()