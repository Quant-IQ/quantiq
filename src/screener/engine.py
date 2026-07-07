"""
Screener Evaluation Engine
Owner: AR (Dev Lead) | Phase 3 Target Module

Design Decision (ADR-0002, 21 Jun 2026):
This module evaluates pre-computed indicator columns only. It does not
calculate RSI, MACD, or any other indicator itself — src/data/indicators.py
is the sole place indicators are calculated project-wide, so screener and
strategy code never silently diverge from each other on indicator values.
Callers must run the relevant indicators.py functions and merge their
columns into the row passed to evaluate_ticker().
"""

import logging
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


class ScreeningEngine:
	"""Evaluates multi-conditional logic (AND/OR) across market data streams."""

	def __init__(self, logic_mode: str = "AND"):
		"""Initializes the evaluation engine with a specific logical gateway mode.

		Args:
		    logic_mode (str): Operational criteria evaluation method ('AND' or
		      'OR').
		"""
		self.logic_mode = logic_mode.upper()
		if self.logic_mode not in {"AND", "OR"}:
			raise ValueError("logic_mode must be either 'AND' or 'OR'")

	def evaluate_ticker(
		self, ticker_data: pd.Series, conditions: List[Dict[str, Any]]
	) -> bool:
		"""Evaluate a single ticker's metrics against a list of filter conditions.

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
				# Fixes Issue 3 (CONCERN): Added relational boundary operator conditions
				if operator == ">":
					results.append(current_val > target_val)
				elif operator == "<":
					results.append(current_val < target_val)
				elif operator == "==":
					results.append(current_val == target_val)
				elif operator == ">=":
					results.append(current_val >= target_val)
				elif operator == "<=":
					results.append(current_val <= target_val)
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
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example — fetch a live ticker, compute real indicators via
	# src.data.indicators (ADR-0002: engine never calculates indicators
	# itself), then evaluate the latest real row. Edge cases live in
	# tests/test_screener_engine.py (pytest), not here.
	try:
		from src.data.fetch import fetch_ohlc
		from src.data.indicators import rsi, sma
	except ImportError:
		sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
		from src.data.fetch import fetch_ohlc
		from src.data.indicators import rsi, sma

	TICKER = "RELIANCE.NS"
	logger.info("--- Screener engine example run: %s ---", TICKER)

	df = fetch_ohlc(TICKER, period="1y", interval="1d")
	if df is None:
		logger.error("Could not fetch %s — check network connection. Exiting.", TICKER)
		sys.exit(1)

	for fn in (lambda d: sma(d, windows=[20, 50]), rsi):
		result = fn(df)
		if result is not None:
			df = result

	latest_row = df.iloc[-1]
	logger.info(
		"Latest real values — RSI=%.1f | SMA20=%.2f | SMA50=%.2f",
		latest_row.get("RSI", float("nan")),
		latest_row.get("SMA20", float("nan")),
		latest_row.get("SMA50", float("nan")),
	)

	conditions = [
		{"metric": "RSI", "operator": "<", "value": 50.0},
		{"metric": "SMA20", "operator": "<", "value": latest_row.get("SMA50", float("inf"))},
	]
	engine = ScreeningEngine(logic_mode="AND")
	is_match = engine.evaluate_ticker(latest_row, conditions)
	logger.info(
		"Condition: RSI<50 AND SMA20<SMA50 (AND mode) — matched: %s", is_match
	)
	logger.info("--- Example run complete ---")
