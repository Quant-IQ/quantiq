"""
RSI indicator wrapper for QuantIQ data pipeline.

Owner: AV (Quant lead) / RT / SS.
Wraps ta.momentum.RSIIndicator with project conventions.
"""

import pandas as pd
from ta.momentum import RSIIndicator


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


if __name__ == "__main__":
	import yfinance as yf

	df = yf.Ticker("RELIANCE.NS").history(period="3mo")
	print(rsi(df["Close"]).tail())
