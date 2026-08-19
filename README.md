# Algorithmic Trading Bot
 
This is my trading bot, one of my first real projects. I built it because I wanted to learn how automated trading actually works instead of just reading about it.
 
The idea is simple. The bot follows a moving average rule to decide when to buy and sell. It can test that rule on made up prices, or place practice trades through the Alpaca API with fake money.
 
This is a learning project, not financial advice. I am still learning, so I kept it honest and simple on purpose.
 
## The rule
 
Buy when the fast average rises above the slow average. Sell when it drops back below. Otherwise just hold and wait. That is the whole idea. The backtest uses daily prices, and the live bot uses 15 minute prices so it can react during the day.
 
## What it does
 
The backtest invents prices for 30 stocks, runs the rule on each one, keeps the best three, and then tries three risk levels on them. The only thing the risk level changes is how much cash goes into each trade, so aggressive earns the most but swings the hardest, and conservative plays it safe. The prices are made up, so these are not real returns. They just show me that all the pieces work together.
 
## Run the backtest
 
```
pip install -r requirements.txt
cd src
python trading_bot.py
```
 
## Paper trading
 
This is the part I am most excited about. The live script runs all the time in paper mode, which is fake money, on a spare computer I leave on. Every 15 minutes it checks the market, and when the market is open it looks at AAPL, MSFT, and SPY and trades only when the averages cross. Most of the time it just says no trade, and that is fine, that is the bot being patient. You need a free Alpaca account and your keys set as environment variables.
 
```
cd src
python live_trading.py
```
 
## The plan
 
I am going to let this run in paper mode for six months before I touch anything. I want to see if it can run reliably day after day without me babysitting it. Since it only buys one share of a few stocks, this is really testing whether I built the system right, not whether it makes money. After that I will take what I learned and start making it better. This is the beginning, not the finished thing.
 
## What's next
 
Things I want to add as I learn more:
 
1. Use real price history in the backtest instead of made up prices.
2. Give each risk level its own buy and sell rules, not just a different trade size.
3. Add a stop loss so a bad trade closes before it hurts too much.
4. Save a record of every check and trade so I can look back and learn from it.
5. Track the biggest drop along the way, not just the final number.
6. Draw a chart of the account value over time.
 
