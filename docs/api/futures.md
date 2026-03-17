# Futures API (선물/옵션)

`client.futures` 네임스페이스를 통해 접근합니다.

## `balance()`

국내 선물/옵션 잔고 조회. **Returns:** `FuturesBalance`

```python
futures = client.futures.balance()
print(f"예탁총액: {futures.deposit_total:,.0f}원")
print(f"평가금액: {futures.eval_amount:,.0f}원")
print(f"평가손익: {futures.pnl_amount:,.0f}원")
print(f"당일실현손익: {futures.realized_pnl:,.0f}원")
print(f"수수료: {futures.commission:,.0f}원")

for pos in futures.positions:
    print(f"  {pos.stock_name}: {pos.quantity}계약")
```

### FuturesBalance Fields

| Field | Type | Description |
|-------|------|-------------|
| `deposit_total` | `float` | 예탁총액 |
| `eval_amount` | `float` | 평가금액 |
| `pnl_amount` | `float` | 평가손익 |
| `realized_pnl` | `float` | 당일 실현손익 |
| `commission` | `float` | 수수료 |
| `positions` | `list[FuturesPosition]` | 보유 포지션 |
