from mcp.server.fastmcp import FastMCP

from connectors.linkedin.client import LinkedInClient, is_configured, get_authorization_url
from core.guard import guarded_tool
from core.metrics import record_invocation


def register_linkedin_tools(mcp: FastMCP) -> None:
    """Register all LinkedIn MCP tools"""
    
    @mcp.tool()
    async def linkedin_get_authorization_url() -> dict:
        """Get the OAuth2 authorization URL for LinkedIn login."""
        if err := guarded_tool("linkedin_get_authorization_url"):
            return err

        if not is_configured():
            record_invocation("linkedin_get_authorization_url", success=False, error="not_configured")
            return {"error": "LinkedIn credentials not configured."}

        url = get_authorization_url()
        return {
            "authorization_url": url,
            "instructions": "Visit this URL to authorize the application, then copy the authorization code from the redirect URL."
        }

    @mcp.tool()
    async def linkedin_get_profile() -> dict:
        """Get the current user's LinkedIn profile information."""
        if err := guarded_tool("linkedin_get_profile"):
            return err

        if not is_configured():
            record_invocation("linkedin_get_profile", success=False, error="not_configured")
            return {"error": "LinkedIn credentials not configured."}

        client = LinkedInClient()
        
        try:
            profile = await client.get_profile()
            record_invocation("linkedin_get_profile", success=True)
            return profile
        except Exception as e:
            record_invocation("linkedin_get_profile", success=False, error=str(e))
            return {"error": str(e)}
        finally:
            await client.close()

    @mcp.tool()
    async def linkedin_get_email() -> dict:
        """Get the current user's LinkedIn email address."""
        if err := guarded_tool("linkedin_get_email"):
            return err

        if not is_configured():
            record_invocation("linkedin_get_email", success=False, error="not_configured")
            return {"error": "LinkedIn credentials not configured."}

        client = LinkedInClient()
        
        try:
            email = await client.get_email_address()
            record_invocation("linkedin_get_email", success=True)
            return email
        except Exception as e:
            record_invocation("linkedin_get_email", success=False, error=str(e))
            return {"error": str(e)}
        finally:
            await client.close()

    @mcp.tool()
    async def linkedin_get_connections(count: int = 50, start: int = 0) -> dict:
        """Get the current user's LinkedIn connections.
        
        Args:
            count: Number of connections to retrieve (default 50)
            start: Starting index for pagination (default 0)
        """
        if err := guarded_tool("linkedin_get_connections"):
            return err

        if not is_configured():
            record_invocation("linkedin_get_connections", success=False, error="not_configured")
            return {"error": "LinkedIn credentials not configured."}

        client = LinkedInClient()
        
        try:
            connections = await client.get_connections(count=count, start=start)
            record_invocation("linkedin_get_connections", success=True)
            return connections
        except Exception as e:
            record_invocation("linkedin_get_connections", success=False, error=str(e))
            return {"error": str(e)}
        finally:
            await client.close()

    @mcp.tool()
    async def linkedin_get_organization() -> dict:
        """Get the organizations (company pages) the user manages.
        
        Returns the organization URNs that the user has access to manage.
        """
        if err := guarded_tool("linkedin_get_organization"):
            return err

        if not is_configured():
            record_invocation("linkedin_get_organization", success=False, error="not_configured")
            return {"error": "LinkedIn credentials not configured."}

        client = LinkedInClient()
        
        try:
            orgs = await client.get_organization_urns()
            record_invocation("linkedin_get_organization", success=True)
            return orgs
        except Exception as e:
            record_invocation("linkedin_get_organization", success=False, error=str(e))
            return {"error": str(e)}
        finally:
            await client.close()

    @mcp.tool()
    async def linkedin_post_share(
        author_urn: str,
        comment: str,
        title: str = None,
        article_url: str = None,
        image_url: str = None
    ) -> dict:
        """Post a share (text, article, or image) on LinkedIn profile or organization.
        
        Args:
            author_urn: The LinkedIn URN of the author (e.g., 'urn:li:person:XXXXX' or 'urn:li:organization:XXXXX')
            comment: The text content of the post
            title: Optional title for article/link shares
            article_url: Optional URL to an article
            image_url: Optional URL to an image
        """
        if err := guarded_tool("linkedin_post_share"):
            return err

        if not is_configured():
            record_invocation("linkedin_post_share", success=False, error="not_configured")
            return {"error": "LinkedIn credentials not configured."}

        client = LinkedInClient()
        
        try:
            result = await client.post_share(
                author_urn=author_urn,
                comment=comment,
                title=title,
                article_url=article_url,
                image_url=image_url
            )
            record_invocation("linkedin_post_share", success=True)
            return result
        except Exception as e:
            record_invocation("linkedin_post_share", success=False, error=str(e))
            return {"error": str(e)}
        finally:
            await client.close()

    @mcp.tool()
    async def linkedin_get_posts(author_urn: str, count: int = 10) -> dict:
        """Get posts from a LinkedIn profile or organization.
        
        Args:
            author_urn: The LinkedIn URN of the author
            count: Number of posts to retrieve (default 10)
        """
        if err := guarded_tool("linkedin_get_posts"):
            return err

        if not is_configured():
            record_invocation("linkedin_get_posts", success=False, error="not_configured")
            return {"error": "LinkedIn credentials not configured."}

        client = LinkedInClient()
        
        try:
            posts = await client.get_posts(author_urn=author_urn, count=count)
            record_invocation("linkedin_get_posts", success=True)
            return posts
        except Exception as e:
            record_invocation("linkedin_get_posts", success=False, error=str(e))
            return {"error": str(e)}
        finally:
            await client.close()

    @mcp.tool()
    async def linkedin_delete_post(post_urn: str) -> dict:
        """Delete a LinkedIn post.
        
        Args:
            post_urn: The LinkedIn URN of the post to delete (e.g., 'urn:li:ugcPost:XXXXX')
        """
        if err := guarded_tool("linkedin_delete_post"):
            return err

        if not is_configured():
            record_invocation("linkedin_delete_post", success=False, error="not_configured")
            return {"error": "LinkedIn credentials not configured."}

        client = LinkedInClient()
        
        try:
            result = await client.delete_post(post_urn=post_urn)
            record_invocation("linkedin_delete_post", success=True)
            return result
        except Exception as e:
            record_invocation("linkedin_delete_post", success=False, error=str(e))
            return {"error": str(e)}
        finally:
            await client.close()

