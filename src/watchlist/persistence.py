import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

WATCHLIST_DIR = Path("watchlists")
WATCHLIST_DIR.mkdir(exist_ok=True)


def save_watchlist(name: str, tickers: list[str]) -> None:
    filepath = WATCHLIST_DIR / f"{name}.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(tickers, f, indent=4)

    logger.info(f"Saved watchlist: {name}")


def load_watchlist(name: str) -> list[str]:
    filepath = WATCHLIST_DIR / f"{name}.json"

    if not filepath.exists():
        logger.warning(f"Watchlist {name} not found")
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        tickers = json.load(f)

    logger.info(f"Loaded watchlist: {name}")
    return tickers