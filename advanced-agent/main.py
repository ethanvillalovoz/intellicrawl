import logging
import argparse
from dotenv import load_dotenv
from src.workflow import Workflow
from src.logging_config import setup_logging
import json
import csv
from io import StringIO
from colorama import Fore, Style, init
import asyncio
import re
from yaspin import yaspin

# Set up logging configuration
setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
# Initialize colorama for colored terminal output
init(autoreset=True)


def display_result(result, query, output_format="text"):
    """
    Display the research results in the specified format.
    Supports text, markdown, JSON, and CSV output.

    Args:
        result: ResearchState object containing results.
        query: The original user query.
        output_format: Output format ("text", "json", "markdown", "csv").
    """
    if output_format == "json":
        print(result.json())
        return

    if output_format == "markdown":
        print(f"# Results for: {query}\n")
        for i, company in enumerate(result.companies, 1):
            print(f"## {i}. {company.name}")
            print(f"- **Website:** {company.website}")
            print(f"- **Pricing:** {company.pricing_model}")
            print(f"- **Open Source:** {company.is_open_source}")
            if company.tech_stack:
                print(f"- **Tech Stack:** {', '.join(company.tech_stack[:5])}")
            if company.language_support:
                print(f"- **Language Support:** {', '.join(company.language_support[:5])}")
            if company.api_available is not None:
                api_status = "Available" if company.api_available else "Not Available"
                print(f"- **API:** {api_status}")
            if company.integration_capabilities:
                print(f"- **Integrations:** {', '.join(company.integration_capabilities[:4])}")
            if company.description and company.description != "Analysis failed":
                print(f"- **Description:** {company.description}")
            print()
        if result.analysis:
            print("### Developer Recommendations\n")
            print(result.analysis)
        return

    if output_format == "csv":
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Name", "Website", "Pricing", "Open Source", "Tech Stack",
            "Language Support", "API", "Integrations", "Description"
        ])
        for company in result.companies:
            writer.writerow([
                company.name,
                company.website,
                company.pricing_model,
                company.is_open_source,
                ", ".join(company.tech_stack[:5]),
                ", ".join(company.language_support[:5]),
                "Available" if company.api_available else "Not Available",
                ", ".join(company.integration_capabilities[:4]),
                company.description
            ])
        print(output.getvalue())
        if result.analysis:
            print("Developer Recommendations:")
            print(result.analysis)
        return

    # Default: colorized text output for terminal
    print(f"\n{Fore.CYAN}📊 Results for: {query}{Style.RESET_ALL}")
    print(Fore.YELLOW + "=" * 60 + Style.RESET_ALL)
    for i, company in enumerate(result.companies, 1):
        print(f"\n{Fore.GREEN}{i}. 🏢 {company.name}{Style.RESET_ALL}")
        print(f"   {Fore.BLUE}🌐 Website:{Style.RESET_ALL} {company.website}")
        print(f"   {Fore.MAGENTA}💰 Pricing:{Style.RESET_ALL} {company.pricing_model}")
        print(f"   {Fore.YELLOW}📖 Open Source:{Style.RESET_ALL} {company.is_open_source}")
        if company.tech_stack:
            print(f"   {Fore.CYAN}🛠️  Tech Stack:{Style.RESET_ALL} {', '.join(company.tech_stack[:5])}")
        if company.language_support:
            print(f"   {Fore.CYAN}💻 Language Support:{Style.RESET_ALL} {', '.join(company.language_support[:5])}")
        if company.api_available is not None:
            api_status = f"{Fore.GREEN}✅ Available{Style.RESET_ALL}" if company.api_available else f"{Fore.RED}❌ Not Available{Style.RESET_ALL}"
            print(f"   {Fore.YELLOW}🔌 API:{Style.RESET_ALL} {api_status}")
        if company.integration_capabilities:
            print(f"   {Fore.CYAN}🔗 Integrations:{Style.RESET_ALL} {', '.join(company.integration_capabilities[:4])}")
        if company.description and company.description != "Analysis failed":
            print(f"   {Fore.WHITE}📝 Description:{Style.RESET_ALL} {company.description}")
        print()
    if result.analysis:
        print(Fore.YELLOW + "Developer Recommendations:" + Style.RESET_ALL)
        print(Fore.YELLOW + "-" * 40 + Style.RESET_ALL)
        print(result.analysis)

    # Summary statistics
    num_companies = len(result.companies)
    pricing_models = [c.pricing_model for c in result.companies if c.pricing_model]
    pricing_count = {p: pricing_models.count(p) for p in set(pricing_models)}
    print(f"\n{Fore.GREEN}Summary:{Style.RESET_ALL}")
    print(f"Companies found: {num_companies}")
    print("Pricing models breakdown:")
    for model, count in pricing_count.items():
        print(f"  {model}: {count}")


def is_safe_query(query: str) -> bool:
    """
    Validate user input to allow only safe characters.

    Args:
        query: The user query string.

    Returns:
        bool: True if query is safe, False otherwise.
    """
    # Only allow letters, numbers, spaces, and basic punctuation
    return bool(re.match(r"^[\w\s\-.,/()]+$", query))


def main():
    """
    Main entry point for the Developer Tools Research Agent.
    Handles user input, runs the research workflow, and displays results.
    Supports batch, single, and interactive modes.
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
        choices=["text", "json", "markdown", "csv"],
        default="text",
        help="Output format for results."
    )
    args = parser.parse_args()

    workflow = Workflow()
    logger.info("Developer Tools Research Agent started")

    if args.batch:
        # Batch mode: read queries from file
        try:
            with open(args.batch, "r") as f:
                queries = [line.strip() for line in f if line.strip()]
            for query in queries:
                # Run workflow for each query and display results
                result = asyncio.run(workflow.run(query))
                display_result(result, query, args.output)
        except Exception as e:
            logger.critical(f"Batch processing failed: {e}")
            print("Batch processing failed. See logs for details.")
    elif args.query:
        # Single query mode
        result = asyncio.run(workflow.run(args.query))
        display_result(result, args.query, args.output)
    else:
        # Interactive mode: prompt user for queries until exit
        print("Developer Tools Research Agent (interactive mode)")
        while True:
            try:
                query = input("\n🔍 Developer Tools Query: ").strip()
                if query.lower() in {"quit", "exit"}:
                    logger.info("User exited the agent.")
                    break
                if query:
                    # Validate user input before running workflow
                    if not is_safe_query(query):
                        print("Invalid query: Only letters, numbers, spaces, and basic punctuation allowed.")
                        logger.warning(f"Blocked potentially unsafe query: {query}")
                        continue
                    # Show spinner while processing query
                    with yaspin(text="Researching...", color="cyan") as spinner:
                        result = asyncio.run(workflow.run(query))
                        spinner.ok("✅ ")
                    display_result(result, query, args.output)
            except Exception as e:
                logger.critical(f"Fatal error in main loop: {e}")
                print("A fatal error occurred. Please check the logs for details.")
                break


if __name__ == "__main__":
    main()