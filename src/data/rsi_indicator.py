import pandas as pd
from ta.momentum import RSIIndicator
def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """Calculate Relative Strength Index for a price series.

    Args:
        close (pd.Series): Closing price series indexed by datetime.
        window (int): RSI lookback period. Default 14 (industry standard).

    Returns:
        pd.Series: RSI values bounded [0, 100]. First (window) values NaN, dropped.
    """
    return RSIIndicator(close=close, window=window).rsi().dropna()
