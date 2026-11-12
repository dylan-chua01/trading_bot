# House rules

## My settings
These are the lines to change for a different market. Every prompt reads them from here.

* Bar size: daily. A "day" in these rules means one bar, so with hourly bars the 200-day line is the 200-bar line.
* Data: from 2020-07-01 through 2026-10-23, from Yahoo Finance through the yfinance library, adjusted for splits and dividends. yfinance treats the end date as exclusive, so pass the day after.
* Calendar: US stock market trading days for signals, trades and marking equity. Crypto trades every day; its weekend and holiday bars are kept for its indicators and its stops.
* Training: 2022-01-03 to 2024-12-31. Locked test: 2025-01-02 to 2026-10-23.
* Study tickers: SPY QQQ IWM DIA XLK XLF XLE XLV XLI XLY XLP XLU XLB XLC XLRE TLT IEF SHY BIL GLD SLV USO DBC BTC-USD ETH-USD SOL-USD.
* Market ticker: SPY. Its uptrend and downtrend days stand for the whole market.
* Engine candidates: SPY QQQ IWM DIA.
* Crypto candidates: BTC-USD ETH-USD SOL-USD.
* Crypto cap: no more than 25% of the portfolio in crypto at any time.
* Safe candidates: BIL SHY IEF TLT GLD.
* Cash ticker: BIL. Idle money sits in it, and every safe candidate has to beat it.
* Studied but never traded: none.
* Sleeve tickers: every study ticker except the cash ticker and the ones never traded.
* Broker: Alpaca. Crypto tickers trade there as BTC/USD, ETH/USD and SOL/USD.
* Cost: 0.05% of the traded value on every stock and ETF buy and sell; 0.25% on every crypto buy and sell.
* Fractional shares and fractional coins are allowed.
* Starting money: $1,000.

Data

* Research data lives in data/prices.parquet and stops at the end date in my settings, so results never change. Reuse it and only download tickers it doesn't have yet. After every download, print the rows, first date, last date and any missing days for each ticker.
* Missing days are checked against each ticker's own calendar: US trading days for stocks and ETFs, every calendar day for crypto.
* If the bar size is shorter than a day, check how much history the source has at that size before using the dates, and tell me if it falls short.
* The live bot downloads the same kind of bars through the latest close into data/live_prices.parquet. It never writes to data/prices.parquet.
* Crypto never stops trading, so its newest bar is always unfinished. The live bot only uses completed bars and drops any bar still forming.

Windows

* Every choice is made on the training window. The locked test runs once, after the choice is made, and nothing gets changed because of it.
* Data from before the training window only warms up the indicators.

Backtests

* Signals use data up to and including that day's close. Every buy and every sell fills at the next day's open and pays the cost in my settings.
* Signals and planned trades happen only on US trading days. Crypto bars from weekends and holidays are still kept, because crypto prices move then and stops can be hit then.
* Start with the starting money and mark equity at every US trading-day close, using each crypto's close from the same date. Fractional shares and coins are fine. Long only, no leverage.
* If price moves push crypto above the crypto cap in my settings, the excess is sold at the next open.
* Each window is its own run: start flat, act at the window's first open on the signal from the close before it, and value anything still open at the window's last close.
* A stop held at the broker fills at the stop price, or at the open if the day opens below it.
* Crypto stops are checked on every calendar day, weekends included. Alpaca only takes stop-limit orders for crypto, so a crypto stop has its limit 2% below the stop price. If the day opens below that limit, the stop does not fill and the position is sold at the next day's open.
* Nothing gets tested until the backtester has passed its checks on fake data, which results/engine_check.json records. The checks include a crypto stop hit on a weekend, a crypto stop that gaps past its limit, a crypto position that drifts over the cap, and a trade that sits across a weekend.
* Every test reports total return, return per year, max drawdown, return per drawdown, trades, win rate, average win, average loss, profit factor, average days held and time in market. Days held counts calendar days. Results are judged on return per drawdown.
* Every test also shows buy-and-hold SPY and buy-and-hold BTC-USD over the same window for comparison.

What words mean

* Bars per year: the number of bars in 252 trading days at my bar size, so 252 for daily bars. A crypto ticker's own measures use 365, because it has a bar every calendar day. Portfolio equity is marked on US trading days, so portfolio measures use 252.
* Return per year: (ending equity / starting equity) to the power of (bars per year / the run's bars), minus 1. Max drawdown: the largest fall from a peak in equity, using closes. Return per drawdown: return per year divided by the size of the max drawdown.
* Profit factor: the total profit of the winning trades divided by the total loss of the losing trades.
* Annualized return of a set of days: the average return of those days, close to close, times bars per year.
* Each ticker's indicators use its own bars. A crypto ticker has a bar every calendar day, so its 200-day line covers 200 calendar days.
* 200-day line: the 200-day simple moving average of the close. A ticker is above its line when that day's close is above that day's line. Signals use this.
* Uptrend day: a day whose previous close was above the previous day's line. Every other day is a downtrend day. Return measures use this, so a day's own move never decides its label. A crypto bar on a weekend or holiday takes the label of the last US trading day before it.
* RSI(2): the 2-period RSI with Wilder's smoothing.
* Wild day: its 20-day volatility (the standard deviation of the last 20 returns times the square root of bars per year) is above its own median over the previous year of bars (bars per year). Every other day is calm.

The system

* The rules the bot trades live in config/system.yaml. The core is whatever that file names: an engine, a safe asset and a line length. Cash means the cash ticker.
* The backtest and the bot import the same signal code from src/signals.py. Signal logic never lives in two places.
* The rules do the trading. AI judgment can only give the core a call of hold, the engine, the safe asset or cash, for 5, 10 or 20 days, and never touches the sleeves. Every call is saved the moment it comes back and never edited, and a live call only counts from the first open after it was saved.
* Paper trading only unless I say live in writing.
* Never open, print or log the .env file or any key.

How we work

* One job per prompt. If a prompt needs something from an earlier prompt that's missing, stop and tell me which prompt to run.
* A prompt that names a dashboard section writes it to dashboard/sections, reruns dashboard/build.py and opens dashboard/index.html. Every prompt ends with a short plain-English summary and its FINGERPRINT line, with percentages to one decimal and ratios to two.
* config/system.yaml only changes when a prompt says to write it, when the kill check switches a sleeve off, or when I say yes.
* No rule changes because of recent results. A change goes back through the full test process first.
* Scheduled reviews can fix code. They never change rules.
* Every idea that gets tested is counted, including the ones that fail.
