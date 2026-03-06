import httpx

from connectors.airtable.config import AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, AIRTABLE_TOKEN


def has_credentials() -> bool:
    return bool(AIRTABLE_TOKEN and AIRTABLE_BASE_ID and AIRTABLE_TABLE_NAME)


async def list_records() -> httpx.Response:
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

    async with httpx.AsyncClient() as client:
        return await client.get(url, headers=headers)
