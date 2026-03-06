from mcp.server.fastmcp import FastMCP

from connectors.trello.client import has_credentials, list_boards
from core.guard import guarded_tool
from core.metrics import record_invocation


def register_trello_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def trello_list_boards() -> dict:
        """List all Trello boards for the authenticated user."""
        if err := guarded_tool("trello_list_boards"):
            return err

        if not has_credentials():
            record_invocation("trello_list_boards", success=False, error="missing_credentials")
            return {"error": "Trello credentials not configured."}

        response = await list_boards()
        if response.status_code != 200:
            record_invocation("trello_list_boards", success=False, error=f"http_{response.status_code}")
            return {"error": response.text}

        boards = response.json()
        return {
            "count": len(boards),
            "boards": [{"id": b["id"], "name": b["name"]} for b in boards],
        }
