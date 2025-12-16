# CLI Service - Agent Context

> **Service**: cli
> **Type**: Python command-line application
> **Role**: Runlayer CLI for MCP server execution

## Quick Context

This is a **Python CLI tool** that end-users install and run to connect to MCP servers through the Runlayer backend.

## When Working Here

You are in a **Python CLI** environment:

- **ALWAYS use `uv`** - Never use `python`, `python3`, or `pip` directly
- Package manager: `uv`
- Distribution: PyPI package installed via `uvx`
- Users run: `uvx runlayer <uuid> --secret <key> --host <url>`

## Critical Commands

```bash
# Run locally
uv run runlayer <uuid> --secret <key> --host <url>

# Tests
make test

# Build
make build
```

## Key Characteristics

- **User-facing**: End-users install and run this tool
- **Authentication**: Handles API key authentication with backend
- **Proxy**: Proxies MCP protocol traffic securely
- **Cross-platform**: Must work on macOS, Linux, Windows

## Common Tasks

### Testing CLI

```bash
uv run runlayer test_uuid --secret test_key --host http://localhost:8000
```

### Adding New Option

1. Update argument parser
2. Implement functionality
3. Update README
4. Add tests

## Common Pitfalls

1. **Never use `python` directly** - Always `uv run`
2. **Never log secrets** - API keys must not appear in logs
3. **Cross-platform paths** - Use `pathlib.Path`
4. **User-friendly errors** - No raw stack traces for users

## Cross-Service Interactions

- **Backend**: Authenticates with and proxies through backend API
- **MCP Servers**: Connects to servers defined in backend

## Security

- Never log API keys or tokens
- Validate all inputs
- Use HTTPS by default
- Provide clear security guidance in docs

## Documentation

- See `CLAUDE.md` in this directory for detailed guide
- See `README.md` for user documentation
- See root `CLAUDE.md` for monorepo patterns
