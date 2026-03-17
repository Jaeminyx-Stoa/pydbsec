"""WebSocket constants for DB Securities real-time API."""

from __future__ import annotations

# WebSocket URLs
WS_URL = "wss://openapi.dbsec.co.kr:7070"
WS_SANDBOX_URL = "wss://openapi.dbsec.co.kr:17070"

# ── TR codes (실시간 시세) ──

# Domestic stock
TR_STOCK_EXECUTION = "S00"  # 주식 체결가
TR_STOCK_ORDERBOOK = "S01"  # 주식 호가
TR_ORDER_FILLED = "IS1"  # 주문 체결 조회
TR_ORDER_RECEIVED = "IS0"  # 주문 접수 조회

# ELW
TR_ELW_EXECUTION = "W00"  # ELW 체결
TR_ELW_ORDERBOOK = "W01"  # ELW 호가

# Index
TR_INDEX_EXECUTION = "U00"  # 업종지수 체결가
