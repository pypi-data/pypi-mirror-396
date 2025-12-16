"""Scan command for MCP Watch."""

import json

import structlog
import typer

from runlayer_cli import __version__
from runlayer_cli.api import RunlayerClient
from runlayer_cli.logging import setup_logging
from runlayer_cli.scan.service import scan_all_clients

logger = structlog.get_logger(__name__)

app = typer.Typer(help="Scan MCP client configurations")


def _print_error(message: str, log_file_path: str) -> None:
    """Print an error message to stderr with log file location."""
    typer.secho(f"Error: {message}", fg=typer.colors.RED, err=True)
    typer.secho(
        f"See logs for details: {log_file_path}",
        fg=typer.colors.YELLOW,
        err=True,
    )


@app.callback(invoke_without_command=True)
def scan(
    ctx: typer.Context,
    secret: str | None = typer.Option(
        None,
        "--secret",
        "-s",
        envvar="RUNLAYER_API_KEY",
        help="API secret for authentication",
    ),
    host: str = typer.Option(
        "http://localhost:3000",
        "--host",
        "-H",
        envvar="RUNLAYER_HOST",
        help="Runlayer API host URL",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Print scan results without submitting to API",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress all output except errors",
    ),
    device_id: str | None = typer.Option(
        None,
        "--device-id",
        help="Custom device identifier (auto-generated if not provided)",
    ),
    org_device_id: str | None = typer.Option(
        None,
        "--org-device-id",
        help="Organization-provided device ID (e.g., MDM asset tag)",
    ),
    no_projects: bool = typer.Option(
        False,
        "--no-projects",
        help="Skip scanning for project-level configurations",
    ),
    project_depth: int = typer.Option(
        5,
        "--project-depth",
        help="Maximum directory depth for project scanning",
    ),
    project_timeout: int = typer.Option(
        60,
        "--project-timeout",
        help="Timeout in seconds for project scanning",
    ),
) -> None:
    """
    Scan all MCP client configurations on this device.

    Discovers MCP servers configured in Cursor, Claude Desktop, Claude Code,
    VS Code, Windsurf, and other supported clients.

    Results are submitted to Runlayer for classification (managed vs shadow).

    Examples:

        # Scan and submit to Runlayer
        runlayer scan --secret $RUNLAYER_API_KEY

        # Dry run - print results without submitting
        runlayer scan --dry-run

        # With MDM-provided device ID
        runlayer scan --secret $KEY --org-device-id $ASSET_TAG

        # Skip project scanning for faster results
        runlayer scan --secret $KEY --no-projects
    """
    # If subcommand was invoked, let it handle things
    if ctx.invoked_subcommand is not None:
        return

    log_file_path = setup_logging(command="scan", quiet_console=quiet)

    # Validate required credentials (unless dry-run)
    if not dry_run and not secret:
        typer.secho(
            "Error: No API key provided. Use --secret or set RUNLAYER_API_KEY",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)

    try:
        # Perform scan
        if not quiet:
            typer.echo("Scanning MCP client configurations...")

        result = scan_all_clients(
            device_id=device_id,
            org_device_id=org_device_id,
            collector_version=__version__,
            scan_projects=not no_projects,
            project_scan_timeout=project_timeout,
            project_scan_depth=project_depth,
        )

        if verbose and not quiet:
            typer.echo(f"  Device ID: {result.device_id[:8]}...")
            typer.echo(f"  Hostname: {result.hostname}")
            typer.echo(f"  OS: {result.os} {result.os_version}")
            for config in result.configurations:
                scope_label = f"[{config.config_scope}]"
                typer.echo(
                    f"  {config.client} {scope_label}: {len(config.servers)} servers"
                )

        if result.total_servers == 0:
            if not quiet:
                typer.secho(
                    "No MCP servers found in any client configuration.",
                    fg=typer.colors.YELLOW,
                )
            raise typer.Exit(0)

        if dry_run:
            # Print payload and exit
            payload = result.to_api_payload()
            typer.echo(json.dumps(payload, indent=2, default=str))
            raise typer.Exit(0)

        # Submit to API
        if not quiet:
            global_count = len(result.global_configs)
            project_count = len(result.project_configs)
            typer.echo(
                f"Submitting {result.total_servers} servers from "
                f"{len(result.configurations)} configs ({global_count} global, {project_count} project)..."
            )

        client = RunlayerClient(hostname=host, secret=secret)  # type: ignore[arg-type]
        response = client.submit_mcp_watch_scan(result.to_api_payload())

        if not quiet:
            typer.secho(
                f"✓ Scan complete: {response['servers_processed']} servers, "
                f"{response['shadow_servers_found']} shadow, "
                f"{response['managed_servers_matched']} managed",
                fg=typer.colors.GREEN,
            )

        logger.info(
            "Scan completed successfully",
            servers_processed=response["servers_processed"],
            shadow_servers=response["shadow_servers_found"],
            managed_servers=response["managed_servers_matched"],
        )

    except typer.Exit:
        raise
    except Exception as e:
        logger.error(
            "Scan failed",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        _print_error(str(e), str(log_file_path))
        raise typer.Exit(1)
