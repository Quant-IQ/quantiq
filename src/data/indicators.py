import logging

import pandas as pd
from ta.trend import MACD, SMAIndicator

# ---------------------------------------------------------------------------
# Module-level logger — no basicConfig here; caller / __main__ configures it
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# MACD
# ---------------------------------------------------------------------------


def macd(
	df: pd.DataFrame,
	window_slow: int = 26,
	window_fast: int = 12,
	window_sign: int = 9,
	column: str = "Close",
) -> pd.DataFrame | None:
	"""Append MACD line, signal line, and histogram columns to an OHLCV DataFrame.

	Uses the ``ta`` library's ``MACD`` class under the hood so indicator
	behaviour is consistent with every other ``ta``-based indicator in this
	codebase. Three new columns are added:

	- ``MACD``        — difference between fast and slow EMAs
	- ``MACD_signal`` — EMA of the MACD line (the trigger line)
	- ``MACD_diff``   — histogram: ``MACD - MACD_signal``

	The returned DataFrame has NaN rows dropped so it is safe to pass directly
	into a vectorbt backtest or a Plotly chart without extra cleanup.

	Args:
	    df (pd.DataFrame): OHLCV DataFrame produced by ``fetch_ohlc`` or
	        ``fetch_batch``. Must contain at minimum the column named by
	        ``column`` (default ``"Close"``). Index must be datetime-like.
	        The function does **not** mutate the caller's object — it works
	        on an internal copy.
	    window_slow (int): Period for the slow EMA. Defaults to ``26``.
	        Standard MACD convention; change only for non-standard strategies.
	    window_fast (int): Period for the fast EMA. Defaults to ``12``.
	        Must be strictly less than ``window_slow``.
	    window_sign (int): Period for the signal EMA. Defaults to ``9``.
	    column (str): Name of the price column to compute MACD on.
	        Defaults to ``"Close"``. Use ``"Adj Close"`` if ``auto_adjust``
	        was not set on the yfinance download (not standard in this project).

	Returns:
	    pd.DataFrame | None: Copy of ``df`` with three columns appended:
	    ``MACD``, ``MACD_signal``, ``MACD_diff``. NaN rows are dropped
	    (first ``window_slow + window_sign - 2`` rows will be removed).
	    Returns ``None`` if input validation fails or computation raises.

	Raises:
	    This function does **not** propagate exceptions — all errors are caught,
	    logged at ``ERROR`` level, and ``None`` is returned. This keeps the
	    indicator layer consistent with the fetch layer's error contract.

	Example:
	    Basic usage with a pre-fetched DataFrame::

	        from src.data.fetch import fetch_ohlc
	        from src.data.indicators import macd

	        df = fetch_ohlc("RELIANCE.NS", period="1y", interval="1d")
	        if df is not None:
	            df_macd = macd(df)
	            if df_macd is not None:
	                print(df_macd[["Close", "MACD", "MACD_signal", "MACD_diff"]].tail())

	    Custom parameters (e.g. faster settings for intraday)::

	        df_macd = macd(df, window_slow=20, window_fast=8, window_sign=6)

	    Chaining with other indicators (all return copies, so safe to chain)::

	        df_with_macd = macd(df)
	        # pass df_with_macd into the next indicator function

	    Guard against None before accessing columns::

	        result = macd(df)
	        if result is None:
	            logger.warning("MACD computation failed — skipping this ticker")
	            # handle gracefully, e.g. skip this ticker in a screener loop

	Note:
	    - ``window_fast`` must be strictly less than ``window_slow``. Passing
	      equal or reversed values raises a ``ValueError`` internally which is
	      caught and logged.
	    - The minimum viable row count is ``window_slow + window_sign - 1``.
	      DataFrames shorter than this will produce an all-NaN result; the
	      function catches this and returns ``None`` with an explanatory warning.
	    - MACD does not use ``High``, ``Low``, or ``Volume`` — only ``Close``
	      (or the column named by ``column``). Passing a DataFrame with those
	      columns missing is fine as long as ``column`` is present.
	"""
	# ------------------------------------------------------------------
	# 1. Input validation — check before touching any computation
	# ------------------------------------------------------------------

	# Reject None input explicitly so the error message is actionable
	if df is None:
		logger.error(
			"macd() received None as input — pass a DataFrame from fetch_ohlc()"
		)
		return None

	# Must be a DataFrame (not a Series, dict, etc.)
	if not isinstance(df, pd.DataFrame):
		logger.error("macd() expected pd.DataFrame, got %s", type(df).__name__)
		return None

	# Must be non-empty
	if df.empty:
		logger.warning("macd() received an empty DataFrame — nothing to compute")
		return None

	# The target price column must exist
	if column not in df.columns:
		logger.error(
			"macd() could not find column '%s' in DataFrame. Available columns: %s",
			column,
			list(df.columns),
		)
		return None

	# window_fast must be strictly less than window_slow — standard MACD contract
	if window_fast >= window_slow:
		logger.error(
			"macd() requires window_fast (%d) < window_slow (%d). "
			"Received equal or inverted values — check your parameters.",
			window_fast,
			window_slow,
		)
		return None

	# All window values must be positive integers
	for name, value in [
		("window_slow", window_slow),
		("window_fast", window_fast),
		("window_sign", window_sign),
	]:
		if not isinstance(value, int) or value <= 0:
			logger.error(
				"macd() parameter '%s' must be a positive integer, got %r",
				name,
				value,
			)
			return None

	# Minimum row count: need at least (window_slow + window_sign - 1) rows
	# for the ta library to produce at least one non-NaN value.
	min_rows = window_slow + window_sign - 1
	if len(df) < min_rows:
		logger.warning(
			"macd() needs at least %d rows for window_slow=%d + window_sign=%d "
			"but DataFrame only has %d rows. Returning None.",
			min_rows,
			window_slow,
			window_sign,
			len(df),
		)
		return None

	# ------------------------------------------------------------------
	# 2. Computation — wrapped in try/except; ta errors must not crash caller
	# ------------------------------------------------------------------
	try:
		# Work on a copy — never mutate the caller's DataFrame
		result = df.copy()

		logger.info(
			"Computing MACD for %d rows "
			"(window_slow=%d, window_fast=%d, window_sign=%d, column='%s')",
			len(result),
			window_slow,
			window_fast,
			window_sign,
			column,
		)

		macd_obj = MACD(
			close=result[column],
			window_slow=window_slow,
			window_fast=window_fast,
			window_sign=window_sign,
			fillna=False,  # explicit NaNs are better than silent zeros
		)

		# Append the three standard MACD columns
		result["MACD"] = macd_obj.macd()  # fast EMA − slow EMA
		result["MACD_signal"] = macd_obj.macd_signal()  # signal (trigger) line
		result["MACD_diff"] = macd_obj.macd_diff()  # histogram value

	except Exception as e:
		logger.error("macd() computation failed unexpectedly: %s", e, exc_info=True)
		return None

	# ------------------------------------------------------------------
	# 3. Post-computation cleanup
	# ------------------------------------------------------------------

	# Drop NaN rows produced by the rolling windows — standard project convention.
	# Callers (vectorbt, Plotly charts, screener engine) all expect clean data.
	rows_before = len(result)
	result.dropna(inplace=True)
	rows_dropped = rows_before - len(result)

	if rows_dropped > 0:
		logger.info(
			"Dropped %d NaN rows after MACD calculation (%d rows remaining)",
			rows_dropped,
			len(result),
		)

	# Sanity check: if dropna() wiped everything, something is very wrong
	if result.empty:
		logger.warning(
			"macd() produced an all-NaN result after dropna() — "
			"DataFrame may be too short or price column contains only NaNs."
		)
		return None

	logger.info(
		"MACD computed successfully — %d usable rows, "
		"columns added: MACD, MACD_signal, MACD_diff",
		len(result),
	)

	return result


# ---------------------------------------------------------------------------
# SMA Indicator
# ---------------------------------------------------------------------------


def calculate_sma(
	df: pd.DataFrame,
	windows: list[int] | None = None,
	col: str = "Close",
) -> pd.DataFrame | None:
	"""Calculate Simple Moving Averages for multiple windows and append as columns.

	Iterates over each window, computes a rolling mean on the specified price
	column via the ``ta`` library's ``SMAIndicator``, and writes the result into
	a new column named ``SMA<window>`` (e.g. ``SMA20``, ``SMA50``).
	Rows where ANY of the new SMA columns are NaN (i.e. the first
	``max(windows) - 1`` rows) are dropped before returning, so the DataFrame
	is safe to pass directly into a vectorbt backtest.

	Args:
		df (pd.DataFrame): OHLCV DataFrame as returned by ``fetch_ohlc`` or
			``fetch_batch``. Must contain the column specified by ``col``.
			Index should be a DatetimeIndex — a non-DatetimeIndex is accepted
			with a warning but may cause issues in downstream vectorbt usage.
		windows (list[int]): Ordered list of rolling window sizes in bars.
			Defaults to ``[20, 50]`` (SMA20 and SMA50 — the Phase 3
			crossover strategy pair). Each window produces one new column:
			``SMA<window>``. Duplicate values are deduplicated automatically.
		col (str): Price column to compute SMA on. Defaults to ``"Close"``.
			Must exist in ``df`` and must not be entirely NaN.

	Returns:
		pd.DataFrame | None: Copy of the input DataFrame with one new column
		per unique window (e.g. ``SMA20``, ``SMA50``) appended.
		Leading NaN rows (up to ``max(windows) - 1``) are dropped.
		Original columns are never modified.
		Returns ``None`` if any unrecoverable error occurs — callers must
		guard against ``None`` before using the result.

	Raises:
		No exceptions are raised — all errors are logged and ``None``
		is returned so the pipeline stays alive on bad input.

	Example:
		Standard crossover pair (SMA20 + SMA50)::

			df = fetch_ohlc("RELIANCE.NS", period="1y")
			df = calculate_sma(df)            # default [20, 50]
			if df is None:
				...                           # handle failure
			# df now has columns: Open High Low Close Volume SMA20 SMA50

		Custom windows::

			df = calculate_sma(df, windows=[10, 20, 200])
			# df now has columns: ... SMA10 SMA20 SMA200

		Generate crossover signal after calling this::

			df["signal"] = (
				(df["SMA20"] > df["SMA50"]) &
				(df["SMA20"].shift(1) <= df["SMA50"].shift(1))
			).astype(int)   # 1 on the bar where SMA20 crosses above SMA50

	Note:
		SMA is the simplest trend indicator — no weighting, equal contribution
		from every bar in the window. Crossover strategies (SMA20 / SMA50)
		are the Phase 3 primary strategy defined in ``CLAUDE.md §11``.
		For smoother, more responsive signals consider EMA (``calculate_ema``),
		which weights recent bars more heavily.
	"""
	if windows is None:
		windows = [20, 50]

	# ------------------------------------------------------------------ #
	# 1. Validate inputs before touching the DataFrame                     #
	# ------------------------------------------------------------------ #
	try:
		# Guard: windows must be a non-empty list
		if not windows:
			logger.error("'windows' is empty — must contain at least one value.")
			return None

		# Guard: every window must be a plain integer >= 1
		# Non-integer values (e.g. 20.5) would be silently truncated or
		# cause unexpected behaviour inside SMAIndicator — reject early.
		for w in windows:
			if not isinstance(w, int):
				logger.error(
					"All window values must be integers, got %s (%s).",
					w,
					type(w).__name__,
				)
				return None
			if w < 1:
				logger.error("Window size must be >= 1, got %d.", w)
				return None

		# Deduplicate windows while preserving order so SMA20 always comes
		# before SMA50 in the column output regardless of input order.
		# e.g. [20, 20, 50] → [20, 50]
		seen: set[int] = set()
		deduped: list[int] = []
		for w in windows:
			if w in seen:
				logger.warning("Duplicate window %d removed from windows list.", w)
			else:
				seen.add(w)
				deduped.append(w)
		windows = deduped

	except Exception as e:
		logger.error("Unexpected error during input validation: %s", e)
		return None

	# ------------------------------------------------------------------ #
	# 2. Validate the DataFrame itself                                     #
	# ------------------------------------------------------------------ #
	try:
		# Guard: empty DataFrame — nothing to compute
		if df.empty:
			logger.error("Input DataFrame is empty — cannot compute SMA.")
			return None

		# Guard: target column must exist
		if col not in df.columns:
			logger.error(
				"Column '%s' not found in DataFrame. Available columns: %s",
				col,
				list(df.columns),
			)
			return None

		# Guard: target column must not be entirely NaN
		# A fully NaN column would produce all-NaN SMA columns, which
		# dropna() would then wipe completely — silent data loss.
		if df[col].isna().all():
			logger.error("Column '%s' is entirely NaN — cannot compute SMA.", col)
			return None

		# Warn if partially NaN — SMAIndicator will silently propagate NaNs
		# through any window that overlaps a NaN value.
		nan_count = df[col].isna().sum()
		if nan_count:
			logger.warning(
				"Column '%s' contains %d NaN value(s) — SMA may be affected.",
				col,
				nan_count,
			)

		# Guard: DataFrame must have enough rows for the largest window.
		# If not, SMAIndicator returns all NaN and dropna() wipes everything.
		# e.g. windows=[200] on a 50-row DataFrame → silent empty result.
		largest_window = max(windows)
		if len(df) < largest_window:
			logger.error(
				"DataFrame has %d rows but largest window is %d — "
				"not enough data to produce any valid SMA value. "
				"Fetch a longer period or reduce the window size.",
				len(df),
				largest_window,
			)
			return None

		# Warn if the index is not a DatetimeIndex — fetch_ohlc always
		# produces one, but a raw DataFrame passed directly might not.
		# Downstream vectorbt usage requires a DatetimeIndex.
		if not isinstance(df.index, pd.DatetimeIndex):
			logger.warning(
				"DataFrame index is not a DatetimeIndex (%s). "
				"Downstream vectorbt usage may fail.",
				type(df.index).__name__,
			)

	except Exception as e:
		logger.error("Unexpected error while validating DataFrame: %s", e)
		return None

	# ------------------------------------------------------------------ #
	# 3. Compute SMAs                                                      #
	# ------------------------------------------------------------------ #
	try:
		# Work on a copy — never mutate the caller's DataFrame.
		# Callers often reuse the same df across multiple indicator calls.
		df = df.copy()

		for window in windows:
			col_name = f"SMA{window}"
			df[col_name] = SMAIndicator(close=df[col], window=window).sma_indicator()
			logger.info(
				"Computed %s (window=%d) — first valid index: %s",
				col_name,
				window,
				df[col_name].first_valid_index(),
			)

	except Exception as e:
		logger.error("SMAIndicator computation failed: %s", e)
		return None

	# ------------------------------------------------------------------ #
	# 4. Drop leading NaN rows                                             #
	# ------------------------------------------------------------------ #
	try:
		# Drop AFTER all windows are computed — not after each one.
		# Reason: a row that passes SMA20's NaN check may still be NaN
		# for SMA50 if dropped mid-loop, producing a false clean row.
		sma_cols = [f"SMA{w}" for w in windows]
		rows_before = len(df)
		df.dropna(subset=sma_cols, inplace=True)
		dropped = rows_before - len(df)

		if dropped:
			logger.info(
				"Dropped %d leading NaN row(s) after SMA calculation "
				"(largest window: %d).",
				dropped,
				largest_window,
			)

		# Sanity check: if the entire DataFrame was wiped after dropna,
		# something went wrong that the row-count guard above didn't catch
		# (e.g. NaNs in the middle of the price series that broke every window).
		if df.empty:
			logger.error(
				"DataFrame is empty after dropna — all rows were NaN. "
				"Check '%s' column for gaps or corrupt data.",
				col,
			)
			return None

	except Exception as e:
		logger.error("Unexpected error during dropna step: %s", e)
		return None

	logger.info(
		"calculate_sma complete — %d rows returned, columns added: %s",
		len(df),
		sma_cols,
	)
	return df


# ---------------------------------------------------------------------------
# Smoke test — run with: python src/data/indicators.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[
			logging.StreamHandler(sys.stdout),
		],
	)

	# Import fetch here (inside __main__) so indicators.py stays import-clean
	# when used as a library — no circular dependency risk
	try:
		from fetch import fetch_ohlc  # works when run from src/data/
	except ImportError:
		from src.data.fetch import fetch_ohlc  # works when run from repo root

	logger.info("--- Smoke test: MACD indicator ---")

	# ---- Test 1: Normal path ----
	logger.info("Test 1 — normal path: RELIANCE.NS, 1y daily")
	df = fetch_ohlc("RELIANCE.NS", period="1y", interval="1d")
	if df is not None:
		result = macd(df)
		if result is not None:
			logger.info(
				"PASSED — shape: %s, columns: %s",
				result.shape,
				list(result.columns),
			)
			logger.info(
				"Last 3 rows:\n%s",
				result[["Close", "MACD", "MACD_signal", "MACD_diff"]]
				.tail(3)
				.to_string(),
			)
		else:
			logger.error("FAILED — macd() returned None on valid input")
	else:
		logger.warning("Skipping Test 1 — fetch returned None (network unavailable?)")

	# ---- Test 2: Empty DataFrame ----
	logger.info("Test 2 — empty DataFrame input")
	result_empty = macd(pd.DataFrame())
	assert result_empty is None, "Expected None for empty DataFrame"
	logger.info("PASSED — returned None for empty DataFrame")

	# ---- Test 3: Missing Close column ----
	logger.info("Test 3 — missing 'Close' column")
	df_no_close = pd.DataFrame({"Open": [100, 101], "High": [102, 103]})
	result_no_close = macd(df_no_close)
	assert result_no_close is None, "Expected None when Close column is absent"
	logger.info("PASSED — returned None for missing Close column")

	# ---- Test 4: window_fast >= window_slow ----
	logger.info("Test 4 — inverted windows (window_fast >= window_slow)")
	if df is not None:
		result_inverted = macd(df, window_fast=26, window_slow=12)
		assert result_inverted is None, "Expected None for inverted window params"
		logger.info("PASSED — returned None for inverted window params")

	# ---- Test 5: DataFrame too short ----
	logger.info("Test 5 — DataFrame shorter than minimum required rows")
	df_short = pd.DataFrame({"Close": [100.0] * 10})  # only 10 rows, need 34
	result_short = macd(df_short)
	assert result_short is None, "Expected None for too-short DataFrame"
	logger.info("PASSED — returned None for too-short DataFrame")

	# ---- Test 6: None input ----
	logger.info("Test 6 — None input")
	result_none = macd(None)  # type: ignore[arg-type]
	assert result_none is None, "Expected None for None input"
	logger.info("PASSED — returned None for None input")

	# ---- Test 7: Custom parameters ----
	logger.info(
		"Test 7 — custom parameters (window_slow=20, window_fast=8, window_sign=6)"
	)
	if df is not None:
		result_custom = macd(df, window_slow=20, window_fast=8, window_sign=6)
		if result_custom is not None:
			logger.info("PASSED — custom params shape: %s", result_custom.shape)
		else:
			logger.error("FAILED — macd() returned None on custom valid params")

	# ---- Test 8: SMA smoke test ----
	logger.info("--- Smoke test: SMA indicator ---")
	if df is not None:
		df_sma = calculate_sma(df.copy())
		if (
			df_sma is not None
			and "SMA20" in df_sma.columns
			and "SMA50" in df_sma.columns
		):
			logger.info(
				"PASSED — calculate_sma() returned %d rows with SMA20, SMA50",
				len(df_sma),
			)
		else:
			logger.error("FAILED — calculate_sma() returned unexpected result")

	logger.info("--- All smoke tests complete ---")
