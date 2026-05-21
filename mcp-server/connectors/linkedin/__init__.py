# mcp-server/connectors/linkedin/__init__.py
from connectors.linkedin.client import LinkedInClient, is_configured
from connectors.linkedin.tools import register_linkedin_tools

__all__ = ["LinkedInClient", "is_configured", "register_linkedin_tools"]

# Import configuration variables
from connectors.linkedin.config import (
    LINKEDIN_CLIENT_ID,
    LINKEDIN_CLIENT_SECRET,
    LINKEDIN_ACCESS_TOKEN,
    LINKEDIN_REFRESH_TOKEN,
    LINKEDIN_REDIRECT_URI,
    LINKEDIN_BASE_URL,
)

