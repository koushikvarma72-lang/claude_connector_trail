# mcp-server/connectors/slack/client.py
import httpx
from connectors.slack.config import SLACK_BOT_TOKEN, SLACK_BASE_URL

class SlackClient:
    def __init__(self):
        self.token = SLACK_BOT_TOKEN
        self.base_url = SLACK_BASE_URL.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=self.headers)
    
    def is_configured(self):
        return bool(self.token)
    
    async def post_message(self, channel: str, text: str, thread_ts: str = None):
        """Post message to channel"""
        payload = {"channel": channel, "text": text}
        if thread_ts:
            payload["thread_ts"] = thread_ts
        
        response = await self.client.post("/chat.postMessage", json=payload)
        return response.json()
    
    async def list_channels(self, types: str = "public_channel"):
        """List workspace channels"""
        response = await self.client.get(
            "/conversations.list",
            params={"types": types}
        )
        return response.json()
    
    async def get_user_info(self, user_id: str):
        """Get user details"""
        response = await self.client.get("/users.info", params={"user": user_id})
        return response.json()
    
    async def upload_file(self, channels: str, file_content: bytes, filename: str, title: str = None):
        """Upload file to channel"""
        response = await self.client.post(
            "/files.upload",
            data={
                "channels": channels,
                "filename": filename,
                "title": title or filename
            },
            files={"file": (filename, file_content)}
        )
        return response.json()
    
    async def close(self):
        await self.client.aclose()