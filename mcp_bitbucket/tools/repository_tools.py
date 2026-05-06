"""Tools MCP para leitura de repositorios e permissoes."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..core.validators import normalize_page, normalize_pagelen, query
from ..infra.client import BitbucketClient
from ..infra.endpoints import repository, repository_list, repository_permissions


def register_repository_read_tools(mcp: FastMCP, client: BitbucketClient) -> None:
    """Registra tools de leitura relacionadas a repositorios."""
    workspace = client.workspace

    @mcp.tool()
    async def list_repositories(
        role: str | None = None,
        q: str | None = None,
        sort: str | None = None,
        pagelen: int | None = None,
        page: int | None = None,
    ) -> dict[str, object]:
        """Lista repositórios no workspace Bitbucket configurado."""
        return await client.request(
            f"{repository_list(workspace)}"
            f"{query({'role': role, 'q': q, 'sort': sort, 'pagelen': normalize_pagelen(pagelen), 'page': normalize_page(page)})}"
        )

    @mcp.tool()
    async def get_repository(repo_slug: str) -> dict[str, object]:
        """Obtém detalhes de um repositório no workspace Bitbucket configurado."""
        return await client.request(repository(workspace, repo_slug))

    @mcp.tool()
    async def list_repository_permissions(
        repo_slug: str,
        q: str | None = None,
        pagelen: int | None = None,
        page: int | None = None,
    ) -> dict[str, object]:
        """Lista permissões de usuários para um repositório."""
        repository(workspace, repo_slug)
        default_query = f'repository.full_name="{workspace}/{repo_slug}"'
        return await client.request(
            f"{repository_permissions()}"
            f"{query({'q': q or default_query, 'pagelen': normalize_pagelen(pagelen), 'page': normalize_page(page)})}"
        )
