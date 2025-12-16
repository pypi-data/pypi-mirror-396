"""MCP Watch scan service - orchestrates the scanning process."""

import time
from dataclasses import dataclass
from typing import Any

import structlog

from runlayer_cli.scan.clients import (
    MCPClientDefinition,
    get_all_clients,
    get_client_by_name,
    get_clients_with_project_configs,
)
from runlayer_cli.scan.config_parser import MCPClientConfig, parse_config_file
from runlayer_cli.scan.device import get_device_metadata, get_or_create_device_id
from runlayer_cli.scan.project_scanner import scan_for_project_configs

logger = structlog.get_logger(__name__)


@dataclass
class ScanResult:
    """Result of a scan operation."""

    device_id: str
    hostname: str | None
    os: str | None
    os_version: str | None
    username: str | None
    org_device_id: str | None
    scan_duration_ms: int
    collector_version: str
    configurations: list[MCPClientConfig]

    @property
    def total_servers(self) -> int:
        """Total number of servers found across all clients."""
        return sum(len(c.servers) for c in self.configurations)

    @property
    def clients_with_servers(self) -> list[str]:
        """List of client names that had servers configured."""
        return [c.client for c in self.configurations]

    @property
    def global_configs(self) -> list[MCPClientConfig]:
        """Configurations from global/user-level config files."""
        return [c for c in self.configurations if c.config_scope == "global"]

    @property
    def project_configs(self) -> list[MCPClientConfig]:
        """Configurations from project-level config files."""
        return [c for c in self.configurations if c.config_scope == "project"]

    def to_api_payload(self) -> dict[str, Any]:
        """Convert to API payload format."""
        return {
            "device_id": self.device_id,
            "hostname": self.hostname,
            "os": self.os,
            "os_version": self.os_version,
            "username": self.username,
            "org_device_id": self.org_device_id,
            "scan_duration_ms": self.scan_duration_ms,
            "collector_version": self.collector_version,
            "configurations": [
                {
                    "client": c.client,
                    "client_version": c.client_version,
                    "config_path": c.config_path,
                    "config_modified_at": c.config_modified_at,
                    "config_scope": c.config_scope,
                    "project_path": c.project_path,
                    "servers": [
                        {
                            "name": s.name,
                            "type": s.type,
                            "command": s.command,
                            "args": s.args,
                            "url": s.url,
                            "env": s.env,
                            "headers": s.headers,
                            "config_hash": s.config_hash,
                        }
                        for s in c.servers
                    ],
                }
                for c in self.configurations
            ],
        }


def scan_all_clients(
    device_id: str | None = None,
    org_device_id: str | None = None,
    collector_version: str = "unknown",
    scan_projects: bool = True,
    project_scan_timeout: int = 60,
    project_scan_depth: int = 5,
) -> ScanResult:
    """
    Scan all known MCP client configurations (global and project-level).

    Args:
        device_id: Override device ID (uses auto-generated if None)
        org_device_id: Organization-provided device ID (e.g., from MDM)
        collector_version: Version of the CLI performing the scan
        scan_projects: Whether to scan for project-level configs (default True)
        project_scan_timeout: Timeout in seconds for project scanning (default 60)
        project_scan_depth: Max directory depth for project scanning (default 5)

    Returns:
        ScanResult with all discovered configurations
    """
    start_time = time.time()

    # Get device info
    actual_device_id = device_id or get_or_create_device_id()
    device_metadata = get_device_metadata()

    configurations: list[MCPClientConfig] = []

    # ==========================================================================
    # PHASE 1: Scan global/user-level configurations
    # ==========================================================================
    logger.info("Scanning global configurations")
    clients = get_all_clients()

    for client_def in clients:
        config_paths = client_def.get_config_paths()

        for config_path in config_paths:
            logger.debug(
                "Scanning global config",
                client=client_def.name,
                path=str(config_path),
            )

            config = parse_config_file(client_def, config_path)
            if config and config.servers:
                config.config_scope = "global"
                configurations.append(config)
                logger.info(
                    "Found MCP servers (global)",
                    client=client_def.name,
                    server_count=len(config.servers),
                    path=str(config_path),
                )

    # ==========================================================================
    # PHASE 2: Scan project-level configurations
    # ==========================================================================
    if scan_projects:
        logger.info("Scanning project-level configurations")
        clients_with_projects = get_clients_with_project_configs()

        project_configs = scan_for_project_configs(
            clients=clients_with_projects,
            timeout=project_scan_timeout,
            max_depth=project_scan_depth,
        )

        for proj_config in project_configs:
            # Get the client definition to use for parsing
            client_def = get_client_by_name(proj_config.client_name)
            if client_def is None:
                continue

            # Create a temporary client def with the project's servers_key
            temp_client_def = MCPClientDefinition(
                name=client_def.name,
                display_name=client_def.display_name,
                paths=[],
                servers_key=proj_config.servers_key,
            )

            config = parse_config_file(temp_client_def, proj_config.config_path)
            if config and config.servers:
                config.config_scope = "project"
                config.project_path = str(proj_config.project_path)
                configurations.append(config)
                logger.info(
                    "Found MCP servers (project)",
                    client=client_def.name,
                    server_count=len(config.servers),
                    config_path=str(proj_config.config_path),
                    project_path=str(proj_config.project_path),
                )

    scan_duration_ms = int((time.time() - start_time) * 1000)

    logger.info(
        "Scan complete",
        total_configs=len(configurations),
        global_configs=len([c for c in configurations if c.config_scope == "global"]),
        project_configs=len([c for c in configurations if c.config_scope == "project"]),
        total_servers=sum(len(c.servers) for c in configurations),
        duration_ms=scan_duration_ms,
    )

    return ScanResult(
        device_id=actual_device_id,
        hostname=device_metadata.get("hostname"),
        os=device_metadata.get("os"),
        os_version=device_metadata.get("os_version"),
        username=device_metadata.get("username"),
        org_device_id=org_device_id,
        scan_duration_ms=scan_duration_ms,
        collector_version=collector_version,
        configurations=configurations,
    )
