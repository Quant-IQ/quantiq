"""
Screener runner — load config, fetch data, compute indicators, evaluate, cache.

Owner: AR
File: src/screener/runner.py
Phase: Phase-3

Per ADR-0002, indicator calculation happens here (the assembly point)
before evaluation — src/screener/engine.py never calculates indicators
itself, it only evaluates pre-computed columns.
"""

import logging
from datetime import date
from typing import List

from src.data.fetch import fetch_ohlc
from src.data.indicators import atr, rsi, sma
from src.data.ticker_map import get_yfinance_symbol
from src.screener.cache import load as cache_load
from src.screener.cache import save as cache_save
from src.screener.config import ScreenerConfig
from src.screener.engine import ScreeningEngine

logger = logging.getLogger(__name__)


def _assemble_indicators(df):
	"""Run the standard indicator set used by screener conditions.

	Computes SMA20/50, RSI, and ATR in sequence. Any indicator step that
	returns None (e.g. df too short) is skipped rather than aborting the
	whole pipeline — later columns simply won't be available, and
	conditions referencing them will fail closed in ``evaluate_ticker``.
	"""
	for fn in (lambda d: sma(d, windows=[20, 50]), rsi, atr):
		result = fn(df)
		if result is not None:
			df = result
	return df


def run(config: ScreenerConfig, use_cache: bool = True) -> List[str]:
	"""Run a screener config against its universe and return matching tickers.

	Args:
		config (ScreenerConfig): Screener definition — universe, conditions,
			logic mode.
		use_cache (bool): If True, check/populate the cache keyed by
			config name + today's date. Defaults to ``True``.

	Returns:
		List[str]: Ticker names (from ``config.universe``) that matched
		the screener's conditions. Tickers that fail to fetch or whose
		indicators can't be computed are skipped and logged — one bad
		ticker never aborts the run.
	"""
	today = date.today()

	if use_cache:
		cached = cache_load(config.name, today)
		if cached is not None:
			logger.info("Using cached results for '%s' (%s)", config.name, today)
			return cached

	engine = ScreeningEngine(logic_mode=config.logic_mode)
	matches: List[str] = []

	for ticker_name in config.universe:
		try:
			symbol = get_yfinance_symbol(ticker_name)
			df = fetch_ohlc(symbol)
			if df is None or df.empty:
				logger.warning("run: no data for '%s' — skipping", ticker_name)
				continue

			df = _assemble_indicators(df)
			if df is None or df.empty:
				logger.warning(
					"run: indicators could not be computed for '%s' — skipping", ticker_name
				)
				continue

			last_row = df.iloc[-1]
			if engine.evaluate_ticker(last_row, config.conditions):
				matches.append(ticker_name)

		except Exception as e:
			logger.error("run: unexpected error screening '%s': %s", ticker_name, e, exc_info=True)
			continue

	if use_cache:
		cache_save(config.name, today, matches)

	logger.info(
		"Screener '%s' matched %d/%d ticker(s)", config.name, len(matches), len(config.universe)
	)
	return matches


if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example — screen real NIFTY tickers for RSI oversold.
	# Edge cases live in tests/test_screener_runner.py (pytest), not here.
	logger.info("--- Screener runner example run ---")

	cfg = ScreenerConfig(
		name="rsi_oversold_demo",
		conditions=[{"metric": "RSI", "operator": "<", "value": 50}],
		universe=["RELIANCE", "TCS", "HDFCBANK"],
	)

	results = run(cfg, use_cache=False)
	logger.info("Tickers with RSI < 50 right now: %s", results or "(none)")
	logger.info("--- Example run complete ---")
