from dataclasses import dataclass

import pandas as pd


@dataclass
class ValidationReport:
	"""
	Data transfer object capturing data health statistics without mutating source states.
	"""

	gaps: int
	bad_ticks: int
	missing_holidays: list[str]


# Strict Constant Layer: Explicit NSE Holiday Registry per specs (2024-2025 dates)
NSE_HOLIDAYS_2024_2025 = {
	# 2024 Core Trading Holidays
	"2024-01-26": "Republic Day",
	"2024-03-08": "Mahashivratri",
	"2024-03-25": "Holi",
	"2024-03-29": "Good Friday",
	"2024-04-11": "Id-Ul-Fitr",
	"2024-04-17": "Ram Navami",
	"2024-05-01": "Maharashtra Day",
	"2024-06-17": "Bakri Id",
	"2024-07-17": "Moharram",
	"2024-08-15": "Independence Day",
	"2024-10-02": "Mahatma Gandhi Jayanti",
	"2024-11-01": "Diwali Laxmi Puja",
	"2024-11-15": "Guru Nanak Jayanti",
	"2024-12-25": "Christmas",
	# 2025 Projected Core Trading Holidays
	"2025-01-26": "Republic Day",
	"2025-03-14": "Holi",
	"2025-03-31": "Id-Ul-Fitr",
	"2025-04-10": "Mahavir Jayanti",
	"2025-04-14": "Dr. Baba Saheb Ambedkar Jayanti",
	"2025-04-18": "Good Friday",
	"2025-05-01": "Maharashtra Day",
	"2025-09-05": "Id-E-Milad",
	"2025-10-02": "Mahatma Gandhi Jayanti",
	"2025-10-22": "Diwali Amavasya (Laxmi Puja)",
	"2025-11-05": "Guru Nanak Jayanti",
	"2025-12-25": "Christmas",
}
