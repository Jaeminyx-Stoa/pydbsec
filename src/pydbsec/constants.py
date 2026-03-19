"""DB Securities OpenAPI constants."""

from __future__ import annotations

BASE_URL = "https://openapi.dbsec.co.kr:8443"

# OAuth endpoints
OAUTH_TOKEN_URL = "/oauth2/token"
OAUTH_REVOKE_URL = "/oauth2/revoke"

# ── Domestic (국내) Trading endpoints ──
DOMESTIC_ORDER = "/api/v1/trading/kr-stock/order"
DOMESTIC_CANCEL_ORDER = "/api/v1/trading/kr-stock/order-cancel"
DOMESTIC_BALANCE = "/api/v1/trading/kr-stock/inquiry/balance"
DOMESTIC_DEPOSIT = "/api/v1/trading/kr-stock/inquiry/acnt-deposit"
DOMESTIC_ABLE_ORDER_QTY = "/api/v1/trading/kr-stock/inquiry/able-orderqty"
DOMESTIC_TRANSACTION_HISTORY = "/api/v1/trading/kr-stock/inquiry/transaction-history"
DOMESTIC_TRADING_HISTORY = "/api/v1/trading/kr-stock/inquiry/trading-history"
DOMESTIC_DAILY_TRADE_REPORT = "/api/v1/trading/kr-stock/inquiry/daliy-trade-report"

# ── Domestic (국내) Quote endpoints ──
DOMESTIC_STOCK_TICKER = "/api/v1/quote/kr-stock/inquiry/stock-ticker"
DOMESTIC_STOCK_PRICE = "/api/v1/quote/kr-stock/inquiry/price"
DOMESTIC_ORDER_BOOK = "/api/v1/quote/kr-stock/inquiry/orderbook"

# ── Domestic (국내) Chart endpoints ──
DOMESTIC_CHART_MINUTE = "/api/v1/quote/kr-chart/min"
DOMESTIC_CHART_DAY = "/api/v1/quote/kr-chart/day"
DOMESTIC_CHART_WEEK = "/api/v1/quote/kr-chart/week"
DOMESTIC_CHART_MONTH = "/api/v1/quote/kr-chart/month"

# ── Overseas (해외) Trading endpoints ──
OVERSEAS_ORDER = "/api/v1/trading/overseas-stock/order"
OVERSEAS_BALANCE = "/api/v1/trading/overseas-stock/inquiry/balance-margin"
OVERSEAS_DEPOSIT = "/api/v1/trading/overseas-stock/inquiry/deposit-detail"
OVERSEAS_ABLE_ORDER_QTY = "/api/v1/trading/overseas-stock/inquiry/able-orderqty"
OVERSEAS_TRANSACTION_HISTORY = "/api/v1/trading/overseas-stock/inquiry/transaction-history"

# ── Overseas (해외) Quote endpoints ──
OVERSEAS_STOCK_TICKER = "/api/v1/quote/overseas-stock/inquiry/stock-ticker"
OVERSEAS_STOCK_PRICE = "/api/v1/quote/overseas-stock/inquiry/price"
OVERSEAS_ORDER_BOOK = "/api/v1/quote/overseas-stock/inquiry/orderbook"

# ── Overseas (해외) Chart endpoints ──
OVERSEAS_CHART_MINUTE = "/api/v1/quote/overseas-stock/chart/min"
OVERSEAS_CHART_DAY = "/api/v1/quote/overseas-stock/chart/day"
OVERSEAS_CHART_WEEK = "/api/v1/quote/overseas-stock/chart/week"
OVERSEAS_CHART_MONTH = "/api/v1/quote/overseas-stock/chart/month"

# ── Futures/Options (선물옵션) Trading endpoints ──
FUTURES_BALANCE = "/api/v1/trading/kr-futureoption/inquiry/balance"

# ── Futures/Options (선물옵션) Quote endpoints ──
FUTURES_OPTION_TICKER = "/api/v1/quote/kr-futureoption/inquiry/option-ticker"
FUTURES_FUTURE_TICKER = "/api/v1/quote/kr-futureoption/inquiry/future-ticker"
FUTURES_OPTION_PRICE = "/api/v1/quote/kr-futureoption/inquiry/price"
FUTURES_OPTION_ORDERBOOK = "/api/v1/quote/kr-futureoption/inquiry/orderbook"
FUTURES_OPTION_DAILY_PRICE = "/api/v1/quote/kr-futureoption/inquiry/daily-price"
FUTURES_OPTION_HOUR_PRICE = "/api/v1/quote/kr-futureoption/inquiry/hour-price"
FUTURES_OPTION_BOARD = "/api/v1/quote/kr-futureoption/inquiry/option-board"

# ── Market codes ──
# Domestic market codes (시세 조회)
MARKET_STOCK = "UJ"  # 주식(통합)
MARKET_STOCK_NXT = "NJ"  # 주식(NXT)
MARKET_ETF = "E"  # ETF
MARKET_ETN = "EN"  # ETN
MARKET_INDEX = "U"  # 업종&지수
MARKET_ELW = "W"  # ELW

# Overseas market codes (시세 조회)
MARKET_NYSE = "FY"
MARKET_NASDAQ = "FN"
MARKET_AMEX = "FA"

# Overseas market codes (종목 조회)
MARKET_NYSE_TICKER = "NY"
MARKET_NASDAQ_TICKER = "NA"
MARKET_AMEX_TICKER = "AM"

# Futures/Options market codes (선물옵션 시세 조회)
MARKET_FUTURES = "FU"  # 선물
MARKET_OPTIONS_MONTHLY = "OF"  # 옵션(월물)
MARKET_OPTIONS_WEEKLY = "WO"  # 위클리 옵션 (코스피/코스닥 위클리T)
MARKET_OPTIONS_WEEKLY_OW = "OW"  # 위클리 옵션 (별도)

# ── Error codes ──
RSP_SUCCESS = "00000"
ERROR_INVALID_APPKEY = "IGW00103"
ERROR_INVALID_APPSECRET = "IGW00105"
ERROR_TOKEN_EXPIRED = "IGW00121"
