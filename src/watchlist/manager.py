"""
Watchlist manager — CRUD over saved StaticWatchlists, wrapping persistence.py.

Owner: AR
File: src/watchlist/manager.py
Phase: Phase-3
"""

import logging
from typing import List

from src.watchlist.persistence import _WATCHLIST_DIR
from src.watchlist.persistence import load as persist_load
from src.watchlist.persistence import save as persist_save
from src.watchlist.static import StaticWatchlist

logger = logging.getLogger(__name__)


def create(name: str, tickers: List[str] | None = None) -> StaticWatchlist:
	"""Create and persist a new static watchlist.

	Args:
		name (str): Watchlist name.
		tickers (List[str] | None): Initial tickers. Defaults to empty.

	Returns:
		StaticWatchlist: The newly created, persisted watchlist.
	"""
	wl = StaticWatchlist(name, tickers)
	persist_save(wl)
	return wl


def get(name: str) -> StaticWatchlist:
	"""Load a watchlist by name.

	Args:
		name (str): Watchlist name.

	Returns:
		StaticWatchlist: Loaded watchlist, or an empty one if not found
		(``persistence.load`` never raises on a missing file).
	"""
	return persist_load(name)


def list_all() -> List[str]:
	"""List the names of all saved watchlists.

	Returns:
		List[str]: Watchlist names with a saved JSON file. Empty list
		if the watchlist directory doesn't exist yet.
	"""
	if not _WATCHLIST_DIR.exists():
		return []
	return sorted(p.stem for p in _WATCHLIST_DIR.glob("*.json"))


def edit(name: str, tickers: List[str]) -> StaticWatchlist:
	"""Replace a watchlist's ticker list and persist the change.

	Args:
		name (str): Watchlist name to edit.
		tickers (List[str]): New ticker list, replacing the old one.

	Returns:
		StaticWatchlist: The updated, persisted watchlist.
	"""
	wl = StaticWatchlist(name, tickers)
	persist_save(wl)
	return wl


def delete(name: str) -> None:
	"""Delete a saved watchlist's file.

	Args:
		name (str): Watchlist name to delete.

	Returns:
		None. Deleting a nonexistent watchlist logs a warning, never
		raises.
	"""
	path = _WATCHLIST_DIR / f"{name.replace('/', '_')}.json"
	if not path.exists():
		logger.warning("delete: watchlist '%s' does not exist — no-op", name)
		return
	path.unlink()
	logger.info("Deleted watchlist '%s'", name)


if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example — full CRUD cycle on a real watchlist.
	# Edge cases live in tests/test_watchlist_manager.py (pytest), not here.
	logger.info("--- Watchlist manager example run ---")

	wl_name = "demo_manager_watchlist"

	create(wl_name, ["RELIANCE", "TCS"])
	logger.info("Created '%s'. All watchlists: %s", wl_name, list_all())

	loaded = get(wl_name)
	logger.info("Loaded '%s': %s", wl_name, loaded.tickers)

	edit(wl_name, ["HDFCBANK", "TITAN"])
	logger.info("Edited '%s': %s", wl_name, get(wl_name).tickers)

	delete(wl_name)
	logger.info("Deleted '%s'. Remaining watchlists: %s", wl_name, list_all())

	logger.info("--- Example run complete ---")
