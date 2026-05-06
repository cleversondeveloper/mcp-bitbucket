"""Factory do servidor MCP com injecao de configuracao e cliente Bitbucket."""

from __future__ import annotations

import asyncio
import logging

from mcp.server.fastmcp import FastMCP

from ..core.permissions import required_scopes
from ..core.settings import BitbucketConfig
from ..infra.client import BitbucketClient
from ..tools.registry import register_tools

logger = logging.getLogger(__name__)


async def _run_security_preflight(client: BitbucketClient, config: BitbucketConfig) -> None:
    await client.request(f"/repositories/{config.workspace}?pagelen=1")
    token_scopes = await client.fetch_oauth_scopes()
    if not token_scopes:
        message = (
            "Não foi possível determinar escopos do token via header x-oauth-scopes."
        )
        if config.strict_scope_check:
            raise RuntimeError(message)
        logger.warning(message)
        return

    expected = set(required_scopes("read"))
    if not config.read_only and config.enable_write:
        expected.update(required_scopes("write"))

    missing = expected - token_scopes
    if missing:
        message = f"Token sem escopos mínimos esperados: {sorted(missing)}"
        if config.strict_scope_check:
            raise RuntimeError(message)
        logger.warning(message)


def create_mcp_server(config: BitbucketConfig | None = None) -> FastMCP:
    """Cria e configura uma instancia FastMCP pronta para uso."""
    resolved_config = config or BitbucketConfig.from_env()
    mcp = FastMCP("bitbucket-local-mcp", json_response=True)
    client = BitbucketClient(resolved_config)
    if resolved_config.scope_check_on_startup:
        asyncio.run(_run_security_preflight(client, resolved_config))
    register_tools(mcp, client)
    return mcp
