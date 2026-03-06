from mcp.server.fastmcp import FastMCP

from core.config import RATE_LIMIT
from connectors.airtable.tools import register_airtable_tools
from connectors.github.tools import register_github_tools
from connectors.system.tools import register_system_tools
from connectors.task_manager.tools import register_task_manager_tools
from connectors.trello.tools import register_trello_tools

mcp = FastMCP("Task Manager MCP")

register_github_tools(mcp)
register_airtable_tools(mcp)
register_trello_tools(mcp)
register_task_manager_tools(mcp)
register_system_tools(mcp)

if __name__ == "__main__":
    print(f"Starting MCP server - Rate limit: {RATE_LIMIT} req/min")
    mcp.run(transport="stdio")
