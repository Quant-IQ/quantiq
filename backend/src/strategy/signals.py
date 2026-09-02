"""
Signal dataclass — one strategy decision for one ticker at one point in time.

Owner: AV
File: src/strategy/signals.py
Phase: Phase-3
"""

import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

VALID_ACTIONS = {"BUY", "SELL", "HOLD"}


@dataclass
class Signal:
	"""A single strategy signal.

	Args:
		ticker (str): Ticker name (key into ``ticker_map.TICKER_MAP``),
			e.g. ``"RELIANCE"``.
		action (str): One of ``"BUY"``, ``"SELL"``, ``"HOLD"``.
		price (float): Price at the bar the signal fired on.
		reason (str): Human-readable explanation, e.g.
			``"SMA20 crossed above SMA50"``.
		timestamp (datetime): When the signal fired (bar timestamp, not
			wall-clock time).

	Raises:
		ValueError: If ``action`` is not one of ``VALID_ACTIONS``.
	"""

	ticker: str
	action: str
	price: float
	reason: str
	timestamp: datetime

	def __post_init__(self) -> None:
		self.action = self.action.upper()
		if self.action not in VALID_ACTIONS:
			logger.error(
				"Signal.__post_init__: invalid action '%s' for ticker '%s' — must be one of %s",
				self.action,
				self.ticker,
				sorted(VALID_ACTIONS),
			)
			raise ValueError(
				f"Signal.action must be one of {sorted(VALID_ACTIONS)}, got {self.action!r}"
			)


if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example — build a Signal from a real fetched price.
	# Edge cases live in tests/test_strategy_signals.py (pytest), not here.
	try:
		from src.data.fetch import fetch_ohlc
	except ImportError:
		sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
		from src.data.fetch import fetch_ohlc

	TICKER = "RELIANCE.NS"
	logger.info("--- Signal example run: %s ---", TICKER)

	df = fetch_ohlc(TICKER, period="5d", interval="1d")
	if df is None:
		logger.error("Could not fetch %s — check network connection. Exiting.", TICKER)
		sys.exit(1)

	latest_close = float(df["Close"].iloc[-1])
	sig = Signal(
		ticker="RELIANCE",
		action="buy",
		price=latest_close,
		reason="Example signal from real latest Close",
		timestamp=df.index[-1].to_pydatetime(),
	)
	logger.info("Built Signal: %s", sig)
	logger.info("--- Example run complete ---")
