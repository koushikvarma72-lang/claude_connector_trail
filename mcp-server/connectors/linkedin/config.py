import os

from core.config import load_connector_env

load_connector_env("linkedin")

# LinkedIn OAuth2 Configuration
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_REFRESH_TOKEN = os.getenv("LINKEDIN_REFRESH_TOKEN")
LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:3000/callback")
LINKEDIN_BASE_URL = os.getenv("LINKEDIN_BASE_URL", "https://api.linkedin.com/v2")
LINKEDIN_AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

