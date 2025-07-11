from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# -----------------------------------------------------------
# CompanyAnalysis: Output structure for LLM company analysis
# -----------------------------------------------------------
class CompanyAnalysis(BaseModel):
    """
    Structured output for LLM company analysis focused on developer tools.
    """
    pricing_model: str  # Free, Freemium, Paid, Enterprise, Unknown
    is_open_source: Optional[bool] = None  # Whether the tool is open source
    tech_stack: List[str] = []            # Technologies used by the company/tool
    description: str = ""                 # Brief description of the company/tool
    api_available: Optional[bool] = None  # Whether an API is available
    language_support: List[str] = []      # Supported programming languages
    integration_capabilities: List[str] = []  # Supported integrations

# -----------------------------------------------------------
# CompanyInfo: General company information and developer fields
# -----------------------------------------------------------
class CompanyInfo(BaseModel):
    """
    General company information, including developer-focused fields.
    """
    name: str                             # Company name
    description: str                      # Company description
    website: str                          # Company website URL
    pricing_model: Optional[str] = None   # Pricing model (optional)
    is_open_source: Optional[bool] = None # Open source status (optional)
    tech_stack: List[str] = []            # Technologies used
    competitors: List[str] = []           # List of competitors

    # Developer-specific fields
    api_available: Optional[bool] = None          # API availability
    language_support: List[str] = []              # Supported languages
    integration_capabilities: List[str] = []      # Integration options
    developer_experience_rating: Optional[str] = None  # Poor, Good, Excellent

# -----------------------------------------------------------
# ResearchState: State object for research workflow
# -----------------------------------------------------------
class ResearchState(BaseModel):
    """
    State object for tracking research workflow and results.
    """
    query: str                                   # User's research query
    extracted_tools: List[str] = []              # Tools extracted from articles
    companies: List[CompanyInfo] = []            # List of company info objects
    search_results: List[Dict[str, Any]] = []    # Raw search results
    analysis: Optional[str] = None               # Final analysis output