import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)


def get_cache_path(config_name: str, date: str) -> Path:
    return CACHE_DIR / f"{config_name}_{date}.json"


def save_cache(config_name: str, date: str, data: dict) -> None:
    cache_file = get_cache_path(config_name, date)

    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_cache(config_name: str, date: str):
    cache_file = get_cache_path(config_name, date)

    if not cache_file.exists():
        return None

    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Cache load failed: {e}")
        return None