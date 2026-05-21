import httpx
from typing import Optional, Dict, Any

from connectors.linkedin.config import (
    LINKEDIN_CLIENT_ID,
    LINKEDIN_CLIENT_SECRET,
    LINKEDIN_ACCESS_TOKEN,
    LINKEDIN_REFRESH_TOKEN,
    LINKEDIN_REDIRECT_URI,
    LINKEDIN_BASE_URL,
    LINKEDIN_TOKEN_URL,
    LINKEDIN_AUTHORIZATION_URL,
)


def is_configured() -> bool:
    """Check if LinkedIn credentials are configured"""
    return bool(LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET)


def get_authorization_url() -> str:
    """Generate OAuth2 authorization URL"""
    scopes = [
        "r_liteprofile",
        "r_emailaddress",
        "w_member_social",
        "r_organization_social",
    ]
    
    params = {
        "response_type": "code",
        "client_id": LINKEDIN_CLIENT_ID,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "state": "random_state_string",
        "scope": " ".join(scopes),
    }
    
    import urllib.parse
    query_string = urllib.parse.urlencode(params)
    return f"{LINKEDIN_AUTHORIZATION_URL}?{query_string}"


async def exchange_code_for_token(authorization_code: str) -> Dict[str, Any]:
    """Exchange authorization code for access token"""
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "client_id": LINKEDIN_CLIENT_ID,
        "client_secret": LINKEDIN_CLIENT_SECRET,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            LINKEDIN_TOKEN_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json()


async def refresh_access_token() -> Dict[str, Any]:
    """Refresh the access token using refresh token"""
    data = {
        "grant_type": "refresh_token",
        "refresh_token": LINKEDIN_REFRESH_TOKEN,
        "client_id": LINKEDIN_CLIENT_ID,
        "client_secret": LINKEDIN_CLIENT_SECRET,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            LINKEDIN_TOKEN_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json()


class LinkedInClient:
    def __init__(self, access_token: Optional[str] = None):
        self.token = access_token or LINKEDIN_ACCESS_TOKEN
        self.base_url = LINKEDIN_BASE_URL.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=self.headers)
    
    async def get_profile(self) -> Dict[str, Any]:
        """Get current user's profile"""
        response = await self.client.get("/me")
        return response.json()
    
    async def get_profile_by_id(self, profile_id: str) -> Dict[str, Any]:
        """Get profile by profile ID"""
        response = await self.client.get(f"/people/{profile_id}")
        return response.json()
    
    async def get_email_address(self) -> Dict[str, Any]:
        """Get current user's email address"""
        response = await self.client.get("/emailAddress")
        return response.json()
    
    async def get_connections(self, count: int = 50, start: int = 0) -> Dict[str, Any]:
        """Get user's connections"""
        response = await self.client.get(
            "/connections",
            params={"count": count, "start": start}
        )
        return response.json()
    
    async def get_organization(self, organization_urn: str) -> Dict[str, Any]:
        """Get organization details"""
        response = await self.client.get(f"/organizations/{organization_urn}")
        return response.json()
    
    async def get_organization_urns(self) -> Dict[str, Any]:
        """Get organization URNs for the user"""
        response = await self.client.get("/organizationAcls")
        return response.json()
    
    async def post_share(
        self,
        author_urn: str,
        comment: str,
        title: Optional[str] = None,
        text: Optional[str] = None,
        article_url: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Post a share on LinkedIn profile or organization"""
        
        # Build the article/link share content
        content = {}
        if article_url:
            content["articleUrl"] = article_url
        if image_url:
            content["imageUrl"] = image_url
        if title:
            content["title"] = title
        
        # Build the post
        post_data = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": comment
                    },
                    "shareMediaCategory": "ARTICLE" if article_url else "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        if content:
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                "status": "READY",
                **content
            }]
        
        response = await self.client.post(
            "/ugcPosts",
            json=post_data
        )
        return response.json()
    
    async def get_posts(self, author_urn: str, count: int = 10) -> Dict[str, Any]:
        """Get posts by an author"""
        response = await self.client.get(
            "/ugcPosts",
            params={
                "q": "authors",
                "authors": f"List({author_urn})",
                "count": count
            }
        )
        return response.json()
    
    async def delete_post(self, post_urn: str) -> Dict[str, Any]:
        """Delete a post"""
        # Extract the ID from the URN
        post_id = post_urn.split(":")[-1]
        response = await self.client.delete(f"/ugcPosts/{post_id}")
        return {"status": response.status_code}
    
    async def close(self):
        await self.client.aclose()

