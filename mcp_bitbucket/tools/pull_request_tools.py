"""Tools MCP para fluxo de pull request no Bitbucket."""

from __future__ import annotations

import time
from collections import deque
from typing import Any

from mcp.server.fastmcp import FastMCP

from ..core.validators import (
    normalize_page,
    normalize_pagelen,
    normalize_positive_int,
    query,
    safe_branch,
    validate_comment,
    validate_description,
    validate_title,
    validate_uuid,
)
from ..infra.client import BitbucketClient
from ..infra.endpoints import (
    pull_request,
    pull_request_approve,
    pull_request_comments,
    pull_request_decline,
    pull_request_merge,
    pull_request_request_changes,
    pull_requests,
)


def register_pull_request_read_tools(mcp: FastMCP, client: BitbucketClient) -> None:
    """Registra tools de leitura para pull requests e comentarios."""
    workspace = client.workspace

    @mcp.tool()
    async def list_open_pull_requests(
        repo_slug: str,
        q: str | None = None,
        sort: str | None = None,
        pagelen: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """Lista pull requests abertos em um repositório."""
        return await client.request(
            f"{pull_requests(workspace, repo_slug)}"
            f"{query({'state': 'OPEN', 'q': q, 'sort': sort, 'pagelen': normalize_pagelen(pagelen), 'page': normalize_page(page)})}"
        )

    @mcp.tool()
    async def get_pull_request(repo_slug: str, pull_request_id: int) -> dict[str, Any]:
        """Obtém detalhes de um pull request."""
        pr_id = normalize_positive_int(pull_request_id, "pull_request_id")
        return await client.request(pull_request(workspace, repo_slug, pr_id))

    @mcp.tool()
    async def list_pull_request_comments(
        repo_slug: str,
        pull_request_id: int,
        pagelen: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """Lista comentários de um pull request."""
        pr_id = normalize_positive_int(pull_request_id, "pull_request_id")
        return await client.request(
            f"{pull_request_comments(workspace, repo_slug, pr_id)}"
            f"{query({'pagelen': normalize_pagelen(pagelen), 'page': normalize_page(page)})}"
        )


def register_pull_request_write_tools(mcp: FastMCP, client: BitbucketClient) -> None:
    """Registra tools de escrita para operacoes de pull request."""
    workspace = client.workspace
    sensitive_ops_timestamps: deque[float] = deque()

    def _enforce_dangerous_confirmation(confirm: bool, confirm_phrase: str | None) -> None:
        if not confirm:
            raise ValueError("Confirmação explícita é obrigatória (`confirm=True`).")
        if (
            client.config.require_confirm_phrase
            and confirm_phrase != client.config.confirm_phrase
        ):
            raise ValueError("Frase de confirmação inválida para operação destrutiva.")

    def _enforce_sensitive_operation_quota() -> None:
        now = time.monotonic()
        window = client.config.sensitive_rate_limit_window_seconds
        while sensitive_ops_timestamps and now - sensitive_ops_timestamps[0] > window:
            sensitive_ops_timestamps.popleft()
        if len(sensitive_ops_timestamps) >= client.config.sensitive_rate_limit_requests:
            raise RuntimeError(
                "Limite interno de operações sensíveis excedido para a janela configurada."
            )
        sensitive_ops_timestamps.append(now)

    @mcp.tool()
    async def create_pull_request_comment(
        repo_slug: str, pull_request_id: int, comment: str
    ) -> dict[str, Any]:
        """Cria um comentário em um pull request."""
        pr_id = normalize_positive_int(pull_request_id, "pull_request_id")
        valid_comment = validate_comment(comment)
        return await client.request(
            pull_request_comments(workspace, repo_slug, pr_id),
            method="POST",
            body={"content": {"raw": valid_comment}},
        )

    @mcp.tool()
    async def create_pull_request(
        repo_slug: str,
        title: str,
        source_branch: str,
        destination_branch: str | None = None,
        description: str | None = None,
        draft: bool | None = None,
        close_source_branch: bool | None = None,
        reviewer_uuids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Cria um pull request no Bitbucket."""
        valid_title = validate_title(title)
        safe_branch(source_branch)
        payload: dict[str, Any] = {
            "title": valid_title,
            "source": {"branch": {"name": source_branch}},
        }

        if destination_branch:
            safe_branch(destination_branch)
            payload["destination"] = {"branch": {"name": destination_branch}}
        if description:
            payload["description"] = validate_description(description)
        if draft is not None:
            payload["draft"] = draft
        if close_source_branch is not None:
            payload["close_source_branch"] = close_source_branch
        if reviewer_uuids:
            payload["reviewers"] = [
                {"uuid": validate_uuid(uuid)} for uuid in reviewer_uuids
            ]

        return await client.request(
            pull_requests(workspace, repo_slug),
            method="POST",
            body=payload,
        )

    @mcp.tool()
    async def add_pull_request_reviewer(
        repo_slug: str, pull_request_id: int, reviewer_uuid: str
    ) -> dict[str, Any]:
        """Adiciona um revisor a um pull request."""
        pr_id = normalize_positive_int(pull_request_id, "pull_request_id")
        valid_uuid = validate_uuid(reviewer_uuid)
        current_pull_request = await client.request(
            pull_request(workspace, repo_slug, pr_id)
        )
        reviewers = [
            {"uuid": reviewer.get("uuid")}
            for reviewer in current_pull_request.get("reviewers", [])
            if reviewer.get("uuid")
        ]
        if valid_uuid not in {reviewer["uuid"] for reviewer in reviewers}:
            reviewers.append({"uuid": valid_uuid})

        payload = {
            "title": current_pull_request.get("title", ""),
            "reviewers": reviewers,
        }

        return await client.request(
            pull_request(workspace, repo_slug, pr_id),
            method="PUT",
            body=payload,
        )

    @mcp.tool()
    async def merge_pull_request(
        repo_slug: str,
        pull_request_id: int,
        confirm: bool,
        confirm_phrase: str | None = None,
        message: str | None = None,
        close_source_branch: bool | None = None,
        merge_strategy: str | None = None,
    ) -> dict[str, Any]:
        """Realiza merge de um pull request. Requer confirmação explícita (`confirm=True`)."""
        if not client.config.allow_merge:
            raise PermissionError(
                "Operação de merge desabilitada pela política (BITBUCKET_ALLOW_MERGE=false)."
            )
        _enforce_dangerous_confirmation(confirm, confirm_phrase)
        _enforce_sensitive_operation_quota()
        pr_id = normalize_positive_int(pull_request_id, "pull_request_id")
        valid_message = validate_comment(message) if message else None
        body = {
            key: value
            for key, value in {
                "message": valid_message,
                "close_source_branch": close_source_branch,
                "merge_strategy": merge_strategy,
            }.items()
            if value is not None
        }
        return await client.request(
            pull_request_merge(workspace, repo_slug, pr_id),
            method="POST",
            body=body,
        )

    @mcp.tool()
    async def decline_pull_request(
        repo_slug: str,
        pull_request_id: int,
        confirm: bool,
        confirm_phrase: str | None = None,
        message: str | None = None,
    ) -> dict[str, Any]:
        """Recusa um pull request. Requer confirmação explícita (`confirm=True`)."""
        _enforce_dangerous_confirmation(confirm, confirm_phrase)
        _enforce_sensitive_operation_quota()
        pr_id = normalize_positive_int(pull_request_id, "pull_request_id")
        valid_message = validate_comment(message) if message else None
        body = {"message": valid_message} if valid_message else None
        return await client.request(
            pull_request_decline(workspace, repo_slug, pr_id),
            method="POST",
            body=body,
        )

    @mcp.tool()
    async def approve_pull_request(
        repo_slug: str, pull_request_id: int
    ) -> dict[str, Any]:
        """Aprova um pull request."""
        pr_id = normalize_positive_int(pull_request_id, "pull_request_id")
        return await client.request(
            pull_request_approve(workspace, repo_slug, pr_id),
            method="POST",
        )

    @mcp.tool()
    async def request_changes(
        repo_slug: str,
        pull_request_id: int,
        confirm: bool,
        confirm_phrase: str | None = None,
    ) -> dict[str, Any]:
        """Solicita alterações em um pull request. Requer confirmação explícita (`confirm=True`)."""
        _enforce_dangerous_confirmation(confirm, confirm_phrase)
        _enforce_sensitive_operation_quota()
        pr_id = normalize_positive_int(pull_request_id, "pull_request_id")
        return await client.request(
            pull_request_request_changes(workspace, repo_slug, pr_id),
            method="POST",
        )
