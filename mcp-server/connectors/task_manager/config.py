import os

from core.config import BACKEND_URL as DEFAULT_BACKEND_URL, load_connector_env

load_connector_env("task_manager")

BACKEND_URL = os.getenv("TASK_MANAGER_BACKEND_URL", DEFAULT_BACKEND_URL).rstrip("/")
