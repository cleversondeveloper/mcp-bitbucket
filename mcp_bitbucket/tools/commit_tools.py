"""Tools MCP para consultas de commit e comentarios em commit."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..core.validators import (
    normalize_page,
    normalize_pagelen,
    parse_author,
    query,
    safe_branch,
    validate_comment,
)
from ..infra.client import BitbucketClient
from ..infra.endpoints import commit, commit_comments, commits, diff, repository


def register_commit_read_tools(mcp: FastMCP, client: BitbucketClient) -> None:
    """Registra tools de leitura para commits e diffs."""
    workspace = client.workspace

    @mcp.tool()
    async def get_latest_commit(
        repo_slug: str, branch: str | None = None
    ) -> dict[str, Any]:
        """Obtém o commit mais recente em uma branch do repositório."""
        repo = await client.request(repository(workspace, repo_slug))
        resolved_branch = branch or repo.get("mainbranch", {}).get("name")
        if not resolved_branch:
            raise RuntimeError(
                f"Repository {workspace}/{repo_slug} does not define a default branch."
            )

        commit_page = await client.request(
            f"{commits(workspace, repo_slug)}/{safe_branch(resolved_branch)}"
            f"{query({'pagelen': 1})}"
        )
        latest_commit = (commit_page.get("values") or [None])[0]
        if not latest_commit:
            raise RuntimeError(
                f"No commits found for {workspace}/{repo_slug} on branch {resolved_branch}."
            )

        author_raw = latest_commit.get("author", {}).get("raw")
        parsed_author = parse_author(author_raw)
        author_user = (
            latest_commit.get("author", {}).get("user", {}).get("display_name")
        )

        return {
            "workspace": workspace,
            "repo_slug": repo_slug,
            "branch": resolved_branch,
            "hash": latest_commit.get("hash"),
            "date": latest_commit.get("date"),
            "message": latest_commit.get("message"),
            "author": {
                "displayName": author_user or parsed_author["name"],
                "email": parsed_author["email"],
                "raw": author_raw,
            },
        }

    @mcp.tool()
    async def list_commits(
        repo_slug: str,
        branch: str | None = None,
        q: str | None = None,
        pagelen: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """Lista commits de um repositório, opcionalmente filtrados por branch."""
        path = commits(workspace, repo_slug)
        if branch:
            path += f"/{safe_branch(branch)}"
        return await client.request(
            f"{path}{query({'q': q, 'pagelen': normalize_pagelen(pagelen), 'page': normalize_page(page)})}"
        )

    @mcp.tool()
    async def get_commit(repo_slug: str, commit_ref: str) -> dict[str, Any]:
        """Obtém detalhes de um commit."""
        return await client.request(commit(workspace, repo_slug, commit_ref))

    @mcp.tool()
    async def get_commit_diff(
        repo_slug: str, spec: str, context: int | None = None
    ) -> dict[str, Any]:
        """Obtém diff de um commit ou diff entre referências."""
        params: dict[str, Any] = {}
        if context is not None:
            params["context"] = max(0, int(context))
        return await client.request(
            f"{diff(workspace, repo_slug, spec)}{query(params)}"
        )


def register_commit_write_tools(mcp: FastMCP, client: BitbucketClient) -> None:
    """Registra tools de escrita para comentarios em commit."""
    workspace = client.workspace

    @mcp.tool()
    async def create_commit_comment(
        repo_slug: str, commit_ref: str, comment: str
    ) -> dict[str, Any]:
        """Cria um comentário em um commit."""
        valid_comment = validate_comment(comment)
        return await client.request(
            commit_comments(workspace, repo_slug, commit_ref),
            method="POST",
            body={"content": {"raw": valid_comment}},
        )
