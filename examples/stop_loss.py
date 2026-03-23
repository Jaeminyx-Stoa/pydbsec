"""Automated stop-loss example.

Monitors a stock price and places a market sell order
when the price drops below a threshold.
"""

import logging
import time

from pydbsec import PyDBSec
from pydbsec.exceptions import APIError, InvalidOrderError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)


def run_stop_loss(
    client: PyDBSec,
    stock_code: str,
    quantity: int,
    stop_price: float,
    check_interval: int = 5,
):
    """Monitor price and sell if it drops below stop_price."""
    log.info("Stop-loss active: %s | qty=%d | stop=%.0f", stock_code, quantity, stop_price)

    while True:
        price = client.domestic.price(stock_code)
        log.info("%s current: %.0f (stop: %.0f)", stock_code, price.current_price, stop_price)

        if price.current_price <= stop_price:
            log.warning("STOP-LOSS TRIGGERED at %.0f", price.current_price)
            try:
                result = client.domestic.sell(
                    stock_code, quantity=quantity, price_type="03"  # market order
                )
                log.info("Sell order placed: order_no=%d", result.order_no)
                return result
            except InvalidOrderError as e:
                log.error("Order failed: %s (rsp_cd=%s)", e, e.rsp_cd)
                raise
            except APIError as e:
                log.error("API error: %s", e)
                raise

        time.sleep(check_interval)


if __name__ == "__main__":
    client = PyDBSec(app_key="YOUR_APP_KEY", app_secret="YOUR_APP_SECRET")

    try:
        run_stop_loss(
            client,
            stock_code="005930",  # Samsung Electronics
            quantity=10,
            stop_price=65000,     # Sell if price drops to 65,000 KRW
            check_interval=10,
        )
    finally:
        client.close()
