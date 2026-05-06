from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_bitbucket.core.settings import BitbucketConfig
from mcp_bitbucket.infra.client import BitbucketClient
from mcp_bitbucket.tools import register_tools


def test_register_tools_full_access():
    mcp = FastMCP("test")
    config = BitbucketConfig(
        workspace="w", _token="t", read_only=False, enable_write=True
    )
    client = BitbucketClient(config)

    register_tools(mcp, client)

    # Check if a write tool is registered
    tool_names = {t.name for t in mcp._tool_manager.list_tools()}
    assert "create_branch" in tool_names
    assert "list_repositories" in tool_names


def test_register_tools_read_only():
    mcp = FastMCP("test")
    config = BitbucketConfig(workspace="w", _token="t", read_only=True)
    client = BitbucketClient(config)

    register_tools(mcp, client)

    # Check if a write tool is NOT registered
    tools = {t.name for t in mcp._tool_manager.list_tools()}
    assert "create_branch" not in tools
    assert "merge_pull_request" not in tools
    # Check if a read tool IS registered
    assert "list_repositories" in tools
    assert "get_repository" in tools


def test_register_tools_write_disabled_by_policy():
    mcp = FastMCP("test")
    config = BitbucketConfig(workspace="w", _token="t", read_only=False, enable_write=False)
    client = BitbucketClient(config)

    register_tools(mcp, client)

    tools = {t.name for t in mcp._tool_manager.list_tools()}
    assert "create_branch" not in tools
    assert "merge_pull_request" not in tools
