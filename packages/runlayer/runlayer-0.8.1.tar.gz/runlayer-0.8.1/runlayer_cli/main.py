import anyio
import sys
from uuid import UUID
import typer
import structlog
import datetime
from typing import Union
from fastmcp.client.transports import (
    SSETransport,
    StdioTransport,
    StreamableHttpTransport,
)
from fastmcp.server.proxy import ProxyClient
from fastmcp.server.proxy import FastMCPProxy
from runlayer_cli.models import LocalCapabilities

from runlayer_cli.middleware import RunlayerMiddleware
from runlayer_cli.oauth import OAuth
from runlayer_cli.api import RunlayerClient, USER_AGENT
from runlayer_cli.commands import deploy_app
from runlayer_cli import __version__
from runlayer_cli.logging import setup_logging

logger = structlog.get_logger("cli")


def version_callback(value: bool):
    """Show version information."""
    if value:
        typer.echo(f"runlayer version {__version__}")
        raise typer.Exit()


app = typer.Typer(help="Run MCP servers via HTTP transport")


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
):
    """Runlayer CLI - Run MCP servers via HTTP transport."""


async def sync_local_capabilities(
    runlayer_api_client: RunlayerClient,
    proxy: FastMCPProxy,
    server_id: str,
) -> None:
    tools = await proxy.get_tools()
    resources = await proxy.get_resources()
    prompts = await proxy.get_prompts()

    local_capabilities = LocalCapabilities(
        tools={
            name: t.to_mcp_tool(include_fastmcp_meta=False) for name, t in tools.items()
        },
        resources={
            name: r.to_mcp_resource(include_fastmcp_meta=False)
            for name, r in resources.items()
        },
        prompts={
            name: p.to_mcp_prompt(include_fastmcp_meta=False)
            for name, p in prompts.items()
        },
        synced_at=datetime.datetime.now(datetime.timezone.utc),
    )

    runlayer_api_client.update_capabilities(server_id, local_capabilities)


def _print_error(message: str, log_file_path: str) -> None:
    """Print an error message to stderr with log file location."""
    typer.secho(f"Error: {message}", fg=typer.colors.RED, err=True)
    typer.secho(
        f"See logs for details: {log_file_path}", fg=typer.colors.YELLOW, err=True
    )


@app.command(name="run", help="Run an MCP server via HTTP transport")
def run(
    server_uuid: str = typer.Argument(..., help="UUID of the MCP server to run"),
    secret: str = typer.Option(
        ..., "--secret", "-s", help="API secret for authentication"
    ),
    host: str = typer.Option(
        "http://localhost:3000", "--host", "-H", help="Runlayer API host URL"
    ),
):
    log_file_path = setup_logging(command="run", quiet_console=True)

    try:
        runlayer_api_client = RunlayerClient(hostname=host, secret=secret)

        server_details = runlayer_api_client.get_server_details(server_uuid)
        server_name = server_details.name

        headers_dict = {}
        headers_dict["User-Agent"] = USER_AGENT

        transport: Union[SSETransport, StdioTransport, StreamableHttpTransport]
        match server_details.transport_type:
            case "sse":
                transport = SSETransport(
                    url=server_details.url,
                    headers=headers_dict,
                    auth=OAuth(mcp_url=server_details.url, client_name=USER_AGENT),
                )
            case "stdio":
                transport_config = server_details.transport_config or {}
                transport = StdioTransport(
                    command=server_details.url,
                    args=transport_config.get("args", []),
                    env=transport_config.get("env", {}),
                )
            case "streaming-http":
                transport = StreamableHttpTransport(
                    url=server_details.url,
                    headers=headers_dict,
                    auth=OAuth(mcp_url=server_details.url, client_name=USER_AGENT),
                )
            case _:
                raise ValueError(
                    f"Unknown transport type: {server_details.transport_type}"
                )

        proxy_client = ProxyClient(transport)

        # Create a factory that reuses the same client instead of creating new ones.
        # This is critical for SSE transports - creating a new SSE connection for each
        # request causes timeouts because some servers (like Atlassian) don't properly
        # respond to subsequent SSE connections from the same OAuth token.
        def reuse_client_factory() -> ProxyClient:
            return proxy_client

        proxy = FastMCPProxy(client_factory=reuse_client_factory, name=server_name)

        proxy.add_middleware(
            RunlayerMiddleware(
                runlayer_api_client=runlayer_api_client,
                proxy=proxy,
                server=server_details,
            )
        )

        logger.info(
            "Starting Runlayer CLI",
            server_name=server_name,
            server_uuid=server_uuid,
        )

        async def tasks():
            if server_details.sync_required:
                await sync_local_capabilities(runlayer_api_client, proxy, server_uuid)
            await proxy.run_stdio_async(
                show_banner=False,
            )

        anyio.run(tasks)
    except KeyboardInterrupt:
        logger.info("MCP server shutdown requested by user")
    except Exception as e:
        logger.error(
            "Error running MCP server",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        _print_error(str(e), str(log_file_path))
        raise typer.Exit(1)


app.add_typer(deploy_app, name="deploy")


def _ensure_backwards_compatibility():
    """Ensure backwards compatibility with the initial CLI release.

    The first version allowed: runlayer <uuid> --secret <key>
    The current version requires: runlayer run <uuid> --secret <key>

    This function detects when a UUID is passed as the first argument
    and automatically inserts the "run" subcommand for backwards compatibility.
    """

    if len(sys.argv) < 2:
        return

    current_command = sys.argv[1]
    commands = app.registered_commands

    if current_command in commands:
        return

    try:
        UUID(current_command)
        sys.argv.insert(1, "run")
    except ValueError:
        pass


def cli():
    _ensure_backwards_compatibility()
    app()


if __name__ == "__main__":
    cli()
