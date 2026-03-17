# pydbsec-mcp

[![npm](https://img.shields.io/npm/v/pydbsec-mcp.svg)](https://www.npmjs.com/package/pydbsec-mcp)

MCP server for **DB Securities (DB증권) OpenAPI** — use Korean/US stock trading with Claude, Cursor, and other AI tools.

## Quick Start

```bash
npx pydbsec-mcp
```

That's it. No manual Python setup required — the wrapper automatically handles installation.

## Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dbsec": {
      "command": "npx",
      "args": ["pydbsec-mcp"],
      "env": {
        "DBSEC_APP_KEY": "your_app_key",
        "DBSEC_APP_SECRET": "your_app_secret"
      }
    }
  }
}
```

## Claude Code

```bash
claude mcp add dbsec -- npx pydbsec-mcp
```

## Available Tools

| Tool | Description |
|------|-------------|
| `get_stock_price` | Stock price lookup (KR/US) |
| `get_balance` | Account balance |
| `get_portfolio_summary` | Unified KR+US portfolio |
| `place_order` | Buy/sell orders |
| `get_order_book` | Order book |
| `get_chart` | Chart data |

## How It Works

The npm wrapper finds the best available Python runtime:

1. **uvx** — fastest, runs directly from PyPI (no install)
2. **pipx** — if available
3. **pip + auto venv** — creates `~/.pydbsec-mcp/venv`, always works if Python 3.10+ exists

## Requirements

- Python 3.10+ (auto-detected)
- DB Securities API credentials ([sign up](https://openapi.dbsec.co.kr))

## Links

- [GitHub](https://github.com/STOA-company/pydbsec)
- [PyPI](https://pypi.org/project/pydbsec/)
- [Documentation](https://stoa-company.github.io/pydbsec)

## License

MIT
