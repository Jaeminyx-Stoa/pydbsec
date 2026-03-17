# Models

pydbsec은 API 응답을 Pydantic v2 모델로 변환합니다. 모든 모델은 `raw` 속성으로 원본 API 응답에 접근할 수 있습니다.

## DomesticBalance

| Field | Type | Description |
|-------|------|-------------|
| `deposit_total` | `float` | 예탁총액 |
| `available_cash` | `float` | 주문가능현금 |
| `eval_total` | `float` | 평가총액 |
| `pnl_amount` | `float` | 평가손익 |
| `pnl_rate` | `float` | 수익률 (%) |
| `positions` | `list[DomesticPosition]` | 보유 종목 |

### DomesticPosition

| Field | Type | Description |
|-------|------|-------------|
| `stock_code` | `str` | 종목코드 (A prefix 포함) |
| `stock_name` | `str` | 종목명 |
| `quantity` | `int` | 보유 수량 |
| `current_price` | `float` | 현재가 |
| `purchase_amount` | `float` | 매입금액 |
| `eval_amount` | `float` | 평가금액 |
| `pnl_amount` | `float` | 평가손익 |
| `pnl_rate` | `float` | 수익률 (%) |

## OverseasBalance

`DomesticBalance`와 동일한 구조. `positions`는 `OverseasPosition` 리스트.

### OverseasPosition

| Field | Type | Description |
|-------|------|-------------|
| `stock_code` | `str` | 티커 심볼 (e.g., "AAPL") |
| `stock_name` | `str` | 종목명 |
| `quantity` | `int` | 보유 수량 |
| `current_price` | `float` | 현재가 |
| `purchase_amount` | `float` | 매입금액 |
| `eval_amount` | `float` | 평가금액 |
| `pnl_amount` | `float` | 평가손익 |
| `pnl_rate` | `float` | 수익률 (%) |

## FuturesBalance

[Futures API](futures.md) 참고.

## StockPrice

| Field | Type | Description |
|-------|------|-------------|
| `current_price` | `float` | 현재가 |
| `change` | `float` | 전일대비 |
| `change_rate` | `float` | 등락률 (%) |
| `volume` | `int` | 거래량 |
| `open_price` | `float` | 시가 |
| `high_price` | `float` | 고가 |
| `low_price` | `float` | 저가 |

## OrderResult

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | 주문 성공 여부 |
| `order_no` | `int` | 주문번호 |
| `message` | `str` | 응답 메시지 |

## OrderBook

현재는 `raw` 딕셔너리로 원본 응답을 제공합니다.

## Raw 데이터 접근

모든 모델은 `raw` 속성으로 원본 API 응답에 접근할 수 있습니다:

```python
balance = client.domestic.balance()
print(balance.raw)  # 원본 dict (Out, Out1 키 포함)

price = client.domestic.price("005930")
print(price.raw)  # {"Out": {"Prpr": "72000", ...}}
```
