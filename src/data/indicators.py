"""
RSI indicator wrapper for QuantIQ data pipeline.
Owner: AV (Quant lead) / RT / SS.
Wraps ta.momentum.RSIIndicator with project conventions.
"""

import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """Calculate Relative Strength Index for a price series.

        Args:
     close (pd.Series): Closing price series indexed by datetime.
     window (int): RSI lookback period. Default 14 (industry standard).

        Returns:
           Returns:
    pd.Series: RSI values bounded [0, 100]. First (window) values will be NaN.
               Caller must call dropna() before backtest per CLAUDE.md §17.
    """

    return RSIIndicator(close=close, window=window).rsi()


"""
ATR indicator wrapper for QuantIQ data pipeline.
Owner: AV (Quant lead) / RT
Wraps ta.volatility.AverageTrueRange with project conventions.
"""


def atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    window: int = 14,
) -> pd.Series:
    """Calculate Average True Range (volatility indicator).

    Args:
        high (pd.Series): High price series.
        low (pd.Series): Low price series.
        close (pd.Series): Close price series.
        window (int): ATR period. Default 14.

    Returns:
        pd.Series: ATR values. All values >= 0 (volatility is non-negative). NaN prefix dropped.

    Example:
        df['ATR'] = atr(df['High'], df['Low'], df['Close'])
    """
    return AverageTrueRange(
        high=high, low=low, close=close, window=window
    ).average_true_range()


if __name__ == "__main__":
    import yfinance as yf

    df = yf.Ticker("RELIANCE.NS").history(period="3mo")
    print("--- RSI Output ---")
    print(rsi(df["Close"]).tail().dropna())
    print("\n--- ATR Output ---")
    print(atr(df["High"], df["Low"], df["Close"]).tail().dropna())
