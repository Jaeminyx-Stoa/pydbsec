"""Integration tests — requires real DB Securities API credentials.

Run with:
    DBSEC_APP_KEY=xxx DBSEC_APP_SECRET=yyy pytest tests/test_integration.py -v

Skipped automatically when credentials are not set.
"""

import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("DBSEC_APP_KEY"),
    reason="DBSEC_APP_KEY not set — skipping integration tests",
)


@pytest.fixture()
def client():
    from pydbsec import PyDBSec

    c = PyDBSec(
        app_key=os.environ["DBSEC_APP_KEY"],
        app_secret=os.environ["DBSEC_APP_SECRET"],
    )
    yield c
    c.close()


class TestDomestic:
    def test_price(self, client):
        price = client.domestic.price("005930")
        assert price.current_price > 0

    def test_chart(self, client):
        chart = client.domestic.chart("005930", period="day")
        assert len(chart.candles) > 0
        assert chart.candles[0].close > 0

    def test_order_book(self, client):
        ob = client.domestic.order_book("005930")
        assert len(ob.asks) > 0 or ob.raw  # at least raw data

    def test_balance(self, client):
        balance = client.domestic.balance()
        assert balance.deposit_total >= 0


class TestOverseas:
    def test_price(self, client):
        price = client.overseas.price("AAPL", market="FN")
        assert price.current_price > 0

    def test_chart(self, client):
        chart = client.overseas.chart("AAPL", period="day", market="FN")
        assert len(chart.candles) > 0


class TestFutures:
    def test_balance(self, client):
        balance = client.futures.balance()
        assert balance.deposit_total >= 0


class TestPortfolio:
    def test_summary(self, client):
        summary = client.portfolio_summary(include_overseas=False)
        assert summary.total_nav >= 0
        assert len(summary.positions) >= 0
