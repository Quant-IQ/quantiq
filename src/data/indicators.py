import logging

import pandas as pd
from ta.trend import MACD

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
        logger.error(
            "macd() expected pd.DataFrame, got %s", type(df).__name__
        )
        return None

    # Must be non-empty
    if df.empty:
        logger.warning("macd() received an empty DataFrame — nothing to compute")
        return None

    # The target price column must exist
    if column not in df.columns:
        logger.error(
            "macd() could not find column '%s' in DataFrame. "
            "Available columns: %s",
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
        result["MACD"]        = macd_obj.macd()         # fast EMA − slow EMA
        result["MACD_signal"] = macd_obj.macd_signal()  # signal (trigger) line
        result["MACD_diff"]   = macd_obj.macd_diff()    # histogram value

    except Exception as e:
        logger.error(
            "macd() computation failed unexpectedly: %s", e, exc_info=True
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
            logger.info("Last 3 rows:\n%s",
                result[["Close", "MACD", "MACD_signal", "MACD_diff"]].tail(3).to_string()
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
    logger.info("Test 7 — custom parameters (window_slow=20, window_fast=8, window_sign=6)")
    if df is not None:
        result_custom = macd(df, window_slow=20, window_fast=8, window_sign=6)
        if result_custom is not None:
            logger.info(
                "PASSED — custom params shape: %s", result_custom.shape
            )
        else:
            logger.error("FAILED — macd() returned None on custom valid params")

    logger.info("--- Smoke test complete ---")






def sma(
    df: pd.DataFrame,
    window: int = 20,
    column: str = "Close",
) -> pd.DataFrame | None:
    """Append SMA column to an OHLCV DataFrame.

    Args:
        df (pd.DataFrame): OHLCV DataFrame. Must contain the column
            named by ``column`` (default ``"Close"``).
        window (int): Rolling window period. Defaults to 20.
        column (str): Price column to compute SMA on. Defaults to ``"Close"``.

    Returns:
        pd.DataFrame | None: Copy of ``df`` with ``SMA_{window}`` column
            appended. Returns None if input validation fails.

    Raises:
        This function does not propagate exceptions — all errors are
        caught, logged at ERROR level, and None is returned.
    """
    # 1. Input validation
    if df is None:
        logger.error("sma() received None as input")
        return None

    if not isinstance(df, pd.DataFrame):
        logger.error("sma() expected pd.DataFrame, got %s", type(df).__name__)
        return None

    if df.empty:
        logger.warning("sma() received an empty DataFrame")
        return None

    if column not in df.columns:
        logger.error(
            "sma() could not find column '%s'. Available: %s",
            column, list(df.columns),
        )
        return None

    if window < 1:
        logger.error("sma() window must be >= 1, got %d", window)
        return None

    # 2. Compute SMA
    try:
        result = df.copy()
        result[f"SMA_{window}"] = result[column].rolling(window=window).mean()
        result.dropna(inplace=True)
        return result
    except Exception as e:
        logger.error("sma() computation failed: %s", e)
        return None




if __name__ == "__main__":
    import yfinance as yf
    import plotly.graph_objects as go
    df = yf.download("RELIANCE.NS", start="2022-01-01", end="2024-12-31",auto_adjust=True)
    df.columns = df.columns.get_level_values(0)
    df.dropna(inplace=True)
    df20 = sma(df, window=20)
    df50 = sma(df, window=50)
    df200 = sma(df, window=200)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close"))
    fig1.add_trace(go.Scatter(x=df20.index, y=df20["SMA_20"], name="SMA 20"))
    fig1.add_trace(go.Scatter(x=df50.index, y=df50["SMA_50"], name="SMA 50"))
    fig1.add_trace(go.Scatter(x=df200.index, y=df200["SMA_200"], name="SMA 200"))
    fig1.update_layout(title="RELIANCE.NS - All SMAs")
    fig1.show()
    # --- Graph 2: Golden Cross & Death Cross ---
    df50 = sma(df, window=50)
    df50["Signal"] = 0
    df50.loc[df50["SMA_50"] < df20.loc[df50.index, "SMA_20"], "Signal"] = 1
    df50.loc[df50["SMA_50"] > df20.loc[df50.index, "SMA_20"], "Signal"] = -1
    df50["Crossover"] = df50["Signal"].diff()
    golden = df50[df50["Crossover"] == 2]
    death = df50[df50["Crossover"] == -2]
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close", opacity=0.6))
    fig2.add_trace(go.Scatter(x=df20.index, y=df20["SMA_20"], name="SMA 20"))
    fig2.add_trace(go.Scatter(x=df50.index, y=df50["SMA_50"], name="SMA 50"))
    fig2.add_trace(go.Scatter(x=golden.index, y=golden["Close"], mode="markers",
                              marker=dict(symbol="triangle-up", color="green", size=12),
                              name="Golden Cross"))
    fig2.add_trace(go.Scatter(x=death.index, y=death["Close"], mode="markers",
                              marker=dict(symbol="triangle-down", color="red", size=12),
                              name="Death Cross"))
    fig2.update_layout(title="Golden Cross & Death Cross")
    fig2.show()

    # --- Graph 3: Price vs SMA 50 ---
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close"))
    fig3.add_trace(go.Scatter(x=df50.index, y=df50["SMA_50"], name="SMA 50"))
    fig3.update_layout(title="Price vs SMA 50")
    fig3.show()

    # --- Graph 4: SMA Slope ---
    df20["SMA_20_slope"] = df20["SMA_20"].diff()
    colors = ["green" if v >= 0 else "red" for v in df20["SMA_20_slope"]]
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=df20.index, y=df20["SMA_20_slope"],
                          marker_color=colors, name="SMA 20 Slope"))
    fig4.update_layout(title="SMA 20 Slope (Momentum)")
    fig4.show()
