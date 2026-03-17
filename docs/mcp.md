# MCP Server (AI 어시스턴트 연동)

pydbsec은 [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 서버를 내장하고 있어, Claude Desktop, Cursor, Claude Code 등 AI 도구에서 DB증권 API를 직접 호출할 수 있습니다.

## 설치

```bash
pip install pydbsec[mcp]
```

## Claude Desktop 연동

`~/Library/Application Support/Claude/claude_desktop_config.json`:

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

Claude Desktop을 재시작하면 바로 사용 가능합니다.

**사용 예시:**

- "삼성전자 현재가 알려줘" → `get_stock_price("005930")`
- "내 잔고 보여줘" → `get_balance()`
- "AAPL 10주 180달러에 매수해줘" → `place_order("AAPL", "buy", 10, 180.0, overseas=True)`

## Claude Code 연동

```bash
claude mcp add dbsec -- env DBSEC_APP_KEY=your_key DBSEC_APP_SECRET=your_secret pydbsec-mcp
```

또는 프로젝트 `.claude/settings.json`:

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
        model="claude-opus-4-6",
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

## 디버깅

### MCP Inspector

```bash
npx @modelcontextprotocol/inspector pydbsec-mcp
```

### 직접 실행

```bash
DBSEC_APP_KEY=your_key DBSEC_APP_SECRET=your_secret pydbsec-mcp
```

### 로그 확인

```python
import logging
logging.basicConfig(level=logging.DEBUG)
# pydbsec-mcp 실행 시 모든 API 요청/응답이 로깅됨
```
