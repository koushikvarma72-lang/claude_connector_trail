from mcp.server.fastmcp import FastMCP

from connectors.airtable.client import has_credentials, list_records
from core.guard import guarded_tool
from core.metrics import record_invocation


def register_airtable_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def airtable_list_records() -> dict:
        """List records from the configured Airtable table."""
        if err := guarded_tool("airtable_list_records"):
            return err

        if not has_credentials():
            record_invocation("airtable_list_records", success=False, error="missing_credentials")
            return {"error": "Airtable credentials not configured."}

        response = await list_records()
        if response.status_code != 200:
            record_invocation("airtable_list_records", success=False, error=f"http_{response.status_code}")
            return {"error": response.text}

        data = response.json()
        return {
            "count": len(data.get("records", [])),
            "records": data.get("records", []),
        }
