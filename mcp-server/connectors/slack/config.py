import os
from core.config import load_connector_env

load_connector_env("slack")

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_BASE_URL = os.getenv("SLACK_BASE_URL", "https://slack.com/api")