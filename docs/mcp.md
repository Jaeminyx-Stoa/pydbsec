# MCP Server (AI 어시스턴트 연동)

pydbsec은 [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 서버를 내장하고 있어, Claude Desktop, Claude Code, Cursor 등 AI 도구에서 DB증권 API를 직접 호출할 수 있습니다.

## 사전 준비

1. [DB증권 OpenAPI](https://openapi.dbsec.co.kr)에서 **App Key / App Secret** 발급
2. Python 3.10 이상 설치

## 설치 방법

두 가지 방법 중 선택:

### 방법 1: pip (권장)

```bash
pip install pydbsec[mcp]
```

설치 후 `pydbsec-mcp` 명령어가 사용 가능합니다.

### 방법 2: npx (Python 환경 자동 관리)

Python 환경 설정 없이 바로 사용:

```bash
npx pydbsec-mcp
```

내부적으로 uvx → pipx → auto venv 순으로 최적의 Python 런타임을 자동 탐지합니다.

## Claude Desktop 연동

### 1. 설정 파일 열기

| OS | 경로 |
|----|------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

### 2. MCP 서버 추가

**pip으로 설치한 경우:**

```json
{
  "mcpServers": {
    "dbsec": {
      "command": "pydbsec-mcp",
      "env": {
        "DBSEC_APP_KEY": "your_app_key",
        "DBSEC_APP_SECRET": "your_app_secret"
      }
    }
  }
}
```

**npx를 사용하는 경우:**

```json
{
  "mcpServers": {
    "dbsec": {
      "command": "npx",
      "args": ["pydbsec-mcp"],
      "env": {
        "DBSEC_APP_KEY": "your_app_key",
        "DBSEC_APP_SECRET": "your_app_secret"
      }
    }
  }
}
```

### 3. Claude Desktop 재시작

설정 저장 후 Claude Desktop을 완전히 종료 후 재시작합니다.

### 4. 확인

채팅창에 다음과 같이 입력해보세요:

- "삼성전자 현재가 알려줘" → `get_stock_price("005930")` 자동 호출
- "내 잔고 보여줘" → `get_balance()` 자동 호출
- "AAPL 10주 180달러에 매수해줘" → `place_order("AAPL", "buy", 10, 180.0, overseas=True)`

## Claude Code 연동

### CLI로 추가

```bash
claude mcp add \
  --env DBSEC_APP_KEY=your_key \
  --env DBSEC_APP_SECRET=your_secret \
  dbsec \
  -- pydbsec-mcp
```

`--env`를 반복해서 여러 환경변수를 전달합니다. 옵션은 서버 이름(`dbsec`) 앞에, 실행 명령(`pydbsec-mcp`)은 `--` 뒤에 위치해야 합니다.

### 또는 설정 파일로 추가

프로젝트 `.claude/settings.json`:

```json
{
  "mcpServers": {
    "dbsec": {
      "command": "pydbsec-mcp",
      "env": {
        "DBSEC_APP_KEY": "your_key",
        "DBSEC_APP_SECRET": "your_secret"
      }
    }
  }
}
```

## Cursor 연동

### 1. 설정 열기

`Cmd+Shift+P` (macOS) / `Ctrl+Shift+P` (Windows) → **"Cursor Settings"** → **MCP** 탭

### 2. 서버 추가

**"Add new MCP server"** 클릭 후:

- **Name**: `dbsec`
- **Type**: `command`
- **Command**: `env DBSEC_APP_KEY=your_key DBSEC_APP_SECRET=your_secret pydbsec-mcp`

또는 프로젝트 루트에 `.cursor/mcp.json` 파일 생성:

```json
{
  "mcpServers": {
    "dbsec": {
      "command": "pydbsec-mcp",
      "env": {
        "DBSEC_APP_KEY": "your_app_key",
        "DBSEC_APP_SECRET": "your_app_secret"
      }
    }
  }
}
```

### 3. 확인

Cursor의 Composer(Agent 모드)에서 "삼성전자 현재가 조회해줘"라고 입력하면 MCP tool이 호출됩니다.

## MCP Tools

| Tool | Description | 예시 질문 |
|------|-------------|----------|
| `get_stock_price` | 주가 조회 (국내/해외) | "삼성전자 현재가?" |
| `get_balance` | 잔고 조회 | "내 국내 주식 잔고" |
| `get_portfolio_summary` | 통합 포트폴리오 | "전체 자산 현황" |
| `place_order` | 매수/매도 주문 | "삼성전자 10주 매수" |
| `get_order_book` | 호가 조회 | "삼성전자 호가창" |
| `get_chart` | 차트 데이터 | "AAPL 일봉 차트" |

### Tool Parameters

#### get_stock_price

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stock_code` | string | required | 종목코드 ("005930", "AAPL") |
| `overseas` | boolean | false | 해외 주식 여부 |
| `market` | string | "" | 시장코드 (UJ, FY, FN, FA) |

#### get_balance

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `overseas` | boolean | false | 해외 잔고 여부 |

#### place_order

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stock_code` | string | required | 종목코드 |
| `side` | string | required | "buy" 또는 "sell" |
| `quantity` | integer | required | 주문 수량 |
| `price` | number | required | 주문 가격 |
| `overseas` | boolean | false | 해외 주문 여부 |

#### get_chart

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stock_code` | string | required | 종목코드 |
| `period` | string | "day" | "minute", "day", "week", "month" |
| `start_date` | string | "" | YYYYMMDD |
| `end_date` | string | "" | YYYYMMDD |
| `overseas` | boolean | false | 해외 여부 |

## Helper Functions

### Anthropic API 직접 사용

MCP 서버 없이, Anthropic API의 tool use로 직접 사용할 수 있습니다:

```python
import anthropic
from pydbsec.mcp.helpers import get_anthropic_tools, execute_tool

client = anthropic.Anthropic()

# 1. Tool definitions 가져오기
tools = get_anthropic_tools()

# 2. Claude에게 질문
messages = [{"role": "user", "content": "삼성전자 현재가 알려줘"}]

while True:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        tools=tools,
        messages=messages,
    )

    if response.stop_reason == "end_turn":
        break

    # 3. Tool 실행
    messages.append({"role": "assistant", "content": response.content})
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = execute_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })
    messages.append({"role": "user", "content": tool_results})

# 4. 최종 응답
for block in response.content:
    if block.type == "text":
        print(block.text)
```

### MCP Client Helper

다른 앱에서 pydbsec MCP 서버에 typed 클라이언트로 연결:

```python
from pydbsec.mcp.helpers import DBSecMCPClient

async with DBSecMCPClient(app_key="...", app_secret="...") as client:
    # Typed return — StockPrice 모델
    price = await client.get_stock_price("005930")
    print(f"현재가: {price.current_price:,.0f}원")

    # Typed return — DomesticBalance 모델
    balance = await client.get_balance()
    print(f"예탁총액: {balance.deposit_total:,.0f}원")

    # Typed return — OrderResult 모델
    order = await client.place_order("005930", "buy", 10, 70000)
    print(f"주문번호: {order.order_no}")
```

### Response Parsing

MCP tool 결과 JSON을 pydbsec Pydantic 모델로 변환:

```python
from pydbsec.mcp.helpers import parse_stock_price, parse_balance, parse_order_result

# JSON string 또는 dict 모두 지원
price = parse_stock_price({"current_price": 72000, "change": 1500, ...})
print(price.current_price)  # 72000.0

balance = parse_balance(data, overseas=True)  # → OverseasBalance
result = parse_order_result(data)  # → OrderResult
```

## 트러블슈팅

### `pydbsec-mcp` 명령어를 찾을 수 없는 경우

pip으로 설치한 경로가 PATH에 포함되어 있는지 확인합니다:

```bash
# 설치 위치 확인
pip show pydbsec | grep Location

# PATH에 없다면 전체 경로로 실행
python -m pydbsec.mcp.server
```

또는 npx 방식으로 전환하면 PATH 문제를 우회할 수 있습니다.

### Claude Desktop에서 MCP 서버가 인식되지 않는 경우

1. JSON 설정 파일의 문법이 올바른지 확인 (쉼표, 따옴표 등)
2. Claude Desktop을 **완전히 종료** 후 재시작 (Dock에서 우클릭 → 종료)
3. `pydbsec-mcp`이 터미널에서 직접 실행되는지 먼저 확인:

```bash
DBSEC_APP_KEY=your_key DBSEC_APP_SECRET=your_secret pydbsec-mcp
```

### API 인증 오류

- App Key / App Secret이 올바른지 확인
- [DB증권 OpenAPI 포털](https://openapi.dbsec.co.kr)에서 서비스가 활성화 상태인지 확인
- 환경변수에 불필요한 공백이나 따옴표가 포함되지 않았는지 확인

### MCP Inspector로 디버깅

MCP 서버의 동작을 직접 테스트할 수 있습니다:

```bash
npx @modelcontextprotocol/inspector pydbsec-mcp
```

브라우저에서 Inspector UI가 열리며, 각 tool을 수동으로 호출하고 응답을 확인할 수 있습니다.
