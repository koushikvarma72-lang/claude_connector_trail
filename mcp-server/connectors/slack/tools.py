# mcp-server/connectors/slack/tools.py
from mcp.types import Tool
from connectors.slack.client import SlackClient, is_configured

def get_tools() -> list[Tool]:
    """Return list of Slack MCP tools"""
    if not is_configured():
        return []
    
    return [
        Tool(
            name="slack_post_message",
            description="Send a message to a Slack channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "description": "Channel ID or name (e.g., #general or C123456)"
                    },
                    "text": {
                        "type": "string",
                        "description": "Message text to send"
                    },
                    "thread_ts": {
                        "type": "string",
                        "description": "Optional thread timestamp to reply in thread"
                    }
                },
                "required": ["channel", "text"]
            }
        ),
        Tool(
            name="slack_list_channels",
            description="List all channels in the Slack workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "types": {
                        "type": "string",
                        "description": "Channel types: public_channel, private_channel, mpim, im",
                        "default": "public_channel"
                    }
                }
            }
        ),
        Tool(
            name="slack_get_channel_info",
            description="Get detailed information about a specific channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Channel ID (e.g., C123456)"
                    }
                },
                "required": ["channel_id"]
            }
        ),
        Tool(
            name="slack_get_user_info",
            description="Get information about a Slack user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID (e.g., U123456)"
                    }
                },
                "required": ["user_id"]
            }
        )
    ]

async def execute_tool(name: str, arguments: dict):
    """Execute a Slack tool by name"""
    client = SlackClient()
    
    try:
        if name == "slack_post_message":
            return await client.post_message(
                channel=arguments["channel"],
                text=arguments["text"],
                thread_ts=arguments.get("thread_ts")
            )
        
        elif name == "slack_list_channels":
            return await client.list_channels(
                types=arguments.get("types", "public_channel")
            )
        
        elif name == "slack_get_channel_info":
            return await client.get_channel_info(
                channel_id=arguments["channel_id"]
            )
        
        elif name == "slack_get_user_info":
            return await client.get_user_info(
                user_id=arguments["user_id"]
            )
        
        else:
            raise ValueError(f"Unknown Slack tool: {name}")
    
    finally:
        await client.close()