"""Export and backup tools."""

from telegraph import export_page, backup_account


def register_export_tools(mcp):
    """Register export-related tools."""

    @mcp.tool()
    def telegraph_export_page(
        path: str,
        format: str = "markdown"
    ) -> dict:
        """
        Export a Telegraph page to Markdown or HTML format.

        Args:
            path: Path to the Telegraph page
            format: Export format - "markdown" or "html" (default: "markdown")

        Returns:
            Exported page with title, path, url, format, and content
        """
        exported = export_page(path, format=format)
        return {
            "title": exported.title,
            "path": exported.path,
            "url": exported.url,
            "format": exported.format,
            "content": exported.content,
        }

    @mcp.tool()
    def telegraph_backup_account(
        access_token: str,
        format: str = "markdown",
        limit: int = 50
    ) -> dict:
        """
        Backup all pages from a Telegraph account.

        Args:
            access_token: Telegraph account access token
            format: Export format - "markdown" or "html" (default: "markdown")
            limit: Maximum number of pages to export (0-200, default: 50)

        Returns:
            Backup object with total_count, exported_count, format, and pages array
        """
        backup = backup_account(
            access_token=access_token,
            format=format,
            limit=limit
        )
        return {
            "total_count": backup.total_count,
            "exported_count": backup.exported_count,
            "format": backup.format,
            "pages": [
                {
                    "title": p.title,
                    "path": p.path,
                    "url": p.url,
                    "content": p.content,
                }
                for p in backup.pages
            ]
        }
