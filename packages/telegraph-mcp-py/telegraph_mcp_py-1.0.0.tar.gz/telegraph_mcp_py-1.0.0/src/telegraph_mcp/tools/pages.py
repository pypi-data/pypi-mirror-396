"""Page management tools."""

from typing import Optional
from telegraph import Telegraph


def register_page_tools(mcp):
    """Register page-related tools."""

    @mcp.tool()
    def telegraph_create_page(
        access_token: str,
        title: str,
        content: str,
        format: str = "html",
        author_name: Optional[str] = None,
        author_url: Optional[str] = None,
        return_content: bool = False
    ) -> dict:
        """
        Create a new Telegraph page.

        Args:
            access_token: Access token of the Telegraph account
            title: Page title (1-256 characters)
            content: Page content (HTML or Markdown string)
            format: Content format - "html" or "markdown" (default: "html")
            author_name: Author name (0-128 characters)
            author_url: Profile link (0-512 characters)
            return_content: If True, content field will be returned

        Returns:
            Page object with URL
        """
        client = Telegraph(access_token=access_token)
        page = client.create_page(
            title=title,
            content=content,
            author_name=author_name,
            author_url=author_url,
            return_content=return_content,
            content_format=format
        )
        result = {
            "path": page.path,
            "url": page.url,
            "title": page.title,
            "description": page.description,
            "views": page.views,
            "author_name": page.author_name,
            "author_url": page.author_url,
        }
        if return_content and page.content:
            result["content"] = page.content
        return result

    @mcp.tool()
    def telegraph_edit_page(
        access_token: str,
        path: str,
        title: str,
        content: str,
        format: str = "html",
        author_name: Optional[str] = None,
        author_url: Optional[str] = None,
        return_content: bool = False
    ) -> dict:
        """
        Edit an existing Telegraph page.

        Args:
            access_token: Access token of the Telegraph account
            path: Path to the page (e.g., "Sample-Page-12-15")
            title: New page title (1-256 characters)
            content: New page content (HTML or Markdown string)
            format: Content format - "html" or "markdown" (default: "html")
            author_name: Author name (0-128 characters)
            author_url: Profile link (0-512 characters)
            return_content: If True, content field will be returned

        Returns:
            Updated Page object
        """
        client = Telegraph(access_token=access_token)
        page = client.edit_page(
            path=path,
            title=title,
            content=content,
            author_name=author_name,
            author_url=author_url,
            return_content=return_content,
            content_format=format
        )
        result = {
            "path": page.path,
            "url": page.url,
            "title": page.title,
            "description": page.description,
            "views": page.views,
        }
        if return_content and page.content:
            result["content"] = page.content
        return result

    @mcp.tool()
    def telegraph_get_page(
        path: str,
        return_content: bool = False
    ) -> dict:
        """
        Get a Telegraph page by its path.

        Args:
            path: Path to the Telegraph page (e.g., "Sample-Page-12-15")
            return_content: If True, content field will be returned

        Returns:
            Page object
        """
        client = Telegraph()
        page = client.get_page(path, return_content=return_content)
        result = {
            "path": page.path,
            "url": page.url,
            "title": page.title,
            "description": page.description,
            "views": page.views,
            "author_name": page.author_name,
            "author_url": page.author_url,
        }
        if return_content and page.content:
            result["content"] = page.content
        return result

    @mcp.tool()
    def telegraph_get_page_list(
        access_token: str,
        offset: int = 0,
        limit: int = 50
    ) -> dict:
        """
        Get a list of pages belonging to a Telegraph account.

        Args:
            access_token: Access token of the Telegraph account
            offset: Sequential number of the first page (default: 0)
            limit: Number of pages to return (0-200, default: 50)

        Returns:
            PageList object with total_count and pages array
        """
        client = Telegraph(access_token=access_token)
        page_list = client.get_page_list(offset=offset, limit=limit)
        return {
            "total_count": page_list.total_count,
            "pages": [
                {
                    "path": p.path,
                    "url": p.url,
                    "title": p.title,
                    "views": p.views,
                }
                for p in page_list.pages
            ]
        }

    @mcp.tool()
    def telegraph_get_views(
        path: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: Optional[int] = None
    ) -> dict:
        """
        Get the number of views for a Telegraph page.

        Args:
            path: Path to the Telegraph page
            year: Required if month is passed (2000-2100)
            month: Required if day is passed (1-12)
            day: Required if hour is passed (1-31)
            hour: Pass to get views for a specific hour (0-24)

        Returns:
            Object with views count
        """
        client = Telegraph()
        views = client.get_views(
            path=path,
            year=year,
            month=month,
            day=day,
            hour=hour
        )
        return {"views": views.views}
