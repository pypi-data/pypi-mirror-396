"""Parse MCP client configuration files."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog

if TYPE_CHECKING:
    from runlayer_cli.scan.clients import MCPClientDefinition

logger = structlog.get_logger(__name__)


@dataclass
class MCPServerConfig:
    """Parsed MCP server configuration."""

    name: str
    type: str  # stdio, sse, http, streaming-http
    command: str | None = None
    args: list[str] | None = None
    url: str | None = None
    env: dict[str, str] | None = None
    headers: dict[str, str] | None = None
    config_hash: str = ""


@dataclass
class MCPClientConfig:
    """Parsed MCP client configuration."""

    client: str
    client_version: str | None = None
    config_path: str | None = None
    config_modified_at: str | None = None
    servers: list[MCPServerConfig] = field(default_factory=list)
    # New fields for global vs project-level configs
    config_scope: str = "global"  # "global" or "project"
    project_path: str | None = (
        None  # Path to project root (only for project-level configs)
    )


def compute_config_hash(server: MCPServerConfig) -> str:
    """
    Compute a canonical hash for a server configuration.

    Hash includes: name, type, command, args, url
    Hash excludes: env, headers (credentials can vary)

    Args order is preserved because argument order is semantically meaningful.
    """
    canonical = {
        "name": server.name,
        "type": server.type,
        "command": server.command,
        "args": list(server.args) if server.args else [],
        "url": server.url,
    }
    canonical_json = json.dumps(canonical, sort_keys=True)
    return hashlib.sha256(canonical_json.encode()).hexdigest()


def _parse_server_entry(name: str, config: dict[str, Any]) -> MCPServerConfig:
    """Parse a single server entry from config file.

    Handles two formats:
    1. Standard MCP format: { "command": "...", "args": [...], "env": {...} }
    2. Claude Desktop extensions format:
       {
         "manifest": {
           "display_name": "...",
           "server": {
             "type": "node",
             "entry_point": "server/index.js",
             "mcp_config": { "command": "node", "args": [...], "env": {...} }
           }
         }
       }
    """
    # Check if this is Claude Desktop extensions format
    if "manifest" in config:
        manifest = config["manifest"]
        # Use display_name as the server name if available
        display_name = manifest.get("display_name", name)
        server_info = manifest.get("server", {})

        # Check for mcp_config which contains standard format
        mcp_config = server_info.get("mcp_config", {})
        if mcp_config:
            # Use mcp_config which has standard command/args
            command = mcp_config.get("command")
            args = mcp_config.get("args")
            env = mcp_config.get("env")
        else:
            # Fallback: parse entry_point if no mcp_config
            entry_point = server_info.get("entry_point", "")
            command = None
            args = None
            env = None

            if entry_point:
                parts = entry_point.split()
                if parts:
                    command = parts[0]
                    args = parts[1:] if len(parts) > 1 else []

        # Map server type (node -> stdio for MCP purposes)
        server_type = server_info.get("type", "stdio")
        if server_type == "node":
            server_type = "stdio"

        server = MCPServerConfig(
            name=display_name,
            type=server_type,
            command=command,
            args=args,
            url=None,
            env=env,
            headers=None,
        )
    else:
        # Standard MCP format
        # Determine transport type
        if "url" in config:
            transport_type = config.get("transport", "sse")
        else:
            transport_type = "stdio"

        server = MCPServerConfig(
            name=name,
            type=transport_type,
            command=config.get("command"),
            args=config.get("args"),
            url=config.get("url"),
            env=config.get("env"),
            headers=config.get("headers"),
        )

    server.config_hash = compute_config_hash(server)
    return server


def parse_config_file(
    client_def: MCPClientDefinition,
    config_path: Path,
) -> MCPClientConfig | None:
    """
    Parse an MCP client configuration file.

    Uses the client definition to determine how to extract servers from the
    config file, handling client-specific JSON structures.

    Args:
        client_def: Client definition with parsing configuration
        config_path: Path to the configuration file

    Returns:
        MCPClientConfig if successfully parsed, None if file doesn't exist or is invalid
    """
    if not config_path.exists():
        logger.debug(
            "Config file not found",
            client=client_def.name,
            path=str(config_path),
        )
        return None

    try:
        with open(config_path, encoding="utf-8") as f:
            raw_config = json.load(f)
    except json.JSONDecodeError as e:
        logger.warning(
            "Failed to parse config file - invalid JSON",
            client=client_def.name,
            path=str(config_path),
            error=str(e),
        )
        return None
    except IOError as e:
        logger.warning(
            "Failed to read config file",
            client=client_def.name,
            path=str(config_path),
            error=str(e),
        )
        return None

    # Get file modification time
    try:
        stat = config_path.stat()
        modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
    except OSError:
        modified_at = None

    # Use the client definition to extract servers from the config
    # This handles client-specific JSON structures
    mcp_servers = client_def.extract_servers(raw_config)

    # Parse each server entry
    servers: list[MCPServerConfig] = []
    for name, server_config in mcp_servers.items():
        if isinstance(server_config, dict):
            try:
                server = _parse_server_entry(name, server_config)
                servers.append(server)
            except Exception as e:
                logger.warning(
                    "Failed to parse server entry",
                    client=client_def.name,
                    server_name=name,
                    error=str(e),
                )
                continue

    if not servers:
        logger.debug(
            "No MCP servers found in config",
            client=client_def.name,
            path=str(config_path),
        )
        return None

    logger.debug(
        "Parsed config file",
        client=client_def.name,
        path=str(config_path),
        server_count=len(servers),
    )

    return MCPClientConfig(
        client=client_def.name,
        client_version=None,  # TODO: Could detect from app version
        config_path=str(config_path),
        config_modified_at=modified_at,
        servers=servers,
    )
