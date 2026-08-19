"""
Live paper trading loop for the Alpaca API.
This runs all the time and checks the market every 15 minutes.
When the market is open it looks at recent 15 minute bars and may place a
practice trade with fake money in paper mode.
US stocks only trade during market hours, so when the market is closed the
bot just waits and checks again later.
This is a learning project and not financial advice.
"""

import os
import time

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.enums import DataFeed

# The stocks I want the bot to watch.
SYMBOLS = ["AAPL", "MSFT", "SPY"]

# The two averages, counted in 15 minute bars.
FAST = 10
SLOW = 30

# How long to wait between checks, in seconds.
WAIT = 15 * 60


def check_symbols(trading, data):
    # Find out which stocks I already own.
    positions = trading.get_all_positions()
    owned = [p.symbol for p in positions]

    for symbol in SYMBOLS:
        # Pull recent 15 minute bars so I can build the two averages.
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame(15, TimeFrameUnit.Minute),
            limit=SLOW + 5,
            feed=DataFeed.IEX,   # the free data feed
        )
        bars = data.get_stock_bars(request).df
        closes = bars["close"].reset_index(drop=True)

        fast_now = closes.tail(FAST).mean()
        slow_now = closes.tail(SLOW).mean()

        # Buy when the fast average is above the slow average and I hold nothing.
        if fast_now > slow_now and symbol not in owned:
            trading.submit_order(MarketOrderRequest(
                symbol=symbol, qty=1, side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY))
            print("Bought", symbol)
        # Sell when the fast average drops below the slow average and I own it.
        elif fast_now < slow_now and symbol in owned:
            trading.submit_order(MarketOrderRequest(
                symbol=symbol, qty=1, side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY))
            print("Sold", symbol)
        else:
            # No clear signal, so I hold and do nothing.
            print("No trade for", symbol)


def run_forever():
    # Set up the Alpaca clients using my keys from the environment.
    key = os.environ["ALPACA_API_KEY"]
    secret = os.environ["ALPACA_SECRET_KEY"]
    trading = TradingClient(key, secret, paper=True)
    data = StockHistoricalDataClient(key, secret)

    # Keep running forever. Check every 15 minutes.
    # Only trade when the market is open, otherwise just wait.
    while True:
        clock = trading.get_clock()
        if clock.is_open:
            check_symbols(trading, data)
        else:
            print("Market is closed, waiting.")
        time.sleep(WAIT)


if __name__ == "__main__":
    # Only run if my keys are set, so it does not crash without them.
    if "ALPACA_API_KEY" in os.environ and "ALPACA_SECRET_KEY" in os.environ:
        run_forever()
    else:
        print("Set ALPACA_API_KEY and ALPACA_SECRET_KEY first, then run again.")
