"""Telegraph MCP Tools."""

from .account import register_account_tools
from .pages import register_page_tools
from .templates import register_template_tools
from .export import register_export_tools


def register_all_tools(mcp):
    """Register all Telegraph tools with the MCP server."""
    register_account_tools(mcp)
    register_page_tools(mcp)
    register_template_tools(mcp)
    register_export_tools(mcp)
