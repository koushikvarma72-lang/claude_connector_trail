import os

from core.config import load_connector_env

load_connector_env("github")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_BASE_URL = os.getenv("GITHUB_BASE_URL", "https://api.github.com").rstrip("/")
