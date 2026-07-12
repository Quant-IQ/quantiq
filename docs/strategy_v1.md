# Plain-English Strategy Specification: SMA Crossover

## 1. Entry Signal
A buy signal is triggered when the short-term 20-period Simple Moving Average (SMA20) crosses above the long-term 50-period Simple Moving Average (SMA50). This indicates a shift toward bullish macro momentum.

## 2. Exit Signal
A sell signal is triggered when the SMA20 crosses below the SMA50. This crossover acts as the primary tool to capture trend reversals and exit the position.

## 3. Position Size
The execution engine allocates a fixed lot size for every trade execution. By default, this is configured to 1 unit per validated trade.

## 4. Stop-loss Rule
To protect capital against unexpected market drops, an Average True Range (ATR) based trailing stop-loss is deployed. It is set at 1.5x ATR14 from the entry execution price.

## 5. Target Instruments
The strategy target universe consists of liquid NIFTY50 stocks, which are dynamically populated via the system's live screener watchlist filter.

## 6. Timeframe
The underlying evaluation system processes market data on a Daily Bars (1D interval) timeframe.

## 7. Why SMA Crossover?
This dual moving average mechanism is simple, mathematical, and highly interpretable. It serves as an excellent foundational learning vehicle for testing core execution loops.

## 8. Known Weaknesses
The primary weaknesses include heavy whipsaws and false entry triggers in choppy, sideways markets, as well as the inherent mathematical lag typical of moving average calculations.
