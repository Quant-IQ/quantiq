"""
SMA20/50 crossover strategy — the Phase 3 primary strategy (CLAUDE.md §11).

Owner: GT
File: src/strategy/sma_crossover.py
Phase: Phase-3

Reads SMA20/SMA50 columns off the df — does not compute them itself
(ADR-0002). Caller (strategy/runner.py) must run
``src.data.indicators.sma(df, windows=[20, 50])`` first.
"""

import logging
from typing import List

import pandas as pd

from src.strategy.base import Strategy
from src.strategy.signals import Signal

logger = logging.getLogger(__name__)


class SMACrossoverStrategy(Strategy):
	"""BUY when SMA20 crosses above SMA50, SELL when it crosses below."""

	@property
	def name(self) -> str:
		return "sma_crossover"

	def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
		"""Generate BUY/SELL signals on SMA20/SMA50 crossovers.

		Args:
			df (pd.DataFrame): Must contain ``ticker`` is not required as a
				column — pass one ticker's df at a time. Must contain
				``Close``, ``SMA20``, ``SMA50``, sorted ascending by date,
				with a ``ticker`` attribute supplied by the caller via
				``df.attrs["ticker"]`` (set by ``strategy/runner.py``).

		Returns:
			List[Signal]: One signal per bar where SMA20 crosses SMA50.
			Returns ``[]`` if required columns are missing or df has
			fewer than 2 rows (no crossover possible).
		"""
		required = {"Close", "SMA20", "SMA50"}
		missing = required - set(df.columns)
		if missing:
			logger.warning(
				"SMACrossoverStrategy.generate_signals: missing column(s) %s — returning []",
				missing,
			)
			return []

		if len(df) < 2:
			logger.info(
				"SMACrossoverStrategy.generate_signals: df has %d row(s), need >= 2 — returning []",
				len(df),
			)
			return []

		ticker = df.attrs.get("ticker", "UNKNOWN")
		signals: List[Signal] = []

		above = df["SMA20"] > df["SMA50"]
		crossed_up = above & ~above.shift(1, fill_value=above.iloc[0])
		crossed_down = ~above & above.shift(1, fill_value=above.iloc[0])

		for ts in df.index[crossed_up]:
			signals.append(
				Signal(
					ticker=ticker,
					action="BUY",
					price=float(df.loc[ts, "Close"]),
					reason="SMA20 crossed above SMA50",
					timestamp=ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts,
				)
			)

		for ts in df.index[crossed_down]:
			signals.append(
				Signal(
					ticker=ticker,
					action="SELL",
					price=float(df.loc[ts, "Close"]),
					reason="SMA20 crossed below SMA50",
					timestamp=ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts,
				)
			)

		signals.sort(key=lambda s: s.timestamp)
		return signals


if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example — fetch RELIANCE.NS, assemble SMA20/50, run the
	# real strategy. Edge cases live in tests/test_strategy_sma_crossover.py
	# (pytest), not here.
	try:
		from src.data.fetch import fetch_ohlc
		from src.data.indicators import sma
	except ImportError:
		sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
		from src.data.fetch import fetch_ohlc
		from src.data.indicators import sma

	TICKER = "RELIANCE.NS"
	logger.info("--- SMACrossoverStrategy example run: %s ---", TICKER)

	df = fetch_ohlc(TICKER, period="1y", interval="1d")
	if df is None:
		logger.error("Could not fetch %s — check network connection. Exiting.", TICKER)
		sys.exit(1)

	sma_result = sma(df, windows=[20, 50])
	if sma_result is not None:
		df = sma_result
	df.attrs["ticker"] = "RELIANCE"

	strat = SMACrossoverStrategy()
	signals = strat.generate_signals(df)
	logger.info("Signals over the last year: %d", len(signals))
	for sig in signals:
		logger.info("  %s", sig)

	logger.info("--- Example run complete ---")
