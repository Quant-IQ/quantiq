"""
Strategy runner — fetch, assemble indicators, run a strategy, collect signals.

Owner: GT
File: src/strategy/runner.py
Phase: Phase-3

This is the assembly point named in ADR-0002: it computes indicators via
src.data.indicators before handing the df to a Strategy, which only ever
reads pre-computed columns.
"""

import logging
from typing import List

from src.data.fetch import fetch_ohlc
from src.data.indicators import rsi, sma
from src.data.ticker_map import get_yfinance_symbol
from src.strategy.base import Strategy
from src.strategy.signals import Signal

logger = logging.getLogger(__name__)


def run(strategy: Strategy, tickers: List[str]) -> List[Signal]:
	"""Run a strategy against a list of tickers and collect all signals.

	Args:
		strategy (Strategy): Strategy instance (e.g. ``SMACrossoverStrategy``,
			``RSIMeanReversionStrategy``).
		tickers (List[str]): Ticker names (keys into ``ticker_map.TICKER_MAP``).

	Returns:
		List[Signal]: All signals from all tickers, in ticker order. A
		ticker that fails to fetch, fails indicator computation, or
		raises inside the strategy is logged and skipped — one bad
		ticker never aborts the whole run.
	"""
	all_signals: List[Signal] = []

	for ticker_name in tickers:
		try:
			symbol = get_yfinance_symbol(ticker_name)
			df = fetch_ohlc(symbol)
			if df is None or df.empty:
				logger.warning("run: no data for '%s' — skipping", ticker_name)
				continue

			sma_result = sma(df, windows=[20, 50])
			if sma_result is not None:
				df = sma_result

			rsi_result = rsi(df)
			if rsi_result is not None:
				df = rsi_result

			df.attrs["ticker"] = ticker_name

			signals = strategy.generate_signals(df)
			all_signals.extend(signals)

		except Exception as e:
			logger.error(
				"run: unexpected error running strategy '%s' on '%s': %s",
				strategy.name,
				ticker_name,
				e,
				exc_info=True,
			)
			continue

	logger.info(
		"Strategy '%s' produced %d signal(s) across %d ticker(s)",
		strategy.name,
		len(all_signals),
		len(tickers),
	)
	return all_signals


if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example — run both Phase-3 strategies across real tickers.
	# Edge cases live in tests/test_strategy_runner.py (pytest), not here.
	from src.strategy.rsi_mean_reversion import RSIMeanReversionStrategy
	from src.strategy.sma_crossover import SMACrossoverStrategy

	logger.info("--- Strategy runner example run ---")

	tickers = ["RELIANCE", "TCS", "HDFCBANK"]

	sma_signals = run(SMACrossoverStrategy(), tickers)
	logger.info("SMA crossover — %d signal(s) across %s", len(sma_signals), tickers)
	for sig in sma_signals[-3:]:
		logger.info("  %s", sig)

	rsi_signals = run(RSIMeanReversionStrategy(), tickers)
	logger.info("RSI mean-reversion — %d signal(s) across %s", len(rsi_signals), tickers)
	for sig in rsi_signals[-3:]:
		logger.info("  %s", sig)

	logger.info("--- Example run complete ---")
