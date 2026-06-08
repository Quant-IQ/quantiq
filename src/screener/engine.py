"""
Screener Evaluation Engine
Owner: AR (Dev Lead) | Phase 3 Target Module
"""

import logging
from typing import Any, Dict, List, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


class ScreeningEngine:
	"""Evaluates multi-conditional logic (AND/OR) across market data streams."""

	def __init__(self, logic_mode: str = "AND"):
		"""
		Initializes the evaluation engine with a specific logical gateway mode.

		Args:
		    logic_mode (str): Operational criteria evaluation method ('AND' or 'OR').
		"""
		self.logic_mode = logic_mode.upper()
		if self.logic_mode not in {"AND", "OR"}:
			raise ValueError("logic_mode must be either 'AND' or 'OR'")

	@staticmethod
	def calculate_rsi(data: pd.DataFrame, window: int = 14) -> pd.Series:
		"""
		Calculate Relative Strength Index (RSI) using Wilders Smoothing Technique.

		Args:
		    data (pd.DataFrame): Dataframe containing a clean 'Close' price column.
		    window (int): The lookback analytics period baseline. Defaults to 14.

		Returns:
		    pd.Series: Vector array series containing the calculated RSI metrics.
		"""
		if "Close" not in data.columns:
			raise KeyError(
				"Input DataFrame must contain a valid 'Close' price vector column."
			)

		delta = data["Close"].diff()
		gain = (delta.where(delta > 0, 0)).ewm(alpha=1 / window, adjust=False).mean()
		loss = (-delta.where(delta < 0, 0)).ewm(alpha=1 / window, adjust=False).mean()

		# Mitigate flat trend division bounds securely
		rs = gain / loss.replace(0, float("inf"))
		rsi = 100 - (100 / (1 + rs))
		return rsi

	@staticmethod
	def calculate_macd(
		data: pd.DataFrame,
		fast_period: int = 12,
		slow_period: int = 26,
		signal_period: int = 9,
	) -> Tuple[pd.Series, pd.Series, pd.Series]:
		"""
		Calculate Moving Average Convergence Divergence (MACD) parameters.

		Args:
		    data (pd.DataFrame): Dataframe containing a clean 'Close' price column.
		    fast_period (int): Short-term line calculation lookback. Defaults to 12.
		    slow_period (int): Long-term line calculation lookback. Defaults to 26.
		    signal_period (int): Smoothing line baseline trigger calculation. Defaults to 9.

		Returns:
		    Tuple[pd.Series, pd.Series, pd.Series]: (macd_line, signal_line, macd_histogram)
		"""
		if "Close" not in data.columns:
			raise KeyError(
				"Input DataFrame must contain a valid 'Close' price vector column."
			)

		ema_fast = data["Close"].ewm(span=fast_period, adjust=False).mean()
		ema_slow = data["Close"].ewm(span=slow_period, adjust=False).mean()

		macd_line = ema_fast - ema_slow
		signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
		macd_histogram = macd_line - signal_line

		return macd_line, signal_line, macd_histogram

	def evaluate_ticker(
		self, ticker_data: pd.Series, conditions: List[Dict[str, Any]]
	) -> bool:
		"""
		Evaluate a single ticker's metrics against a list of filter conditions.

		Args:
		    ticker_data (pd.Series): Combined technical/fundamental values for an asset.
		    conditions (List[Dict[str, Any]]): Dict list containing 'metric', 'operator', and 'value'.
		        Example: [{'metric': 'RSI', 'operator': '<', 'value': 30}]

		Returns:
		    bool: True if the asset complies with the criteria validation rules.
		"""
		if not conditions:
			return False

		results = []
		for cond in conditions:
			metric = cond.get("metric")
			operator = cond.get("operator")
			target_val = cond.get("value")

			if metric not in ticker_data:
				logger.warning(
					"Metric %s missing from provided data tracking row.", metric
				)
				results.append(False)
				continue

			current_val = ticker_data[metric]

			try:
				# Dynamic conditional logic gate evaluation
				if operator == ">":
					results.append(current_val > target_val)
				elif operator == "<":
					results.append(current_val < target_val)
				elif operator == "==":
					results.append(current_val == target_val)
				else:
					logger.error(
						"Unsupported rule parsing operator encountered: %s", operator
					)
					results.append(False)
			except Exception as e:
				logger.error(
					"Type comparison failed for metric %s with value %s: %s",
					metric,
					target_val,
					e,
				)
				results.append(False)

		if self.logic_mode == "AND":
			return all(results)
		return any(results)


if __name__ == "__main__":
	# Internal Smoke Test / Sanity Check to confirm operational integrity
	logging.basicConfig(level=logging.INFO)
	logger.info("Running ScreeningEngine internal smoke test pipeline...")

	# Mock historical data framing block to verify mathematical helpers
	mock_df = pd.DataFrame(
		{"Close": [100.0, 102.0, 101.0, 105.0, 107.0, 106.0, 108.0] * 5}
	)

	rsi_output = ScreeningEngine.calculate_rsi(mock_df)
	macd_l, signal_l, hist_l = ScreeningEngine.calculate_macd(mock_df)

	logger.info("Indicator calculations compiled successfully.")
	logger.info("Current baseline testing RSI sample value: %s", rsi_output.iloc[-1])

	# Mock data payload row mimicking data engineering pipeline outputs
	mock_row = pd.Series({"RSI": 28.5, "SMA20": 2450.0, "SMA50": 2400.0})

	# Target criteria matrix
	test_conditions = [
		{"metric": "RSI", "operator": "<", "value": 30.0},
		{"metric": "SMA20", "operator": ">", "value": 2400.0},
	]

	test_engine = ScreeningEngine(logic_mode="AND")
	is_match = test_engine.evaluate_ticker(mock_row, test_conditions)
	logger.info("Smoke test complete. Asset verification signature: %s", is_match)
