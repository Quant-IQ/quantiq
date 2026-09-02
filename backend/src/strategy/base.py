"""
Strategy base class — pure signal generation from a pre-assembled DataFrame.

Owner: GT
File: src/strategy/base.py
Phase: Phase-3

Per ADR-0002 (grill session, 21 Jun 2026), strategies never calculate their
own indicators. The df passed to ``generate_signals`` is assembled upstream
by ``strategy/runner.py`` (fetch -> indicators.py -> strategy) and already
carries every column the strategy needs (e.g. SMA20, SMA50, RSI). This keeps
strategies trivially unit-testable — inject a df with known columns, assert
signals — and keeps indicators.py the one place indicators are computed.
"""

import logging
from abc import ABC, abstractmethod
from typing import List

import pandas as pd

from src.strategy.signals import Signal

logger = logging.getLogger(__name__)


class Strategy(ABC):
	"""Abstract base for all strategies. Subclasses implement pure functions
	from an indicator-bearing DataFrame to a list of Signals."""

	@property
	@abstractmethod
	def name(self) -> str:
		"""Short, stable identifier for this strategy, e.g. ``"sma_crossover"``."""
		raise NotImplementedError

	@abstractmethod
	def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
		"""Generate signals from an already-indicator-assembled DataFrame.

		Args:
			df (pd.DataFrame): OHLCV + indicator columns, sorted ascending
				by date. The exact indicator columns required depend on
				the subclass (e.g. SMA20/SMA50 for crossover, RSI for
				mean-reversion) — callers must assemble these before
				calling, this method must not compute them itself.

		Returns:
			List[Signal]: Zero or more signals, one per bar where the
			strategy's entry/exit condition fired. Returns ``[]`` if the
			df is too short or no condition fired — never raises on
			ordinary "no signal" cases.
		"""
		raise NotImplementedError


if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example — use the real SMACrossoverStrategy (a concrete
	# subclass of this ABC) against real fetched + indicator-assembled
	# data, to show the contract end-to-end. Edge cases for the ABC
	# itself live in tests/test_strategy_base.py (pytest), not here.
	try:
		from src.data.fetch import fetch_ohlc
		from src.data.indicators import sma
		from src.strategy.sma_crossover import SMACrossoverStrategy
	except ImportError:
		sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
		from src.data.fetch import fetch_ohlc
		from src.data.indicators import sma
		from src.strategy.sma_crossover import SMACrossoverStrategy

	TICKER = "RELIANCE.NS"
	logger.info("--- Strategy ABC example run: %s via SMACrossoverStrategy ---", TICKER)

	df = fetch_ohlc(TICKER, period="1y", interval="1d")
	if df is None:
		logger.error("Could not fetch %s — check network connection. Exiting.", TICKER)
		sys.exit(1)

	sma_result = sma(df, windows=[20, 50])
	if sma_result is not None:
		df = sma_result
	df.attrs["ticker"] = "RELIANCE"

	strategy: Strategy = SMACrossoverStrategy()
	logger.info("Strategy name (from ABC property): %s", strategy.name)

	signals = strategy.generate_signals(df)
	logger.info("Signals generated: %d", len(signals))
	for sig in signals[-3:]:
		logger.info("  %s", sig)

	logger.info("--- Example run complete ---")
