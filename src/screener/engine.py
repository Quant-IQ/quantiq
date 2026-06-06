"""
Screener Evaluation Engine
Owner: AR (Dev Lead) | Phase 3 Target Module
"""

import logging
from typing import Any, Dict, List

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

	# Mock data payload row mimicking data engineering pipeline outputs
	mock_row = pd.Series({"RSI": 28.5, "SMA20": 2450.0, "SMA50": 2400.0})

	# Target criteria matrix
	test_conditions = [
		{"metric": "RSI", "operator": "<", "value": 30.0},
		{
			"metric": "SMA20",
			"operator": ">",
			"value": 2400.0,
		},  # Fixed: Comparing float against float
	]

	test_engine = ScreeningEngine(logic_mode="AND")
	is_match = test_engine.evaluate_ticker(mock_row, test_conditions)
	logger.info("Smoke test complete. Asset verification signature: %s", is_match)
