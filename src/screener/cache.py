"""
Screener output cache — JSON, keyed by config name + run date.

Owner: SmS
File: src/screener/cache.py
Phase: Phase-3

Cache miss or corrupt file means "rerun the screener", never raise — the
screener itself is the source of truth, the cache is a pure speed-up.
"""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache" / "screeners"


def _cache_path(config_name: str, run_date: date) -> Path:
	"""Return the JSON cache path for a screener config name + run date."""
	safe_name = config_name.replace("/", "_")
	return _CACHE_DIR / f"{safe_name}__{run_date.isoformat()}.json"


def save(config_name: str, run_date: date, results: List[str]) -> None:
	"""Write screener results to the JSON cache.

	Args:
		config_name (str): Screener config name (``ScreenerConfig.name``).
		run_date (date): Date the screener was run.
		results (List[str]): Ticker names that matched the screener.

	Returns:
		None. Failures are logged, not raised — a failed cache write
		should never block returning results to the caller.
	"""
	_CACHE_DIR.mkdir(parents=True, exist_ok=True)
	path = _cache_path(config_name, run_date)

	try:
		with open(path, "w", encoding="utf-8") as f:
			json.dump({"config_name": config_name, "run_date": run_date.isoformat(), "results": results}, f)
		logger.info("Cached %d result(s) for '%s' (%s)", len(results), config_name, run_date)
	except OSError as e:
		logger.error("Failed to write screener cache for '%s': %s", config_name, e)


def load(config_name: str, run_date: date) -> Optional[List[str]]:
	"""Read screener results from the JSON cache.

	Args:
		config_name (str): Screener config name.
		run_date (date): Date the screener was run.

	Returns:
		List[str] | None: Cached ticker list, or ``None`` on cache miss
		or corrupt file — callers must treat ``None`` as "rerun the
		screener", never raise.
	"""
	path = _cache_path(config_name, run_date)

	if not path.exists():
		logger.info("Cache miss for '%s' (%s) — no cache file", config_name, run_date)
		return None

	try:
		with open(path, "r", encoding="utf-8") as f:
			data: Dict[str, Any] = json.load(f)
		return data["results"]
	except (json.JSONDecodeError, KeyError, OSError) as e:
		logger.warning(
			"Corrupt or unreadable screener cache for '%s' (%s): %s — treating as miss",
			config_name,
			run_date,
			e,
		)
		return None


if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example — cache a real screener run, then load it back.
	# Edge cases live in tests/test_screener_cache.py (pytest), not here.
	logger.info("--- Screener cache example run ---")

	config_name = "rsi_oversold_demo"
	run_date = date.today()

	cached = load(config_name, run_date)
	if cached is not None:
		logger.info("Cache hit for '%s' (%s): %s", config_name, run_date, cached)
	else:
		logger.info("Cache miss for '%s' (%s) — saving a fresh result", config_name, run_date)
		save(config_name, run_date, ["RELIANCE", "HDFCBANK"])
		cached = load(config_name, run_date)
		logger.info("Just-saved result loaded back: %s", cached)

	logger.info("--- Example run complete ---")
