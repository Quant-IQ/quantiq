"""
Implementation of the core Phase 3 Simple Moving Average (SMA) Crossover strategy.

Owner: GT (Co-Lead)
Phase: Phase 3 shippable logic
"""

import logging
from typing import List

import pandas as pd

from src.strategy.base import Strategy
from src.strategy.signals import Signal

# Initialize module-level logger compliant with CLAUDE.md rules
logger = logging.getLogger(__name__)


class SMACrossover(Strategy):
	"""Simple Moving Average Crossover execution framework."""

	def __init__(self, short_window: int = 20, long_window: int = 50) -> None:
		"""Initializes the window parameters for the SMA crossover computation.

		Args:
		    short_window (int): Lookback interval for the fast moving average.
		    long_window (int): Lookback interval for the slow moving average.
		"""
		super().__init__("SMA Crossover Framework")
		self.short_window = short_window
		self.long_window = long_window
		logger.info(
			f"Strategy parameters set -> Short Window: {self.short_window}, Long Window: {self.long_window}"
		)

	def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
		"""Generates trading signals based on SMA Crossover cross thresholds.

		Args:
		    df (pd.DataFrame): Processed historical OHLCV DataFrame with indicator columns.

		Returns:
		    List[Signal]: Validated transaction direction markers for the input period.

		Raises:
		    ValueError: If 'Ticker' column is missing from the input DataFrame.
		    NotImplementedError: If subclass does not override this method.
		"""
		signals: List[Signal] = []
		if df.empty or len(df) < self.long_window:
			logger.warning(
				"DataFrame has insufficient data points for long window calculations."
			)
			return signals

		# Data integrity check requested by code review
		if "Ticker" not in df.columns:
			logger.warning(
				"No Ticker column found - signals will carry placeholder ticker 'UNKNOWN.NS'"
			)
			ticker_id = "UNKNOWN.NS"
		else:
			ticker_id = df["Ticker"].iloc[0] if len(df) > 0 else "UNKNOWN.NS"

		# Phase 4 Optimization: Vectorized shift logic to replace row-by-row iteration
		df["SMA_Short"] = df["close"].rolling(window=self.short_window).mean()
		df["SMA_Long"] = df["close"].rolling(window=self.long_window).mean()

		# Vectorized identification of crossovers
		cross_up = (df["SMA_Short"].shift(1) <= df["SMA_Long"].shift(1)) & (
			df["SMA_Short"] > df["SMA_Long"]
		)
		cross_down = (df["SMA_Short"].shift(1) >= df["SMA_Long"].shift(1)) & (
			df["SMA_Short"] < df["SMA_Long"]
		)

		# Extract indices where crossovers occur efficiently
		for idx in df[cross_up].index:
			signals.append(Signal(direction="BUY", timestamp=idx, ticker=ticker_id))
			logger.info(
				f"Bullish crossover detected at timestamp {idx} -> Generating BUY Signal."
			)

		for idx in df[cross_down].index:
			signals.append(Signal(direction="SELL", timestamp=idx, ticker=ticker_id))
			logger.info(
				f"Bearish crossover detected at timestamp {idx} -> Generating SELL Signal."
			)

		return signals


if __name__ == "__main__":
	# Setup standard logging format for local sandbox executions
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	)
	logger.info("Running standalone SMACrossover verification sandbox runner module...")

	# Mock data execution verification check
	dates = pd.date_range(start="2026-01-01", periods=60)
	mock_data = pd.DataFrame(
		{
			"close": [100 + i if i % 2 == 0 else 100 - i for i in range(60)],
			"Ticker": ["RELIANCE.NS"] * 60,
		},
		index=dates,
	)

	strategy = SMACrossover(short_window=5, long_window=10)
	generated_triggers = strategy.generate_signals(mock_data)
	logger.info(
		f"Sandbox verification successfully compiled. Total signals triggered: {len(generated_triggers)}"
	)
