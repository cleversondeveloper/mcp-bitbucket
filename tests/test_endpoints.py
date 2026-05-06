from __future__ import annotations

from mcp_bitbucket.infra.endpoints import (
    branch,
    commit,
    diff,
    pull_request,
    pull_request_comments,
    repository,
    repository_list,
)


def test_repository_endpoints() -> None:
    assert repository("team space", "repo") == "/repositories/team%20space/repo"
    assert repository_list("team space") == "/repositories/team%20space"


def test_commit_and_diff_endpoints() -> None:
    assert commit("team", "repo", "abc123") == "/repositories/team/repo/commit/abc123"
    assert diff("team", "repo", "feature/test..main") == (
        "/repositories/team/repo/diff/feature%2Ftest..main"
    )


def test_pull_request_endpoints() -> None:
    assert pull_request("team", "repo", 12) == "/repositories/team/repo/pullrequests/12"
    assert pull_request_comments("team", "repo", 12) == (
        "/repositories/team/repo/pullrequests/12/comments"
    )
    assert branch("team", "repo", "feature/test") == (
        "/repositories/team/repo/refs/branches/feature%2Ftest"
    )
