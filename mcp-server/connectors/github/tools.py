from mcp.server.fastmcp import FastMCP

from connectors.github.client import has_credentials, list_repositories
from core.guard import guarded_tool
from core.metrics import record_invocation


def register_github_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def github_list_repos() -> dict:
        """List repositories for the authenticated GitHub user."""
        if err := guarded_tool("github_list_repos"):
            return err

        if not has_credentials():
            record_invocation("github_list_repos", success=False, error="missing_credentials")
            return {"error": "GitHub credentials not configured."}

        response = await list_repositories()
        if response.status_code != 200:
            record_invocation("github_list_repos", success=False, error=f"http_{response.status_code}")
            return {"error": response.text}

        repos = response.json()
        return {
            "count": len(repos),
            "repositories": [{"name": r["name"], "full_name": r["full_name"]} for r in repos],
        }
