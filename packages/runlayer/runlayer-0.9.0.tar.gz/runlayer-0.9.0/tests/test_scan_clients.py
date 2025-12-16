"""Tests for MCP client definitions."""

import platform
from pathlib import Path
from unittest import mock

import pytest

from runlayer_cli.scan.clients import (
    ConfigPath,
    MCPClientDefinition,
    get_all_clients,
    get_client_by_name,
    get_clients_with_project_configs,
)


class TestConfigPath:
    def test_resolve_home_expansion(self):
        """Test ~ expansion works."""
        config_path = ConfigPath("~/test/config.json", platform="all")
        result = config_path.resolve()
        assert result == Path.home() / "test" / "config.json"

    @mock.patch.dict("os.environ", {"APPDATA": "C:/Users/Test/AppData/Roaming"})
    def test_resolve_windows_env(self):
        """Test Windows environment variable expansion."""
        config_path = ConfigPath("%APPDATA%/Test/config.json", platform="all")
        result = config_path.resolve()
        assert "Test" in str(result)

    @mock.patch("platform.system", return_value="Darwin")
    def test_resolve_returns_none_for_wrong_platform(self, mock_system):
        """Test that wrong platform returns None."""
        config_path = ConfigPath("/test/config.json", platform="windows")
        result = config_path.resolve()
        assert result is None

    @mock.patch("platform.system", return_value="Darwin")
    def test_resolve_works_for_matching_platform(self, mock_system):
        """Test that matching platform resolves path."""
        config_path = ConfigPath("/test/config.json", platform="macos")
        result = config_path.resolve()
        assert result == Path("/test/config.json")

    @mock.patch("platform.system", return_value="Darwin")
    def test_resolve_works_for_all_platform(self, mock_system):
        """Test that 'all' platform always resolves."""
        config_path = ConfigPath("/test/config.json", platform="all")
        result = config_path.resolve()
        assert result == Path("/test/config.json")


class TestMCPClientDefinition:
    def test_get_config_paths_returns_list(self):
        """Test that get_config_paths returns a list."""
        client = MCPClientDefinition(
            name="test",
            display_name="Test",
            paths=[ConfigPath("/test/config.json", platform="all")],
        )
        paths = client.get_config_paths()
        assert isinstance(paths, list)
        assert len(paths) == 1

    def test_extract_servers_standard_format(self):
        """Test extracting servers from standard mcpServers key."""
        client = MCPClientDefinition(
            name="test",
            display_name="Test",
            paths=[],
            servers_key="mcpServers",
        )
        config_data = {
            "mcpServers": {
                "server1": {"command": "npx"},
                "server2": {"url": "https://example.com"},
            }
        }
        servers = client.extract_servers(config_data)
        assert len(servers) == 2
        assert "server1" in servers
        assert "server2" in servers

    def test_extract_servers_nested_key(self):
        """Test extracting servers from nested key like mcp.servers."""
        client = MCPClientDefinition(
            name="test",
            display_name="Test",
            paths=[],
            servers_key="mcp.servers",
        )
        config_data = {
            "mcp": {
                "servers": {
                    "server1": {"command": "npx"},
                }
            }
        }
        servers = client.extract_servers(config_data)
        assert len(servers) == 1
        assert "server1" in servers

    def test_extract_servers_root_level(self):
        """Test extracting servers from root level (empty servers_key)."""
        client = MCPClientDefinition(
            name="test",
            display_name="Test",
            paths=[],
            servers_key="",
        )
        config_data = {
            "server1": {"command": "npx"},
            "server2": {"url": "https://example.com"},
            "otherKey": "not a server",
        }
        servers = client.extract_servers(config_data)
        assert len(servers) == 2
        assert "server1" in servers
        assert "otherKey" not in servers

    def test_extract_servers_with_wildcard_key(self):
        """Test extracting servers from wildcard key like projects.*.mcpServers."""
        client = MCPClientDefinition(
            name="test",
            display_name="Test",
            paths=[],
            servers_key="mcpServers",
            additional_servers_keys=["projects.*.mcpServers"],
        )
        config_data = {
            "mcpServers": {
                "global-server": {"command": "npx"},
            },
            "projects": {
                "/path/to/project-a": {
                    "mcpServers": {
                        "project-a-server": {"command": "node"},
                    }
                },
                "/path/to/project-b": {
                    "mcpServers": {
                        "project-b-server": {"command": "python"},
                    }
                },
            },
        }
        servers = client.extract_servers(config_data)
        assert len(servers) == 3
        assert "global-server" in servers
        # Project servers get prefixed with project path
        assert any("project-a-server" in k for k in servers.keys())
        assert any("project-b-server" in k for k in servers.keys())

    def test_disabled_client_excluded(self):
        """Test that disabled clients are not returned by get_all_clients."""
        # This tests the registry behavior
        clients = get_all_clients()
        for client in clients:
            assert client.enabled is True


class TestGetAllClients:
    def test_returns_list(self):
        """Test that get_all_clients returns a list."""
        clients = get_all_clients()
        assert isinstance(clients, list)
        assert len(clients) > 0

    def test_includes_known_clients(self):
        """Test that known clients are included."""
        clients = get_all_clients()
        names = [c.name for c in clients]
        # v0 supported clients
        assert "cursor" in names
        assert "claude_desktop" in names
        assert "claude_code" in names
        assert "vscode" in names
        assert "windsurf" in names
        # Descoped from v0
        assert "warp" not in names
        assert "raycast" not in names


class TestGetClientByName:
    def test_returns_client_if_exists(self):
        """Test that existing client is returned."""
        client = get_client_by_name("cursor")
        assert client is not None
        assert client.name == "cursor"

    def test_returns_none_if_not_exists(self):
        """Test that None is returned for unknown client."""
        client = get_client_by_name("nonexistent")
        assert client is None


class TestGetClientsWithProjectConfigs:
    def test_returns_only_clients_with_project_config(self):
        """Test that only clients with project configs are returned."""
        clients = get_clients_with_project_configs()
        for client in clients:
            assert client.project_config is not None

    def test_includes_expected_clients(self):
        """Test that expected clients with project configs are included."""
        clients = get_clients_with_project_configs()
        names = [c.name for c in clients]
        # These clients have project configs
        assert "claude_code" in names
        assert "vscode" in names
        assert "windsurf" in names
        # These don't
        assert "cursor" not in names
        assert "claude_desktop" not in names


class TestClientServersKey:
    """Test that each client has the correct servers_key configured."""

    def test_vscode_uses_servers_key(self):
        """VS Code uses 'servers' not 'mcpServers'."""
        client = get_client_by_name("vscode")
        assert client is not None
        assert client.servers_key == "servers", "VS Code must use 'servers' key, not 'mcpServers'"

    def test_cursor_uses_mcpservers_key(self):
        """Cursor uses standard 'mcpServers' key."""
        client = get_client_by_name("cursor")
        assert client is not None
        assert client.servers_key == "mcpServers"

    def test_claude_desktop_uses_extensions_key(self):
        """Claude Desktop uses 'extensions' key for extensions-installations.json."""
        client = get_client_by_name("claude_desktop")
        assert client is not None
        assert client.servers_key == "extensions"

    def test_claude_code_uses_mcpservers_key(self):
        """Claude Code uses standard 'mcpServers' key."""
        client = get_client_by_name("claude_code")
        assert client is not None
        assert client.servers_key == "mcpServers"

    def test_claude_code_has_additional_keys(self):
        """Claude Code has additional keys for projects.*.mcpServers."""
        client = get_client_by_name("claude_code")
        assert client is not None
        assert client.additional_servers_keys is not None
        assert "projects.*.mcpServers" in client.additional_servers_keys

    def test_windsurf_uses_mcpservers_key(self):
        """Windsurf uses standard 'mcpServers' key."""
        client = get_client_by_name("windsurf")
        assert client is not None
        assert client.servers_key == "mcpServers"
