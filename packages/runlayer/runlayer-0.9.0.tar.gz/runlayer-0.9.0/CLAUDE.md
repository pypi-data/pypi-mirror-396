# CLI Service - AI Assistant Guide

> **Context**: You are working in the **cli** service of the Runlayer monorepo. This is the Runlayer CLI tool.

## Service Overview

- **Technology**: Python CLI application
- **Purpose**: Execute MCP servers through authenticated proxy
- **Package Manager**: uv (NEVER use `python` or `pip` directly)
- **Distribution**: Published to PyPI, installed via `uvx runlayer`

## Key Responsibilities

- Provide CLI interface for connecting to MCP servers
- Handle authentication with Runlayer backend
- Proxy MCP protocol traffic securely
- Manage API keys and server UUIDs

## Development Workflow

### Running Commands

**ALWAYS use `uv` for Python operations:**

```bash
# Run the CLI locally
uv run runlayer_cli <server_uuid> --secret <api_key> --host <url>

# Run tests
make test

# Type checking
make type-check

# Linting
make lint

# Build package
make build
```

### File Structure

```
cli/
├── runlayer_cli/        # Main package
│   ├── __init__.py
│   ├── main.py          # CLI entry point
│   ├── auth.py          # Authentication logic
│   ├── proxy.py         # MCP protocol proxy
│   └── ...
├── tests/               # Test suite
├── pyproject.toml       # Package configuration
├── uv.lock             # Dependency lock file
└── README.md
```

## Usage Pattern

The CLI is used by end-users to connect to MCP servers:

```bash
# Typical usage (from any directory)
uvx runlayer <server_uuid> --secret <your_api_key> --host <runlayer_url>

# Or installed globally
uv pip install runlayer
runlayer <server_uuid> --secret <api_key> --host <url>
```

## Critical Rules

1. **Use uv exclusively**: Never use `python`, `python3`, or `pip` directly
2. **Follow CLI conventions**: Use argparse or typer for argument parsing
3. **Handle errors gracefully**: Provide clear error messages for users
4. **Secure credential handling**: Never log API keys or secrets
5. **Cross-platform compatibility**: Ensure works on macOS, Linux, Windows

## Common Tasks

### Adding a New CLI Option

1. Update argument parser in `main.py`
2. Add logic to handle new option
3. Update README.md with new option documentation
4. Add tests for new functionality
5. Run: `make test`

### Testing Locally

```bash
# Run CLI in development mode
uv run runlayer_cli <test_server_uuid> --secret <test_key> --host http://localhost:8000

# Run with debug output
uv run runlayer_cli <uuid> --secret <key> --host <url> --verbose
```

### Building and Publishing

```bash
# Build package
uv build

# Test package locally
uv pip install dist/runlayer-*.whl

# Publish to PyPI (when ready)
uv publish
```

## Cross-Service Interactions

- **Backend**: CLI authenticates with backend API
- **MCP Servers**: CLI proxies traffic to/from MCP servers via backend
- **Users**: End-users install and run this CLI tool

## Environment Considerations

- **No .env file**: Configuration via command-line arguments only
- **Credentials**: Passed via `--secret` flag (stored by user)
- **Host URL**: Configurable via `--host` flag

## Testing

```bash
# Run full test suite
make test

# Run specific test
uv run pytest tests/test_auth.py

# Run with coverage
uv run pytest --cov=runlayer_cli
```

## Security Considerations

1. **Never log secrets**: Ensure API keys and tokens are never logged
2. **Validate inputs**: Sanitize all user inputs
3. **HTTPS only**: Default to HTTPS for host URLs
4. **Credential storage**: Don't store credentials in files (user responsibility)

## Common Pitfalls

1. **Don't use `python` directly** - Always use `uv run`
2. **Cross-platform paths** - Use `pathlib.Path` for file paths
3. **Error handling** - Provide helpful error messages, not stack traces
4. **Exit codes** - Use proper exit codes (0 for success, non-zero for errors)

## Documentation

- See `README.md` for user-facing documentation
- See root `CLAUDE.md` for monorepo conventions
- See backend documentation for API integration details

## Distribution

This package is distributed via PyPI and used with `uvx`:

```bash
# Users run (no installation needed)
uvx runlayer <uuid> --secret <key> --host <url>
```

## Related Services

- **Backend**: Provides the API that CLI communicates with
- **MCP Servers**: Defined in backend, executed via this CLI
- **OAuth Broker**: May be called during OAuth flows
