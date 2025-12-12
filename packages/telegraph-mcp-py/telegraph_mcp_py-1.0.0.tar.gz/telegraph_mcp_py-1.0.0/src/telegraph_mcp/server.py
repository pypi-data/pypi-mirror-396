"""Telegraph MCP Server - Main server implementation."""

from mcp.server.fastmcp import FastMCP

from .tools import register_all_tools
from .resources import register_resources
from .prompts import register_prompts

# Create the MCP server
mcp = FastMCP(
    name="telegraph-mcp-py",
)

# Register all components
register_all_tools(mcp)
register_resources(mcp)
register_prompts(mcp)


def main():
    """Run the Telegraph MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
