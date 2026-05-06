"""Tools MCP para leitura de workspaces e projetos."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..core.validators import normalize_page, normalize_pagelen, query
from ..infra.client import BitbucketClient
from ..infra.endpoints import projects, workspaces


def register_workspace_read_tools(mcp: FastMCP, client: BitbucketClient) -> None:
    """Registra tools de leitura relacionadas a workspace."""
    workspace = client.workspace

    @mcp.tool()
    async def list_projects(
        q: str | None = None,
        sort: str | None = None,
        pagelen: int | None = None,
        page: int | None = None,
    ) -> dict[str, object]:
        """Lista projetos no workspace Bitbucket configurado."""
        return await client.request(
            f"{projects(workspace)}"
            f"{query({'q': q, 'sort': sort, 'pagelen': normalize_pagelen(pagelen), 'page': normalize_page(page)})}"
        )

    @mcp.tool()
    async def list_workspaces(
        q: str | None = None,
        role: str | None = None,
        pagelen: int | None = None,
        page: int | None = None,
    ) -> dict[str, object]:
        """Lista workspaces Bitbucket visíveis para o usuário autenticado."""
        return await client.request(
            f"{workspaces()}"
            f"{query({'q': q, 'role': role, 'pagelen': normalize_pagelen(pagelen), 'page': normalize_page(page)})}"
        )
