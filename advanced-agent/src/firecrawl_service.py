import os
import logging
from firecrawl import FirecrawlApp, ScrapeOptions
from dotenv import load_dotenv

# Import and set up logging
from .logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


class FirecrawlService:
    """
    Service class for interacting with the Firecrawl API.
    Provides methods for searching companies and scraping company pages.
    """

    def __init__(self):
        """
        Initialize FirecrawlApp with API key from environment.
        Raises ValueError if FIRECRAWL_API_KEY is missing.
        """
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            logger.error("Missing FIRECRAWL_API_KEY environment variable")
            raise ValueError("Missing FIRECRAWL_API_KEY environment variable")
        self.app = FirecrawlApp(api_key=api_key)

    def search_companies(self, query: str, num_results: int = 5):
        """
        Search for companies related to the query and retrieve pricing info.
        Returns a list of search results in markdown format.
        """
        try:
            result = self.app.search(
                query=f"{query} company pricing",
                limit=num_results,
                scrape_options=ScrapeOptions(
                    formats=["markdown"]
                )
            )
            return result
        except ConnectionError as ce:
            logger.error(f"Network error during search_companies: {ce}")
            return []
        except Exception as e:
            logger.exception("Unexpected error in search_companies")
            return []

    def scrape_company_pages(self, url: str):
        """
        Scrape the content of a company page at the given URL.
        Returns the result in markdown format, or None if an error occurs.
        """
        try:
            result = self.app.scrape_url(
                url,
                formats=["markdown"]
            )
            return result
        except ValueError as ve:
            logger.warning(f"Invalid URL provided: {url} - {ve}")
            return None
        except Exception as e:
            logger.exception("Unexpected error in scrape_company_pages")
            return None