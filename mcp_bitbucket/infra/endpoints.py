"""Builders de endpoints Bitbucket com sanitizacao de segmentos de path."""

from __future__ import annotations

from ..core.validators import (
    repo_path,
    safe_branch,
    safe_ref,
    workspace_path,
    workspace_slug,
)


def repository(workspace: str, repo_slug: str) -> str:
    """Retorna endpoint de repositorio."""
    return repo_path(workspace, repo_slug)


def repository_list(workspace: str) -> str:
    """Retorna endpoint de listagem de repositorios."""
    return f"/repositories/{workspace_slug(workspace)}"


def projects(workspace: str) -> str:
    """Retorna endpoint de projetos do workspace."""
    return f"{workspace_path(workspace)}/projects"


def workspaces() -> str:
    """Retorna endpoint de workspaces visiveis."""
    return "/workspaces"


def branches(workspace: str, repo_slug: str) -> str:
    """Retorna endpoint de branches do repositorio."""
    return f"{repository(workspace, repo_slug)}/refs/branches"


def branch(workspace: str, repo_slug: str, branch_name: str) -> str:
    """Retorna endpoint de branch especifica."""
    return f"{branches(workspace, repo_slug)}/{safe_branch(branch_name)}"


def commits(workspace: str, repo_slug: str) -> str:
    """Retorna endpoint de commits do repositorio."""
    return f"{repository(workspace, repo_slug)}/commits"


def commit(workspace: str, repo_slug: str, ref: str) -> str:
    """Retorna endpoint de commit por referencia."""
    return f"{repository(workspace, repo_slug)}/commit/{safe_ref(ref)}"


def commit_comments(workspace: str, repo_slug: str, ref: str) -> str:
    """Retorna endpoint de comentarios de commit."""
    return f"{commit(workspace, repo_slug, ref)}/comments"


def diff(workspace: str, repo_slug: str, spec: str) -> str:
    """Retorna endpoint de diff entre referencias."""
    return f"{repository(workspace, repo_slug)}/diff/{safe_ref(spec)}"


def pull_requests(workspace: str, repo_slug: str) -> str:
    """Retorna endpoint de pull requests do repositorio."""
    return f"{repository(workspace, repo_slug)}/pullrequests"


def pull_request(workspace: str, repo_slug: str, pull_request_id: int) -> str:
    """Retorna endpoint de pull request especifico."""
    return f"{pull_requests(workspace, repo_slug)}/{pull_request_id}"


def pull_request_comments(workspace: str, repo_slug: str, pull_request_id: int) -> str:
    """Retorna endpoint de comentarios de pull request."""
    return f"{pull_request(workspace, repo_slug, pull_request_id)}/comments"


def pull_request_merge(workspace: str, repo_slug: str, pull_request_id: int) -> str:
    """Retorna endpoint de merge de pull request."""
    return f"{pull_request(workspace, repo_slug, pull_request_id)}/merge"


def pull_request_decline(workspace: str, repo_slug: str, pull_request_id: int) -> str:
    """Retorna endpoint de recusa de pull request."""
    return f"{pull_request(workspace, repo_slug, pull_request_id)}/decline"


def pull_request_approve(workspace: str, repo_slug: str, pull_request_id: int) -> str:
    """Retorna endpoint de aprovacao de pull request."""
    return f"{pull_request(workspace, repo_slug, pull_request_id)}/approve"


def pull_request_request_changes(
    workspace: str, repo_slug: str, pull_request_id: int
) -> str:
    """Retorna endpoint para solicitar alteracoes em pull request."""
    return f"{pull_request(workspace, repo_slug, pull_request_id)}/request-changes"


def repository_permissions() -> str:
    """Retorna endpoint de permissoes de repositorios para o usuario autenticado."""
    return "/user/permissions/repositories"
