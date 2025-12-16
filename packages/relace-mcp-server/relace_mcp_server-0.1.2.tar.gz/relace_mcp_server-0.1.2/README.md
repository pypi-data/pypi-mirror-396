# relace-mcp-server

[![PyPI](https://img.shields.io/pypi/v/relace-mcp-server)](https://pypi.org/project/relace-mcp-server/)

Official Relace MCP server.

Currently supports [Fast Agentic Search](https://www.relace.ai/blog/fast-agentic-search) via the `relace_search` tool.

## Installation

A valid [Relace API key](https://app.relace.ai/settings/api-keys) is required.

### Cursor

```json
"relace": {
    "command": "uvx",
    "args": [
        "relace-mcp-server"
    ],
    "env": {
        "RELACE_API_KEY": "rlc-xxx"
    }
}
```

### Claude Code

```sh
claude mcp add relace --env RELACE_API_KEY=rlc-xxx -- uvx relace-mcp-server
```
