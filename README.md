# Algorithmic Trading Bot

A simple stock trading bot in Python. It uses a moving average rule to decide when to buy and sell. It can run on made up prices to test the idea, or place practice trades through the Alpaca API with fake money.

This is a learning project, not financial advice.

## The rule

Buy when the fast average rises above the slow average. Sell when it falls back below. Otherwise hold and do nothing. The backtest uses daily prices. The live bot uses 15 minute prices so it can react during the day.

## What it does

The backtest makes prices for 30 stocks, tests the rule on each, keeps the best three, and runs them at three risk levels. The risk level only changes how much cash goes into each trade, so aggressive earns the most and swings the most, while conservative stays calmer. Because the prices are made up, these are not real returns. They only show that the parts work.

## Run the backtest

```
pip install -r requirements.txt
cd src
python trading_bot.py
```

## Paper trading

The live script runs all the time in paper mode, which is fake money, on a spare computer. It checks the market every 15 minutes. When the market is open it looks at recent 15 minute bars for AAPL, MSFT, and SPY and trades only when the averages cross, so most checks will say no trade. US stocks only trade during market hours, so when the market is closed the bot just waits. It needs a free Alpaca account, with the keys set as environment variables.

```
cd src
python live_trading.py
```

## The plan

I am running this in paper mode for six months before I change anything. The point of that time is to see if the bot runs reliably day after day: it places orders correctly, handles the market being closed, and keeps going. Since it only buys one share of a few stocks, this mostly tests whether the system works, not whether it makes real money. After six months I will use what I learned to improve the rules and slowly build it into a bigger and better platform.

## What's next

These are the changes I plan to make after the six months of paper trading:

1. Use real price history in the backtest instead of made up prices.
2. Give each risk level its own buy and sell rules, not just a different trade size.
3. Add a stop loss so a losing trade closes before it gets too big.
4. Save a record of every check and trade so I can review what happened.
5. Track the biggest drop along the way, not just the final money.
6. Draw a chart of the account value over time.
