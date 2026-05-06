from __future__ import annotations

from mcp_bitbucket import TOOL_PERMISSIONS, required_scopes


def test_required_scopes_returns_read_scopes() -> None:
    assert required_scopes("read") == (
        "account",
        "pullrequest",
        "repository",
        "workspace",
    )


def test_required_scopes_returns_write_scopes() -> None:
    assert required_scopes("write") == ("pullrequest:write", "repository:write")


def test_every_tool_permission_has_scopes() -> None:
    assert TOOL_PERMISSIONS
    assert all(permission.scopes for permission in TOOL_PERMISSIONS)
