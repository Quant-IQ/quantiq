# Strategy Specification Document: SMA Crossover (v1)
**Owner:** GT (Co-Lead / Quant Track)
**Status:** Draft for Review (Phase-3 / Issue #31)

---

## 1. Entry Signal
A long position (BUY) is triggered at the close of a daily trading session when the 20-period Simple Moving Average (SMA20) crosses completely above the 50-period Simple Moving Average (SMA50).

## 2. Exit Signal
An active long position is closed (SELL) immediately at the daily session close when the SMA20 crosses back below the SMA50. This acts as the standard indicator-driven regime switch exit.

## 3. Position Sizing
For version 1, a fixed lot allocation model is utilized. The system defaults to a baseline entry size of exactly 1 unit per validated trading signal. Capital scaling or dynamic risk sizing models are deferred to version v0.0.2.

## 4. Stop-Loss Rule
Risk management enforces a strict, dynamic ATR-based trailing stop-loss mechanism. Upon initial entry, an absolute protective floor is established at established at 1.5x ATR(14) below the execution fill price. The stop tracks higher alongside favorable price action but never adjusts downward.

## 5. Target Instruments
The strategy is executed exclusively across Indian equities listed on the National Stock Exchange (NSE). The asset universe is restricted to NIFTY50 liquid components filtered dynamically via the active screener pipeline module.

## 6. Timeframe
The underlying system loops exclusively on daily interval bars (1-day session closes). Intraday fractional trends are ignored to align with the core phase backtesting structures.

## 7. Why SMA Crossover?
This dual-moving average system serves as a transparent, mathematically unambiguous learning vehicle for programmatic alpha design. It provides a reliable benchmark for infrastructure validation, indicator library testing, and portfolio performance tracking.

## 8. Known Weaknesses
* **Whipsaws in Sideways Regimes:** The system generates frequent false breakthrough signals and cascading trade friction when target assets enter non-trending or range-bound execution patterns.
* **Lagging Nature:** Because simple moving averages weigh historical price metrics uniformly, entry and liquidation execution inherently suffer from mechanical trend confirmation delay.
