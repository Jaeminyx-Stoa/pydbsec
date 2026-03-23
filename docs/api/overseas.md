# Overseas API (해외 주식)

`client.overseas` 네임스페이스를 통해 접근합니다.

## Trading

### `buy(stock_code, quantity, price=0, **kwargs)`

해외 주식 매수 주문.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stock_code` | `str` | required | 티커 심볼 (e.g., "AAPL") |
| `quantity` | `int` | required | 주문 수량 |
| `price` | `float` | `0` | 주문가 |
| `price_type` | `str` | `"1"` | 호가유형 ("1"=지정가) |

**Returns:** `OrderResult`

### `sell(stock_code, quantity, price=0, **kwargs)`

해외 주식 매도 주문. 파라미터는 `buy()`와 동일.

### `cancel(order_no, stock_code, quantity)`

주문 취소. **Returns:** `OrderResult`

## Account

### `balance(**kwargs)`

해외 주식 잔고 조회. **Returns:** `OverseasBalance`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `balance_type` | `str` | `"2"` | "1"=외화잔고, "2"=주식상세, "3"=국가별, "9"=실현손익 |
| `commission_type` | `str` | `"1"` | "0"=미포함, "1"=매수만, "2"=매수+매도 |
| `currency_type` | `str` | `"2"` | "1"=원화, "2"=외화 |

```python
balance = client.overseas.balance()
for pos in balance.positions:
    print(f"{pos.stock_code}: ${pos.eval_amount:,.2f}")
```

### `deposit()`

해외 예수금 조회. **Returns:** `dict`

### `orderable_quantity(stock_code, price, side="2")`

주문 가능 수량. **Returns:** `dict`

## Quote

### `price(stock_code, market="FY")`

해외 현재가 조회. **Returns:** `StockPrice`

| Market Code | Description |
|-------------|-------------|
| `FY` | NYSE (기본값) |
| `FN` | NASDAQ |
| `FA` | AMEX |

```python
aapl = client.overseas.price("AAPL", market="FN")
print(f"${aapl.current_price:.2f} ({aapl.change_rate:+.2f}%)")
```

### `order_book(stock_code, market="FY")`

호가 조회. **Returns:** `OrderBook`

### `tickers(market="NY")`

종목 목록 조회. **Returns:** `dict | list[dict]`

## History

### `transaction_history(start_date, end_date, **kwargs)`

거래 내역 조회 (YYYYMMDD). **Returns:** `dict | list[dict]`

## Chart

### `chart(stock_code, period="day", **kwargs)`

차트 데이터. 파라미터는 Domestic `chart()`와 동일 (market 기본값만 `"FY"`).

**Returns:** [`ChartData`](models.md#chartdata)
