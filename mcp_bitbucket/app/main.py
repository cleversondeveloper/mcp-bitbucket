"""Entrypoint de linha de comando para executar o servidor MCP Bitbucket."""

import argparse

from ..core.settings import BitbucketConfig
from .mcp_server import create_mcp_server


def main() -> None:
    """Processa argumentos de CLI e inicia o servidor MCP."""
    parser = argparse.ArgumentParser(description="Bitbucket MCP Server")
    parser.add_argument(
        "--read-only", action="store_true", help="Run in read-only mode"
    )
    parser.add_argument("--workspace", help="Bitbucket workspace slug")
    parser.add_argument(
        "--transport", default="stdio", choices=["stdio"], help="Transport type"
    )

    args = parser.parse_args()

    # Load base config from env
    try:
        config = BitbucketConfig.from_env()
    except RuntimeError:
        # Fallback for when env vars are missing but might be provided via CLI
        # (Though token is still required in env for now based on current BitbucketConfig.from_env)
        config = None

    # Override with CLI args if provided
    if config:
        from dataclasses import replace

        changes = {}
        if args.read_only:
            changes["read_only"] = True
        if args.workspace:
            changes["workspace"] = args.workspace

        if changes:
            config = replace(config, **changes)
    else:
        # If config couldn't be loaded from env, we still need at least the token
        # This part might need more robust handling if we want full CLI support
        pass

    create_mcp_server(config).run(transport=args.transport)


if __name__ == "__main__":
    main()
