"""
Watchlist persistence — save/load StaticWatchlist as JSON.

Owner: SmS
File: src/watchlist/persistence.py
Phase: Phase-3

Missing file means empty watchlist, never raise — a watchlist that hasn't
been saved yet is a normal state, not an error.
"""

import json
import logging
from pathlib import Path

from src.watchlist.static import StaticWatchlist

logger = logging.getLogger(__name__)

_WATCHLIST_DIR = Path(__file__).resolve().parent.parent / "data" / "watchlists"


def _path_for(name: str) -> Path:
	safe_name = name.replace("/", "_")
	return _WATCHLIST_DIR / f"{safe_name}.json"


def save(watchlist: StaticWatchlist) -> None:
	"""Persist a StaticWatchlist to JSON.

	Args:
		watchlist (StaticWatchlist): Watchlist to save. Saved under its
			own ``.name`` as the filename.

	Returns:
		None. Write failures are logged, not raised.
	"""
	_WATCHLIST_DIR.mkdir(parents=True, exist_ok=True)
	path = _path_for(watchlist.name)

	try:
		with open(path, "w", encoding="utf-8") as f:
			json.dump({"name": watchlist.name, "tickers": watchlist.tickers}, f)
		logger.info("Saved watchlist '%s' (%d tickers)", watchlist.name, len(watchlist))
	except OSError as e:
		logger.error("Failed to save watchlist '%s': %s", watchlist.name, e)


def load(name: str) -> StaticWatchlist:
	"""Load a StaticWatchlist from JSON.

	Args:
		name (str): Watchlist name to load.

	Returns:
		StaticWatchlist: Loaded watchlist, or an empty watchlist with
		the given ``name`` if the file is missing or corrupt — never
		raises, since "not saved yet" is a normal state.
	"""
	path = _path_for(name)

	if not path.exists():
		logger.info("load: no saved file for '%s' — returning empty watchlist", name)
		return StaticWatchlist(name)

	try:
		with open(path, "r", encoding="utf-8") as f:
			data = json.load(f)
		return StaticWatchlist(data["name"], data["tickers"])
	except (json.JSONDecodeError, KeyError, OSError) as e:
		logger.warning(
			"load: corrupt or unreadable watchlist file for '%s': %s — returning empty watchlist",
			name,
			e,
		)
		return StaticWatchlist(name)


if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example — save a real watchlist, then load it back.
	# Edge cases live in tests/test_watchlist_persistence.py (pytest),
	# not here.
	logger.info("--- Watchlist persistence example run ---")

	wl_name = "demo_largecaps"
	wl = StaticWatchlist(wl_name, ["RELIANCE", "TCS", "HDFCBANK"])
	save(wl)
	logger.info("Saved watchlist '%s' with %d ticker(s)", wl.name, len(wl))

	loaded = load(wl_name)
	logger.info("Loaded back: %s", loaded.tickers)

	logger.info("--- Example run complete ---")
