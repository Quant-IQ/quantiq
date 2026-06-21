"""
Static watchlist — a hand-curated, manually edited list of tickers.

Owner: SmS
File: src/watchlist/static.py
Phase: Phase-3
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


class StaticWatchlist:
	"""A manually curated watchlist of ticker names."""

	def __init__(self, name: str, tickers: List[str] | None = None):
		"""Args:
		name (str): Watchlist name, e.g. ``"my_largecaps"``.
		tickers (List[str] | None): Initial ticker names. Defaults to empty.

		Raises:
			ValueError: If ``name`` is empty.
		"""
		if not name or not name.strip():
			raise ValueError("StaticWatchlist.name must be a non-empty string")
		self.name = name
		self._tickers: List[str] = list(dict.fromkeys(tickers or []))  # dedupe, preserve order

	@property
	def tickers(self) -> List[str]:
		"""Current ticker list, in insertion order."""
		return list(self._tickers)

	def add(self, ticker: str) -> None:
		"""Add a ticker. No-op (with a log) if already present.

		Args:
			ticker (str): Ticker name to add.
		"""
		if ticker in self._tickers:
			logger.info("StaticWatchlist.add: '%s' already in '%s' — no-op", ticker, self.name)
			return
		self._tickers.append(ticker)

	def remove(self, ticker: str) -> None:
		"""Remove a ticker. No-op (with a log) if not present.

		Args:
			ticker (str): Ticker name to remove.
		"""
		if ticker not in self._tickers:
			logger.warning(
				"StaticWatchlist.remove: '%s' not in '%s' — no-op", ticker, self.name
			)
			return
		self._tickers.remove(ticker)

	def __len__(self) -> int:
		return len(self._tickers)

	def __contains__(self, ticker: str) -> bool:
		return ticker in self._tickers


if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example — build a watchlist from real screener output.
	# Edge cases live in tests/test_watchlist_static.py (pytest), not here.
	try:
		from src.screener.config import ScreenerConfig
		from src.screener.runner import run as run_screener
	except ImportError:
		sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
		from src.screener.config import ScreenerConfig
		from src.screener.runner import run as run_screener

	logger.info("--- StaticWatchlist example run ---")

	cfg = ScreenerConfig(
		name="static_watchlist_demo",
		conditions=[{"metric": "RSI", "operator": "<", "value": 60}],
		universe=["RELIANCE", "TCS", "HDFCBANK"],
	)
	matches = run_screener(cfg, use_cache=False)
	logger.info("Screener matched: %s", matches)

	wl = StaticWatchlist("my_watchlist", matches)
	logger.info("Watchlist '%s' has %d ticker(s): %s", wl.name, len(wl), wl.tickers)

	wl.add("TITAN")
	logger.info("After adding TITAN: %s", wl.tickers)

	logger.info("--- Example run complete ---")
