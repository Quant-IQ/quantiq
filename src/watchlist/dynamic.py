"""
Dynamic watchlist — auto-updates from a screener config on refresh().

Owner: SmS
File: src/watchlist/dynamic.py
Phase: Phase-3

If the screener fails on refresh, retain the last cached ticker list and
log — a dynamic watchlist should never go silently empty just because one
screener run had a network hiccup.
"""

import logging
from typing import List

from src.screener.config import ScreenerConfig
from src.screener.runner import run as run_screener

logger = logging.getLogger(__name__)


class DynamicWatchlist:
	"""A watchlist whose tickers come from re-running a screener config."""

	def __init__(self, screener_config: ScreenerConfig):
		"""Args:
		screener_config (ScreenerConfig): Screener definition to re-run
			on each ``refresh()`` call.
		"""
		self.screener_config = screener_config
		self._tickers: List[str] = []

	@property
	def tickers(self) -> List[str]:
		"""Current ticker list — last successful refresh, or empty if never refreshed."""
		return list(self._tickers)

	def refresh(self) -> List[str]:
		"""Re-run the screener and update the ticker list.

		Returns:
			List[str]: The new ticker list on success. On screener
			failure, the previous ticker list is retained and returned
			unchanged — never raises, never silently empties.
		"""
		try:
			new_tickers = run_screener(self.screener_config, use_cache=False)
			self._tickers = new_tickers
			logger.info(
				"DynamicWatchlist.refresh: '%s' updated to %d ticker(s)",
				self.screener_config.name,
				len(new_tickers),
			)
		except Exception as e:
			logger.error(
				"DynamicWatchlist.refresh: screener '%s' failed (%s) — retaining last %d ticker(s)",
				self.screener_config.name,
				e,
				len(self._tickers),
				exc_info=True,
			)
		return list(self._tickers)


if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example — refresh a dynamic watchlist off a real screener
	# run. Edge cases live in tests/test_watchlist_dynamic.py (pytest),
	# not here.
	logger.info("--- DynamicWatchlist example run ---")

	cfg = ScreenerConfig(
		name="dynamic_watchlist_demo",
		conditions=[{"metric": "RSI", "operator": "<", "value": 60}],
		universe=["RELIANCE", "TCS", "HDFCBANK"],
	)
	wl = DynamicWatchlist(cfg)

	result = wl.refresh()
	logger.info("Refreshed — tickers: %s", result)

	logger.info("--- Example run complete ---")
