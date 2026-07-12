# Strategy Specification: EMA Crossover with RSI Momentum Filter (GT Spec)

## 1. Entry Signal
A buy signal is triggered when the fast 9-period Exponential Moving Average (EMA9) crosses above the slow 21-period Exponential Moving Average (EMA21), representing a bullish trend shift, AND the 14-period Relative Strength Index (RSI14) is strictly above 50. This secondary filter ensures the crossover is backed by true buying momentum and is not a low-volume false breakout.

## 2. Exit Signal
A sell/exit signal is triggered when either of the following conditions is met:
1. The fast EMA9 crosses back below the slow EMA21, indicating a trend exhaustion.
2. The RSI14 drops below 40, signaling a sudden loss of bullish market momentum before the moving averages can mathematically cross.

## 3. Position Size
To maintain structural consistency for execution testing, the engine allocates a fixed lot size. The default configuration is locked to 1 unit per validated asset trade.

## 4. Stop-loss Rule
To preserve capital against sudden adverse market swings, a dynamic volatility-based stop-loss is deployed using the Average True Range (ATR). The trailing stop-loss is anchored at 2.0 times ATR14 below the entry execution price and adjusts upward with the price.

## 5. Target Instruments
The strategy targets high-liquidity assets from the NIFTY50 index. These are dynamically filtered and populated into the active watchlist via the backend's screening matrix to minimize execution slippages.

## 6. Timeframe
The underlying validation and backtesting engines evaluate price data streams on a Daily Bars (1D interval) timeframe to filter out intraday market noise.

## 7. Why This Combination?
Moving averages are lagging trend indicators that suffer heavily during sideways market phases. By combining the faster-reacting EMA crossover with the RSI momentum filter, the system filters out choppy consolidation periods, executing trades only when a directional trend has significant velocity.

## 8. Known Weaknesses
The primary weaknesses include vulnerability to sudden, violent macroeconomic reversals where price gaps down instantly, bypassing the historical ATR trailing threshold before the exit trigger can fire.
