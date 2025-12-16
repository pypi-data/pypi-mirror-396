# Runlayer CLI

The Runlayer CLI enables secure execution of trusted MCP servers with enterprise-grade security, auditing, and permission management. Run Model Context Protocol servers through an authenticated proxy that enforces access controls, maintains audit logs, and manages permissions - allowing AI agents to safely connect to internal systems without exposing credentials or running unvetted code locally.

The CLI also provides deployment capabilities to build and deploy Docker-based services to your Runlayer infrastructure, and scanning capabilities to discover MCP server configurations across devices.

## Quick Start

The easiest way to get started is to **copy the complete command from the server overview page in your Runlayer app** - it includes all the required parameters pre-filled for your server.

Alternatively, you can construct the command manually:

```bash
uvx runlayer run <server_uuid> --secret <your_api_key> --host <runlayer_url>
```

## Commands

### `run` - Run an MCP Server

Run an MCP server through the Runlayer proxy.

#### Command Arguments

- `server_uuid`: UUID of your MCP server (found in your Runlayer deployment)

#### Command Options

- `--secret`, `-s`: Your Runlayer API key (found under your user settings)
- `--host`: Your Runlayer instance URL (e.g., https://runlayer.example.com)

#### Example

```bash
uvx runlayer run abc123-def456 --secret my_api_key --host https://runlayer.example.com
```

### `deploy` - Deploy a Service

Deploy a Docker-based service to your Runlayer infrastructure based on a `runlayer.yaml` configuration file.

#### Command Options

- `--config`, `-c`: Path to runlayer.yaml config file (default: `runlayer.yaml`)
- `--secret`, `-s`: Your Runlayer API key (required, must have admin permissions)
- `--host`, `-H`: Your Runlayer instance URL (default: `http://localhost:3000`)
- `--env-file`, `-e`: Path to .env file for environment variable substitution (optional, defaults to `.env` in config file directory or current directory)

#### Example

```bash
uvx runlayer deploy --config runlayer.yaml --secret my_admin_key --host https://runlayer.example.com
```

#### Configuration File (`runlayer.yaml`)

The deploy command reads from a `runlayer.yaml` file that defines your service configuration:

```yaml
name: my-awesome-service
runtime: docker

build:
  dockerfile: Dockerfile
  context: .
  platform: x86  # or "arm"

service:
  port: 8000
  path: /api

infrastructure:
  cpu: 512
  memory: 1024

env:
  DATABASE_URL: postgres://...
  API_KEY: secret123
```

#### Environment Variable Substitution

The CLI supports standard Docker Compose / shell-style environment variable substitution in your `runlayer.yaml` file. This allows you to reference local environment variables or values from a `.env` file without hardcoding sensitive values.

**Variable Syntax:**

- `${VAR}` - Required variable (error if not set)
- `${VAR:-default}` - Use default value if variable is unset or empty
- `${VAR-default}` - Use default value only if variable is unset (not if empty)
- `$$DEPLOYMENT_URL`, `$$RUNLAYER_URL`, `$$RUNLAYER_OAUTH_CALLBACK_URL` - Reserved system variables (backend replaces at deploy time)

**Example Configuration:**

```yaml
name: my-service
env:
  API_KEY: ${MY_API_KEY}                      # Required - error if not set
  DATABASE_URL: ${DATABASE_URL}               # Required
  LOG_LEVEL: ${LOG_LEVEL:-info}               # Default to 'info' if not set
  DEBUG: ${DEBUG:-false}                      # Default to 'false'
  WEBHOOK_URL: $$DEPLOYMENT_URL/webhook    # Backend replaces (double $$)
```

**Usage:**

```bash
# Using environment variables
export MY_API_KEY=secret123
export DATABASE_URL=postgres://localhost/db
uvx runlayer deploy --secret my_admin_key --host https://runlayer.example.com

# Using a .env file (auto-discovered from config file directory or current directory)
# Place .env file next to runlayer.yaml or in current directory
uvx runlayer deploy --secret my_admin_key --host https://runlayer.example.com

# Using a specific .env file
uvx runlayer deploy --secret my_admin_key --host https://runlayer.example.com --env-file .env.prod
```

**Auto-discovery:** The CLI automatically looks for a `.env` file in:
1. The same directory as your `runlayer.yaml` config file
2. The current working directory (if config file is elsewhere)

If you specify `--env-file`, it will use that file instead of auto-discovery.

**Standard .env file format:**

```
MY_API_KEY=secret123
DATABASE_URL=postgres://localhost/db
LOG_LEVEL=debug
```

**Note:** Variables from `.env` files override values from `os.environ`. The `$$VAR` syntax (double dollar sign) is reserved for backend variable substitution and will not be replaced by the CLI.

### `deploy init` - Initialize a New Deployment

Create a new deployment and generate a `runlayer.yaml` configuration file.

#### Example

```bash
uvx runlayer deploy init --config runlayer.yaml --secret my_admin_key --host https://runlayer.example.com
```

### `scan` - Scan MCP Client Configurations

Scan for MCP server configurations across supported clients (Cursor, Claude Desktop, Claude Code, VS Code, Windsurf) and submit results to Runlayer for classification.

#### Command Options

- `--secret`, `-s`: Your Runlayer API key (required unless `--dry-run`)
- `--host`, `-H`: Your Runlayer instance URL (default: `http://localhost:3000`)
- `--dry-run`, `-n`: Print scan results as JSON without submitting to API
- `--verbose`, `-v`: Enable verbose output
- `--quiet`, `-q`: Suppress all output except errors
- `--org-device-id`: Organization-provided device ID (e.g., MDM asset tag)
- `--no-projects`: Skip scanning for project-level configurations

#### Example

```bash
uvx runlayer scan --secret $RUNLAYER_API_KEY --host https://runlayer.example.com
```

## Logs

Logs are written to `~/.runlayer/logs/`. Set `LOG_LEVEL` environment variable to control verbosity (DEBUG, INFO, WARNING, ERROR).
