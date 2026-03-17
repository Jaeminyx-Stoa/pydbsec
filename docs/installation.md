# Installation

## Requirements

- Python 3.10+
- DB증권 OpenAPI 계정 ([가입](https://openapi.dbsec.co.kr))

## 설치

=== "기본 (REST + CLI)"

    ```bash
    pip install pydbsec
    ```

=== "WebSocket 포함"

    ```bash
    pip install pydbsec[ws]
    ```

=== "MCP Server 포함"

    ```bash
    pip install pydbsec[mcp]
    ```

=== "전체"

    ```bash
    pip install pydbsec[ws,mcp]
    ```

## API 키 발급

1. [DB증권 홈페이지](https://www.dbsec.co.kr)에서 계좌 개설
2. [OpenAPI 포털](https://openapi.dbsec.co.kr)에서 사용 신청
3. App Key / App Secret 발급

## 확인

```python
import pydbsec
print(pydbsec.__version__)
```

```bash
pydbsec --help
```
