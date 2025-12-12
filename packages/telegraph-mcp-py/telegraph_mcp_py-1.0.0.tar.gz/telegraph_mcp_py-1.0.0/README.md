# Telegraph MCP Server (Python)

A Model Context Protocol (MCP) server that provides tools for interacting with the Telegraph API (telegra.ph). This Python implementation allows Claude and other LLM clients to create, manage, and export Telegraph pages.

## Features

- **Account Management**: Create accounts, update info, manage access tokens
- **Page Operations**: Create, edit, retrieve, and list pages
- **Template System**: Create pages using pre-built templates
- **Export & Backup**: Export pages to Markdown/HTML, backup entire accounts
- **MCP Resources**: Access Telegraph pages as MCP resources
- **MCP Prompts**: Guided workflows for common tasks

## Installation

### Using uvx (Recommended)

```bash
uvx telegraph-mcp-py
```

### Using pip

```bash
pip install telegraph-mcp-py
```

### From Source

```bash
git clone https://github.com/NehoraiHadad/telegraph-mcp
cd telegraph-mcp/telegraph-mcp-py
pip install -e .
```

## Usage

### With Claude Code

```bash
claude mcp add telegraph-py -- uvx telegraph-mcp-py
```

### With Claude Desktop

Add to your Claude Desktop configuration (`~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "telegraph-py": {
      "command": "uvx",
      "args": ["telegraph-mcp-py"]
    }
  }
}
```

Or if installed via pip:

```json
{
  "mcpServers": {
    "telegraph-py": {
      "command": "telegraph-mcp-py"
    }
  }
}
```

## Available Tools

### Account Management

| Tool | Description |
|------|-------------|
| `telegraph_create_account` | Create a new Telegraph account |
| `telegraph_edit_account_info` | Update account information |
| `telegraph_get_account_info` | Get account details |
| `telegraph_revoke_access_token` | Revoke and regenerate access token |

### Page Management

| Tool | Description |
|------|-------------|
| `telegraph_create_page` | Create a new page (supports HTML/Markdown) |
| `telegraph_edit_page` | Edit an existing page |
| `telegraph_get_page` | Get page by path |
| `telegraph_get_page_list` | List all pages for an account |
| `telegraph_get_views` | Get page view statistics |

### Templates

| Tool | Description |
|------|-------------|
| `telegraph_list_templates` | List available templates |
| `telegraph_create_from_template` | Create page from template |

### Export & Backup

| Tool | Description |
|------|-------------|
| `telegraph_export_page` | Export page to Markdown/HTML |
| `telegraph_backup_account` | Backup all account pages |

## Resources

Access Telegraph pages directly as MCP resources:

```
telegraph://page/{path}
```

Example: `telegraph://page/Sample-Page-12-15`

## Prompts

Pre-defined prompts for guided workflows:

- `create_blog_post` - Guide for creating blog posts
- `create_documentation` - Guide for creating documentation
- `summarize_page` - Summarize an existing page

## Examples

### Creating a Page with Markdown

```python
# Via MCP tool call
telegraph_create_page(
    access_token="your-token",
    title="My First Post",
    content="# Hello World\n\nThis is my first Telegraph page!",
    format="markdown"
)
```

### Using Templates

```python
telegraph_create_from_template(
    access_token="your-token",
    template="blog_post",
    title="My Blog Post",
    data={
        "intro": "Welcome to my blog!",
        "sections": [
            {"heading": "Section 1", "content": "First section content"},
            {"heading": "Section 2", "content": "Second section content"}
        ],
        "conclusion": "Thanks for reading!"
    }
)
```

### Exporting a Page

```python
telegraph_export_page(
    path="Sample-Page-12-15",
    format="markdown"
)
```

## Development

### Setup

```bash
cd telegraph-mcp-py
pip install -e ".[dev]"
```

### Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector uvx telegraph-mcp-py
```

## Related Packages

- [telegraph-mcp](https://www.npmjs.com/package/telegraph-mcp) - TypeScript MCP server
- [telegraph-api-py](https://pypi.org/project/telegraph-api-py/) - Python Telegraph client
- [telegraph-api-client](https://www.npmjs.com/package/telegraph-api-client) - TypeScript Telegraph client

## License

MIT License - see [LICENSE](LICENSE) for details.
