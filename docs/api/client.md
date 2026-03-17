# Client

## PyDBSec

메인 동기 클라이언트입니다.

```python
from pydbsec import PyDBSec

client = PyDBSec(
    app_key="YOUR_APP_KEY",
    app_secret="YOUR_APP_SECRET",
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `app_key` | `str` | required | DB증권 API App Key |
| `app_secret` | `str` | required | DB증권 API App Secret |
| `token` | `str \| None` | `None` | 기존 토큰 재사용 |
| `token_type` | `str \| None` | `None` | 토큰 타입 (e.g., "Bearer") |
| `expires_at` | `datetime \| None` | `None` | 토큰 만료 시각 |
| `timeout` | `float` | `30` | HTTP 요청 타임아웃 (초) |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `token` | `str` | 현재 access token |
| `token_type` | `str \| None` | 토큰 타입 |
| `expires_at` | `datetime \| None` | 토큰 만료 시각 |
| `domestic` | `DomesticAPI` | 국내 주식 API |
| `overseas` | `OverseasAPI` | 해외 주식 API |
| `futures` | `FuturesAPI` | 선물/옵션 API |

### Methods

| Method | Description |
|--------|-------------|
| `close()` | 토큰 revoke 및 세션 종료 |

Context manager (`with` 구문) 지원.

---

## AsyncPyDBSec

비동기 클라이언트입니다. API는 `PyDBSec`과 동일하며 모든 메서드가 `async`입니다.

```python
from pydbsec import AsyncPyDBSec

async with AsyncPyDBSec(app_key="...", app_secret="...") as client:
    balance = await client.domestic.balance()
```

`async with` 구문 지원.
