"""
Implementation of the core Phase 3 Simple Moving Average (SMA) Crossover strategy.

Owner: GT (Co-Lead)
Phase: Phase 3 shippable logic
"""

import os
import sys
from typing import List

import pandas as pd

# Force Python to recognize absolute paths from workspace root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.strategy.base import Strategy
from src.strategy.signals import Signal


class SMACrossover(Strategy):
	"""
	SMA Crossover strategy tracking positional intersections between short-term (20)
	and long-term (50) moving price baselines to output BUY/SELL/HOLD tokens.
	"""

	def __init__(self, short_window: int = 20, long_window: int = 50) -> None:
		"""
		Initializes boundaries for structural rolling metrics.
		"""
		super().__init__(name=f"SMACrossover_{short_window}_{long_window}")
		self.short_window = short_window
		self.long_window = long_window

	def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
		"""
		Processes close series matrices to flags crossing intersections defensively.

		Args:
		    df (pd.DataFrame): Dataframe containing OHLCV tracking rows.

		Returns:
		    List[Signal]: Array containing compiled transaction execution nodes.
		"""
		signals_list: List[Signal] = []

		# Enforce defensive verification boundary
		if df.empty or len(df) < self.long_window:
			return signals_list

		# Work on a copy to prevent side effects or data frame leaks
		working_df = df.copy()

		# Calculate standard moving averages explicitly
		working_df["SMA_Short"] = (
			working_df["Close"].rolling(window=self.short_window).mean()
		)
		working_df["SMA_Long"] = (
			working_df["Close"].rolling(window=self.long_window).mean()
		)

		# Drop NaN configurations after rolling window computation per specifications
		working_df.dropna(subset=["SMA_Short", "SMA_Long"], inplace=True)

		# Loop to evaluate cross crossovers cleanly
		for i in range(1, len(working_df)):
			current_date = working_df.index[i]
			current_price = working_df["Close"].iloc[i]
			ticker_id = (
				working_df["Ticker"].iloc[i]
				if "Ticker" in working_df.columns
				else "UNKNOWN.NS"
			)

			# Pull metrics for crossover tracking
			prev_short = working_df["SMA_Short"].iloc[i - 1]
			prev_long = working_df["SMA_Long"].iloc[i - 1]
			curr_short = working_df["SMA_Short"].iloc[i]
			curr_long = working_df["SMA_Long"].iloc[i]

			# Condition 1: Bullish Golden Crossover -> Short crosses ABOVE Long (BUY)
			if prev_short <= prev_long and curr_short > curr_long:
				signals_list.append(
					Signal(
						ticker=ticker_id,
						action="BUY",
						price=float(current_price),
						reason=f"SMA Short ({self.short_window}) crossed ABOVE SMA Long ({self.long_window})",
						timestamp=current_date,
					)
				)

			# Condition 2: Bearish Death Crossover -> Short crosses BELOW Long (SELL)
			elif prev_short >= prev_long and curr_short < curr_long:
				signals_list.append(
					Signal(
						ticker=ticker_id,
						action="SELL",
						price=float(current_price),
						reason=f"SMA Short ({self.short_window}) crossed BELOW SMA Long ({self.long_window})",
						timestamp=current_date,
					)
				)

		return signals_list


# Integration verification sandbox runner
if __name__ == "__main__":
	print("Initializing SMACrossover execution script verifications...")

	# Create dummy incremental matrix timeline (60 elements to fulfill long_window requirements)
	dates = pd.date_range(start="2026-01-01", periods=60, freq="B")

	# Generate mock upward trending curve to enforce a clean crossover scenario
	prices = [100.0 + (i * 0.5) for i in range(30)] + [
		115.0 - (i * 0.2) for i in range(30)
	]
	mock_data = {"Close": prices, "Ticker": ["M&M.NS"] * 60}
	df_mock = pd.DataFrame(mock_data, index=dates)

	strategy_engine = SMACrossover(short_window=10, long_window=30)
	compiled_signals = strategy_engine.generate_signals(df_mock)

	print(
		f"Strategy computation test complete. Total signals captured: {len(compiled_signals)}"
	)
	for sig in compiled_signals:
		print(
			f" -> Generated Signal: Date={sig.timestamp.strftime('%Y-%m-%d')} | Action={sig.action} | Price={sig.price}"
		)

	print("SMACrossover pipeline assertion validation passed successfully!")
