"""
Technical indicators module.

Owner: AK
File: src/data/indicators.py
Phase: Phase-2

Provides Series-to-Series technical indicator functions used by the
screening and analytics pipeline.
"""

import logging

import pandas as pd
from ta.trend import EMAIndicator

logger = logging.getLogger(__name__)


def ema(close: pd.Series, window: int) -> pd.Series:
	"""
	Calculate Exponential Moving Average (EMA).

	Args:
	close: Series containing closing prices.
	window: EMA lookback period. Must be greater than 0.

	Returns:
	pd.Series: EMA values with NaN rows removed.

	Raises:
	ValueError: If window is less than or equal to 0.
	TypeError: If close is not a pandas Series.

	Example:
	>>> ema_series = ema(close, window=20)
	>>> ema_series.tail()
	"""
	if not isinstance(close, pd.Series):
		raise TypeError("close must be a pandas Series")

	if window <= 0:
		raise ValueError("window must be greater than 0")

	logger.debug("Calculating EMA with window=%s", window)

	ema_series = EMAIndicator(close=close, window=window).ema_indicator()

	return ema_series.dropna()


if __name__ == "__main__":
	sample_close = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109])

	result = ema(sample_close, window=3)
	logger.info("EMA smoke test completed. Rows=%d", len(result))
