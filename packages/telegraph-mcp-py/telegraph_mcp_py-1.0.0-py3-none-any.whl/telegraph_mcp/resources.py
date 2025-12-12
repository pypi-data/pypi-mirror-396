"""MCP Resources for Telegraph."""

import json
from telegraph import Telegraph


def register_resources(mcp):
    """Register Telegraph resources."""

    @mcp.resource("telegraph://page/{path}")
    def get_telegraph_page(path: str) -> str:
        """
        Get content of a Telegraph page by its path.

        Returns the page data as JSON string.
        """
        client = Telegraph()
        page = client.get_page(path, return_content=True)

        # Convert content to serializable format if present
        content = None
        if page.content:
            content = _serialize_content(page.content)

        return json.dumps({
            "path": page.path,
            "url": page.url,
            "title": page.title,
            "description": page.description,
            "views": page.views,
            "author_name": page.author_name,
            "author_url": page.author_url,
            "content": content,
        }, indent=2, ensure_ascii=False)


def _serialize_content(content):
    """Serialize Telegraph content nodes to JSON-safe format."""
    if content is None:
        return None

    result = []
    for node in content:
        if isinstance(node, str):
            result.append(node)
        elif hasattr(node, 'to_dict'):
            result.append(node.to_dict())
        elif isinstance(node, dict):
            result.append(node)
        else:
            result.append(str(node))
    return result
