"""Account management tools."""

from typing import Optional, List
from telegraph import Telegraph


def register_account_tools(mcp):
    """Register account-related tools."""

    @mcp.tool()
    def telegraph_create_account(
        short_name: str,
        author_name: Optional[str] = None,
        author_url: Optional[str] = None
    ) -> dict:
        """
        Create a new Telegraph account.

        Args:
            short_name: Account name (1-32 characters)
            author_name: Default author name (0-128 characters)
            author_url: Default profile link (0-512 characters)

        Returns:
            Account object with access_token
        """
        client = Telegraph()
        account = client.create_account(
            short_name=short_name,
            author_name=author_name,
            author_url=author_url
        )
        return {
            "short_name": account.short_name,
            "author_name": account.author_name,
            "author_url": account.author_url,
            "access_token": account.access_token,
            "auth_url": account.auth_url,
        }

    @mcp.tool()
    def telegraph_edit_account_info(
        access_token: str,
        short_name: Optional[str] = None,
        author_name: Optional[str] = None,
        author_url: Optional[str] = None
    ) -> dict:
        """
        Update information about a Telegraph account.

        Args:
            access_token: Access token of the Telegraph account
            short_name: New account name (1-32 characters)
            author_name: New default author name (0-128 characters)
            author_url: New default profile link (0-512 characters)

        Returns:
            Updated Account object
        """
        client = Telegraph(access_token=access_token)
        account = client.edit_account_info(
            short_name=short_name,
            author_name=author_name,
            author_url=author_url
        )
        return {
            "short_name": account.short_name,
            "author_name": account.author_name,
            "author_url": account.author_url,
        }

    @mcp.tool()
    def telegraph_get_account_info(
        access_token: str,
        fields: Optional[List[str]] = None
    ) -> dict:
        """
        Get information about a Telegraph account.

        Args:
            access_token: Access token of the Telegraph account
            fields: List of fields to return (short_name, author_name, author_url, auth_url, page_count)

        Returns:
            Account object with requested fields
        """
        client = Telegraph(access_token=access_token)
        account = client.get_account_info(fields=fields)
        return {
            "short_name": account.short_name,
            "author_name": account.author_name,
            "author_url": account.author_url,
            "auth_url": account.auth_url,
            "page_count": account.page_count,
        }

    @mcp.tool()
    def telegraph_revoke_access_token(access_token: str) -> dict:
        """
        Revoke access_token and generate a new one.

        Args:
            access_token: Access token of the Telegraph account to revoke

        Returns:
            Account object with new access_token and auth_url
        """
        client = Telegraph(access_token=access_token)
        account = client.revoke_access_token()
        return {
            "short_name": account.short_name,
            "access_token": account.access_token,
            "auth_url": account.auth_url,
        }
