import os
import logging
from firecrawl import FirecrawlApp, ScrapeOptions
from dotenv import load_dotenv
import diskcache
import asyncio

# Import and set up logging
from .logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize diskcache for persistent caching of API responses
cache = diskcache.Cache("./.firecrawl_cache")


class FirecrawlService:
    """
    Service class for interacting with the Firecrawl API.
    Provides methods for searching companies and scraping company pages.
    Supports both synchronous and asynchronous operations.
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
        Synchronously search for companies related to the query and retrieve pricing info.
        Uses diskcache to avoid redundant API requests.
        Returns a list of search results in markdown format.
        """
        cache_key = f"search:{query}:{num_results}"
        if cache_key in cache:
            logger.info(f"Cache hit for search_companies: {cache_key}")
            return cache[cache_key]
        try:
            result = self.app.search(
                query=f"{query} company pricing",
                limit=num_results,
                scrape_options=ScrapeOptions(formats=["markdown"])
            )
            cache[cache_key] = result
            logger.info(f"Cache set for search_companies: {cache_key}")
            return result
        except Exception as e:
            logger.exception("Unexpected error in search_companies")
            return []

    def scrape_company_pages(self, url: str):
        """
        Synchronously scrape the content of a company page at the given URL.
        Uses diskcache to avoid redundant API requests.
        Returns the result in markdown format, or None if an error occurs.
        """
        cache_key = f"scrape:{url}"
        if cache_key in cache:
            logger.info(f"Cache hit for scrape_company_pages: {cache_key}")
            return cache[cache_key]
        try:
            result = self.app.scrape_url(
                url,
                formats=["markdown"]
            )
            cache[cache_key] = result
            logger.info(f"Cache set for scrape_company_pages: {cache_key}")
            return result
        except Exception as e:
            logger.exception("Unexpected error in scrape_company_pages")
            return None

    async def search_companies_async(self, query: str, num_results: int = 5):
        """
        Asynchronously call the synchronous search method.
        """
        return self.search_companies(query, num_results)

    async def scrape_company_pages_async(self, url: str):
        """
        Asynchronously call the synchronous scrape method.
        """
        return self.scrape_company_pages(url)