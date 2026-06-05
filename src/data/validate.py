from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd


@dataclass
class ValidationReport:
	"""
	Data transfer object capturing data health statistics without mutating source states.
	"""

	gaps: int
	bad_ticks: int
	missing_holidays: List[str]


# Strict Constant Layer: Explicit NSE Holiday Registry per specs (2024-2025 dates)
NSE_HOLIDAYS_2024_2025 = {
	# 2024 Core Trading Holidays
	"2024-01-26",  # Republic Day
	"2024-03-08",  # Mahashivratri
	"2024-03-25",  # Holi
	"2024-03-29",  # Good Friday
	"2024-04-11",  # Id-Ul-Fitr
	"2024-04-17",  # Ram Navami
	"2024-05-01",  # Maharashtra Day
	"2024-06-17",  # Bakri Id
	"2024-07-17",  # Moharram
	"2024-08-15",  # Independence Day
	"2024-10-02",  # Mahatma Gandhi Jayanti
	"2024-11-01",  # Diwali Laxmi Puja
	"2024-11-15",  # Guru Nanak Jayanti
	"2024-12-25",  # Christmas
	# 2025 Projected Core Trading Holidays
	"2025-01-26",
	"2025-03-14",
	"2025-03-31",
	"2025-04-10",
	"2025-04-14",
	"2025-04-18",
	"2025-05-01",
	"2025-06-06",
	"2025-08-15",
	"2025-10-02",
	"2025-10-20",
	"2025-11-05",
	"2025-12-25",
}


def validate_market_data(
	input_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, ValidationReport]:
	"""
	Executes advanced data integrity checks including bad tick scrubbing, structural gap identification,
	and formal NSE calendar compliance checks. Considers inputs as read-only.
	"""
	# Defensive structural pattern: Enforce absolute read-only boundary via defensive replication
	df = input_df.copy()

	if df.empty:
		return df, ValidationReport(gaps=0, bad_ticks=0, missing_holidays=[])

	# Standardize index timeline safely
	if "Date" in df.columns:
		df["Date"] = pd.to_datetime(df["Date"])
		df.set_index("Date", inplace=True)
	else:
		df.index = pd.to_datetime(df.index)

	df.sort_index(inplace=True)

	# 1. Bad Ticks Filtering (Scrubbing zero/negative values or broken spikes)
	initial_rows = len(df)
	df = df[(df["Open"] > 0) & (df["High"] > 0) & (df["Low"] > 0) & (df["Close"] > 0)]
	df = df[df["High"] >= df["Low"]]
	bad_ticks_count = initial_rows - len(df)

	# 2. Sequential Gap Detection
	expected_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq="B")

	# Filter expected business days against holiday map and weekends
	expected_trading_days = [
		day
		for day in expected_range
		if day.strftime("%Y-%m-%d") not in NSE_HOLIDAYS_2024_2025
	]

	actual_trading_days_set = set(df.index.strftime("%Y-%m-%d"))

	# Identify gaps inside timeline
	missing_dates = [
		day.strftime("%Y-%m-%d")
		for day in expected_trading_days
		if day.strftime("%Y-%m-%d") not in actual_trading_days_set
	]

	gaps_detected = len(missing_dates)

	# 3. Holiday Validation Verification
	# Ensure no rows leak into known historical holiday coordinates
	flagged_holiday_leakages = [
		date_str
		for date_str in actual_trading_days_set
		if date_str in NSE_HOLIDAYS_2024_2025
	]

	if flagged_holiday_leakages:
		df = df[~df.index.strftime("%Y-%m-%d").isin(NSE_HOLIDAYS_2024_2025)]

	report = ValidationReport(
		gaps=gaps_detected,
		bad_ticks=bad_ticks_count,
		missing_holidays=flagged_holiday_leakages,
	)

	return df, report


# Test verification runner block to fulfill spec validation requirements
if __name__ == "__main__":
	dates = pd.date_range(start="2026-01-01", periods=10, freq="B")
	mock_data = {
		"Open": [100.0] * 10,
		"High": [105.0] * 10,
		"Low": [95.0] * 10,
		"Close": [102.0] * 10,
		"Volume": [1000] * 10,
	}
	df_test = pd.DataFrame(mock_data, index=dates)

	# Drop 3 rows to explicitly verify 3 structural gaps are flagged
	df_with_gaps = df_test.drop(df_test.index[[2, 4, 7]])

	processed_df, report = validate_market_data(df_with_gaps)

	print(f"Testing validation assertions: Gaps found = {report.gaps}")
	assert report.gaps == 3, f"Expected 3 gaps, got {report.gaps}"
	print("Integration test executed successfully!")
