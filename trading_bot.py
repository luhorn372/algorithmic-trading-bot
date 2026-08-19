"""
Simple moving average trading bot backtest.
It runs on made up prices, so it works with no account and no download.
This is a learning project and not financial advice.
"""

import numpy as np
import pandas as pd

# I fix the random seed so the made up prices are the same every run.
np.random.seed(7)

# Settings for the trading rule.
FAST = 20          # fast average window in days
SLOW = 50          # slow average window in days
START_CASH = 100000
N_STOCKS = 30
N_DAYS = 750       # about three years of trading days


def make_prices(n_days):
    # Build a fake price path with a small upward drift and daily noise.
    daily_return = np.random.normal(0.0004, 0.02, n_days)
    price = 100 * np.cumprod(1 + daily_return)
    return pd.Series(price)


def backtest(prices, cash_fraction):
    # Walk day by day and follow the crossover rule.
    fast = prices.rolling(FAST).mean()
    slow = prices.rolling(SLOW).mean()

    cash = START_CASH
    shares = 0.0

    for i in range(len(prices)):
        price = prices.iloc[i]

        # Skip the early days where the averages are not ready yet.
        if np.isnan(fast.iloc[i]) or np.isnan(slow.iloc[i]):
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

    # Cash out any shares I am still holding at the last price.
    final = cash + shares * prices.iloc[-1]
    return final


def total_return(final):
    return (final - START_CASH) / START_CASH


def main():
    # Step 1: make 30 fake stocks.
    stocks = {f"STOCK{i:02d}": make_prices(N_DAYS) for i in range(N_STOCKS)}

    # Step 2: test the rule on each stock using a plain half cash trade.
    scores = {}
    for name, prices in stocks.items():
        final = backtest(prices, cash_fraction=0.5)
        scores[name] = total_return(final)

    # Step 3: keep the best three stocks by return.
    ranked = sorted(scores, key=scores.get, reverse=True)
    best_three = ranked[:3]
    print("Best three stocks by return on made up data:")
    for name in best_three:
        print(f"  {name}: {scores[name]:.1%}")

    # Step 4: run three risk levels on the best three and compare.
    # The only difference is how much cash goes into each trade.
    risk_levels = {"aggressive": 1.0, "moderate": 0.6, "conservative": 0.3}
    print("\nRisk levels on the best three stocks, shown as average return:")
    for level, fraction in risk_levels.items():
        returns = []
        for name in best_three:
            final = backtest(stocks[name], cash_fraction=fraction)
            returns.append(total_return(final))
        avg = sum(returns) / len(returns)
        print(f"  {level}: {avg:.1%}")

    print("\nNote: these prices are made up, so these are not real returns.")


if __name__ == "__main__":
    main()
