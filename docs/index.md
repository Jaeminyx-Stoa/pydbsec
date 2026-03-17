# pydbsec

**DB증권 OpenAPI Python 래퍼** — 3줄이면 잔고 조회, 5줄이면 자동매매

```python
from pydbsec import PyDBSec

client = PyDBSec(app_key="YOUR_KEY", app_secret="YOUR_SECRET")
print(client.domestic.price("005930").current_price)  # 삼성전자 현재가
```

## Features

- **국내 주식**: 잔고, 시세, 호가, 매수/매도/취소, 차트, 거래내역
- **해외 주식**: 잔고, 시세, 호가, 매수/매도/취소, 차트, 거래내역
- **선물/옵션**: 잔고 조회
- **Sync + Async**: `PyDBSec` / `AsyncPyDBSec`
- **Type-safe**: Pydantic v2 모델 응답, IDE 자동완성
- **Auto token**: OAuth2 토큰 자동 발급/갱신
- **Auto pagination**: 연속 조회 자동 처리

## Installation

```bash
pip install pydbsec
```

Python 3.10+ 필요. 의존성: `httpx`, `pydantic`.

## Prerequisites

1. [DB증권 계좌 개설](https://www.dbsec.co.kr)
2. [OpenAPI 포털](https://openapi.dbsec.co.kr)에서 사용 신청
3. App Key / App Secret 발급

## Links

- [GitHub](https://github.com/STOA-company/pydbsec)
- [PyPI](https://pypi.org/project/pydbsec/)
- [Quick Start →](quickstart.md)
