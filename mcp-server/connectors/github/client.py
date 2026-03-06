import httpx

from connectors.github.config import GITHUB_BASE_URL, GITHUB_TOKEN


def has_credentials() -> bool:
    return bool(GITHUB_TOKEN and GITHUB_BASE_URL)


async def list_repositories() -> httpx.Response:
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    async with httpx.AsyncClient() as client:
        return await client.get(f"{GITHUB_BASE_URL}/user/repos", headers=headers)
