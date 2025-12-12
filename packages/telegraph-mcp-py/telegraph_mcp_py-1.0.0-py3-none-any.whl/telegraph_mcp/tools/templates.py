"""Template tools."""

from typing import Optional, Dict, Any
from telegraph import Telegraph, list_templates, create_from_template, nodes_to_json


def register_template_tools(mcp):
    """Register template-related tools."""

    @mcp.tool()
    def telegraph_list_templates() -> list:
        """
        List all available page templates with their fields.

        Returns:
            List of available templates with their names, descriptions, and required fields
        """
        templates = list_templates()
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "fields": t["fields"]
            }
            for t in templates
        ]

    @mcp.tool()
    def telegraph_create_from_template(
        access_token: str,
        template: str,
        title: str,
        data: Dict[str, Any],
        author_name: Optional[str] = None,
        author_url: Optional[str] = None,
        return_content: bool = False
    ) -> dict:
        """
        Create a new Telegraph page using a template.

        Available templates:
        - blog_post: Blog post with intro, sections, and conclusion
        - documentation: Technical documentation with overview, installation, usage, API reference
        - article: Article with subtitle, body paragraphs
        - changelog: Version changelog with added/changed/fixed sections
        - tutorial: Step-by-step tutorial with prerequisites and steps

        Args:
            access_token: Access token of the Telegraph account
            template: Template name (blog_post, documentation, article, changelog, tutorial)
            title: Page title
            data: Template data fields (varies by template)
            author_name: Author name
            author_url: Author URL
            return_content: If True, content will be returned

        Returns:
            Page object with URL
        """
        # Generate content from template
        nodes = create_from_template(template, data)
        content_json = nodes_to_json(nodes)

        client = Telegraph(access_token=access_token)
        page = client.create_page(
            title=title,
            content=content_json,
            author_name=author_name,
            author_url=author_url,
            return_content=return_content
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
