# Quick Start

## 설치

```bash
pip install pydbsec
```

## 기본 사용법

### 클라이언트 초기화

```python
from pydbsec import PyDBSec

client = PyDBSec(app_key="YOUR_APP_KEY", app_secret="YOUR_APP_SECRET")
```

### 국내 주식

=== "잔고 조회"

    ```python
    balance = client.domestic.balance()
    print(f"예탁총액: {balance.deposit_total:,.0f}원")
    print(f"주문가능: {balance.available_cash:,.0f}원")

    for pos in balance.positions:
        print(f"  {pos.stock_name}: {pos.quantity}주 (손익: {pos.pnl_amount:,.0f}원)")
    ```

=== "시세 조회"

    ```python
    price = client.domestic.price("005930")  # 삼성전자
    print(f"현재가: {price.current_price:,.0f}원 ({price.change_rate:+.2f}%)")
    print(f"거래량: {price.volume:,}")
    ```

=== "매수/매도"

    ```python
    # 지정가 매수
    result = client.domestic.buy("005930", quantity=10, price=70000)
    print(f"주문번호: {result.order_no}")

    # 매도
    result = client.domestic.sell("005930", quantity=5, price=72000)
    ```

=== "차트"

    ```python
    chart = client.domestic.chart(
        "005930",
        period="day",
        start_date="20240101",
        end_date="20240131",
    )
    ```

### 해외 주식

```python
# 시세 조회
aapl = client.overseas.price("AAPL", market="FN")  # NASDAQ
print(f"AAPL: ${aapl.current_price:.2f}")

# 잔고
us_balance = client.overseas.balance()

# 매수
result = client.overseas.buy("AAPL", quantity=5, price=180.0)
```

### 선물/옵션

```python
futures = client.futures.balance()
print(f"예탁총액: {futures.deposit_total:,.0f}원")
```

## Context Manager

세션 종료 시 토큰을 자동으로 해제합니다:

```python
with PyDBSec(app_key="...", app_secret="...") as client:
    balance = client.domestic.balance()
# with 블록을 벗어나면 토큰 자동 revoke
```

## Async

```python
import asyncio
from pydbsec import AsyncPyDBSec

async def main():
    async with AsyncPyDBSec(app_key="...", app_secret="...") as client:
        balance = await client.domestic.balance()
        price = await client.domestic.price("005930")

asyncio.run(main())
```

## 토큰 재사용

이미 발급받은 토큰이 있다면 재사용할 수 있습니다:

```python
from datetime import datetime

client = PyDBSec(
    app_key="...",
    app_secret="...",
    token="existing_token",
    token_type="Bearer",
    expires_at=datetime(2024, 12, 31, 23, 59, 59),
)
```

## 에러 처리

```python
from pydbsec import PyDBSec, TokenError, APIError

try:
    client = PyDBSec(app_key="invalid", app_secret="invalid")
    balance = client.domestic.balance()
except TokenError as e:
    print(f"인증 실패: {e} (status: {e.status_code})")
except APIError as e:
    print(f"API 오류: {e} (code: {e.rsp_cd})")
```

## Market Codes

### 국내 시세

| 코드 | 설명 |
|------|------|
| `UJ` | 주식 (통합, 기본값) |
| `NJ` | 주식 (NXT) |
| `E` | ETF |
| `EN` | ETN |
| `U` | 업종/지수 |
| `W` | ELW |

### 해외 시세

| 코드 | 설명 |
|------|------|
| `FY` | NYSE (기본값) |
| `FN` | NASDAQ |
| `FA` | AMEX |

### 해외 종목 조회

| 코드 | 설명 |
|------|------|
| `NY` | NYSE |
| `NA` | NASDAQ |
| `AM` | AMEX |
