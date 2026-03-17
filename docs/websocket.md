# WebSocket (실시간)

DB증권 실시간 시세 데이터를 WebSocket으로 수신합니다.

## 설치

```bash
pip install pydbsec[ws]
```

## 사용법

```python
from pydbsec import PyDBSec

client = PyDBSec(app_key="...", app_secret="...")

async with client.ws as ws:
    await ws.subscribe("005930", tr_code="S00")  # 삼성전자 체결가
    await ws.subscribe("005930", tr_code="S01")  # 삼성전자 호가

    async for msg in ws:
        print(f"[{msg.tr_code}] {msg.data}")
```

## TR Codes

| Code | Description |
|------|-------------|
| `S00` | 주식 체결가 |
| `S01` | 주식 호가 |
| `IS1` | 주문 체결 조회 |
| `IS0` | 주문 접수 조회 |
| `W00` | ELW 체결 |
| `W01` | ELW 호가 |
| `U00` | 업종지수 체결가 |

## WebSocket URLs

| 환경 | URL |
|------|-----|
| Production | `wss://openapi.dbsec.co.kr:7070` |
| Sandbox | `wss://openapi.dbsec.co.kr:17070` |

## 옵션

```python
from pydbsec.ws import DBSecWebSocket, WS_SANDBOX_URL

ws = DBSecWebSocket(
    token_manager,
    ws_url=WS_SANDBOX_URL,         # Sandbox 사용
    reconnect=True,                 # 자동 재연결 (기본값)
    reconnect_delay=3.0,            # 재연결 대기 시간
    max_reconnect_attempts=10,      # 최대 재연결 시도
)
```

## 구독 관리

```python
async with client.ws as ws:
    # 구독
    await ws.subscribe("005930", tr_code="S00")
    print(ws.subscriptions)  # {("005930", "S00")}

    # 해제
    await ws.unsubscribe("005930", tr_code="S00")
```

!!! note
    연결 전에 `subscribe()`를 호출하면 큐에 저장되었다가 연결 시 자동으로 구독됩니다.
