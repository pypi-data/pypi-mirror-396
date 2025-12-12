"""MCP Prompts for Telegraph."""


def register_prompts(mcp):
    """Register Telegraph prompts."""

    @mcp.prompt()
    def create_blog_post(topic: str) -> str:
        """Guide for creating a blog post on Telegraph."""
        return f"""Help me create a blog post about: {topic}

Please structure it with:
1. An engaging title
2. An introduction paragraph
3. 2-3 main sections with headers (use ## for h4 in Telegraph)
4. A conclusion

Use Markdown format. When ready, I'll use the telegraph_create_page tool with format="markdown" to publish it.

Example structure:
```markdown
Introduction paragraph here...

## First Section
Content...

## Second Section
Content...

## Conclusion
Summary...
```"""

    @mcp.prompt()
    def create_documentation(project_name: str) -> str:
        """Guide for creating documentation on Telegraph."""
        return f"""Help me create documentation for: {project_name}

Structure:
1. Project overview
2. Installation/Setup instructions
3. Usage examples with code blocks
4. API reference (if applicable)
5. FAQ or troubleshooting section

Use Markdown format. Code blocks should use triple backticks with language specification.
When ready, use the telegraph_create_page tool with format="markdown" to publish.

You can also use the telegraph_create_from_template tool with template="documentation" for a pre-structured layout."""

    @mcp.prompt()
    def summarize_page(path: str) -> str:
        """Summarize an existing Telegraph page."""
        return f"""Please fetch and summarize the Telegraph page at path: {path}

Steps:
1. Use the telegraph_get_page tool with return_content=true to fetch the page
2. Provide a brief summary (2-3 sentences)
3. List the key points covered
4. Identify the target audience

If the page doesn't exist, let me know and suggest alternatives."""
