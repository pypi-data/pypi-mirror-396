"""MCP client application definitions and configuration paths."""

from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ConfigPath:
    """A configuration file path with platform specification.

    Attributes:
        path: Path template string. Supports:
            - ~ for home directory
            - Environment variables like %APPDATA%, $HOME
        platform: Target platform ("macos", "windows", or "all")
    """

    path: str
    platform: str = "all"  # "macos", "windows", or "all"

    def resolve(self) -> Path | None:
        """Resolve the path for the current platform.

        Returns:
            Resolved Path if platform matches, None otherwise.
        """
        current_platform = {
            "Darwin": "macos",
            "Windows": "windows",
            "Linux": "linux",
        }.get(platform.system())

        if self.platform != "all" and self.platform != current_platform:
            return None

        # Expand environment variables (handles both Unix $VAR and Windows %VAR%)
        expanded = os.path.expandvars(self.path)
        # Expand ~ to home directory
        return Path(expanded).expanduser()


@dataclass
class ProjectConfigPattern:
    """Pattern for finding project-level config files.

    Attributes:
        relative_path: Path relative to project root (e.g., ".mcp.json", ".vscode/mcp.json")
        servers_key: JSON key containing server definitions (may differ from global config)
    """

    relative_path: str
    servers_key: str = "mcpServers"


@dataclass
class MCPClientDefinition:
    """Definition of an MCP client application.

    This data model is designed to be:
    1. Easy to update when clients change their config locations
    2. Declarative - parsing behavior is defined by data, not code
    3. Self-documenting - each field has a clear purpose

    Attributes:
        name: Internal identifier (lowercase, snake_case)
        display_name: Human-readable name for logging/display
        paths: List of possible GLOBAL config file locations
        servers_key: JSON key path to the servers dictionary for GLOBAL configs
            - "mcpServers" - standard MCP format
            - "servers" - alternative format (VS Code)
            - "" (empty) - servers are at root level
        additional_servers_keys: Additional key paths to extract servers from
            (e.g., for Claude Code's "projects.*.mcpServers" structure)
        project_config: Optional pattern for project-level configs
        enabled: Whether to scan this client (allows disabling without removing)
        notes: Optional notes about this client's config format
    """

    name: str
    display_name: str
    paths: list[ConfigPath]
    servers_key: str = "mcpServers"  # JSON key for GLOBAL configs
    additional_servers_keys: list[str] | None = (
        None  # Extra paths like "projects.*.mcpServers"
    )
    project_config: ProjectConfigPattern | None = None  # Optional project-level config
    enabled: bool = True
    notes: str | None = None

    def get_config_paths(self) -> list[Path]:
        """Get all valid config paths for the current platform.

        Returns:
            List of resolved paths that exist on the current platform.
        """
        resolved: list[Path] = []
        for config_path in self.paths:
            path = config_path.resolve()
            if path is not None:
                resolved.append(path)
        return resolved

    def _extract_from_key_path(
        self, config_data: dict[str, Any], key_path: str
    ) -> dict[str, Any]:
        """Extract servers from a specific key path.

        Supports wildcard '*' for iterating over dictionary keys.
        E.g., "projects.*.mcpServers" extracts mcpServers from each project.

        Args:
            config_data: Parsed JSON config file contents
            key_path: Dot-separated key path, with optional '*' wildcards

        Returns:
            Dictionary of server_name -> server_config
        """
        if not key_path:
            # Servers are at root level - return any dict entries that look like servers
            return {
                k: v
                for k, v in config_data.items()
                if isinstance(v, dict) and ("command" in v or "url" in v)
            }

        keys = key_path.split(".")
        result: dict[str, Any] = {}

        def traverse(current: Any, remaining_keys: list[str], prefix: str = "") -> None:
            if not remaining_keys:
                if isinstance(current, dict):
                    for name, config in current.items():
                        if isinstance(config, dict):
                            # Add prefix to disambiguate servers from different projects
                            full_name = f"{prefix}{name}" if prefix else name
                            result[full_name] = config
                return

            key = remaining_keys[0]
            rest = remaining_keys[1:]

            if key == "*":
                # Wildcard - iterate over all dict keys
                if isinstance(current, dict):
                    for sub_key, sub_value in current.items():
                        new_prefix = f"{prefix}{sub_key}/" if prefix else f"{sub_key}/"
                        traverse(sub_value, rest, new_prefix)
            else:
                # Regular key - navigate into it
                if isinstance(current, dict) and key in current:
                    traverse(current[key], rest, prefix)

        traverse(config_data, keys)
        return result

    def extract_servers(self, config_data: dict[str, Any]) -> dict[str, Any]:
        """Extract the servers dictionary from parsed config data.

        Args:
            config_data: Parsed JSON config file contents

        Returns:
            Dictionary of server_name -> server_config, or empty dict if not found
        """
        # Extract from primary key path
        servers = self._extract_from_key_path(config_data, self.servers_key)

        # Extract from additional key paths (e.g., projects.*.mcpServers for Claude Code)
        if self.additional_servers_keys:
            for key_path in self.additional_servers_keys:
                additional = self._extract_from_key_path(config_data, key_path)
                servers.update(additional)

        return servers


# =============================================================================
# MCP CLIENT REGISTRY
# =============================================================================
#
# To add a new client:
#   1. Add a new MCPClientDefinition to MCP_CLIENTS list
#   2. Specify all known config paths for each platform
#   3. Set servers_key based on the client's JSON structure
#   4. Add a note if there's anything unusual about the format
#
# To update a client:
#   1. Find the client in MCP_CLIENTS by name
#   2. Update the paths or servers_key as needed
#   3. Update notes if the format changed
#
# To disable a client temporarily:
#   1. Set enabled=False on the client definition
#
# =============================================================================

MCP_CLIENTS: list[MCPClientDefinition] = [
    MCPClientDefinition(
        name="cursor",
        display_name="Cursor",
        paths=[
            ConfigPath("~/.cursor/mcp.json", platform="macos"),
            ConfigPath("%USERPROFILE%/.cursor/mcp.json", platform="windows"),
        ],
        servers_key="mcpServers",
        project_config=None,  # Cursor only has global config
    ),
    MCPClientDefinition(
        name="claude_desktop",
        display_name="Claude Desktop",
        paths=[
            ConfigPath(
                "~/Library/Application Support/Claude/extensions-installations.json",
                platform="macos",
            ),
            ConfigPath(
                "%APPDATA%/Claude/extensions-installations.json", platform="windows"
            ),
        ],
        servers_key="extensions",  # Extensions format, not mcpServers
        project_config=None,  # Claude Desktop only has global config
        notes="Uses extensions format with manifest.server.type and manifest.server.entry_point",
    ),
    MCPClientDefinition(
        name="claude_code",
        display_name="Claude Code",
        paths=[
            ConfigPath("~/.claude.json", platform="macos"),
            ConfigPath("%USERPROFILE%/.claude.json", platform="windows"),
        ],
        servers_key="mcpServers",
        additional_servers_keys=[
            "projects.*.mcpServers"
        ],  # Project-specific servers in global file
        project_config=ProjectConfigPattern(
            relative_path=".mcp.json",
            servers_key="mcpServers",
        ),
        notes="Has mcpServers at root AND projects.*.mcpServers for project-specific configs in same file",
    ),
    MCPClientDefinition(
        name="vscode",
        display_name="VS Code",
        paths=[
            ConfigPath(
                "~/Library/Application Support/Code/User/mcp.json", platform="macos"
            ),
            ConfigPath("%APPDATA%/Code/User/mcp.json", platform="windows"),
        ],
        servers_key="servers",  # VS Code uses "servers" NOT "mcpServers"!
        project_config=ProjectConfigPattern(
            relative_path=".vscode/mcp.json",
            servers_key="servers",  # Project config also uses "servers"
        ),
        notes="VS Code uses 'servers' key (not 'mcpServers') for both global and project configs",
    ),
    MCPClientDefinition(
        name="windsurf",
        display_name="Windsurf",
        paths=[
            ConfigPath("~/.codeium/windsurf/mcp_config.json", platform="macos"),
            ConfigPath(
                "%USERPROFILE%/.codeium/windsurf/mcp_config.json", platform="windows"
            ),
        ],
        servers_key="mcpServers",
        project_config=ProjectConfigPattern(
            relative_path=".windsurf/mcp_config.json",
            servers_key="mcpServers",
        ),
        notes="Has both global and project-level (.windsurf/mcp_config.json) configs",
    ),
    # ==========================================================================
    # DESCOPED FROM v0 - Add these in a future release
    # ==========================================================================
    # MCPClientDefinition(
    #     name="warp",
    #     display_name="Warp",
    #     paths=[
    #         ConfigPath(
    #             "~/Library/Group Containers/2BBY89MBSN.dev.warp/Library/Application Support/dev.warp.Warp-Stable/mcp/config.json",
    #             platform="macos",
    #         ),
    #         ConfigPath("%APPDATA%/Warp/mcp/config.json", platform="windows"),
    #     ],
    #     servers_key="mcpServers",
    #     notes="Descoped from v0 - complex path, Windows path unverified",
    # ),
    # MCPClientDefinition(
    #     name="raycast",
    #     display_name="Raycast",
    #     paths=[
    #         ConfigPath("???", platform="macos"),  # TODO: Research exact path
    #     ],
    #     servers_key="mcpServers",
    #     notes="Descoped from v0 - config path needs research",
    # ),
]


def get_all_clients() -> list[MCPClientDefinition]:
    """Get all enabled MCP client definitions.

    Returns:
        List of MCPClientDefinition for enabled clients only.
    """
    return [c for c in MCP_CLIENTS if c.enabled]


def get_client_by_name(name: str) -> MCPClientDefinition | None:
    """Get a specific client definition by name.

    Args:
        name: Client name (e.g., "cursor", "claude_desktop")

    Returns:
        MCPClientDefinition if found, None otherwise.
    """
    for client in MCP_CLIENTS:
        if client.name == name:
            return client
    return None


def get_clients_with_project_configs() -> list[MCPClientDefinition]:
    """Get all enabled clients that have project-level config patterns.

    Returns:
        List of MCPClientDefinition for clients with project_config defined.
    """
    return [c for c in MCP_CLIENTS if c.enabled and c.project_config is not None]
