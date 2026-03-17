# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
