import logging

import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator, SMAIndicator
from ta.volatility import AverageTrueRange, BollingerBands

# ---------------------------------------------------------------------------
# Module-level logger — no basicConfig here; caller / __main__ configures it
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# MACD
# ---------------------------------------------------------------------------


def movingAverageConvergenceDivergence(
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
	        from src.data.indicators import movingAverageConvergenceDivergence

	        df = fetch_ohlc("RELIANCE.NS", period="1y", interval="1d")
	        if df is not None:
	            df_macd = movingAverageConvergenceDivergence(df)
	            if df_macd is not None:
	                print(df_macd[["Close", "MACD", "MACD_signal", "MACD_diff"]].tail())

	    Custom parameters (e.g. faster settings for intraday)::

	        df_macd = movingAverageConvergenceDivergence(df, window_slow=20, window_fast=8, window_sign=6)

	    Chaining with other indicators (all return copies, so safe to chain)::

	        df_with_macd = movingAverageConvergenceDivergence(df)
	        # pass df_with_macd into the next indicator function

	    Guard against None before accessing columns::

	        result = movingAverageConvergenceDivergence(df)
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
			"movingAverageConvergenceDivergence() received None as input — pass a DataFrame from fetch_ohlc()"
		)
		return None

	# Must be a DataFrame (not a Series, dict, etc.)
	if not isinstance(df, pd.DataFrame):
		logger.error(
			"movingAverageConvergenceDivergence() expected pd.DataFrame, got %s",
			type(df).__name__,
		)
		return None

	# Must be non-empty
	if df.empty:
		logger.warning(
			"movingAverageConvergenceDivergence() received an empty DataFrame — nothing to compute"
		)
		return None

	# The target price column must exist
	if column not in df.columns:
		logger.error(
			"movingAverageConvergenceDivergence() could not find column '%s' in DataFrame. Available columns: %s",
			column,
			list(df.columns),
		)
		return None

	# window_fast must be strictly less than window_slow — standard MACD contract
	if window_fast >= window_slow:
		logger.error(
			"movingAverageConvergenceDivergence() requires window_fast (%d) < window_slow (%d). "
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
				"movingAverageConvergenceDivergence() parameter '%s' must be a positive integer, got %r",
				name,
				value,
			)
			return None

	# Minimum row count: need at least (window_slow + window_sign - 1) rows
	# for the ta library to produce at least one non-NaN value.
	min_rows = window_slow + window_sign - 1
	if len(df) < min_rows:
		logger.warning(
			"movingAverageConvergenceDivergence() needs at least %d rows for window_slow=%d + window_sign=%d "
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
		logger.error(
			"movingAverageConvergenceDivergence() computation failed unexpectedly: %s",
			e,
			exc_info=True,
		)
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
			"movingAverageConvergenceDivergence() produced an all-NaN result after dropna() — "
			"DataFrame may be too short or price column contains only NaNs."
		)
		return None

	logger.info(
		"MACD computed successfully — %d usable rows, "
		"columns added: MACD, MACD_signal, MACD_diff",
		len(result),
	)

	return result


# Alias — shorthand, same function as movingAverageConvergenceDivergence()
macd = movingAverageConvergenceDivergence


# ---------------------------------------------------------------------------
# EMA
# ---------------------------------------------------------------------------
def exponentialMovingAverage(
	df: pd.DataFrame, window: int, col: str = "Close"
) -> pd.DataFrame | None:
	"""Calculate Exponential Moving Average and append as a column.

	Matches the df-in/df-out contract used by ``simpleMovingAverage``, ``movingAverageConvergenceDivergence``,
	and ``bollingerBands`` (ADR-0002) — indicators.py is the sole place
	indicators are calculated, and every indicator appends to one DataFrame
	so downstream callers (screener, strategy) work off a single row of
	merged columns instead of reassembling separate Series.

	Args:
		df (pd.DataFrame): OHLCV DataFrame produced by ``fetch_ohlc`` or
			``fetch_batch``. Must contain the column named by ``col``.
		window (int): EMA lookback period. Must be a positive integer.
		col (str): Price column to compute EMA on. Defaults to ``"Close"``.

	Returns:
		pd.DataFrame | None: Copy of ``df`` with one new column
		``EMA<window>`` appended. Leading NaN rows (first ``window - 1``)
		are dropped. Returns ``None`` if validation or computation fails.
	"""
	if df is None:
		logger.error(
			"exponentialMovingAverage() received None as input — pass a DataFrame from fetch_ohlc()"
		)
		return None

	if not isinstance(df, pd.DataFrame):
		logger.error(
			"exponentialMovingAverage() expected pd.DataFrame, got %s",
			type(df).__name__,
		)
		return None

	if df.empty:
		logger.warning(
			"exponentialMovingAverage() received an empty DataFrame — nothing to compute"
		)
		return None

	if col not in df.columns:
		logger.error(
			"exponentialMovingAverage() could not find column '%s' in DataFrame. Available columns: %s",
			col,
			list(df.columns),
		)
		return None

	if not isinstance(window, int) or window <= 0:
		logger.error(
			"exponentialMovingAverage() parameter 'window' must be a positive integer, got %r",
			window,
		)
		return None

	try:
		result = df.copy()
		col_name = f"EMA{window}"

		logger.info(
			"Computing EMA for %d rows (window=%d, col='%s')",
			len(result),
			window,
			col,
		)

		result[col_name] = EMAIndicator(
			close=result[col],
			window=window,
		).ema_indicator()

	except Exception as e:
		logger.error(
			"exponentialMovingAverage() computation failed unexpectedly: %s",
			e,
			exc_info=True,
		)
		return None

	rows_before = len(result)
	result.dropna(subset=[col_name], inplace=True)
	rows_dropped = rows_before - len(result)

	if rows_dropped > 0:
		logger.info(
			"Dropped %d NaN rows after EMA calculation (%d rows remaining)",
			rows_dropped,
			len(result),
		)

	if result.empty:
		logger.warning(
			"exponentialMovingAverage() produced an all-NaN result after dropna() — "
			"DataFrame may be too short for window=%d.",
			window,
		)
		return None

	logger.info(
		"EMA computed successfully — %d usable rows, column added: %s",
		len(result),
		col_name,
	)
	return result


# Alias — shorthand, same function as exponentialMovingAverage()
ema = exponentialMovingAverage


# ---------------------------------------------------------------------------
# RSI
# ---------------------------------------------------------------------------
def relativeStrengthIndex(
	df: pd.DataFrame, window: int = 14, col: str = "Close"
) -> pd.DataFrame | None:
	"""Calculate Relative Strength Index and append as a column.

	Uses ``ta.momentum.RSIIndicator`` (Wilder smoothing) so the project has
	exactly one RSI implementation — ``indicators.py`` is the sole place
	indicators are calculated (ADR-0002). Screener and strategy code read
	the ``RSI`` column off the df rather than computing their own.

	Args:
		df (pd.DataFrame): OHLCV DataFrame produced by ``fetch_ohlc`` or
			``fetch_batch``. Must contain the column named by ``col``.
		window (int): RSI lookback period. Standard default is ``14``.
			Must be a positive integer.
		col (str): Price column to compute RSI on. Defaults to ``"Close"``.

	Returns:
		pd.DataFrame | None: Copy of ``df`` with one new column ``RSI``
		appended. Leading NaN rows (first ``window`` rows) are dropped.
		Returns ``None`` if validation or computation fails.
	"""
	if df is None:
		logger.error(
			"relativeStrengthIndex() received None as input — pass a DataFrame from fetch_ohlc()"
		)
		return None

	if not isinstance(df, pd.DataFrame):
		logger.error(
			"relativeStrengthIndex() expected pd.DataFrame, got %s", type(df).__name__
		)
		return None

	if df.empty:
		logger.warning(
			"relativeStrengthIndex() received an empty DataFrame — nothing to compute"
		)
		return None

	if col not in df.columns:
		logger.error(
			"relativeStrengthIndex() could not find column '%s' in DataFrame. Available columns: %s",
			col,
			list(df.columns),
		)
		return None

	if not isinstance(window, int) or window <= 0:
		logger.error(
			"relativeStrengthIndex() parameter 'window' must be a positive integer, got %r",
			window,
		)
		return None

	try:
		result = df.copy()

		logger.info(
			"Computing RSI for %d rows (window=%d, col='%s')",
			len(result),
			window,
			col,
		)

		result["RSI"] = RSIIndicator(close=result[col], window=window).rsi()

	except Exception as e:
		logger.error(
			"relativeStrengthIndex() computation failed unexpectedly: %s",
			e,
			exc_info=True,
		)
		return None

	rows_before = len(result)
	result.dropna(subset=["RSI"], inplace=True)
	rows_dropped = rows_before - len(result)

	if rows_dropped > 0:
		logger.info(
			"Dropped %d NaN rows after RSI calculation (%d rows remaining)",
			rows_dropped,
			len(result),
		)

	if result.empty:
		logger.warning(
			"relativeStrengthIndex() produced an all-NaN result after dropna() — "
			"DataFrame may be too short for window=%d.",
			window,
		)
		return None

	logger.info(
		"RSI computed successfully — %d usable rows, column added: RSI", len(result)
	)
	return result


# Alias — shorthand, same function as relativeStrengthIndex()
rsi = relativeStrengthIndex


# ---------------------------------------------------------------------------
# ATR
# ---------------------------------------------------------------------------
def averageTrueRange(df: pd.DataFrame, window: int = 14) -> pd.DataFrame | None:
	"""Calculate Average True Range and append as a column.

	Uses ``ta.volatility.AverageTrueRange``, which requires High, Low, and
	Close columns (unlike the other indicators in this module, which only
	need a single price column).

	Args:
		df (pd.DataFrame): OHLCV DataFrame produced by ``fetch_ohlc`` or
			``fetch_batch``. Must contain ``High``, ``Low``, and ``Close``.
		window (int): ATR lookback period. Standard default is ``14``.
			Must be a positive integer.

	Returns:
		pd.DataFrame | None: Copy of ``df`` with one new column ``ATR``
		appended. Leading NaN rows (first ``window`` rows) are dropped.
		Returns ``None`` if validation or computation fails.
	"""
	if df is None:
		logger.error(
			"averageTrueRange() received None as input — pass a DataFrame from fetch_ohlc()"
		)
		return None

	if not isinstance(df, pd.DataFrame):
		logger.error(
			"averageTrueRange() expected pd.DataFrame, got %s", type(df).__name__
		)
		return None

	if df.empty:
		logger.warning(
			"averageTrueRange() received an empty DataFrame — nothing to compute"
		)
		return None

	missing = [c for c in ("High", "Low", "Close") if c not in df.columns]
	if missing:
		logger.error(
			"averageTrueRange() missing required column(s) %s. Available columns: %s",
			missing,
			list(df.columns),
		)
		return None

	if not isinstance(window, int) or window <= 0:
		logger.error(
			"averageTrueRange() parameter 'window' must be a positive integer, got %r",
			window,
		)
		return None

	try:
		result = df.copy()

		logger.info("Computing ATR for %d rows (window=%d)", len(result), window)

		result["ATR"] = AverageTrueRange(
			high=result["High"],
			low=result["Low"],
			close=result["Close"],
			window=window,
		).average_true_range()

	except Exception as e:
		logger.error(
			"averageTrueRange() computation failed unexpectedly: %s", e, exc_info=True
		)
		return None

	rows_before = len(result)
	result.dropna(subset=["ATR"], inplace=True)
	rows_dropped = rows_before - len(result)

	if rows_dropped > 0:
		logger.info(
			"Dropped %d NaN rows after ATR calculation (%d rows remaining)",
			rows_dropped,
			len(result),
		)

	if result.empty:
		logger.warning(
			"averageTrueRange() produced an all-NaN result after dropna() — "
			"DataFrame may be too short for window=%d.",
			window,
		)
		return None

	logger.info(
		"ATR computed successfully — %d usable rows, column added: ATR", len(result)
	)
	return result


# Alias — shorthand, same function as averageTrueRange()
atr = averageTrueRange


# ---------------------------------------------------------------------------
# VWAP — manual implementation; `ta` library has no daily VWAP (CLAUDE.md §20.3)
# ---------------------------------------------------------------------------
def volumeWeightedAveragePrice(df: pd.DataFrame) -> pd.DataFrame | None:
	"""Calculate cumulative Volume Weighted Average Price and append as a column.

	``ta`` does not provide a daily VWAP, so this is computed manually per
	CLAUDE.md §20.3: typical price (HLC/3) weighted by volume, cumulative
	from the start of the DataFrame. Resets only if the caller resamples
	per-day before calling — this function does not reset per trading day
	on its own.

	Args:
		df (pd.DataFrame): OHLCV DataFrame produced by ``fetch_ohlc`` or
			``fetch_batch``. Must contain ``High``, ``Low``, ``Close``,
			and ``Volume``.

	Returns:
		pd.DataFrame | None: Copy of ``df`` with one new column ``VWAP``
		appended. Returns ``None`` if validation fails.
	"""
	if df is None:
		logger.error(
			"volumeWeightedAveragePrice() received None as input — pass a DataFrame from fetch_ohlc()"
		)
		return None

	if not isinstance(df, pd.DataFrame):
		logger.error(
			"volumeWeightedAveragePrice() expected pd.DataFrame, got %s",
			type(df).__name__,
		)
		return None

	if df.empty:
		logger.warning(
			"volumeWeightedAveragePrice() received an empty DataFrame — nothing to compute"
		)
		return None

	missing = [c for c in ("High", "Low", "Close", "Volume") if c not in df.columns]
	if missing:
		logger.error(
			"volumeWeightedAveragePrice() missing required column(s) %s. Available columns: %s",
			missing,
			list(df.columns),
		)
		return None

	if (df["Volume"] == 0).all():
		logger.warning(
			"volumeWeightedAveragePrice() received all-zero Volume — VWAP would be undefined"
		)
		return None

	try:
		result = df.copy()

		logger.info("Computing VWAP for %d rows", len(result))

		typical_price = (result["High"] + result["Low"] + result["Close"]) / 3
		result["VWAP"] = (typical_price * result["Volume"]).cumsum() / result[
			"Volume"
		].cumsum()

	except Exception as e:
		logger.error(
			"volumeWeightedAveragePrice() computation failed unexpectedly: %s",
			e,
			exc_info=True,
		)
		return None

	rows_before = len(result)
	result.dropna(subset=["VWAP"], inplace=True)
	rows_dropped = rows_before - len(result)

	if rows_dropped > 0:
		logger.info(
			"Dropped %d NaN row(s) after VWAP calculation (%d rows remaining)",
			rows_dropped,
			len(result),
		)

	if result.empty or result["VWAP"].isna().all():
		logger.warning("volumeWeightedAveragePrice() produced an all-NaN result")
		return None

	logger.info("VWAP computed successfully — %d rows, column added: VWAP", len(result))
	return result


# Alias — shorthand, same function as volumeWeightedAveragePrice()
vwap = volumeWeightedAveragePrice


# SMA Indicator
# ---------------------------------------------------------------------------


def simpleMovingAverage(
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
			df = simpleMovingAverage(df)            # default [20, 50]
			if df is None:
				...                           # handle failure
			# df now has columns: Open High Low Close Volume SMA20 SMA50

		Custom windows::

			df = simpleMovingAverage(df, windows=[10, 20, 200])
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
		"simpleMovingAverage complete — %d rows returned, columns added: %s",
		len(df),
		sma_cols,
	)
	return df


# Alias — shorthand, same function as simpleMovingAverage()
sma = simpleMovingAverage


# ---------------------------------------------------------------------------
# Smoke test — run with: python src/data/indicators.py
# ---------------------------------------------------------------------------


# Bollinger Bands


def bollingerBands(
	df: pd.DataFrame,
	window: int = 20,
	window_dev: float = 2.0,
	col: str = "Close",
) -> pd.DataFrame | None:
	"""Add Bollinger Bands (BB_upper, BB_mid, BB_lower, BB_width, BB_pct_b) to a OHLCV DataFrame.

	Bollinger Bands consist of three lines built around a Simple Moving Average:

	    Middle Band  = SMA(close, window)
	    Upper Band   = Middle Band + (window_dev × rolling std-dev)
	    Lower Band   = Middle Band - (window_dev × rolling std-dev)

	Two derived columns are also computed:

	    BB_width   = (Upper - Lower) / Middle
	                 Normalised band width. Values near zero indicate a
	                 "Bollinger Squeeze" — low volatility, possible breakout ahead.
	                 Values that spike sharply signal high volatility expansion.

	    BB_pct_b   = (Close - Lower) / (Upper - Lower)
	                 %b ("percent b") — positions the close within the band.
	                 > 1.0  → price above upper band (strong momentum / possible overextension)
	                 = 1.0  → price exactly on upper band
	                 = 0.5  → price at middle band (SMA)
	                 = 0.0  → price exactly on lower band
	                 < 0.0  → price below lower band (weak momentum / possible overextension)

	Args:
	    df (pd.DataFrame): OHLCV DataFrame with a DatetimeIndex.
	        Must contain the column named by ``col``. Typically the output of
	        ``fetch_ohlc()`` or ``fetch_batch()``, which already have
	        ``Open``, ``High``, ``Low``, ``Close``, ``Volume``.
	    window (int): Lookback period for the SMA and rolling standard deviation.
	        Standard default is 20 (represents ~1 trading month of daily bars).
	        Shorter windows (e.g. 10) react faster but produce noisier bands.
	        Longer windows (e.g. 50) smooth the bands but lag more.
	        Must be >= 2. Must be <= len(df), otherwise all outputs are NaN.
	    window_dev (float): Number of standard deviations for the upper and lower bands.
	        Standard default is 2.0, which statistically contains ~95% of price
	        action assuming a normal distribution (Bollinger's original setting).
	        1.0 → tighter bands, more signals, more false positives.
	        2.5 or 3.0 → wider bands, fewer signals, higher confidence per signal.
	        Must be > 0.
	    col (str): Column name to use as the price series. Defaults to ``"Close"``.
	        Can be changed to ``"Adj Close"`` or any other numeric column present
	        in the DataFrame.

	Returns:
	    pd.DataFrame | None: Input DataFrame with five columns appended in-place:

	        - ``BB_upper``  (float): Upper Bollinger Band.
	        - ``BB_mid``    (float): Middle Band (SMA of ``col``).
	        - ``BB_lower``  (float): Lower Bollinger Band.
	        - ``BB_width``  (float): Normalised band width (BB_upper - BB_lower) / BB_mid.
	        - ``BB_pct_b``  (float): %b — price position within the band.

	        Rows with NaN in any of the five columns (the first ``window - 1`` rows)
	        are dropped before returning. The caller receives a clean, ready-to-use
	        DataFrame with no NaN rows in the BB columns.

	        Returns ``None`` (logged, not raised) if ``df`` is empty, ``col`` is
	        missing, ``window`` < 2, or ``window_dev`` <= 0.

	Example:
	    Basic usage with default 20-period, 2-std-dev bands::

	        df = fetch_ohlc("RELIANCE.NS", period="1y", interval="1d")
	        if df is not None:
	            df = bollingerBands(df)
	            print(df[["Close", "BB_upper", "BB_mid", "BB_lower"]].tail())

	    Custom settings — tighter 10-period bands with 1.5 std-dev::

	        df = bollingerBands(df, window=10, window_dev=1.5)

	    Squeeze detection — identify consolidation periods::

	        df = bollingerBands(df)
	        squeeze_rows = df[df["BB_width"] < df["BB_width"].quantile(0.1)]
	        logger.info("Squeeze periods found: %d rows", len(squeeze_rows))

	    %b based signal (price crossing above midline)::

	        df = bollingerBands(df)
	        cross_above_mid = (df["BB_pct_b"] > 0.5) & (df["BB_pct_b"].shift(1) <= 0.5)
	        logger.info("Mid-band upward crossovers: %d", cross_above_mid.sum())

	Note:
	    - Uses ``ta.volatility.BollingerBands`` internally, which computes the
	      rolling std-dev with ``ddof=0`` (population std, not sample std).
	      This matches John Bollinger's original specification.
	    - BB_pct_b will produce a ZeroDivisionError-equivalent (NaN) on any row
	      where Upper == Lower (i.e. zero volatility). This is handled silently
	      by pandas division; such rows are dropped by the final ``dropna``.
	    - Bollinger Bands are a lagging indicator — the first valid row appears
	      at index position ``window - 1``. Always verify ``len(df)`` is
	      substantially greater than ``window`` before calling.
	    - Never interpret band touch alone as a signal. Always combine with
	      momentum indicators (RSI, MACD) and trend context. See research notes
	      in ``docs/`` for the BB + MACD combined strategy.
	"""
	# ------------------------------------------------------------------ #
	# 1. Input validation                                                   #
	# ------------------------------------------------------------------ #

	if df.empty:
		logger.error("bollingerBands() received an empty DataFrame — nothing to compute")
		return None

	if col not in df.columns:
		logger.error(
			"bollingerBands() could not find column '%s' in DataFrame. Available columns: %s",
			col,
			list(df.columns),
		)
		return None

	if window < 2:
		logger.error(
			"bollingerBands() requires window >= 2, got %d. "
			"Bollinger Bands require at least 2 data points for std-dev.",
			window,
		)
		return None

	if window_dev <= 0:
		logger.error(
			"bollingerBands() requires window_dev > 0, got %s. "
			"Standard deviation multiplier cannot be zero or negative.",
			window_dev,
		)
		return None

	if len(df) < window:
		# Not a hard error — but all outputs will be NaN and then dropped,
		# leaving an empty DataFrame. Log a prominent warning so the caller
		# knows why they got nothing back.
		logger.warning(
			"DataFrame has only %d rows but window=%d — "
			"all Bollinger Band values will be NaN after dropna. "
			"Fetch more data or reduce window.",
			len(df),
			window,
		)

	logger.info(
		"Computing Bollinger Bands for %d rows | window=%d | window_dev=%.1f | col=%s",
		len(df),
		window,
		window_dev,
		col,
	)

	try:
		# Work on a copy — never mutate the caller's DataFrame.
		result = df.copy()

		# -------------------------------------------------------------- #
		# 2. Compute bands via ta.volatility.BollingerBands                #
		#                                                                   #
		# BollingerBands internally computes:                               #
		#   middle = close.rolling(window).mean()                           #
		#   std    = close.rolling(window).std(ddof=0)  ← population std    #
		#   upper  = middle + (window_dev * std)                            #
		#   lower  = middle - (window_dev * std)                            #
		# -------------------------------------------------------------- #

		bb = BollingerBands(
			close=result[col],
			window=window,
			window_dev=window_dev,
		)

		result["BB_upper"] = bb.bollinger_hband()  # Upper band
		result["BB_mid"] = bb.bollinger_mavg()  # Middle band (SMA)
		result["BB_lower"] = bb.bollinger_lband()  # Lower band

		# -------------------------------------------------------------- #
		# 3. Derived metrics                                                #
		# -------------------------------------------------------------- #

		# BB_width: normalised distance between bands relative to the midpoint.
		# Formula: (Upper - Lower) / Middle
		# This makes the width scale-independent — comparable across different
		# price levels and tickers. A squeeze is visible as a multi-period
		# trough in BB_width.
		result["BB_width"] = (result["BB_upper"] - result["BB_lower"]) / result["BB_mid"]

		# BB_pct_b: %b — where within the band the close sits.
		# Formula: (Close - Lower) / (Upper - Lower)
		# Values > 1 or < 0 mean price has broken outside the bands.
		# When Upper == Lower (zero volatility edge case), the result is NaN —
		# pandas division by zero yields NaN silently; handled by dropna below.
		result["BB_pct_b"] = (result[col] - result["BB_lower"]) / (
			result["BB_upper"] - result["BB_lower"]
		)

	except Exception as e:
		logger.error("bollingerBands() computation failed unexpectedly: %s", e, exc_info=True)
		return None

	# ------------------------------------------------------------------ #
	# 4. Drop NaN rows produced by the rolling window warm-up period        #
	#                                                                       #
	# The first (window - 1) rows have no valid SMA yet, so BB_upper,       #
	# BB_mid, BB_lower, BB_width, and BB_pct_b are all NaN. Drop them        #
	# before returning so the caller gets a clean DataFrame ready for        #
	# signal generation or backtesting.                                      #
	# ------------------------------------------------------------------ #

	rows_before = len(result)
	result.dropna(
		subset=["BB_upper", "BB_mid", "BB_lower", "BB_width", "BB_pct_b"], inplace=True
	)
	rows_dropped = rows_before - len(result)

	if rows_dropped > 0:
		logger.debug(
			"Dropped %d NaN warm-up rows (window=%d). Remaining rows: %d",
			rows_dropped,
			window,
			len(result),
		)

	if result.empty:
		logger.warning(
			"DataFrame is empty after dropna — all rows were NaN. "
			"This usually means len(df) < window (%d). Fetch more data.",
			window,
		)
		return None

	# ------------------------------------------------------------------ #
	# 5. Summary log — quick sanity check on the output                    #
	# ------------------------------------------------------------------ #

	last = result.iloc[-1]
	logger.info(
		"Bollinger Bands computed — latest bar | "
		"Close=%.2f | BB_upper=%.2f | BB_mid=%.2f | BB_lower=%.2f | "
		"BB_width=%.4f | BB_pct_b=%.4f",
		last[col],
		last["BB_upper"],
		last["BB_mid"],
		last["BB_lower"],
		last["BB_width"],
		last["BB_pct_b"],
	)

	return result


# Alias — shorthand, same function as bollingerBands()
bb = bollingerBands




if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example run — fetch a live ticker and print actual computed
	# values, rather than a synthetic smoke test. Edge cases live in
	# tests/test_indicators.py (pytest), not here.
	try:
		from fetch import fetch_ohlc  # works when run from src/data/
	except ImportError:
		from src.data.fetch import fetch_ohlc  # works when run from repo root

	TICKER = "RELIANCE.NS"
	logger.info("--- Indicator example run: %s, 1y daily ---", TICKER)

	df = fetch_ohlc(TICKER, period="1y", interval="1d")
	if df is None:
		logger.error("Could not fetch %s — check network connection. Exiting.", TICKER)
		sys.exit(1)

	for fn in (
		lambda d: movingAverageConvergenceDivergence(d),
		lambda d: sma(d, windows=[20, 50]),
		lambda d: ema(d, window=20),
		rsi,
		atr,
		vwap,
		bollingerBands,
	):
		result = fn(df)
		if result is not None:
			df = result

	cols = [
		c
		for c in (
			"Close",
			"SMA20",
			"SMA50",
			"EMA20",
			"RSI",
			"ATR",
			"VWAP",
			"MACD",
			"MACD_signal",
			"BB_upper",
			"BB_mid",
			"BB_lower",
		)
		if c in df.columns
	]

	logger.info("Latest 5 rows for %s:\n%s", TICKER, df[cols].tail(5).to_string())
	logger.info(
		"Latest values — Close=%.2f | SMA20=%.2f | SMA50=%.2f | EMA20=%.2f | RSI=%.1f | ATR=%.2f",
		df["Close"].iloc[-1],
		df["SMA20"].iloc[-1] if "SMA20" in df.columns else float("nan"),
		df["SMA50"].iloc[-1] if "SMA50" in df.columns else float("nan"),
		df["EMA20"].iloc[-1] if "EMA20" in df.columns else float("nan"),
		df["RSI"].iloc[-1] if "RSI" in df.columns else float("nan"),
		df["ATR"].iloc[-1] if "ATR" in df.columns else float("nan"),
	)
	logger.info("--- Example run complete (%d rows) ---", len(df))
