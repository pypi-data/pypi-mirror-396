"""Basic tests for the CLI."""

import re
import tempfile
import typer
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner
import yaml

from runlayer_cli.main import app

runner = CliRunner()


def strip_ansi(text: str) -> str:
    """Strip ANSI escape codes from text."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


def test_help_command():
    """Test that the help command shows usage information."""
    # Test top-level help
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    plain_output = strip_ansi(result.stdout)
    assert "Run MCP servers via HTTP transport" in plain_output
    assert "--version" in plain_output

    # Test run command help
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    plain_output = strip_ansi(result.stdout)
    assert "Run an MCP server via HTTP transport" in plain_output
    assert "SERVER_UUID" in plain_output
    assert "--secret" in plain_output
    assert "--host" in plain_output


def test_version_command():
    """Test that the version command shows version information."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    plain_output = strip_ansi(result.stdout)
    assert "runlayer version" in plain_output

    # Test short version flag
    result = runner.invoke(app, ["-v"])
    assert result.exit_code == 0
    plain_output = strip_ansi(result.stdout)
    assert "runlayer version" in plain_output


def test_run_command_requires_arguments():
    """Test that run command requires server UUID and secret."""
    result = runner.invoke(app, ["run"])
    assert result.exit_code != 0
    # Should fail because required arguments are missing


def test_default_command_behavior():
    """Test that run command requires secret argument."""
    result = runner.invoke(app, ["run", "test-uuid"])
    assert result.exit_code != 0


def test_run_command_with_secret_requires_host():
    """Test that run command with server UUID and secret still requires host."""
    result = runner.invoke(app, ["run", "test-uuid", "--secret", "test-secret"])
    assert result.exit_code != 0
    # Should fail because --host is missing (or connection fails)


def test_validate_command_requires_args():
    """Test that validate command requires secret and config."""
    # Missing secret
    result = runner.invoke(app, ["deploy", "validate", "--config", "test.yaml"])
    assert result.exit_code != 0

    # Missing config (should work with default)
    result = runner.invoke(app, ["deploy", "validate", "--secret", "test-secret"])
    # May fail due to missing file or connection, but should not fail due to missing args
    assert result.exit_code != 0  # Will fail on file not found or connection


def test_validate_command_success():
    """Test validate command with valid YAML."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        config = {
            "name": "test-service",
            "runtime": "docker",
            "service": {"port": 8000},
        }
        yaml.dump(config, f)
        config_path = f.name

    try:
        with patch("runlayer_cli.commands.deploy.validate_service") as mock_validate:
            runner.invoke(
                app,
                [
                    "deploy",
                    "validate",
                    "--config",
                    config_path,
                    "--secret",
                    "test-secret",
                    "--host",
                    "http://localhost:3000",
                ],
            )
            # Should call validate_service
            mock_validate.assert_called_once_with(
                config_path=config_path,
                secret="test-secret",
                host="http://localhost:3000",
                env_file=None,
            )
    finally:
        Path(config_path).unlink()


def test_validate_command_error():
    """Test validate command with invalid YAML."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("invalid: yaml: content")
        config_path = f.name

    try:
        with patch("runlayer_cli.commands.deploy.validate_service") as mock_validate:
            # Make validate_service raise an error
            mock_validate.side_effect = typer.Exit(1)

            result = runner.invoke(
                app,
                [
                    "deploy",
                    "validate",
                    "--config",
                    config_path,
                    "--secret",
                    "test-secret",
                    "--host",
                    "http://localhost:3000",
                ],
            )
            # Should have called validate_service and exited with error
            assert result.exit_code != 0
            mock_validate.assert_called_once()
    finally:
        Path(config_path).unlink()
