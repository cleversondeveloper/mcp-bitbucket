"""Tools MCP para leitura e escrita de branches no Bitbucket."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..core.validators import normalize_page, normalize_pagelen, query, safe_branch
from ..infra.client import BitbucketClient
from ..infra.endpoints import branch, branches


def register_branch_read_tools(mcp: FastMCP, client: BitbucketClient) -> None:
    """Registra tools de leitura relacionadas a branches."""
    workspace = client.workspace

    @mcp.tool()
    async def list_branches(
        repo_slug: str,
        q: str | None = None,
        sort: str | None = None,
        pagelen: int | None = None,
        page: int | None = None,
    ) -> dict[str, object]:
        """Lista branches de um repositório."""
        return await client.request(
            f"{branches(workspace, repo_slug)}"
            f"{query({'q': q, 'sort': sort, 'pagelen': normalize_pagelen(pagelen), 'page': normalize_page(page)})}"
        )

    @mcp.tool()
    async def get_branch(repo_slug: str, branch_name: str) -> dict[str, object]:
        """Obtém detalhes de uma branch."""
        return await client.request(branch(workspace, repo_slug, branch_name))


def register_branch_write_tools(mcp: FastMCP, client: BitbucketClient) -> None:
    """Registra tools de escrita relacionadas a branches."""
    workspace = client.workspace

    @mcp.tool()
    async def create_branch(
        repo_slug: str, branch_name: str, target_hash: str
    ) -> dict[str, object]:
        """Cria uma branch a partir do hash de commit de destino."""
        safe_branch(branch_name)
        return await client.request(
            branches(workspace, repo_slug),
            method="POST",
            body={"name": branch_name, "target": {"hash": target_hash}},
        )
