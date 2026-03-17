# awesome-quant PR Draft for pydbsec

## Target Section

**Python > Trading & Backtesting**

This section (line 84 of the README) contains broker API wrappers and trading
libraries. Comparable entries already in this section include:

- `tda-api` - "Gather data and trade equities, options, and ETFs via TDAmeritrade."
- `alpaca-trade-api` - "Python interface for retrieving real-time and historical prices from Alpaca API as well as trade execution."
- `pysentosa` - "Python API for sentosa trading system."
- `metatrader5` - "API Connector to MetaTrader 5 Terminal" (listed under Data Sources but also relevant)
- `PRISM-INSIGHT` - "AI-powered stock analysis system ... via KIS API, supporting Korean & US markets."
- `vnpy` - "VeighNa is a Python-based open source quantitative trading system development framework."

pydbsec fits here because it is a broker API wrapper that supports both trading
(buy/sell orders) and market data retrieval (prices, charts, balances), similar
to `tda-api` and `alpaca-trade-api`.

## Exact Line to Add

Add the following line at the end of the "Trading & Backtesting" section
(before the blank line preceding `### Risk Analysis`):

```markdown
- [pydbsec](https://github.com/STOA-company/pydbsec) - Python wrapper for DB Securities (DB증권) OpenAPI with sync/async support.
```

## Draft PR

### Title

```
Add pydbsec - Python wrapper for DB Securities OpenAPI
```

### Description

```
## Add pydbsec to Python > Trading & Backtesting

[pydbsec](https://github.com/STOA-company/pydbsec) is a Python wrapper for
the DB Securities (DB증권) OpenAPI, a Korean brokerage.

**Features:**
- Domestic (KRX) and overseas (US, etc.) stock trading and market data
- Balance inquiry, price quotes, order execution, chart data
- Sync (`PyDBSec`) and async (`AsyncPyDBSec`) clients
- Type-safe responses with Pydantic v2
- Automatic OAuth2 token refresh and pagination handling
- Published on PyPI: `pip install pydbsec`

This addition complements existing Korean market entries like PRISM-INSIGHT
(KIS API) and FinanceDataReader, and follows the same pattern as other broker
API wrappers in the section (tda-api, alpaca-trade-api, pysentosa).
```
