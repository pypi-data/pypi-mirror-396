"""Tests for config file parsing."""

import json
from pathlib import Path

import pytest

from runlayer_cli.scan.clients import ConfigPath, MCPClientDefinition, get_client_by_name
from runlayer_cli.scan.config_parser import (
    MCPServerConfig,
    compute_config_hash,
    parse_config_file,
)


def make_client_def(servers_key: str = "mcpServers") -> MCPClientDefinition:
    """Create a test client definition."""
    return MCPClientDefinition(
        name="test",
        display_name="Test Client",
        paths=[],
        servers_key=servers_key,
    )


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


class TestComputeConfigHash:
    def test_same_config_same_hash(self):
        """Same configuration produces same hash."""
        server1 = MCPServerConfig(name="test", type="stdio", command="npx")
        server2 = MCPServerConfig(name="test", type="stdio", command="npx")
        assert compute_config_hash(server1) == compute_config_hash(server2)

    def test_different_name_different_hash(self):
        """Different names produce different hashes."""
        server1 = MCPServerConfig(name="test1", type="stdio", command="npx")
        server2 = MCPServerConfig(name="test2", type="stdio", command="npx")
        assert compute_config_hash(server1) != compute_config_hash(server2)

    def test_env_excluded_from_hash(self):
        """Environment variables don't affect hash."""
        server1 = MCPServerConfig(
            name="test", type="stdio", command="npx", env={"KEY": "value1"}
        )
        server2 = MCPServerConfig(
            name="test", type="stdio", command="npx", env={"KEY": "value2"}
        )
        assert compute_config_hash(server1) == compute_config_hash(server2)

    def test_hash_is_64_chars(self):
        """Hash is full SHA-256 (64 hex chars)."""
        server = MCPServerConfig(name="test", type="stdio", command="npx")
        hash_value = compute_config_hash(server)
        assert len(hash_value) == 64


class TestParseConfigFile:
    def test_nonexistent_file_returns_none(self, tmp_path):
        """Non-existent file returns None."""
        client_def = make_client_def()
        result = parse_config_file(client_def, tmp_path / "nonexistent.json")
        assert result is None

    def test_invalid_json_returns_none(self, tmp_path):
        """Invalid JSON returns None."""
        config_file = tmp_path / "config.json"
        config_file.write_text("not valid json")
        client_def = make_client_def()
        result = parse_config_file(client_def, config_file)
        assert result is None

    def test_empty_servers_returns_none(self, tmp_path):
        """Config with no servers returns None."""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"mcpServers": {}}))
        client_def = make_client_def()
        result = parse_config_file(client_def, config_file)
        assert result is None

    def test_parses_stdio_server(self, tmp_path):
        """Parses stdio server configuration."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "mcpServers": {
                        "test-server": {
                            "command": "npx",
                            "args": ["-y", "@modelcontextprotocol/server-test"],
                        }
                    }
                }
            )
        )
        client_def = MCPClientDefinition(
            name="cursor",
            display_name="Cursor",
            paths=[],
            servers_key="mcpServers",
        )
        result = parse_config_file(client_def, config_file)
        assert result is not None
        assert result.client == "cursor"
        assert len(result.servers) == 1
        assert result.servers[0].name == "test-server"
        assert result.servers[0].type == "stdio"
        assert result.servers[0].command == "npx"

    def test_parses_sse_server(self, tmp_path):
        """Parses SSE server configuration."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "mcpServers": {
                        "remote-server": {
                            "url": "https://example.com/mcp",
                            "transport": "sse",
                        }
                    }
                }
            )
        )
        client_def = make_client_def()
        result = parse_config_file(client_def, config_file)
        assert result is not None
        assert result.servers[0].type == "sse"
        assert result.servers[0].url == "https://example.com/mcp"

    def test_parses_custom_servers_key(self, tmp_path):
        """Parses config with non-standard servers key."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "mcp": {
                        "servers": {
                            "custom-server": {"command": "node", "args": ["server.js"]}
                        }
                    }
                }
            )
        )
        client_def = make_client_def(servers_key="mcp.servers")
        result = parse_config_file(client_def, config_file)
        assert result is not None
        assert len(result.servers) == 1
        assert result.servers[0].name == "custom-server"

    def test_parses_root_level_servers(self, tmp_path):
        """Parses config with servers at root level."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "my-server": {"command": "npx", "args": ["-y", "some-package"]},
                    "another-server": {"url": "https://api.example.com/mcp"},
                }
            )
        )
        client_def = make_client_def(servers_key="")
        result = parse_config_file(client_def, config_file)
        assert result is not None
        assert len(result.servers) == 2


class TestParseConfigFileWithFixtures:
    def test_parse_cursor_config(self, fixtures_dir):
        """Parse real Cursor config fixture."""
        client_def = get_client_by_name("cursor")
        assert client_def is not None
        result = parse_config_file(client_def, fixtures_dir / "cursor_config.json")

        assert result is not None
        assert len(result.servers) == 2
        server_names = [s.name for s in result.servers]
        assert "filesystem" in server_names
        assert "github" in server_names

    def test_parse_vscode_config_with_servers_key(self, fixtures_dir):
        """Parse VS Code config which uses 'servers' not 'mcpServers'."""
        client_def = get_client_by_name("vscode")
        assert client_def is not None
        result = parse_config_file(client_def, fixtures_dir / "vscode_config.json")

        assert result is not None
        assert len(result.servers) == 2
        server_names = [s.name for s in result.servers]
        assert "github-copilot" in server_names
        assert "filesystem" in server_names

    def test_vscode_config_not_parsed_with_wrong_key(self, fixtures_dir):
        """VS Code config should NOT parse if using wrong servers_key."""
        # Try to parse VS Code config with wrong key
        wrong_client_def = MCPClientDefinition(
            name="test",
            display_name="Test",
            paths=[],
            servers_key="mcpServers",  # Wrong! VS Code uses "servers"
        )
        result = parse_config_file(wrong_client_def, fixtures_dir / "vscode_config.json")

        # Should return None because mcpServers key doesn't exist
        assert result is None

    def test_parse_sse_server(self, fixtures_dir):
        """Parse SSE server config fixture."""
        client_def = MCPClientDefinition(
            name="test",
            display_name="Test",
            paths=[],
            servers_key="mcpServers",
        )
        result = parse_config_file(client_def, fixtures_dir / "sse_server_config.json")

        assert result is not None
        assert result.servers[0].type == "sse"
        assert result.servers[0].url == "https://api.example.com/mcp/sse"
        assert result.servers[0].headers is not None

    def test_parse_claude_code_with_projects(self, fixtures_dir):
        """Parse Claude Code config with both global and project servers."""
        client_def = get_client_by_name("claude_code")
        assert client_def is not None
        result = parse_config_file(client_def, fixtures_dir / "claude_code_config.json")

        assert result is not None
        # Should have 3 servers: 1 global + 2 project-specific
        assert len(result.servers) == 3
        server_names = [s.name for s in result.servers]
        assert "global-server" in server_names
        # Project servers are prefixed with project path
        assert any("project-a-server" in name for name in server_names)
        assert any("project-b-server" in name for name in server_names)

    def test_parse_claude_desktop_extensions_format(self, fixtures_dir):
        """Parse Claude Desktop config with extensions format."""
        client_def = get_client_by_name("claude_desktop")
        assert client_def is not None
        result = parse_config_file(
            client_def, fixtures_dir / "claude_desktop_config.json"
        )

        assert result is not None
        assert len(result.servers) == 2
        server_names = [s.name for s in result.servers]
        # Should use display_name from manifest
        assert "Read and Write Apple Notes" in server_names
        assert "Filesystem" in server_names

        # Check that command was parsed from mcp_config
        notes_server = next(
            s for s in result.servers if s.name == "Read and Write Apple Notes"
        )
        assert notes_server.command == "node"
        assert notes_server.args == ["${__dirname}/server/index.js"]
        assert notes_server.type == "stdio"  # "node" is mapped to "stdio"
        assert notes_server.env == {"HOME": "${HOME}"}
