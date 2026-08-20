
import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed

# Settings for the trading rule.
FAST = 20          # fast average window in days
SLOW = 50          # slow average window in days
START_CASH = 100000

# The stocks and funds I want to test. A mix of big names and some ETFs.
UNIVERSE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM",
    "V", "JNJ", "WMT", "PG", "DIS", "KO", "PEP", "INTC", "CSCO",
    "NFLX", "AMD", "BA", "XOM", "CVX", "HD", "MCD", "NKE",
    "SPY", "QQQ", "DIA", "IWM", "VTI",
]


def get_prices():
    # Read my keys from the environment.
    key = os.environ["ALPACA_API_KEY"]
    secret = os.environ["ALPACA_SECRET_KEY"]
    client = StockHistoricalDataClient(key, secret)

    # Ask for about three years of daily bars up to today.
    end = datetime.now()
    start = end - timedelta(days=365 * 3)

    request = StockBarsRequest(
        symbol_or_symbols=UNIVERSE,
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
        feed=DataFeed.IEX,   # the free data feed
    )
    bars = client.get_stock_bars(request).df

    # Turn the closes into one column per stock, lined up by date.
    closes = bars["close"].unstack(level=0)
    return closes


def backtest(prices, cash_fraction):
    # Walk day by day and follow the crossover rule.
    fast = prices.rolling(FAST).mean()
    slow = prices.rolling(SLOW).mean()

    cash = START_CASH
    shares = 0.0

    for i in range(len(prices)):
        price = prices.iloc[i]

        # Skip days with no price or where the averages are not ready yet.
        if np.isnan(price) or np.isnan(fast.iloc[i]) or np.isnan(slow.iloc[i]):
            continue

        # Buy when the fast average is above the slow average and I hold nothing.
        if fast.iloc[i] > slow.iloc[i] and shares == 0:
            spend = cash * cash_fraction
            shares = spend / price
            cash = cash - spend
        # Sell when the fast average drops below the slow average and I hold shares.
        elif fast.iloc[i] < slow.iloc[i] and shares > 0:
            cash = cash + shares * price
            shares = 0.0

    # Cash out any shares I am still holding at the last real price.
    last_price = prices.dropna().iloc[-1]
    final = cash + shares * last_price
    return final


def total_return(final):
    return (final - START_CASH) / START_CASH


def main():
    print("Pulling real daily prices from Alpaca, please wait.")
    closes = get_prices()

    # Test the rule on each stock using a plain half cash trade.
    scores = {}
    for name in closes.columns:
        prices = closes[name]
        # Skip any stock that did not return enough history.
        if prices.dropna().shape[0] < SLOW + 5:
            continue
        final = backtest(prices, cash_fraction=0.5)
        scores[name] = total_return(final)

    # Keep the best three stocks by return.
    ranked = sorted(scores, key=scores.get, reverse=True)
    best_three = ranked[:3]
    print("\nBest three stocks by return on real data:")
    for name in best_three:
        print(f"  {name}: {scores[name]:.1%}")

    # Run three risk levels on the best three and compare.
    # The only difference is how much cash goes into each trade.
    risk_levels = {"aggressive": 1.0, "moderate": 0.6, "conservative": 0.3}
    print("\nRisk levels on the best three stocks, shown as average return:")
    for level, fraction in risk_levels.items():
        returns = []
        for name in best_three:
            final = backtest(closes[name], cash_fraction=fraction)
            returns.append(total_return(final))
        avg = sum(returns) / len(returns)
        print(f"  {level}: {avg:.1%}")

    print("\nNote: this uses real prices, so these are the rule's real results.")


if __name__ == "__main__":
    # Only run if my keys are set, since real data needs them.
    if "ALPACA_API_KEY" in os.environ and "ALPACA_SECRET_KEY" in os.environ:
        main()
    else:
        print("Set ALPACA_API_KEY and ALPACA_SECRET_KEY first, then run again.")
