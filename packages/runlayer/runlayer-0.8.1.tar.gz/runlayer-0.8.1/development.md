# Development

## Testing

See `./AGENTS.md` for testing instructions.

### Testing from Cursor

Use this configuration:

```json
"my-server": {
    "command": "uv",
    "args": [
        "run",
        "--directory",
        "/Users/vitorbal/Code/Runlayer/cli",
        "runlayer",
        "<server_uuid>",
        "--secret",
        "<api_key>",
        "--host",
        "<runlayer_url>"
    ]
}
```
