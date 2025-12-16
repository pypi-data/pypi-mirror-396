"""Tests for scan service orchestration."""

import json
from pathlib import Path
from unittest import mock

import pytest

from runlayer_cli.scan.service import ScanResult, scan_all_clients


class TestScanAllClients:
    def test_returns_scan_result(self):
        """Returns ScanResult dataclass."""
        result = scan_all_clients(scan_projects=False)  # Skip project scan for speed
        assert isinstance(result, ScanResult)
        assert result.device_id is not None
        assert result.configurations is not None

    def test_includes_device_metadata(self):
        """Result includes device metadata."""
        result = scan_all_clients(scan_projects=False)
        assert result.hostname is not None
        assert result.os is not None

    def test_custom_device_id_used(self):
        """Custom device ID overrides auto-generated."""
        result = scan_all_clients(device_id="custom-id", scan_projects=False)
        assert result.device_id == "custom-id"

    def test_scan_duration_recorded(self):
        """Scan duration is recorded in milliseconds."""
        result = scan_all_clients(scan_projects=False)
        assert result.scan_duration_ms >= 0

    def test_collector_version_recorded(self):
        """Collector version is recorded."""
        result = scan_all_clients(collector_version="1.2.3", scan_projects=False)
        assert result.collector_version == "1.2.3"

    def test_org_device_id_passed_through(self):
        """Organization device ID is passed through."""
        result = scan_all_clients(org_device_id="mdm-asset-123", scan_projects=False)
        assert result.org_device_id == "mdm-asset-123"

    @mock.patch("runlayer_cli.scan.service.get_all_clients")
    @mock.patch("runlayer_cli.scan.service.get_clients_with_project_configs")
    def test_scans_all_enabled_clients(
        self, mock_get_project_clients, mock_get_clients, tmp_path
    ):
        """Scans all enabled clients."""
        from runlayer_cli.scan.clients import ConfigPath, MCPClientDefinition

        # Create a test config file
        config_file = tmp_path / "test_config.json"
        config_file.write_text(
            json.dumps({"mcpServers": {"test-server": {"command": "npx"}}})
        )

        mock_get_clients.return_value = [
            MCPClientDefinition(
                name="test_client",
                display_name="Test Client",
                paths=[ConfigPath(str(config_file), platform="all")],
                servers_key="mcpServers",
            )
        ]
        mock_get_project_clients.return_value = []  # No project configs

        result = scan_all_clients(scan_projects=False)
        assert len(result.configurations) == 1
        assert result.configurations[0].client == "test_client"


class TestScanResultProperties:
    def test_total_servers_property(self):
        """total_servers sums servers from all configurations."""
        from runlayer_cli.scan.config_parser import MCPClientConfig, MCPServerConfig

        result = ScanResult(
            device_id="test",
            hostname="test",
            os="darwin",
            os_version="14.0",
            username="user",
            org_device_id=None,
            scan_duration_ms=100,
            collector_version="1.0.0",
            configurations=[
                MCPClientConfig(
                    client="client1",
                    servers=[
                        MCPServerConfig(name="s1", type="stdio"),
                        MCPServerConfig(name="s2", type="stdio"),
                    ],
                ),
                MCPClientConfig(
                    client="client2",
                    servers=[
                        MCPServerConfig(name="s3", type="sse"),
                    ],
                ),
            ],
        )

        assert result.total_servers == 3

    def test_clients_with_servers_property(self):
        """clients_with_servers returns list of client names."""
        from runlayer_cli.scan.config_parser import MCPClientConfig, MCPServerConfig

        result = ScanResult(
            device_id="test",
            hostname="test",
            os="darwin",
            os_version="14.0",
            username="user",
            org_device_id=None,
            scan_duration_ms=100,
            collector_version="1.0.0",
            configurations=[
                MCPClientConfig(
                    client="cursor",
                    servers=[MCPServerConfig(name="s1", type="stdio")],
                ),
                MCPClientConfig(
                    client="vscode",
                    servers=[MCPServerConfig(name="s2", type="stdio")],
                ),
            ],
        )

        assert result.clients_with_servers == ["cursor", "vscode"]

    def test_global_and_project_configs_properties(self):
        """global_configs and project_configs filter correctly."""
        from runlayer_cli.scan.config_parser import MCPClientConfig, MCPServerConfig

        result = ScanResult(
            device_id="test",
            hostname="test",
            os="darwin",
            os_version="14.0",
            username="user",
            org_device_id=None,
            scan_duration_ms=100,
            collector_version="1.0.0",
            configurations=[
                MCPClientConfig(
                    client="cursor",
                    servers=[MCPServerConfig(name="s1", type="stdio")],
                    config_scope="global",
                ),
                MCPClientConfig(
                    client="vscode",
                    servers=[MCPServerConfig(name="s2", type="stdio")],
                    config_scope="project",
                    project_path="/path/to/project",
                ),
            ],
        )

        assert len(result.global_configs) == 1
        assert result.global_configs[0].client == "cursor"
        assert len(result.project_configs) == 1
        assert result.project_configs[0].client == "vscode"


class TestScanResultToApiPayload:
    def test_converts_to_dict(self):
        """ScanResult can be converted to API payload."""
        result = scan_all_clients(scan_projects=False)
        payload = result.to_api_payload()
        assert isinstance(payload, dict)
        assert "device_id" in payload
        assert "configurations" in payload

    def test_payload_includes_all_fields(self):
        """API payload includes all expected fields."""
        from runlayer_cli.scan.config_parser import MCPClientConfig, MCPServerConfig

        result = ScanResult(
            device_id="test-device",
            hostname="test-host",
            os="darwin",
            os_version="14.0",
            username="testuser",
            org_device_id="mdm-123",
            scan_duration_ms=500,
            collector_version="1.0.0",
            configurations=[
                MCPClientConfig(
                    client="cursor",
                    client_version="0.1.0",
                    config_path="/path/to/config.json",
                    config_modified_at="2024-01-01T00:00:00Z",
                    config_scope="global",
                    servers=[
                        MCPServerConfig(
                            name="test-server",
                            type="stdio",
                            command="npx",
                            args=["-y", "test"],
                            env={"KEY": "value"},
                            config_hash="abc123",
                        )
                    ],
                )
            ],
        )

        payload = result.to_api_payload()

        assert payload["device_id"] == "test-device"
        assert payload["hostname"] == "test-host"
        assert payload["os"] == "darwin"
        assert payload["os_version"] == "14.0"
        assert payload["username"] == "testuser"
        assert payload["org_device_id"] == "mdm-123"
        assert payload["scan_duration_ms"] == 500
        assert payload["collector_version"] == "1.0.0"
        assert len(payload["configurations"]) == 1

        config = payload["configurations"][0]
        assert config["client"] == "cursor"
        assert config["config_scope"] == "global"
        assert len(config["servers"]) == 1

        server = config["servers"][0]
        assert server["name"] == "test-server"
        assert server["type"] == "stdio"
        assert server["command"] == "npx"
        assert server["args"] == ["-y", "test"]
        assert server["env"] == {"KEY": "value"}
        assert server["config_hash"] == "abc123"
