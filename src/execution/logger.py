"""Utilities for logging paper-trade signals.

This module records paper-trade signals in a CSV audit log. The log
directory is created automatically if it does not exist. Trade logs are
written using a TimedRotatingFileHandler configured for long-term audit
retention.
"""

from __future__ import annotations

import csv
import io
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "trades.csv"

logger = logging.getLogger(__name__)

_handler: TimedRotatingFileHandler | None = None


def _get_handler() -> TimedRotatingFileHandler:
	"""Create or return the rotating CSV handler.

	Returns:
	    TimedRotatingFileHandler: Configured handler for trade logs.

	Raises:
	    OSError: If the log directory cannot be created.
	"""
	global _handler

	if _handler is not None:
		return _handler

	LOG_DIR.mkdir(parents=True, exist_ok=True)

	file_exists = LOG_FILE.exists()

	handler = TimedRotatingFileHandler(
		filename=LOG_FILE,
		when="midnight",
		interval=1,
		backupCount=1825,  # 5 years
		encoding="utf-8",
	)

	if not file_exists or LOG_FILE.stat().st_size == 0:
		with LOG_FILE.open("w", newline="", encoding="utf-8") as file:
			writer = csv.writer(file)
			writer.writerow(["timestamp", "ticker", "action", "price", "reason"])

	_handler = handler
	return handler


def log_signal(
	ticker: str,
	action: str,
	price: float,
	reason: str,
) -> None:
	"""Append a trade signal to the paper-trading audit log.

	Args:
	    ticker: Trading symbol (for example ``"RELIANCE.NS"``).
	    action: Trading action (``"BUY"``, ``"SELL"``, or ``"HOLD"``).
	    price: Signal price.
	    reason: Human-readable explanation for the signal.

	Returns:
	    None

	Raises:
	    OSError: If the log file cannot be written.
	"""
	try:
		handler = _get_handler()

		buffer = io.StringIO()
		writer = csv.writer(buffer)
		writer.writerow(
			[
				logging.Formatter.formatTime(
					logging.Formatter(),
					logging.makeLogRecord({}),
					"%Y-%m-%dT%H:%M:%S",
				),
				ticker,
				action,
				price,
				reason,
			]
		)

		handler.acquire()
		try:
			handler.stream.write(buffer.getvalue())
			handler.flush()
		finally:
			handler.release()

	except OSError:
		logger.exception("Failed to write trade signal.")
		raise


if __name__ == "__main__":
	log_signal(
		ticker="RELIANCE.NS",
		action="BUY",
		price=2847.50,
		reason="SMA20 crossed above SMA50",
	)
	print("Smoke test completed successfully.")
