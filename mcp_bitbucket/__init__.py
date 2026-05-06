"""Interface publica da biblioteca MCP Bitbucket."""

from __future__ import annotations

from .app.mcp_server import create_mcp_server
from .core.pagination import has_next_page, next_page_url, page_values
from .core.permissions import TOOL_PERMISSIONS, ToolPermission, required_scopes
from .core.settings import BitbucketConfig
from .infra.client import BitbucketClient

__all__ = [
    "TOOL_PERMISSIONS",
    "BitbucketClient",
    "BitbucketConfig",
    "ToolPermission",
    "create_mcp_server",
    "has_next_page",
    "next_page_url",
    "page_values",
    "required_scopes",
]
