# gbizinfo-mcp

MCP server for gBizINFO REST API v2.

## Features

- 19 gBizINFO endpoints exposed as 19 MCP tools (1:1 mapping)
- stdio transport
- Raw JSON response passthrough
- Environment-based API token configuration

## Requirements

- Python 3.11+
- `uv`
- gBizINFO API token

## Environment Variables

- `GBIZINFO_API_TOKEN` (required)
- `GBIZINFO_BASE_URL` (optional, default: `https://api.info.gbiz.go.jp/hojin`)
- `GBIZINFO_TIMEOUT_SECONDS` (optional, default: `20`)

## Local Setup

```bash
uv sync --group dev
```

## Run Locally

```bash
GBIZINFO_API_TOKEN=your_token uv run gbizinfo-mcp
```

## Run via uvx from GitHub

```bash
GBIZINFO_API_TOKEN=your_token \
uvx --from "gbizinfo-mcp @ git+https://github.com/<OWNER>/gbizinfo-mcp.git@<TAG_OR_SHA>" \
  gbizinfo-mcp
```

## MCP Client Configuration Example (stdio)

Claude Desktop / Codex style:

```json
{
  "mcpServers": {
    "gbizinfo": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/koizumikento/jma-data-mcp.git",
        "gbizinfo-mcp"
      ],
      "env": {
        "GBIZINFO_API_TOKEN": "your_token"
      }
    }
  }
}
```

## Tool List

- `hojin_search`
- `hojin_update_info_basic`
- `hojin_update_info_certification`
- `hojin_update_info_commendation`
- `hojin_update_info_corporation`
- `hojin_update_info_finance`
- `hojin_update_info_patent`
- `hojin_update_info_procurement`
- `hojin_update_info_subsidy`
- `hojin_update_info_workplace`
- `hojin_get_basic`
- `hojin_get_certification`
- `hojin_get_commendation`
- `hojin_get_corporation`
- `hojin_get_finance`
- `hojin_get_patent`
- `hojin_get_procurement`
- `hojin_get_subsidy`
- `hojin_get_workplace`

## Quality Checks

```bash
uv run ruff check .
uv run ty check
uv run pytest
```
