## 1. RSI Mean Reversion (Intermediate Regime)

### Comprehensive Study

The Relative Strength Index (RSI) is a velocity oscillator that measures
the speed and change of price movements. The fundamental theory behind
why it works is **structural market overreaction**. In liquid markets
like the NIFTY50, institutional algorithms and retail panic often push
stock prices to short-term extremes due to sudden news, liquidity
vacuums, or momentum chasing.

When the RSI reaches an extreme oversold level, it mathematically
signifies that down-days have overwhelmingly dominated up-days to a
point that is statistically unsustainable without a corrective bounce.
QuantIQ exploits this by buying the asset exactly when the selling
pressure exhausts itself, catching the rubber-band snapback as price
returns to its moving equilibrium.

### Specification Blueprint

-   **Entry signal** - `RSI(14)` crosses below 30 = **BUY**
-   **Exit signal** - `RSI(14)` crosses above 70 = **SELL**
-   **Position size** - fixed lot (Default 1 unit)
-   **Stop-loss rule** - ATR-based trailing stop (1.5x ATR14 from entry)
-   **Target instruments** - NIFTY50 stocks via dynamic watchlist from
    screener
-   **Timeframe** - daily bars (1d interval)
-   **Why RSI Mean Reversion?** - Highly effective in range-bound,
    sideways market regimes where price regularly cycles between clear
    horizontal support and resistance thresholds.
-   **Known weaknesses** - Highly prone to "catching a falling knife" if
    a stock experiences a fundamental structural shift, keeping the RSI
    deeply oversold (`< 30`) while the price continuously plummets.

------------------------------------------------------------------------

## 2. MACD Histogram Strategy (Momentum-Trend Hybrid)

### Comprehensive Study

The Moving Average Convergence Divergence (MACD) Histogram measures the
distance between the fast MACD line (12-period EMA minus 26-period EMA)
and its signal line (9-period EMA). Why does this work for an automated
system? Because it tracks **momentum acceleration**.

While normal moving average crossovers lag heavily, the histogram
functions as a derivative of price speed. When the histogram crosses
above the zero line, it indicates that short-term buying momentum is
accelerating faster than macro trends. For QuantIQ, this acts as an
early warning system to catch explosive new macro trends right at their
genesis point rather than waiting for slow, lagging confirmations.

### Specification Blueprint

-   **Entry signal** - `MACD Histogram (12, 26, 9)` crosses above 0 =
    **BUY**
-   **Exit signal** - `MACD Histogram (12, 26, 9)` crosses below 0 =
    **SELL**
-   **Position size** - fixed lot (Default 1 unit)
-   **Stop-loss rule** - ATR-based trailing stop (1.5x ATR14 from entry)
-   **Target instruments** - NIFTY50 stocks via dynamic watchlist from
    screener
-   **Timeframe** - daily bars (1d interval)
-   **Why MACD Histogram?** - Bridges the gap between pure
    trend-following and momentum, alerting the engine to structural
    shifts earlier than standard moving averages.
-   **Known weaknesses** - Whipsaws relentlessly in choppy, tight
    sideways ranges where the histogram frequently flickers above and
    below zero without establishing directional continuation.

------------------------------------------------------------------------

## 3. Bollinger Bands + RSI Combo (Advanced Production Baseline)

### Comprehensive Study

This strategy relies on **multi-factor confluence filtering**. Bollinger
Bands represent a dynamic pricing channel wrapped around a 20-period
simple moving average, set at ±2 standard deviations. Statistically, 95%
of price action should contained within these bands.

Standalone indicators are prone to high failure rates. However, by
marrying volatility channels with momentum indicators, QuantIQ forces a
dual-gate condition: price must touch the lower band (a statistical
price extreme) **at the exact same time** that the RSI drops below 30 (a
momentum exhaustion extreme). This drastically removes system noise by
verifying that an asset is structurally overextended from both a
volatility standpoint and a velocity standpoint before risking
production capital.

### Specification Blueprint

-   **Entry signal** - Close price touches/breaches
    `Lower Bollinger Band (20, 2σ)` **AND** `RSI(14) < 30` = **BUY**
-   **Exit signal** - Close price touches/breaches
    `Upper Bollinger Band (20, 2σ)` **OR** `RSI(14) > 70` = **SELL**
-   **Position size** - fixed lot (Default 1 unit)
-   **Stop-loss rule** - ATR-based trailing stop (1.5x ATR14 from entry)
-   **Target instruments** - NIFTY50 stocks via dynamic watchlist from
    screener
-   **Timeframe** - daily bars (1d interval)
-   **Why Bollinger Bands + RSI?** - It creates a robust,
    institutional-grade filter that protects capital by weeding out
    false mean-reversion signals in aggressive macro trends.
-   **Known weaknesses** - Low signal frequency. Because both conditions
    must align perfectly, the engine will frequently pass on trades
    during prolonged, steady macro trends that rise without hitting
    mathematical volatility extremes.

------------------------------------------------------------------------

## 4. Ichimoku Cloud Strategy (Institutional Trend-Following)

### Comprehensive Study

The Ichimoku Kinko Hyo system is a complete multi-timeframe trend
forecasting mechanism. Unlike simple moving averages that only calculate
close prices, Ichimoku utilizes the midpoints of historical highs and
lows (`Tenkan-sen` and `Kijun-sen`), providing a truer reflection of
**equilibrium pricing**.

The fundamental engine component, the `Kumo Cloud`, projects dynamic
support and resistance forward into the future based on past volatility
boundaries. When price breaks cleanly out of the cloud and the fast line
crosses over the slow line, it confirms that market equilibrium has
fundamentally shifted into a strong, sustained macro trend. It works for
automated production systems because it ensures you are always aligned
with the dominant institutional trend flow.

### Specification Blueprint

-   **Entry signal** - `Tenkan-sen` crosses above `Kijun-sen` **AND**
    closing price is strictly above the `Kumo Cloud` = **BUY**
-   **Exit signal** - `Tenkan-sen` crosses below `Kijun-sen` **OR**
    closing price breaks below the `Kumo Cloud` = **SELL**
-   **Position size** - fixed lot (Default 1 unit)
-   **Stop-loss rule** - ATR-based trailing stop (1.5x ATR14 from entry)
-   **Target instruments** - NIFTY50 stocks via dynamic watchlist from
    screener
-   **Timeframe** - daily bars (1d interval)
-   **Why Ichimoku Cloud?** - A visual and programmatic powerhouse for
    macro trend retention, keeping the production engine safe from
    mid-trend minor pullbacks.
-   **Known weaknesses** - Highly complex matrix parameter logic that
    creates substantial execution lag, resulting in heavy signal decay
    if price gets stuck inside the cloud itself.
