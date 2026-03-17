# CLI

코드 없이 터미널에서 DB증권 API를 사용합니다.

## 설정

```bash
export DBSEC_APP_KEY="your_app_key"
export DBSEC_APP_SECRET="your_app_secret"
```

또는 `--key`, `--secret` 플래그를 사용합니다.

## 명령어

### 주가 조회

```bash
pydbsec price 005930                        # 삼성전자
pydbsec price AAPL --overseas --market FN   # NASDAQ
pydbsec --json price 005930                 # JSON 출력
```

### 잔고 조회

```bash
pydbsec balance                             # 국내
pydbsec balance --overseas                  # 해외
```

### 통합 포트폴리오

```bash
pydbsec portfolio
```

### 매수 / 매도

```bash
pydbsec buy 005930 10 70000                 # 삼성전자 10주 70000원 매수
pydbsec sell 005930 5 72000                 # 5주 72000원 매도
pydbsec buy AAPL 5 180 --overseas           # 해외 매수
```

## 출력 예시

```
$ pydbsec price 005930
005930
  Price:  72,000.00
  Change: +1,500.00 (+2.13%)
  Volume: 15,000,000
  High:   72,500.00  Low: 70,500.00  Open: 71,000.00
```

```
$ pydbsec balance
Domestic Balance
  Total:          15,000,000 KRW
  Cash:            8,000,000 KRW
  P&L:               500,000 KRW (+3.45%)
  Positions:
    A005930  삼성전자              50    7,200,000  P&L:      200,000
```
