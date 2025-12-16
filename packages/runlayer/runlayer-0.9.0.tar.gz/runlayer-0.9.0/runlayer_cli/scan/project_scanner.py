"""Scan for project-level MCP configuration files using find command.

Note: macOS Spotlight (mdfind) does NOT index hidden files or files in hidden
directories, so we must use the find command instead.
"""

from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from runlayer_cli.scan.clients import MCPClientDefinition

logger = structlog.get_logger(__name__)


@dataclass
class ProjectConfig:
    """A discovered project-level MCP configuration."""

    config_path: Path
    project_path: Path  # Root of the project (parent of config)
    client_name: str
    servers_key: str


# Directories to exclude from search (improves performance)
EXCLUDED_DIRECTORIES: list[str] = [
    "node_modules",
    ".git",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    "target",
    "vendor",
    "Library/Caches",
    "Library/Application Support",  # macOS global configs
    "AppData",  # Windows global configs
    ".Trash",
    "tmp",
    "temp",
    ".cache",
    ".npm",
    ".yarn",
]


def scan_for_project_configs(
    clients: list[MCPClientDefinition],
    timeout: int = 60,
    max_depth: int = 5,
) -> list[ProjectConfig]:
    """
    Scan for project-level MCP configuration files using find command.

    Uses find on macOS/Linux and PowerShell on Windows.

    Args:
        clients: List of client definitions with project_config patterns
        timeout: Maximum seconds to wait for search (default 60)
        max_depth: Maximum directory depth to search (default 5)

    Returns:
        List of discovered ProjectConfig instances
    """
    # Build lookup of what to search for
    # { "filename": [("client_name", "servers_key", "path_contains"), ...] }
    search_patterns: dict[str, list[tuple[str, str, str | None]]] = {}

    for client in clients:
        if client.project_config:
            rel_path = client.project_config.relative_path
            # Extract just the filename for search
            filename = Path(rel_path).name
            # Extract parent dir pattern if any (e.g., ".vscode" from ".vscode/mcp.json")
            path_contains = None
            if "/" in rel_path:
                path_contains = rel_path.rsplit("/", 1)[0]  # ".vscode"

            if filename not in search_patterns:
                search_patterns[filename] = []
            search_patterns[filename].append(
                (
                    client.name,
                    client.project_config.servers_key,
                    path_contains,
                )
            )

    if not search_patterns:
        logger.debug("No clients with project configs to scan")
        return []

    logger.info(
        "Scanning for project configs using find",
        filenames=list(search_patterns.keys()),
        max_depth=max_depth,
    )

    # Use platform-specific search
    system = platform.system()
    if system == "Darwin" or system == "Linux":
        found_paths = _search_unix(list(search_patterns.keys()), timeout, max_depth)
    elif system == "Windows":
        found_paths = _search_windows(list(search_patterns.keys()), timeout, max_depth)
    else:
        logger.warning(f"Unsupported platform for project scanning: {system}")
        return []

    # Match found paths to clients
    found_configs: list[ProjectConfig] = []
    for path in found_paths:
        filename = path.name
        if filename not in search_patterns:
            continue

        for client_name, servers_key, path_contains in search_patterns[filename]:
            # If we expect a parent dir (e.g., ".vscode"), verify it's there as a
            # path component (not just a substring). For ".vscode/mcp.json", the
            # parent directory must be exactly ".vscode", not ".vscode_backup".
            if path_contains and path.parent.name != path_contains:
                continue

            # Determine project root
            project_path = _get_project_root(path, path_contains)

            found_configs.append(
                ProjectConfig(
                    config_path=path,
                    project_path=project_path,
                    client_name=client_name,
                    servers_key=servers_key,
                )
            )
            logger.debug(
                "Found project config",
                client=client_name,
                config_path=str(path),
                project_path=str(project_path),
            )

    logger.info("Project config scan complete", found=len(found_configs))
    return found_configs


def _search_unix(filenames: list[str], timeout: int, max_depth: int) -> list[Path]:
    """
    Use find command to locate MCP config files on macOS/Linux.

    Note: We use find instead of mdfind because Spotlight does NOT index
    hidden files (starting with .) or files in hidden directories.
    """
    found_paths: list[Path] = []
    home = str(Path.home())

    # Build the -name conditions: ( -name ".mcp.json" -o -name "mcp.json" -o ... )
    name_conditions: list[str] = []
    for filename in filenames:
        if name_conditions:
            name_conditions.extend(["-o", "-name", filename])
        else:
            name_conditions.extend(["-name", filename])

    # Build exclusion conditions
    exclude_conditions: list[str] = []
    for excluded in EXCLUDED_DIRECTORIES:
        exclude_conditions.extend(["!", "-path", f"*/{excluded}/*"])

    cmd = [
        "find",
        home,
        "-maxdepth",
        str(max_depth),
        "-type",
        "f",
        "(",
        *name_conditions,
        ")",
        *exclude_conditions,
    ]

    try:
        logger.debug(f"Running find command with {len(filenames)} filename patterns")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        # find returns exit code 1 if some dirs are unreadable, but still outputs results
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            path = Path(line)
            if path.is_file():
                found_paths.append(path)

    except subprocess.TimeoutExpired:
        logger.warning(f"find command timed out after {timeout}s")
    except FileNotFoundError:
        logger.warning("find command not found")
    except Exception as e:
        logger.warning(f"find command failed: {e}")

    return found_paths


def _escape_powershell_string(value: str) -> str:
    """
    Escape a string for safe use in PowerShell single-quoted strings.

    In PowerShell single-quoted strings, only single quotes need escaping
    (doubled to ''). Other special characters like $, `, and " are treated
    literally within single quotes.
    """
    return value.replace("'", "''")


def _search_windows(filenames: list[str], timeout: int, max_depth: int) -> list[Path]:
    """
    Use PowerShell to find MCP config files on Windows.
    """
    found_paths: list[Path] = []
    home = str(Path.home())

    # Escape all user-controlled strings for PowerShell single-quoted context
    safe_home = _escape_powershell_string(home)
    safe_filenames = [_escape_powershell_string(f) for f in filenames]
    safe_excludes = [_escape_powershell_string(d) for d in EXCLUDED_DIRECTORIES]

    # Build PowerShell filename filter using single quotes (prevents injection)
    filename_list = ", ".join([f"'{f}'" for f in safe_filenames])
    exclude_list = ", ".join([f"'{d}'" for d in safe_excludes])

    if not isinstance(max_depth, int) or max_depth < 0 or max_depth > 10:
        logger.warning(
            f"Invalid max_depth '{max_depth}' provided. Using default max_depth=5."
        )
        max_depth = 5

    cmd = f"""
    $excludeDirs = @({exclude_list})
    Get-ChildItem -Path '{safe_home}' -Recurse -Depth {max_depth} -File -Force -ErrorAction SilentlyContinue |
    Where-Object {{
        $path = $_.FullName
        $_.Name -in @({filename_list}) -and
        -not ($excludeDirs | ForEach-Object {{ $path -like "*\\$_\\*" }} | Where-Object {{ $_ }})
    }} |
    Select-Object -ExpandProperty FullName
    """

    try:
        logger.debug(
            f"Running PowerShell search with {len(filenames)} filename patterns"
        )

        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            path = Path(line)
            if path.is_file():
                found_paths.append(path)

    except subprocess.TimeoutExpired:
        logger.warning(f"PowerShell search timed out after {timeout}s")
    except Exception as e:
        logger.warning(f"PowerShell search failed: {e}")

    return found_paths


def _get_project_root(config_path: Path, path_contains: str | None) -> Path:
    """
    Determine the project root directory from a config file path.

    For ".mcp.json" -> parent directory is project root
    For ".vscode/mcp.json" -> grandparent directory is project root
    """
    if path_contains:
        # Config is in a subdirectory like .vscode/
        # Go up one more level
        return config_path.parent.parent
    else:
        # Config is at project root
        return config_path.parent
