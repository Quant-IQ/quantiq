"""
Fundamental screener filters — P/E, D/E, ROE via yf.Ticker.info.

Owner: AV
File: src/screener/filters/fundamental.py
Phase: Phase-3

yf.Ticker.info is an unofficial, unstructured dict — fields are frequently
missing or None depending on the ticker and data availability. Every
lookup here is None-guarded; a missing field means the filter excludes
the ticker (fails closed) rather than raising.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def _safe_get(info: Dict[str, Any], key: str) -> Optional[float]:
	"""Fetch a numeric field from yf.Ticker.info, returning None on absence."""
	value = info.get(key)
	if value is None:
		return None
	try:
		return float(value)
	except (TypeError, ValueError):
		logger.warning("_safe_get: field '%s' present but not numeric: %r", key, value)
		return None


def pe_below(info: Dict[str, Any], threshold: float) -> bool:
	"""True if trailing P/E is below ``threshold``.

	Args:
		info (Dict[str, Any]): Result of ``yf.Ticker(ticker).info``.
		threshold (float): Upper P/E bound.

	Returns:
		bool: ``False`` if ``trailingPE`` is missing or non-numeric
		(fails closed — an unknown P/E never passes a "cheap stock" filter).
	"""
	pe = _safe_get(info, "trailingPE")
	if pe is None:
		logger.warning("pe_below: 'trailingPE' missing — excluding ticker")
		return False
	return pe < threshold


def debt_to_equity_below(info: Dict[str, Any], threshold: float) -> bool:
	"""True if debt-to-equity ratio is below ``threshold``.

	Args:
		info (Dict[str, Any]): Result of ``yf.Ticker(ticker).info``.
		threshold (float): Upper D/E bound. Note ``yfinance`` reports
			``debtToEquity`` as a percentage (e.g. ``45.2`` means 45.2%,
			not 0.452) — callers should pass thresholds in the same scale.

	Returns:
		bool: ``False`` if ``debtToEquity`` is missing or non-numeric.
	"""
	de = _safe_get(info, "debtToEquity")
	if de is None:
		logger.warning("debt_to_equity_below: 'debtToEquity' missing — excluding ticker")
		return False
	return de < threshold


def roe_above(info: Dict[str, Any], threshold: float) -> bool:
	"""True if return on equity is above ``threshold``.

	Args:
		info (Dict[str, Any]): Result of ``yf.Ticker(ticker).info``.
		threshold (float): Lower ROE bound. ``yfinance`` reports
			``returnOnEquity`` as a decimal fraction (e.g. ``0.15`` = 15%).

	Returns:
		bool: ``False`` if ``returnOnEquity`` is missing or non-numeric.
	"""
	roe = _safe_get(info, "returnOnEquity")
	if roe is None:
		logger.warning("roe_above: 'returnOnEquity' missing — excluding ticker")
		return False
	return roe > threshold


if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example — pull live fundamentals for RELIANCE.NS via
	# yf.Ticker.info and run every filter against the real values.
	# Edge cases live in tests/test_screener_filters_fundamental.py
	# (pytest), not here.
	import yfinance as yf

	TICKER = "RELIANCE.NS"
	logger.info("--- Fundamental filters example run: %s ---", TICKER)

	info = yf.Ticker(TICKER).info
	logger.info(
		"Real fields — trailingPE=%s | debtToEquity=%s | returnOnEquity=%s",
		info.get("trailingPE"),
		info.get("debtToEquity"),
		info.get("returnOnEquity"),
	)

	logger.info("pe_below(25): %s", pe_below(info, 25))
	logger.info("debt_to_equity_below(100): %s", debt_to_equity_below(info, 100))
	logger.info("roe_above(0.10): %s", roe_above(info, 0.10))
	logger.info("--- Example run complete ---")
