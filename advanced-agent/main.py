import logging
import argparse
from dotenv import load_dotenv
from src.logging_config import setup_logging
import json
import csv
from io import StringIO
from pathlib import Path
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


def _model_to_dict(model):
    """Return a plain dictionary for Pydantic v1 or v2 models."""
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return json.loads(model.json())


def _model_to_json(model):
    """Return formatted JSON for Pydantic v1 or v2 models."""
    if hasattr(model, "model_dump_json"):
        return model.model_dump_json(indent=2)
    return model.json(indent=2)


def render_result(result, query, output_format="text", colorize=True):
    """
    Render research results in the specified format.
    Supports text, markdown, JSON, and CSV output.

    Args:
        result: ResearchState object containing results.
        query: The original user query.
        output_format: Output format ("text", "json", "markdown", "csv").
        colorize: Whether text output should include terminal colors.

    Returns:
        str: Rendered output.
    """
    if output_format == "json":
        return _model_to_json(result)

    if output_format == "markdown":
        lines = [f"# Results for: {query}", ""]
        for i, company in enumerate(result.companies, 1):
            lines.append(f"## {i}. {company.name}")
            lines.append(f"- **Website:** {company.website}")
            lines.append(f"- **Pricing:** {company.pricing_model}")
            lines.append(f"- **Open Source:** {company.is_open_source}")
            if company.tech_stack:
                lines.append(f"- **Tech Stack:** {', '.join(company.tech_stack[:5])}")
            if company.language_support:
                lines.append(f"- **Language Support:** {', '.join(company.language_support[:5])}")
            if company.api_available is not None:
                api_status = "Available" if company.api_available else "Not Available"
                lines.append(f"- **API:** {api_status}")
            if company.integration_capabilities:
                lines.append(f"- **Integrations:** {', '.join(company.integration_capabilities[:4])}")
            if company.description and company.description != "Analysis failed":
                lines.append(f"- **Description:** {company.description}")
            lines.append("")
        if result.analysis:
            lines.extend(["### Developer Recommendations", "", result.analysis])
        return "\n".join(lines).rstrip() + "\n"

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
        if result.analysis:
            writer.writerow([])
            writer.writerow(["Developer Recommendations", result.analysis])
        return output.getvalue()

    # Default: text output for terminal or plain files.
    cyan = Fore.CYAN if colorize else ""
    yellow = Fore.YELLOW if colorize else ""
    green = Fore.GREEN if colorize else ""
    blue = Fore.BLUE if colorize else ""
    magenta = Fore.MAGENTA if colorize else ""
    red = Fore.RED if colorize else ""
    white = Fore.WHITE if colorize else ""
    reset = Style.RESET_ALL if colorize else ""

    lines = [
        f"",
        f"{cyan}📊 Results for: {query}{reset}",
        yellow + "=" * 60 + reset,
    ]
    for i, company in enumerate(result.companies, 1):
        lines.append(f"\n{green}{i}. 🏢 {company.name}{reset}")
        lines.append(f"   {blue}🌐 Website:{reset} {company.website}")
        lines.append(f"   {magenta}💰 Pricing:{reset} {company.pricing_model}")
        lines.append(f"   {yellow}📖 Open Source:{reset} {company.is_open_source}")
        if company.tech_stack:
            lines.append(f"   {cyan}🛠️  Tech Stack:{reset} {', '.join(company.tech_stack[:5])}")
        if company.language_support:
            lines.append(f"   {cyan}💻 Language Support:{reset} {', '.join(company.language_support[:5])}")
        if company.api_available is not None:
            api_status = f"{green}✅ Available{reset}" if company.api_available else f"{red}❌ Not Available{reset}"
            lines.append(f"   {yellow}🔌 API:{reset} {api_status}")
        if company.integration_capabilities:
            lines.append(f"   {cyan}🔗 Integrations:{reset} {', '.join(company.integration_capabilities[:4])}")
        if company.description and company.description != "Analysis failed":
            lines.append(f"   {white}📝 Description:{reset} {company.description}")
    if result.analysis:
        lines.append(yellow + "Developer Recommendations:" + reset)
        lines.append(yellow + "-" * 40 + reset)
        lines.append(result.analysis)

    # Summary statistics
    num_companies = len(result.companies)
    pricing_models = [c.pricing_model for c in result.companies if c.pricing_model]
    pricing_count = {p: pricing_models.count(p) for p in set(pricing_models)}
    lines.append(f"\n{green}Summary:{reset}")
    lines.append(f"Companies found: {num_companies}")
    lines.append("Pricing models breakdown:")
    for model, count in pricing_count.items():
        lines.append(f"  {model}: {count}")
    return "\n".join(lines).rstrip() + "\n"


def render_batch_results(results, output_format="text", colorize=False):
    """
    Render multiple query results for a single output file.

    JSON output is emitted as a valid list. Other formats are separated by rules.
    """
    if output_format == "json":
        payload = [
            {"query": query, "result": _model_to_dict(result)}
            for query, result in results
        ]
        return json.dumps(payload, indent=2)

    if output_format == "csv":
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Query", "Name", "Website", "Pricing", "Open Source", "Tech Stack",
            "Language Support", "API", "Integrations", "Description", "Recommendation"
        ])
        for query, result in results:
            for company in result.companies:
                writer.writerow([
                    query,
                    company.name,
                    company.website,
                    company.pricing_model,
                    company.is_open_source,
                    ", ".join(company.tech_stack[:5]),
                    ", ".join(company.language_support[:5]),
                    "Available" if company.api_available else "Not Available",
                    ", ".join(company.integration_capabilities[:4]),
                    company.description,
                    result.analysis or "",
                ])
        return output.getvalue()

    separator = "\n\n---\n\n" if output_format in {"markdown", "text"} else "\n"
    return separator.join(
        render_result(result, query, output_format, colorize=colorize).rstrip()
        for query, result in results
    ) + "\n"


def display_result(result, query, output_format="text"):
    """Display rendered research results to stdout."""
    print(render_result(result, query, output_format, colorize=True), end="")


def write_output_file(output_file, content):
    """Write rendered output to disk, creating parent directories if needed."""
    path = Path(output_file)
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"Saved output to {path}")


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
    parser.add_argument(
        "--output-file",
        type=str,
        help="Optional path to write rendered output. Existing files are overwritten."
    )
    args = parser.parse_args()

    from src.workflow import Workflow

    workflow = Workflow()
    logger.info("Developer Tools Research Agent started")

    if args.batch:
        # Batch mode: read queries from file
        try:
            with open(args.batch, "r") as f:
                queries = [line.strip() for line in f if line.strip()]
            batch_results = []
            for query in queries:
                # Run workflow for each query and display results
                result = asyncio.run(workflow.run(query))
                if args.output_file:
                    batch_results.append((query, result))
                else:
                    display_result(result, query, args.output)
            if args.output_file:
                content = render_batch_results(batch_results, args.output, colorize=False)
                write_output_file(args.output_file, content)
        except Exception as e:
            logger.critical(f"Batch processing failed: {e}")
            print("Batch processing failed. See logs for details.")
    elif args.query:
        # Single query mode
        result = asyncio.run(workflow.run(args.query))
        if args.output_file:
            content = render_result(result, args.query, args.output, colorize=False)
            write_output_file(args.output_file, content)
        else:
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
                    if args.output_file:
                        content = render_result(result, query, args.output, colorize=False)
                        write_output_file(args.output_file, content)
                    else:
                        display_result(result, query, args.output)
            except Exception as e:
                logger.critical(f"Fatal error in main loop: {e}")
                print("A fatal error occurred. Please check the logs for details.")
                break


if __name__ == "__main__":
    main()
