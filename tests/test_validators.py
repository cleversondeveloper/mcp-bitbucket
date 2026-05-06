from __future__ import annotations

import pytest

from mcp_bitbucket.core.validators import (
    normalize_page,
    normalize_pagelen,
    repo_path,
    safe_branch,
    safe_ref,
    safe_repo_slug,
    validate_comment,
    validate_description,
    validate_title,
    validate_uuid,
    workspace_path,
)


def test_repo_path_encodes_workspace_and_repo_slug() -> None:
    assert (
        repo_path("team space", "repo.name") == "/repositories/team%20space/repo.name"
    )


def test_workspace_path_encodes_workspace() -> None:
    assert workspace_path("team space") == "/workspaces/team%20space"


def test_safe_repo_slug_rejects_path_injection() -> None:
    with pytest.raises(ValueError, match="repo_slug"):
        safe_repo_slug("../repo")


def test_safe_branch_encodes_slashes_for_paths() -> None:
    assert safe_branch("feature/test") == "feature%2Ftest"


def test_safe_ref_accepts_commit_range_and_encodes_slashes() -> None:
    assert safe_ref("feature/test..main") == "feature%2Ftest..main"


def test_pagination_limits_pagelen_and_requires_positive_values() -> None:
    assert normalize_pagelen(500) == 100
    assert normalize_page(2) == 2

    with pytest.raises(ValueError, match="pagelen"):
        normalize_pagelen(0)

    with pytest.raises(ValueError, match="page"):
        normalize_page(0)


def test_validate_title() -> None:
    assert validate_title("Valid Title") == "Valid Title"

    with pytest.raises(ValueError, match="empty"):
        validate_title("   ")

    with pytest.raises(ValueError, match="exceeds"):
        validate_title("A" * 256)


def test_validate_comment_and_description() -> None:
    assert validate_comment("Valid comment") == "Valid comment"
    assert validate_description("Valid desc") == "Valid desc"

    with pytest.raises(ValueError, match="exceeds"):
        validate_comment("A" * 32001)


def test_validate_uuid() -> None:
    # Standard UUID
    assert (
        validate_uuid("12345678-1234-5678-1234-567812345678")
        == "{12345678-1234-5678-1234-567812345678}"
    )

    # UUID already with braces
    assert (
        validate_uuid("{12345678-1234-5678-1234-567812345678}")
        == "{12345678-1234-5678-1234-567812345678}"
    )

    # Invalid UUID
    with pytest.raises(ValueError, match="Invalid UUID"):
        validate_uuid("not-a-uuid")
