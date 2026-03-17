# Rate Limiting

DB증권 API는 엔드포인트별 초당 요청 제한이 있습니다. pydbsec은 이를 자동으로 준수합니다.

## 기본 동작

Rate limiting은 **기본적으로 활성화**되어 있습니다.

```python
from pydbsec import PyDBSec

# rate_limit=True (기본값)
client = PyDBSec(app_key="...", app_secret="...")
```

## 비활성화

```python
client = PyDBSec(app_key="...", app_secret="...", rate_limit=False)
```

!!! warning
    비활성화하면 API 요청이 제한에 걸려 IP 차단될 수 있습니다.

## 엔드포인트별 제한

| 엔드포인트 | 초당 제한 |
|-----------|----------|
| 주문 (국내/해외) | 10 |
| 주문 취소 | 3 |
| 잔고 조회 | 2 |
| 거래내역 조회 | 2 |
| 시세 조회 | 2 |
| 호가 조회 | 2 |
| 주문가능수량 | 2 |
| 예수금 조회 | 1 |

## 동작 방식

Token bucket 알고리즘을 사용합니다:

- 각 엔드포인트별 독립적인 버킷
- 버스트 허용 (초당 제한까지 즉시 처리)
- 초과 시 자동 대기 (blocking)
- Async에서는 `asyncio.sleep` 사용 (non-blocking)
