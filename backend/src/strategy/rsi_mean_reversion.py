"""
RSI mean-reversion strategy — BUY oversold, SELL overbought.

Owner: AV
File: src/strategy/rsi_mean_reversion.py
Phase: Phase-3

Reads the RSI column off the df — does not compute it itself (ADR-0002).
Caller (strategy/runner.py) must run ``src.data.indicators.rsi(df)`` first.
"""

import logging
from typing import List

import pandas as pd

from src.strategy.base import Strategy
from src.strategy.signals import Signal

logger = logging.getLogger(__name__)


class RSIMeanReversionStrategy(Strategy):
	"""BUY when RSI < oversold_threshold, SELL when RSI > overbought_threshold."""

	def __init__(self, oversold_threshold: float = 30.0, overbought_threshold: float = 70.0):
		"""Args:
		oversold_threshold (float): RSI level below which a BUY fires. Defaults to 30.0.
		overbought_threshold (float): RSI level above which a SELL fires. Defaults to 70.0.
		"""
		self.oversold_threshold = oversold_threshold
		self.overbought_threshold = overbought_threshold

	@property
	def name(self) -> str:
		return "rsi_mean_reversion"

	def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
		"""Generate BUY/SELL signals on RSI threshold crosses.

		Args:
			df (pd.DataFrame): Must contain ``Close`` and ``RSI``, sorted
				ascending by date, with ``df.attrs["ticker"]`` set by the
				caller. Needs at least 14 rows for RSI to be meaningful
				(matches indicators.py's default RSI window).

		Returns:
			List[Signal]: One signal per bar where RSI is below the
			oversold threshold (BUY) or above the overbought threshold
			(SELL). Returns ``[]`` if required columns are missing or
			df has fewer than 14 rows.
		"""
		required = {"Close", "RSI"}
		missing = required - set(df.columns)
		if missing:
			logger.warning(
				"RSIMeanReversionStrategy.generate_signals: missing column(s) %s — returning []",
				missing,
			)
			return []

		if len(df) < 14:
			logger.info(
				"RSIMeanReversionStrategy.generate_signals: df has %d row(s), need >= 14 — returning []",
				len(df),
			)
			return []

		ticker = df.attrs.get("ticker", "UNKNOWN")
		signals: List[Signal] = []

		for ts, row in df.iterrows():
			if pd.isna(row["RSI"]):
				continue
			if row["RSI"] < self.oversold_threshold:
				signals.append(
					Signal(
						ticker=ticker,
						action="BUY",
						price=float(row["Close"]),
						reason=f"RSI {row['RSI']:.1f} below oversold threshold {self.oversold_threshold}",
						timestamp=ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts,
					)
				)
			elif row["RSI"] > self.overbought_threshold:
				signals.append(
					Signal(
						ticker=ticker,
						action="SELL",
						price=float(row["Close"]),
						reason=f"RSI {row['RSI']:.1f} above overbought threshold {self.overbought_threshold}",
						timestamp=ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts,
					)
				)

		return signals


if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example — fetch RELIANCE.NS, assemble RSI, run the real
	# strategy. Edge cases live in tests/test_strategy_rsi_mean_reversion.py
	# (pytest), not here.
	try:
		from src.data.fetch import fetch_ohlc
		from src.data.indicators import rsi
	except ImportError:
		sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
		from src.data.fetch import fetch_ohlc
		from src.data.indicators import rsi

	TICKER = "RELIANCE.NS"
	logger.info("--- RSIMeanReversionStrategy example run: %s ---", TICKER)

	df = fetch_ohlc(TICKER, period="1y", interval="1d")
	if df is None:
		logger.error("Could not fetch %s — check network connection. Exiting.", TICKER)
		sys.exit(1)

	rsi_result = rsi(df)
	if rsi_result is not None:
		df = rsi_result
	df.attrs["ticker"] = "RELIANCE"

	strat = RSIMeanReversionStrategy()
	signals = strat.generate_signals(df)
	logger.info("Signals over the last year: %d", len(signals))
	for sig in signals:
		logger.info("  %s", sig)

	logger.info("--- Example run complete ---")
