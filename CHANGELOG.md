# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-03-17

### Added

- **MCP Server** — AI 어시스턴트 (Claude Desktop, Cursor 등)에서 DB증권 API 직접 호출
  - `pip install pydbsec[mcp]` → `pydbsec-mcp` 실행
  - Tools: get_stock_price, get_balance, get_portfolio_summary, place_order, get_order_book, get_chart
  - stdio transport (Claude Desktop config에 추가하여 사용)

[0.4.0]: https://github.com/STOA-company/pydbsec/compare/v0.3.0...v0.4.0

## [0.3.0] - 2026-03-17

### Added

- **CLI tool** — `pydbsec` command for terminal-based API access
  - `pydbsec price 005930` — stock price lookup
  - `pydbsec balance` / `pydbsec balance --overseas` — balance inquiry
  - `pydbsec portfolio` — unified KR+US portfolio summary
  - `pydbsec buy/sell` — order placement
  - `--json` flag for raw JSON output
  - Credentials via `DBSEC_APP_KEY`/`DBSEC_APP_SECRET` env vars or `--key`/`--secret` flags
- **Rate limiting** (enabled by default) — token bucket per endpoint, respects DB Securities rate limits
- **`portfolio_summary()`** — unified domestic+overseas balance in a single call
- **Configurable logging** — `PyDBSec(log_level=logging.DEBUG)`

### Fixed

- All 60 mypy strict type errors resolved (0 errors on 19 source files)
- `base_url` propagation to `TokenManager`
- Async token refresh event loop blocking

[0.3.0]: https://github.com/STOA-company/pydbsec/compare/v0.2.0...v0.3.0

## [0.2.0] - 2026-03-17

### Added

- **WebSocket real-time data**: `DBSecWebSocket` async client for live market data
  - Production `wss://openapi.dbsec.co.kr:7070`, sandbox `:17070`
  - TR codes: S00 (체결가), S01 (호가), IS0/IS1 (주문접수/체결), W00/W01 (ELW), U00 (업종지수)
  - Async iterator protocol (`async for msg in ws`)
  - Auto-reconnect with configurable retry
  - Optional dependency: `pip install pydbsec[ws]`
- `PyDBSec.ws` / `AsyncPyDBSec.ws` lazy property for WebSocket access

### Fixed

- `base_url` not propagated to `TokenManager` — token requests now use custom base_url
- Async token refresh blocked event loop — now uses `asyncio.to_thread()`

### Changed

- HTTP clients use persistent connection pools (`httpx.Client` / `AsyncClient`)
- Pagination results merged into single `dict` (Out1/Out2 lists concatenated)
- Return type simplified to `dict[str, Any]` (no more `dict | list[dict]` union)
- Error codes extracted to constants (`ERROR_TOKEN_EXPIRED`, etc.)

[0.2.0]: https://github.com/STOA-company/pydbsec/compare/v0.1.0...v0.2.0

## [0.1.0] - 2026-03-17

### Added

- `PyDBSec` synchronous client
- `AsyncPyDBSec` asynchronous client
- OAuth2 token management with auto-refresh and thread-safe locking
- httpx-based HTTP client with automatic pagination (`cont_yn`/`cont_key`)
- **Domestic (국내) API**: balance, price, order_book, buy/sell/cancel, chart, deposit, orderable_quantity, transaction_history, trading_history, daily_trade_report, tickers
- **Overseas (해외) API**: balance, price, order_book, buy/sell/cancel, chart, deposit, orderable_quantity, transaction_history, tickers
- **Futures (선물) API**: balance
- Pydantic v2 typed response models: `DomesticBalance`, `OverseasBalance`, `FuturesBalance`, `StockPrice`, `OrderBook`, `OrderResult`
- Custom exceptions: `PyDBSecError`, `TokenError`, `TokenExpiredError`, `APIError`
- Context manager support (`with` / `async with`)
- `py.typed` marker (PEP 561)
- GitHub Actions CI (Python 3.10–3.13)
- PyPI trusted publishing workflow

[0.1.0]: https://github.com/STOA-company/pydbsec/releases/tag/v0.1.0
