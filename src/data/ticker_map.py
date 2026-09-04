"""
Ticker name → yfinance symbol + Dhan integer security ID mapping.

Dhan uses integer security IDs, never ISIN strings (CLAUDE.md §20.1). IDs are
exchange/account-specific and must be looked up via
``dhan.fetch_security_list("compact")`` — they are never guessed or hardcoded
from memory. Entries below with a confirmed ``dhan_id`` came from CLAUDE.md
§12/§20.1. Every other entry is intentionally ``None`` until someone runs the
lookup and fills it in — ``get_dhan_id()`` raises rather than silently
returning a wrong instrument ID, since a wrong security ID placed against a
live order would buy/sell the wrong stock.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TickerInfo:
	"""One ticker's mapping across yfinance and Dhan.

	Attributes:
		yfinance_symbol (str): NSE/BSE ticker with exchange suffix, e.g.
			``"RELIANCE.NS"``. Always carries ``.NS`` or ``.BO``.
		dhan_id (int | None): Dhan NSE_EQ integer security ID. ``None``
			means "not yet looked up" — fill in via
			``dhan.fetch_security_list("compact")``, never guess.
	"""

	yfinance_symbol: str
	dhan_id: int | None


# ---------------------------------------------------------------------------
# NIFTY50 + notebook-section tickers. Add entries here as Dhan IDs are
# confirmed via dhan.fetch_security_list("compact") — do not hardcode a
# number you haven't looked up.
# ---------------------------------------------------------------------------
TICKER_MAP: dict[str, TickerInfo] = {
	"RELIANCE": TickerInfo("RELIANCE.NS", 11536),
	"HDFCBANK": TickerInfo("HDFCBANK.NS", 1333),
	"TCS": TickerInfo("TCS.NS", None),
	"INFY": TickerInfo("INFY.NS", None),
	"HCLTECH": TickerInfo("HCLTECH.NS", None),
	"ICICIBANK": TickerInfo("ICICIBANK.NS", None),
	"AXISBANK": TickerInfo("AXISBANK.NS", None),
	"TVSMOTOR": TickerInfo("TVSMOTOR.NS", None),
	"M&M": TickerInfo("M&M.NS", None),
	"LT": TickerInfo("LT.NS", None),
	"TITAN": TickerInfo("TITAN.NS", None),
}


def get_yfinance_symbol(name: str) -> str:
	"""Look up the yfinance symbol for a ticker name.

	Args:
		name (str): Common ticker name, e.g. ``"RELIANCE"``. Case-sensitive,
			matches the keys in ``TICKER_MAP``.

	Returns:
		str: yfinance symbol with exchange suffix, e.g. ``"RELIANCE.NS"``.

	Raises:
		KeyError: If ``name`` is not in ``TICKER_MAP``.
	"""
	if name not in TICKER_MAP:
		logger.error(
			"get_yfinance_symbol: '%s' not in TICKER_MAP. Known tickers: %s",
			name,
			sorted(TICKER_MAP.keys()),
		)
		raise KeyError(
			f"'{name}' not found in TICKER_MAP. "
			f"Known tickers: {sorted(TICKER_MAP.keys())}"
		)
	return TICKER_MAP[name].yfinance_symbol


def get_dhan_id(name: str) -> int:
	"""Look up the Dhan integer security ID for a ticker name.

	Args:
		name (str): Common ticker name, e.g. ``"RELIANCE"``.

	Returns:
		int: Dhan NSE_EQ security ID.

	Raises:
		KeyError: If ``name`` is not in ``TICKER_MAP``.
		ValueError: If the ticker exists but its Dhan ID has not been
			looked up yet (still ``None``). Never falls back to a guessed
			value — an incorrect ID would place orders against the wrong
			instrument.
	"""
	if name not in TICKER_MAP:
		logger.error(
			"get_dhan_id: '%s' not in TICKER_MAP. Known tickers: %s",
			name,
			sorted(TICKER_MAP.keys()),
		)
		raise KeyError(
			f"'{name}' not found in TICKER_MAP. "
			f"Known tickers: {sorted(TICKER_MAP.keys())}"
		)

	dhan_id = TICKER_MAP[name].dhan_id
	if dhan_id is None:
		logger.error(
			"get_dhan_id: '%s' has no confirmed Dhan ID yet. "
			"Run dhan.fetch_security_list('compact') and add it to TICKER_MAP "
			"— do not guess.",
			name,
		)
		raise ValueError(
			f"'{name}' has no confirmed Dhan ID in TICKER_MAP. "
			"Look it up via dhan.fetch_security_list('compact') first."
		)
	return dhan_id


if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example — list every known ticker and its mapping status.
	# Edge cases live in tests/test_ticker_map.py (pytest), not here.
	logger.info("--- TICKER_MAP example run ---")
	for name in sorted(TICKER_MAP.keys()):
		symbol = get_yfinance_symbol(name)
		try:
			dhan_id = get_dhan_id(name)
			logger.info("%-12s -> yfinance=%-14s dhan_id=%s", name, symbol, dhan_id)
		except ValueError:
			logger.info("%-12s -> yfinance=%-14s dhan_id=NOT CONFIRMED YET", name, symbol)
	logger.info("--- Example run complete (%d tickers) ---", len(TICKER_MAP))
