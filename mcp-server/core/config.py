import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)

_loaded_connector_envs: set[str] = set()


def load_connector_env(connector_name: str) -> None:
    if connector_name in _loaded_connector_envs:
        return

    connector_env_path = PROJECT_ROOT / f".env.{connector_name}"
    if connector_env_path.exists():
        load_dotenv(dotenv_path=connector_env_path, override=False)

    _loaded_connector_envs.add(connector_name)

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "https://task-manager-backend-production-1f80.up.railway.app",
).rstrip("/")
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MIN", 30))
