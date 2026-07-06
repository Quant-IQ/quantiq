from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


def log_signal(
	ticker: str,
	action: str,
	price: float,
	reason: str,
) -> None:
	"""Append a trade signal to logs/trades.csv.

	Creates the file with a header row on first write.
	Subsequent calls append to the file.
	"""
	logs_dir = Path("logs")
	logs_dir.mkdir(exist_ok=True)

	file_path = logs_dir / "trades.csv"

	file_exists = file_path.exists()

	with open(file_path, "a", newline="", encoding="utf-8") as csvfile:
		writer = csv.writer(csvfile)

		if not file_exists:
			writer.writerow(["timestamp", "ticker", "action", "price", "reason"])

		writer.writerow(
			[
				datetime.now().isoformat(),
				ticker,
				action,
				price,
				reason,
			]
		)
