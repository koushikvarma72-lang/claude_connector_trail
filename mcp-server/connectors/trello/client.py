import httpx

from connectors.trello.config import TRELLO_API_KEY, TRELLO_TOKEN


def has_credentials() -> bool:
    return bool(TRELLO_API_KEY and TRELLO_TOKEN)


async def list_boards() -> httpx.Response:
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
    url = "https://api.trello.com/1/members/me/boards"

    async with httpx.AsyncClient() as client:
        return await client.get(url, params=params)
