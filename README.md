# pydbsec

[![PyPI version](https://img.shields.io/pypi/v/pydbsec.svg)](https://pypi.org/project/pydbsec/)
[![Python](https://img.shields.io/pypi/pyversions/pydbsec.svg)](https://pypi.org/project/pydbsec/)
[![CI](https://github.com/Jaeminyx-Stoa/pydbsec/actions/workflows/ci.yml/badge.svg)](https://github.com/Jaeminyx-Stoa/pydbsec/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**DB증권 OpenAPI Python 래퍼** — 3줄이면 잔고 조회, 5줄이면 자동매매

> DB증권 OpenAPI를 쉽게 사용할 수 있는 Python 라이브러리입니다.
> [한국투자증권의 PyKIS](https://github.com/Soju06/python-kis)처럼, DB증권도 Python 한 줄이면 됩니다.

```python
from pydbsec import PyDBSec

client = PyDBSec(app_key="...", app_secret="...")
print(client.domestic.price("005930").current_price)  # 삼성전자 현재가
```

## Features

- **국내 주식**: 잔고 조회, 시세, 매수/매도, 차트, 거래내역
- **해외 주식**: 잔고 조회, 시세, 매수/매도, 차트, 거래내역
- **선물/옵션**: 잔고 조회
- **CLI 도구**: `pydbsec price 005930` — 터미널에서 바로 조회
- **WebSocket**: 실시간 체결가/호가 스트리밍
- **Rate Limiting**: API 초당 요청 제한 자동 준수
- **Portfolio Summary**: 국내+해외 통합 잔고
- **Sync + Async**: `PyDBSec` / `AsyncPyDBSec`
- **Type-safe**: Pydantic v2 모델, mypy strict 통과
- **Auto token**: OAuth2 토큰 자동 발급/갱신
- **Auto pagination**: 연속 조회 자동 병합

## Installation

```bash
pip install pydbsec            # REST + CLI
pip install pydbsec[ws]        # + WebSocket 실시간
```

## CLI

코드 없이 터미널에서 바로 사용:

```bash
# 환경변수 설정
export DBSEC_APP_KEY="your_app_key"
export DBSEC_APP_SECRET="your_app_secret"

# 주가 조회
pydbsec price 005930                       # 삼성전자
pydbsec price AAPL --overseas --market FN  # NASDAQ AAPL

# 잔고 조회
pydbsec balance                            # 국내
pydbsec balance --overseas                 # 해외

# 통합 포트폴리오
pydbsec portfolio

# 주문
pydbsec buy 005930 10 70000                # 삼성전자 10주 70000원 매수
pydbsec sell 005930 5 72000                # 매도

# JSON 출력
pydbsec --json price 005930
```

## Quick Start (Python)

```python
from pydbsec import PyDBSec

client = PyDBSec(app_key="YOUR_APP_KEY", app_secret="YOUR_APP_SECRET")

# 국내 주식 잔고 조회
balance = client.domestic.balance()
print(f"예탁총액: {balance.deposit_total:,.0f}원")
print(f"주문가능: {balance.available_cash:,.0f}원")
for pos in balance.positions:
    print(f"  {pos.stock_name}: {pos.quantity}주 (평가손익: {pos.pnl_amount:,.0f}원)")

# 주가 조회
price = client.domestic.price("005930")  # 삼성전자
print(f"현재가: {price.current_price:,.0f}원 ({price.change_rate:+.2f}%)")

# 매수 주문
result = client.domestic.buy("005930", quantity=10, price=70000)
print(f"주문번호: {result.order_no}")

# 해외 주식
us_price = client.overseas.price("AAPL", market="FN")  # NASDAQ
print(f"AAPL: ${us_price.current_price:.2f}")

# 통합 포트폴리오 (국내+해외)
summary = client.portfolio_summary()
print(f"총 자산: {summary['total_nav']:,.0f}원")

# 세션 종료
client.close()
```

### Context Manager

```python
with PyDBSec(app_key="...", app_secret="...") as client:
    balance = client.domestic.balance()
```

### Async

```python
import asyncio
from pydbsec import AsyncPyDBSec

async def main():
    async with AsyncPyDBSec(app_key="...", app_secret="...") as client:
        balance = await client.domestic.balance()
        price = await client.domestic.price("005930")

asyncio.run(main())
```

### WebSocket (실시간)

```python
from pydbsec import PyDBSec

client = PyDBSec(app_key="...", app_secret="...")

async with client.ws as ws:
    await ws.subscribe("005930", tr_code="S00")  # 삼성전자 체결가
    async for msg in ws:
        print(msg.tr_code, msg.data)
```

Requires: `pip install pydbsec[ws]`

### Rate Limiting

기본적으로 활성화되어 있으며, API 초당 요청 제한을 자동으로 준수합니다.

```python
client = PyDBSec(app_key="...", app_secret="...", rate_limit=True)   # 기본값
client = PyDBSec(app_key="...", app_secret="...", rate_limit=False)  # 비활성화
```

### Logging

```python
import logging
client = PyDBSec(app_key="...", app_secret="...", log_level=logging.DEBUG)
```

### MCP Server (AI 어시스턴트 연동)

Claude Desktop, Cursor 등 AI 도구에서 DB증권 API를 직접 호출할 수 있습니다.

```bash
pip install pydbsec[mcp]
```

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "dbsec": {
      "command": "pydbsec-mcp",
      "env": {
        "DBSEC_APP_KEY": "your_app_key",
        "DBSEC_APP_SECRET": "your_app_secret"
      }
    }
  }
}
```

**Claude Code**:

```bash
claude mcp add \
  --env DBSEC_APP_KEY=your_key \
  --env DBSEC_APP_SECRET=your_secret \
  dbsec \
  -- pydbsec-mcp
```

AI에게 "삼성전자 현재가 알려줘" → `get_stock_price("005930")` 자동 호출.

**Anthropic API에서 직접 사용**:

```python
from pydbsec.mcp.helpers import get_anthropic_tools, execute_tool
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    tools=get_anthropic_tools(),
    messages=[{"role": "user", "content": "삼성전자 현재가 알려줘"}],
)

# Agentic loop에서 tool 실행
for block in response.content:
    if block.type == "tool_use":
        result = execute_tool(block.name, block.input)
```

## API Reference

### `client.domestic` — 국내 주식

| Method | Description |
|--------|-------------|
| `balance()` | 잔고 조회 |
| `price(stock_code)` | 현재가 조회 |
| `order_book(stock_code)` | 호가 조회 |
| `tickers()` | 종목 목록 |
| `buy(stock_code, quantity, price)` | 매수 주문 |
| `sell(stock_code, quantity, price)` | 매도 주문 |
| `cancel(order_no, stock_code, quantity)` | 주문 취소 |
| `deposit()` | 예수금 조회 |
| `orderable_quantity(stock_code, price)` | 주문가능수량 |
| `transaction_history()` | 체결/미체결 내역 |
| `trading_history(start_date, end_date)` | 거래 내역 |
| `daily_trade_report(date)` | 일별 거래 보고서 |
| `chart(stock_code, period=...)` | 차트 데이터 |

### `client.overseas` — 해외 주식

| Method | Description |
|--------|-------------|
| `balance()` | 잔고 조회 |
| `price(stock_code, market=...)` | 현재가 조회 |
| `order_book(stock_code, market=...)` | 호가 조회 |
| `tickers(market=...)` | 종목 목록 |
| `buy(stock_code, quantity, price)` | 매수 주문 |
| `sell(stock_code, quantity, price)` | 매도 주문 |
| `cancel(order_no, stock_code, quantity)` | 주문 취소 |
| `deposit()` | 예수금 조회 |
| `transaction_history(start_date, end_date)` | 거래 내역 |
| `chart(stock_code, period=...)` | 차트 데이터 |

### `client.futures` — 선물/옵션

| Method | Description |
|--------|-------------|
| `balance()` | 선물옵션 잔고 조회 |

### `client.portfolio_summary()` — 통합 포트폴리오

```python
summary = client.portfolio_summary()
# {"total_nav": 15000000, "cash": 5000000, "profit": 500000, "ror": 3.45, "positions": [...]}
```

### `client.ws` — WebSocket 실시간

| TR Code | Description |
|---------|-------------|
| `S00` | 주식 체결가 |
| `S01` | 주식 호가 |
| `IS1` | 주문 체결 |
| `IS0` | 주문 접수 |
| `W00` / `W01` | ELW 체결 / 호가 |
| `U00` | 업종지수 체결가 |

### Market Codes

**국내 시세**: `"UJ"` (주식), `"E"` (ETF), `"EN"` (ETN)

**해외 시세**: `"FY"` (NYSE), `"FN"` (NASDAQ), `"FA"` (AMEX)

**해외 종목조회**: `"NY"` (NYSE), `"NA"` (NASDAQ), `"AM"` (AMEX)

## Prerequisites

DB증권 OpenAPI 사용을 위해:

1. [DB증권 계좌 개설](https://www.dbsec.co.kr)
2. [OpenAPI 사용 신청](https://openapi.dbsec.co.kr)
3. App Key / App Secret 발급

## 사용 전 유의사항

### License

pydbsec는 [MIT License](LICENSE)를 따릅니다. MIT License에서 규정하는 조건 안에서 자유롭게 수정/재배포/사용이 가능합니다.

### 면책 조항

- pydbsec의 동작에는 불완전한 부분이나 버그가 있을 수 있습니다. 또한 pydbsec의 API는 언제든 변경될 수 있습니다.
- pydbsec의 제작자는 이 코드에 대해서 어떤 것도 보장하지 않습니다. 코드 사용 중 생긴 **어떠한 종류의 피해(버그, 사용자의 실수, 투자로 인한 손실 등)에 대해서도 책임지지 않습니다.**
- pydbsec는 개인 투자 용도로만 개발되었습니다.

### 기타

- pydbsec를 사용하기 위해서는 Python 3.10 버전 이상이 필요합니다.
- pydbsec는 아직 개발 단계입니다. 버그나 기능 요청 등의 피드백은 [Issues](https://github.com/Jaeminyx-Stoa/pydbsec/issues)나 [Pull Request](https://github.com/Jaeminyx-Stoa/pydbsec/pulls)를 통해 부탁드립니다.

## Documentation

[https://jaeminyx-stoa.github.io/pydbsec](https://jaeminyx-stoa.github.io/pydbsec)

## License

MIT
