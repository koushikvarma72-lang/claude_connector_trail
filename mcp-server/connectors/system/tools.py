from mcp.server.fastmcp import FastMCP

from core.config import RATE_LIMIT
from core.guard import guarded_tool
from core.metrics import get_metrics_snapshot, reset_metrics


def register_system_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def get_usage_metrics() -> dict:
        """Get MCP server usage metrics."""
        if err := guarded_tool("get_usage_metrics"):
            return err

        return get_metrics_snapshot(RATE_LIMIT)

    @mcp.tool()
    async def reset_usage_metrics() -> dict:
        """Reset all usage metrics back to zero."""
        if err := guarded_tool("reset_usage_metrics"):
            return err

        return reset_metrics()
