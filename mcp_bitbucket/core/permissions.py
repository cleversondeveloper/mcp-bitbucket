from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ToolAccess = Literal["read", "write"]


@dataclass(frozen=True)
class ToolPermission:
    name: str
    access: ToolAccess
    scopes: tuple[str, ...]
    description: str


REPOSITORY_READ_SCOPE = "repository"
REPOSITORY_WRITE_SCOPE = "repository:write"
PULLREQUEST_READ_SCOPE = "pullrequest"
PULLREQUEST_WRITE_SCOPE = "pullrequest:write"
WORKSPACE_READ_SCOPE = "workspace"
ACCOUNT_READ_SCOPE = "account"


TOOL_PERMISSIONS: tuple[ToolPermission, ...] = (
    ToolPermission(
        "get_latest_commit",
        "read",
        (REPOSITORY_READ_SCOPE,),
        "Read repository metadata and commits.",
    ),
    ToolPermission(
        "list_commits",
        "read",
        (REPOSITORY_READ_SCOPE,),
        "List repository commits.",
    ),
    ToolPermission(
        "get_commit",
        "read",
        (REPOSITORY_READ_SCOPE,),
        "Read one commit.",
    ),
    ToolPermission(
        "get_commit_diff",
        "read",
        (REPOSITORY_READ_SCOPE,),
        "Read diff content.",
    ),
    ToolPermission(
        "create_commit_comment",
        "write",
        (REPOSITORY_WRITE_SCOPE,),
        "Create commit comments.",
    ),
    ToolPermission(
        "list_repositories",
        "read",
        (REPOSITORY_READ_SCOPE,),
        "List repositories in the configured workspace.",
    ),
    ToolPermission(
        "get_repository",
        "read",
        (REPOSITORY_READ_SCOPE,),
        "Read repository metadata.",
    ),
    ToolPermission(
        "list_projects",
        "read",
        (WORKSPACE_READ_SCOPE,),
        "List projects in the configured workspace.",
    ),
    ToolPermission(
        "list_workspaces",
        "read",
        (WORKSPACE_READ_SCOPE,),
        "List workspaces visible to the authenticated user.",
    ),
    ToolPermission(
        "list_branches",
        "read",
        (REPOSITORY_READ_SCOPE,),
        "List repository branches.",
    ),
    ToolPermission(
        "get_branch",
        "read",
        (REPOSITORY_READ_SCOPE,),
        "Read one branch.",
    ),
    ToolPermission(
        "create_branch",
        "write",
        (REPOSITORY_WRITE_SCOPE,),
        "Create branches.",
    ),
    ToolPermission(
        "list_open_pull_requests",
        "read",
        (PULLREQUEST_READ_SCOPE,),
        "List open pull requests.",
    ),
    ToolPermission(
        "get_pull_request",
        "read",
        (PULLREQUEST_READ_SCOPE,),
        "Read one pull request.",
    ),
    ToolPermission(
        "list_pull_request_comments",
        "read",
        (PULLREQUEST_READ_SCOPE,),
        "List pull request comments.",
    ),
    ToolPermission(
        "create_pull_request_comment",
        "write",
        (PULLREQUEST_WRITE_SCOPE,),
        "Create pull request comments.",
    ),
    ToolPermission(
        "create_pull_request",
        "write",
        (PULLREQUEST_WRITE_SCOPE,),
        "Create pull requests.",
    ),
    ToolPermission(
        "add_pull_request_reviewer",
        "write",
        (PULLREQUEST_WRITE_SCOPE,),
        "Update pull request reviewers.",
    ),
    ToolPermission(
        "merge_pull_request",
        "write",
        (PULLREQUEST_WRITE_SCOPE,),
        "Merge pull requests.",
    ),
    ToolPermission(
        "decline_pull_request",
        "write",
        (PULLREQUEST_WRITE_SCOPE,),
        "Decline pull requests.",
    ),
    ToolPermission(
        "approve_pull_request",
        "write",
        (PULLREQUEST_WRITE_SCOPE,),
        "Approve pull requests.",
    ),
    ToolPermission(
        "request_changes",
        "write",
        (PULLREQUEST_WRITE_SCOPE,),
        "Request changes in pull requests.",
    ),
    ToolPermission(
        "list_repository_permissions",
        "read",
        (ACCOUNT_READ_SCOPE,),
        "Read repository permissions visible to the authenticated user.",
    ),
)


def required_scopes(access: ToolAccess | None = None) -> tuple[str, ...]:
    scopes = {
        scope
        for permission in TOOL_PERMISSIONS
        if access is None or permission.access == access
        for scope in permission.scopes
    }
    return tuple(sorted(scopes))
