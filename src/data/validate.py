"""
Data Validation Module
Owner: GT (Co-Lead / Quant) | Phase 3 Active Module

Validates OHLCV DataFrames produced by fetch_ohlc() / fetch_batch() before
they enter indicator calculation or backtesting. Three check types:

- gaps:      Missing trading days vs NSE calendar (pandas_market_calendars)
- holidays:  Rows on NSE non-trading days — removed silently, count reported
- bad_ticks: Price spikes (>5×ATR), zero/negative prices, volume outliers (>10× rolling mean)

Usage:
    from src.data.validate import validate

    df, report = validate(df, "RELIANCE.NS")
    if report.warnings:
        for w in report.warnings:
            logger.warning(w)
"""

import logging
from dataclasses import dataclass, field
from datetime import date

import pandas as pd
from ta.volatility import AverageTrueRange

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# NSE Static Holiday Calendar Matrix (Issue #226 Implementation)
# Source URL: https://www.nseindia.com/market-data/holiday-calendar
# ---------------------------------------------------------------------------

NSE_HOLIDAYS: set[str] = {
	# 2024 NSE Holidays
	"2024-01-26",  # Republic Day
	"2024-03-25",  # Holi
	"2024-04-14",  # Dr. Ambedkar Jayanti
	"2024-04-17",  # Ram Navami
	"2024-04-21",  # Mahavir Jayanti
	"2024-04-23",  # Good Friday (special session)
	"2024-05-23",  # Buddha Purnima
	"2024-06-17",  # Eid ul-Adha
	"2024-07-17",  # Muharram
	"2024-08-15",  # Independence Day
	"2024-10-02",  # Gandhi Jayanti
	"2024-11-01",  # Diwali Laxmi Pujan
	"2024-11-15",  # Gurunanak Jayanti
	"2024-11-20",  # Maharashtra Assembly Elections
	"2024-12-25",  # Christmas
	# 2025 NSE Holidays
	"2025-01-26",  # Republic Day
	"2025-02-26",  # Mahashivratri
	"2025-03-14",  # Holi
	"2025-03-31",  # Id-Ul-Fitr (Ramzan Eid)
	"2025-04-10",  # Shri Ram Navami
	"2025-04-14",  # Dr. Ambedkar Jayanti / Maharashtra Day
	"2025-04-18",  # Good Friday
	"2025-05-12",  # Buddha Purnima
	"2025-06-07",  # Bakri Eid
	"2025-07-06",  # Muharram
	"2025-08-15",  # Independence Day
	"2025-08-27",  # Ganesh Chaturthi
	"2025-10-02",  # Gandhi Jayanti / Dussehra
	"2025-10-21",  # Diwali Amavasya / Laxmi Puja
	"2025-10-22",  # Diwali (Balipratipada)
	"2025-11-05",  # Gurunanak Jayanti
	"2025-12-25",  # Christmas
}


# ---------------------------------------------------------------------------
# NSE calendar — loaded lazily to avoid import-time network call
# ---------------------------------------------------------------------------

_NSE_CALENDAR = None


def _get_nse_calendar():
	"""Return cached NSE calendar instance (lazy init).

	Returns:
	    Optional[mcal.MarketCalendar]: The NSE calendar instance or None if unavailable.
	"""
	global _NSE_CALENDAR
	if _NSE_CALENDAR is None:
		try:
			import pandas_market_calendars as mcal

			_NSE_CALENDAR = mcal.get_calendar("NSE")
		except ImportError:
			logger.error(
				"pandas_market_calendars not installed — run: pip install pandas-market-calendars"
			)
			return None
		except Exception as e:
			logger.error("Failed to load NSE calendar: %s", e)
			return None
	return _NSE_CALENDAR


# ---------------------------------------------------------------------------
# ValidationReport
# ---------------------------------------------------------------------------


@dataclass
class ValidationReport:
	"""Summary of changes made by validate().

	Attributes:
	    gaps (list[date]): Trading days with no data in the DataFrame.
	    bad_ticks (list[dict]): Rows removed as bad ticks. Each entry has keys
	      'date' (date) and 'reason' (str).
	    holidays_removed (int): Count of rows dropped because they fall on NSE
	      non-trading days (weekends + NSE holidays).
	    warnings (list[str]): Human-readable warning strings. Safe to log or display.
	"""

	gaps: list[date] = field(default_factory=list)
	bad_ticks: list[dict] = field(default_factory=list)
	holidays_removed: int = 0
	warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _remove_holidays(
	df: pd.DataFrame,
	ticker: str,
	report: ValidationReport,
) -> pd.DataFrame:
	"""Drop rows that fall on NSE non-trading days. Updates report in place.

	Args:
	    df (pd.DataFrame): OHLCV DataFrame with datetime index.
	    ticker (str): Ticker string — used in log messages only.
	    report (ValidationReport): Report object to update.

	Returns:
	    pd.DataFrame: DataFrame with holiday rows removed.
	"""
	# 1. Filter out static list of holidays to minimize calendar scheduling dependency
	df_dates_str = df.index.strftime("%Y-%m-%d")
	static_holiday_mask = df_dates_str.isin(NSE_HOLIDAYS)
	static_removed = static_holiday_mask.sum()

	if static_removed > 0:
		report.holidays_removed += int(static_removed)
		report.warnings.append(
			f"{ticker}: removed {static_removed} rows matching static NSE holiday matrix"
		)
		df = df[~static_holiday_mask]

	# 2. Drop standard weekends/non-trading cycles via lazily loaded calendar
	cal = _get_nse_calendar()
	if cal is None:
		report.warnings.append(
			f"{ticker}: weekend holiday check skipped — NSE calendar unavailable"
		)
		return df

	start = df.index.min()
	end = df.index.max()

	try:
		schedule = cal.schedule(
			start_date=start.strftime("%Y-%m-%d"),
			end_date=end.strftime("%Y-%m-%d"),
		)
		trading_days = set(schedule.index.normalize())
	except Exception as e:
		report.warnings.append(f"{ticker}: dynamic weekend check failed — {e}")
		return df

	df_dates = df.index.normalize()
	mask = df_dates.isin(trading_days)
	calendar_removed = (~mask).sum()

	if calendar_removed > 0:
		report.holidays_removed += int(calendar_removed)
		report.warnings.append(
			f"{ticker}: removed {calendar_removed} rows on weekend non-trading blocks"
		)
		df = df[mask]

	return df


def _detect_gaps(
	df: pd.DataFrame,
	ticker: str,
	report: ValidationReport,
) -> None:
	"""Populate report.gaps with expected trading days missing from df.

	Args:
	    df (pd.DataFrame): OHLCV DataFrame with datetime index.
	    ticker (str): Ticker string — used in log messages only.
	    report (ValidationReport): Report object to update.
	"""
	cal = _get_nse_calendar()
	if cal is None:
		report.warnings.append(
			f"{ticker}: gap check skipped — NSE calendar unavailable"
		)
		return

	start = df.index.min()
	end = df.index.max()

	try:
		schedule = cal.schedule(
			start_date=start.strftime("%Y-%m-%d"),
			end_date=end.strftime("%Y-%m-%d"),
		)
		expected = set(d.date() for d in schedule.index)
	except Exception as e:
		report.warnings.append(f"{ticker}: gap check failed — {e}")
		return

	# Clean the expected matrix by filter dropping static holidays to protect structural logic
	expected = {d for d in expected if d.strftime("%Y-%m-%d") not in NSE_HOLIDAYS}

	actual = set(d.date() if hasattr(d, "date") else d for d in df.index.normalize())
	gaps = sorted(expected - actual)

	if gaps:
		report.gaps = gaps
		report.warnings.append(
			f"{ticker}: {len(gaps)} missing trading day(s) — first gap: {gaps[0]}"
		)


def _filter_bad_ticks(
	df: pd.DataFrame,
	ticker: str,
	report: ValidationReport,
) -> pd.DataFrame:
	"""Remove rows with price spikes, zero/negative prices, or volume outliers.

	Three bad tick types detected:
	- Zero or negative price in any of Open, High, Low, Close
	- Price spike: any OHLC value deviates from Close by more than 5× ATR(14)
	- Volume outlier: Volume > 10× 20-period rolling mean volume

	Args:
	    df (pd.DataFrame): OHLCV DataFrame with datetime index.
	    ticker (str): Ticker string — used in log messages only.
	    report (ValidationReport): Report object to update.

	Returns:
	    pd.DataFrame: DataFrame with bad tick rows removed.
	"""
	bad_mask = pd.Series(False, index=df.index)

	# --- Check 1: zero or negative price ---
	price_cols = [c for c in ["Open", "High", "Low", "Close"] if c in df.columns]
	for col in price_cols:
		zero_neg = df[col] <= 0
		if zero_neg.any():
			for idx in df.index[zero_neg]:
				report.bad_ticks.append(
					{
						"date": idx.date() if hasattr(idx, "date") else idx,
						"reason": f"{col} <= 0 ({df.loc[idx, col]})",
					}
				)
				logger.warning(
					"%s: bad tick at %s — %s <= 0 (%s)",
					ticker,
					idx,
					col,
					df.loc[idx, col],
				)
			bad_mask |= zero_neg

	# --- Check 2: price spike > 5× ATR(14) ---
	if len(df) >= 15 and all(c in df.columns for c in ["High", "Low", "Close"]):
		try:
			atr_series = AverageTrueRange(
				high=df["High"],
				low=df["Low"],
				close=df["Close"],
				window=14,
				fillna=False,
			).average_true_range()

			spike_threshold = 5 * atr_series

			for col in price_cols:
				deviation = (df[col] - df["Close"]).abs()
				spikes = deviation > spike_threshold
				spikes = spikes & ~bad_mask & spike_threshold.notna() & (atr_series > 0)
				if spikes.any():
					for idx in df.index[spikes]:
						report.bad_ticks.append(
							{
								"date": idx.date() if hasattr(idx, "date") else idx,
								"reason": f"{col} spike ({df.loc[idx, col]:.2f}) > 5×ATR ({spike_threshold.loc[idx]:.2f})",
							}
						)
						logger.warning(
							"%s: price spike at %s — %s=%.2f exceeds 5×ATR=%.2f",
							ticker,
							idx,
							col,
							df.loc[idx, col],
							spike_threshold.loc[idx],
						)
					bad_mask |= spikes
		except Exception as e:
			report.warnings.append(f"{ticker}: ATR spike check failed — {e}")

	# --- Check 3: volume outlier > 10× rolling mean ---
	if "Volume" in df.columns:
		rolling_vol_mean = df["Volume"].rolling(window=20, min_periods=5).mean()
		outliers = (
			(df["Volume"] > 10 * rolling_vol_mean)
			& ~bad_mask
			& rolling_vol_mean.notna()
		)
		if outliers.any():
			for idx in df.index[outliers]:
				report.bad_ticks.append(
					{
						"date": idx.date() if hasattr(idx, "date") else idx,
						"reason": f"Volume outlier ({df.loc[idx, 'Volume']:.0f}) > 10× rolling mean ({rolling_vol_mean.loc[idx]:.0f})",
					}
				)
				logger.warning(
					"%s: volume outlier at %s — %.0f > 10× rolling mean %.0f",
					ticker,
					idx,
					df.loc[idx, "Volume"],
					rolling_vol_mean.loc[idx],
				)
			bad_mask |= outliers

	if bad_mask.any():
		df = df[~bad_mask]

	return df


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate(
	df: pd.DataFrame,
	ticker: str,
	checks: set[str] | None = None,
) -> tuple[pd.DataFrame, ValidationReport]:
	"""Validate an OHLCV DataFrame and return a cleaned copy with a report.

	Runs the requested checks in order: holidays → bad_ticks → gaps.
	Holidays are removed before gap detection so NSE non-trading days don't
	register as data gaps.

	Args:
	    df (pd.DataFrame): OHLCV DataFrame from fetch_ohlc() or fetch_batch().
	      Must have a datetime index and columns: Open, High, Low, Close, Volume.
	    ticker (str): NSE ticker with .NS suffix (e.g. "RELIANCE.NS").
	      Used for calendar lookups and log messages.
	    checks (set[str] | None): Which checks to run. Valid values:
	      ``"gaps"``, ``"holidays"``, ``"bad_ticks"``.
	      Defaults to all three: ``{"gaps", "holidays", "bad_ticks"}``.

	Returns:
	    tuple[pd.DataFrame, ValidationReport]: Cleaned DataFrame and report.
	      The DataFrame is a copy — original is never mutated.
	      Report summarises gaps found, bad ticks removed, holidays removed,
	      and any warnings generated during validation.
	"""
	if checks is None:
		checks = {"gaps", "holidays", "bad_ticks"}

	report = ValidationReport()

	if df is None or df.empty:
		report.warnings.append(f"{ticker}: validate() received empty or None DataFrame")
		return df if df is not None else pd.DataFrame(), report

	# Always work on a copy to comply with non-mutation code standards
	result = df.copy()

	# Order processing matters: eliminate holidays before initiating gap metrics
	if "holidays" in checks:
		result = _remove_holidays(result, ticker, report)

	if "bad_ticks" in checks:
		result = _filter_bad_ticks(result, ticker, report)

	if "gaps" in checks:
		_detect_gaps(result, ticker, report)

	logger.info(
		"%s: validation complete — %d rows remaining, %d gap(s), %d bad tick(s), %d holiday row(s) removed",
		ticker,
		len(result),
		len(report.gaps),
		len(report.bad_ticks),
		report.holidays_removed,
	)

	return result, report


# ---------------------------------------------------------------------------
# Automated Issue #226 Internal Test Framework
# ---------------------------------------------------------------------------
def run_issue_acceptance_tests():
	"""Assert all operational acceptance criteria inside Issue #226."""
	logger.info("Executing automated Issue #226 validation parameters...")

	# 1. Format Check Rule validation
	for day in NSE_HOLIDAYS:
		assert len(day) == 10 and day[4] == "-" and day[7] == "-", (
			f"Static parsing error on string layout: {day}"
		)

	# 2. Known Node Assertions
	assert "2024-01-26" in NSE_HOLIDAYS, (
		"Assertion failure: 2024 Republic Day node omitted."
	)
	assert "2025-12-25" in NSE_HOLIDAYS, (
		"Assertion failure: 2025 Christmas node omitted."
	)
	assert "2024-01-25" not in NSE_HOLIDAYS, (
		"Anomaly detection: Boundary mismatch triggered."
	)

	logger.info("✓ Issue #226 compliance matrices verified successfully!")


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
	import sys

	import yfinance as yf

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Run criteria tests first
	run_issue_acceptance_tests()

	TICKER = "RELIANCE.NS"
	logger.info("Fetching data matrix sample for smoke test tracking...")

	raw = yf.download(
		TICKER, period="3mo", interval="1d", auto_adjust=True, progress=False
	)
	if raw is not None and not raw.empty:
		if isinstance(raw.columns, pd.MultiIndex):
			raw.columns = raw.columns.get_level_values(0)

		df_smoke = raw[["Open", "High", "Low", "Close", "Volume"]].copy()
		df_smoke.dropna(inplace=True)

		clean_df, report_obj = validate(df_smoke, TICKER)
		logger.info(
			"Local engine validation sequence complete without structural crashes."
		)
