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

| Field | Type | Description |
|-------|------|-------------|
| `asks` | `list[OrderBookLevel]` | 매도 호가 (최우선 매도가부터) |
| `bids` | `list[OrderBookLevel]` | 매수 호가 (최우선 매수가부터) |
| `total_ask_volume` | `int` | 총 매도 잔량 |
| `total_bid_volume` | `int` | 총 매수 잔량 |

### OrderBookLevel

| Field | Type | Description |
|-------|------|-------------|
| `price` | `float` | 호가 |
| `volume` | `int` | 잔량 |

```python
ob = client.domestic.order_book("005930")
print(f"매도1호가: {ob.asks[0].price:,.0f}원 ({ob.asks[0].volume:,}주)")
print(f"매수1호가: {ob.bids[0].price:,.0f}원 ({ob.bids[0].volume:,}주)")
```

## ChartData

`chart()` 메서드의 반환 타입입니다.

| Field | Type | Description |
|-------|------|-------------|
| `candles` | `list[ChartCandle]` | OHLCV 캔들 리스트 |

### ChartCandle

| Field | Type | Description |
|-------|------|-------------|
| `date` | `str` | 거래일 (YYYYMMDD) |
| `time` | `str` | 거래시간 (분봉 전용) |
| `open` | `float` | 시가 |
| `high` | `float` | 고가 |
| `low` | `float` | 저가 |
| `close` | `float` | 종가 |
| `volume` | `int` | 거래량 |

```python
chart = client.domestic.chart("005930", period="day", start_date="20260301", end_date="20260320")
for c in chart.candles:
    print(f"{c.date}: {c.close:,.0f}원 (vol: {c.volume:,})")
```

## Raw 데이터 접근

모든 모델은 `raw` 속성으로 원본 API 응답에 접근할 수 있습니다:

```python
balance = client.domestic.balance()
print(balance.raw)  # 원본 dict (Out, Out1 키 포함)

price = client.domestic.price("005930")
print(price.raw)  # {"Out": {"Prpr": "72000", ...}}
```
