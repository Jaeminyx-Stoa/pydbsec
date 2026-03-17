# Domestic API (국내 주식)

`client.domestic` 네임스페이스를 통해 접근합니다.

## Trading

### `buy(stock_code, quantity, price=0, **kwargs)`

국내 주식 매수 주문.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stock_code` | `str` | required | 종목코드 (e.g., "005930") |
| `quantity` | `int` | required | 주문 수량 |
| `price` | `float` | `0` | 주문가 (0이면 시장가) |
| `price_type` | `str` | `"00"` | 호가유형 ("00"=지정가, "03"=시장가) |

**Returns:** `OrderResult`

```python
result = client.domestic.buy("005930", quantity=10, price=70000)
print(result.order_no)  # 주문번호
```

### `sell(stock_code, quantity, price=0, **kwargs)`

국내 주식 매도 주문. 파라미터는 `buy()`와 동일.

### `cancel(order_no, stock_code, quantity)`

주문 취소.

| Parameter | Type | Description |
|-----------|------|-------------|
| `order_no` | `int` | 원주문번호 |
| `stock_code` | `str` | 종목코드 |
| `quantity` | `int` | 취소 수량 |

**Returns:** `OrderResult`

## Account

### `balance(query_type="2")`

잔고 조회. **Returns:** `DomesticBalance`

```python
balance = client.domestic.balance()
print(balance.deposit_total)   # 예탁총액
print(balance.available_cash)  # 주문가능현금
print(balance.pnl_amount)     # 평가손익
for pos in balance.positions:
    print(pos.stock_name, pos.quantity, pos.pnl_rate)
```

### `deposit()`

예수금 조회. **Returns:** `dict`

### `orderable_quantity(stock_code, price, side="2")`

주문 가능 수량 조회. **Returns:** `dict`

## Quote

### `price(stock_code, market="UJ")`

현재가 조회. **Returns:** `StockPrice`

```python
price = client.domestic.price("005930")
print(price.current_price)  # 현재가
print(price.change_rate)    # 등락률 (%)
print(price.volume)         # 거래량
```

### `order_book(stock_code, market="UJ")`

호가 조회. **Returns:** `OrderBook`

### `tickers(market="UJ")`

종목 목록 조회. **Returns:** `dict | list[dict]`

## History

### `transaction_history(**kwargs)`

당일 체결/미체결 내역. **Returns:** `dict | list[dict]`

### `trading_history(start_date, end_date)`

기간별 거래 내역 (YYYYMMDD). **Returns:** `dict | list[dict]`

### `daily_trade_report(date)`

일별 거래 보고서 (YYYYMMDD). **Returns:** `dict | list[dict]`

## Chart

### `chart(stock_code, period="day", **kwargs)`

차트 데이터 조회.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stock_code` | `str` | required | 종목코드 |
| `period` | `str` | `"day"` | `"minute"`, `"day"`, `"week"`, `"month"` |
| `start_date` | `str` | `""` | YYYYMMDD |
| `end_date` | `str` | `""` | YYYYMMDD |
| `time_interval` | `str` | `"60"` | 분봉 간격 (60=1분, 300=5분) |

**Returns:** `dict | list[dict]`
