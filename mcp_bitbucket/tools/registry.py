"""Registro central das tools MCP, separadas por leitura e escrita."""

from __future__ import annotations

from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..infra.client import BitbucketClient
from .branch_tools import register_branch_read_tools, register_branch_write_tools
from .commit_tools import register_commit_read_tools, register_commit_write_tools
from .pull_request_tools import (
    register_pull_request_read_tools,
    register_pull_request_write_tools,
)
from .repository_tools import register_repository_read_tools
from .workspace_tools import register_workspace_read_tools

ToolRegistrar = Callable[[FastMCP, BitbucketClient], None]

READ_TOOL_REGISTRARS: tuple[ToolRegistrar, ...] = (
    register_repository_read_tools,
    register_commit_read_tools,
    register_branch_read_tools,
    register_pull_request_read_tools,
    register_workspace_read_tools,
)

WRITE_TOOL_REGISTRARS: tuple[ToolRegistrar, ...] = (
    register_commit_write_tools,
    register_branch_write_tools,
    register_pull_request_write_tools,
)


def register_read_tools(mcp: FastMCP, client: BitbucketClient) -> None:
    """Registra todas as tools de leitura no servidor MCP."""
    for registrar in READ_TOOL_REGISTRARS:
        registrar(mcp, client)


def register_write_tools(mcp: FastMCP, client: BitbucketClient) -> None:
    """Registra todas as tools de escrita no servidor MCP."""
    for registrar in WRITE_TOOL_REGISTRARS:
        registrar(mcp, client)


def register_tools(mcp: FastMCP, client: BitbucketClient) -> None:
    """Registra tools de leitura e, se permitido, tools de escrita."""
    register_read_tools(mcp, client)
    if not client.config.read_only and client.config.enable_write:
        register_write_tools(mcp, client)
