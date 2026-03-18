---
hide:
  - navigation
  - toc
---

<style>
.md-typeset h1 { display: none; }
.hero { text-align: center; padding: 2rem 0; }
.hero h2 { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; }
.hero p.subtitle { font-size: 1.3rem; opacity: 0.8; margin-bottom: 2rem; }
.hero .buttons { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }
.hero .buttons a { padding: 0.75rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 1rem; }
.hero .buttons .primary { background: #7c4dff; color: white; }
.hero .buttons .secondary { border: 2px solid #7c4dff; color: #7c4dff; }
.features { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin: 3rem 0; }
.feature { padding: 1.5rem; border-radius: 12px; border: 1px solid var(--md-default-fg-color--lightest); }
.feature h3 { margin-top: 0; }
.badges { display: flex; gap: 0.5rem; justify-content: center; margin-bottom: 1.5rem; flex-wrap: wrap; }
.by-stoa { font-size: 0.9rem; opacity: 0.6; margin-top: 0.5rem; }
.by-stoa a { color: inherit; text-decoration: underline; }
</style>

<div class="hero" markdown>

## pydbsec
<p class="by-stoa">by <a href="https://github.com/STOA-company">STOA Company</a> — Makers of <a href="https://quantus.kr">Quantus</a></p>

<p class="subtitle">DB증권 OpenAPI Python 래퍼<br>3줄이면 잔고 조회, 5줄이면 자동매매</p>

<div class="badges">
  <a href="https://pypi.org/project/pydbsec/"><img src="https://img.shields.io/pypi/v/pydbsec.svg" alt="PyPI"></a>
  <a href="https://pypi.org/project/pydbsec/"><img src="https://img.shields.io/pypi/pyversions/pydbsec.svg" alt="Python"></a>
  <a href="https://github.com/STOA-company/pydbsec/actions"><img src="https://github.com/STOA-company/pydbsec/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT"></a>
</div>

```python
from pydbsec import PyDBSec

client = PyDBSec(app_key="...", app_secret="...")
print(client.domestic.price("005930").current_price)  # 삼성전자 현재가
```

<div class="buttons">
<a href="installation/" class="primary">시작하기</a>
<a href="https://github.com/STOA-company/pydbsec" class="secondary">GitHub</a>
</div>

</div>

---

<div class="features" markdown>

<div class="feature" markdown>
### :material-chart-line: 국내 + 해외 주식
잔고 조회, 시세, 호가, 매수/매도, 차트, 거래내역 — 국내(KRX)와 해외(NYSE/NASDAQ/AMEX) 모두 지원
</div>

<div class="feature" markdown>
### :material-console: CLI 도구
`pydbsec price 005930` — 코드 없이 터미널에서 바로 주가 조회, 잔고 확인, 주문 실행
</div>

<div class="feature" markdown>
### :material-robot: MCP Server
`npx pydbsec-mcp` — Claude Desktop, Cursor 등 AI 도구에서 "삼성전자 현재가 알려줘" 한마디로 조회
</div>

<div class="feature" markdown>
### :material-lightning-bolt: WebSocket 실시간
체결가, 호가 실시간 스트리밍 — `async for tick in ws` 패턴으로 간편하게
</div>

<div class="feature" markdown>
### :material-shield-check: Rate Limiting
API 초당 요청 제한 자동 준수 — 실수로 IP 차단당하는 걸 방지
</div>

<div class="feature" markdown>
### :material-language-python: Type-Safe
Pydantic v2 모델 + mypy strict 통과 — IDE 자동완성, 타입 안전성 보장
</div>

</div>

---

## Before & After

기존에 DB증권 API를 Python으로 쓰려면:

```python
# 30줄 넘는 코드...
token_resp = httpx.post("https://openapi.dbsec.co.kr:8443/oauth2/token",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={"grant_type": "client_credentials", "appkey": "...", "appsecretkey": "...", "scope": "oob"})
access_token = token_resp.json()["access_token"]
price_resp = httpx.post("https://openapi.dbsec.co.kr:8443/api/v1/quote/kr-stock/inquiry/price",
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"},
    json={"In": {"InputCondMrktDivCode": "UJ", "InputIscd1": "005930"}})
print(price_resp.json()["Out"]["Prpr"])  # 필드명이 뭐였더라?
```

**pydbsec을 쓰면:**

```python
from pydbsec import PyDBSec

client = PyDBSec(app_key="...", app_secret="...")
print(client.domestic.price("005930").current_price)  # 끝
```

---

## 다양한 사용법

=== "Python"

    ```python
    from pydbsec import PyDBSec

    with PyDBSec(app_key="...", app_secret="...") as client:
        balance = client.domestic.balance()
        print(f"예탁총액: {balance.deposit_total:,.0f}원")
    ```

=== "CLI"

    ```bash
    export DBSEC_APP_KEY="..." DBSEC_APP_SECRET="..."
    pydbsec price 005930
    pydbsec balance
    pydbsec portfolio
    ```

=== "MCP (AI)"

    ```json
    {
      "mcpServers": {
        "dbsec": {
          "command": "npx",
          "args": ["pydbsec-mcp"],
          "env": { "DBSEC_APP_KEY": "...", "DBSEC_APP_SECRET": "..." }
        }
      }
    }
    ```

=== "Async"

    ```python
    from pydbsec import AsyncPyDBSec

    async with AsyncPyDBSec(app_key="...", app_secret="...") as client:
        balance = await client.domestic.balance()
        price = await client.domestic.price("005930")
    ```

---

## 설치

```bash
pip install pydbsec            # REST + CLI
pip install pydbsec[ws]        # + WebSocket
pip install pydbsec[mcp]       # + MCP Server
pip install pydbsec[ws,mcp]    # All features
```

[시작하기 :material-arrow-right:](installation.md){ .md-button .md-button--primary }
[API 레퍼런스 :material-arrow-right:](api/client.md){ .md-button }
