# DB증권 OpenAPI Python 자동매매 — pydbsec으로 3줄이면 끝

DB증권 계좌로 자동매매를 구현하고 싶은데, 공식 Python SDK가 없어서 막막했던 적 있으신가요?

## 문제: DB증권 API를 Python으로 쓰려면 직접 HTTP 요청을 짜야 했다

DB증권 OpenAPI는 REST 기반이지만 Python 래퍼가 없었습니다. 그래서 토큰 발급부터 시세 조회까지 전부 직접 구현해야 했죠. 한국투자증권에는 [PyKIS](https://github.com/Soju06/python-kis)가 있고, 키움에는 `pykiwoom`이 있는데 DB증권만 빠져 있었습니다.

실제로 삼성전자 현재가 하나 조회하려면 이런 코드를 작성해야 했습니다:

```python
import httpx
from datetime import datetime, timedelta

# 1) 토큰 발급
token_resp = httpx.post(
    "https://openapi.dbsec.co.kr:8443/oauth2/token",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={
        "grant_type": "client_credentials",
        "appkey": "YOUR_APP_KEY",
        "appsecretkey": "YOUR_APP_SECRET",
        "scope": "oob",
    },
)
token_data = token_resp.json()
access_token = token_data["access_token"]
expires_at = datetime.now() + timedelta(seconds=int(token_data["expires_in"]))

# 2) 시세 조회
price_resp = httpx.post(
    "https://openapi.dbsec.co.kr:8443/api/v1/quote/kr-stock/inquiry/price",
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    },
    json={"In": {"InputCondMrktDivCode": "UJ", "InputIscd1": "005930"}},
)
result = price_resp.json()
print(result["Out"]["TrdPrc"])  # 현재가... 그런데 키가 뭐였더라?
```

**30줄이 넘습니다.** 토큰 만료 처리는요? 연속 조회(페이지네이션)는요? 에러 처리는요? 코드가 금방 100줄을 넘기고, 본래 하고 싶었던 전략 개발은 뒷전이 됩니다.

## 해결: pydbsec — DB증권 전용 Python 래퍼

[**pydbsec**](https://github.com/STOA-company/pydbsec)은 DB증권 OpenAPI를 감싼 Python 라이브러리입니다. 한국투자증권의 PyKIS처럼, DB증권도 Python 한 줄이면 됩니다.

위의 30줄짜리 코드가 이렇게 바뀝니다:

```python
from pydbsec import PyDBSec

client = PyDBSec(app_key="YOUR_APP_KEY", app_secret="YOUR_APP_SECRET")
print(client.domestic.price("005930").current_price)  # 삼성전자 현재가
```

**3줄.** 토큰 발급, 갱신, 페이지네이션 전부 내부에서 알아서 처리합니다.

## 빠른 시작

### 설치

```bash
pip install pydbsec
```

Python 3.10 이상이면 됩니다. 의존성은 `httpx`와 `pydantic` 딱 두 개뿐입니다.

### 사전 준비

1. [DB증권 계좌 개설](https://www.dbsec.co.kr)
2. [OpenAPI 포털](https://openapi.dbsec.co.kr)에서 사용 신청
3. App Key / App Secret 발급

### 잔고 조회

```python
from pydbsec import PyDBSec

client = PyDBSec(app_key="YOUR_APP_KEY", app_secret="YOUR_APP_SECRET")

balance = client.domestic.balance()
print(f"예탁총액: {balance.deposit_total:,.0f}원")
print(f"주문가능: {balance.available_cash:,.0f}원")

for pos in balance.positions:
    print(f"  {pos.stock_name}: {pos.quantity}주 (손익: {pos.pnl_amount:,.0f}원)")
```

### 매수/매도

```python
# 삼성전자 10주 지정가 매수
result = client.domestic.buy("005930", quantity=10, price=70000)
print(f"주문번호: {result.order_no}")

# 시장가 매도
result = client.domestic.sell("005930", quantity=5, price_type="03")
```

### 해외 주식

```python
# NASDAQ AAPL 현재가
aapl = client.overseas.price("AAPL", market="FN")
print(f"AAPL: ${aapl.current_price:.2f} ({aapl.change_rate:+.2f}%)")

# 해외 잔고 조회
us_balance = client.overseas.balance()
print(f"해외 평가액: ${us_balance.eval_total:,.2f}")
```

### 비동기(Async) 지원

FastAPI나 비동기 봇과 함께 쓸 때 유용합니다:

```python
import asyncio
from pydbsec import AsyncPyDBSec

async def main():
    async with AsyncPyDBSec(app_key="...", app_secret="...") as client:
        balance = await client.domestic.balance()
        price = await client.domestic.price("005930")
        print(f"삼성전자: {price.current_price:,.0f}원")

asyncio.run(main())
```

### Context Manager

세션 종료(토큰 해제)를 깔끔하게 처리합니다:

```python
with PyDBSec(app_key="...", app_secret="...") as client:
    balance = client.domestic.balance()
    # with 블록을 벗어나면 토큰 자동 해제
```

## 주요 기능 정리

| 기능 | 설명 |
|------|------|
| **국내 주식** | 잔고, 시세, 호가, 매수/매도, 주문 취소, 차트(분/일/주/월), 체결내역 |
| **해외 주식** | 잔고, 시세, 호가, 매수/매도, 주문 취소, 차트, 거래내역 |
| **선물/옵션** | 잔고 조회 |
| **토큰 자동 관리** | OAuth2 발급/갱신/해제 전부 자동. 만료 10분 전 자동 재발급 |
| **연속 조회 자동 처리** | 페이지네이션 `cont_yn`/`cont_key` 내부 처리 |
| **Type-safe** | Pydantic v2 모델로 응답 타입 보장. IDE 자동완성 지원 |
| **Sync + Async** | `PyDBSec` (동기) / `AsyncPyDBSec` (비동기) 둘 다 지원 |
| **에러 처리** | `APIError`, `TokenError` 등 구조화된 예외 클래스 |

## 왜 pydbsec인가?

**직접 HTTP를 짜면 생기는 문제들을 전부 해결합니다:**

- 토큰 만료? 자동 감지 후 재발급합니다. `IGW00121` 에러 코드까지 처리합니다.
- 페이지네이션? 잔고가 여러 페이지에 걸쳐 있어도 자동으로 모아줍니다.
- 응답 파싱? `Out`, `Out1` 같은 raw 키 대신 `balance.positions`, `price.current_price` 같은 Pythonic한 속성으로 접근합니다.
- 타입 힌트? Pydantic v2 모델이라 IDE에서 자동완성이 됩니다.

## 시작하기

```bash
pip install pydbsec
```

GitHub: [https://github.com/STOA-company/pydbsec](https://github.com/STOA-company/pydbsec)

DB증권으로 퀀트 전략을 돌리고 계신 분, 자동매매 봇을 만들고 계신 분이라면 한번 써보세요. Star를 눌러주시면 개발에 큰 힘이 됩니다.

버그 리포트, 기능 제안, PR 모두 환영합니다. [Issues](https://github.com/STOA-company/pydbsec/issues)에 남겨주세요.
