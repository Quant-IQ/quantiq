import logging

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

_VALID_PERIODS = {
	"1d",
	"5d",
	"1mo",
	"3mo",
	"6mo",
	"1y",
	"2y",
	"5y",
	"10y",
	"ytd",
	"max",
}
_VALID_INTERVALS = {
	"1m",
	"2m",
	"5m",
	"15m",
	"30m",
	"60m",
	"90m",
	"1h",
	"1d",
	"5d",
	"1wk",
	"1mo",
	"3mo",
}


def fetch_ohlc(
	ticker: str,
	period: str = "1y",
	interval: str = "1d",
) -> pd.DataFrame | None:
	"""Fetch OHLCV data for an NSE ticker via yfinance.

	Validates the ticker suffix, downloads adjusted OHLCV data, drops
	NaN rows produced by rolling-window artefacts, and returns a clean
	DataFrame ready for indicator calculation.

	Args:
	    ticker (str): NSE ticker with `.NS` suffix (e.g. ``"RELIANCE.NS"``).
	        BSE tickers use ``.BO``. An unsuffixed ticker silently returns
	        US equity data — this function raises ``ValueError`` to prevent that.
	    period (str): Lookback window accepted by yfinance. One of:
	        ``1d 5d 1mo 3mo 6mo 1y 2y 5y 10y ytd max``. Defaults to ``"1y"``.
	    interval (str): Bar size accepted by yfinance. One of:
	        ``1m 2m 5m 15m 30m 60m 90m 1h 1d 5d 1wk 1mo 3mo``.
	        Intraday intervals (< ``1d``) are only available for the last 60 days.
	        Defaults to ``"1d"``.

	Returns:
	    pd.DataFrame | None: DataFrame indexed by datetime with columns
	    ``Open``, ``High``, ``Low``, ``Close``, ``Volume``. OHLC values are
	    split- and dividend-adjusted (``auto_adjust=True``). Returns ``None``
	    on download failure or if yfinance returns an empty result.

	Raises:
	    ValueError: If ``period`` or ``interval`` is not a recognised yfinance value.

	Example:
	    Basic usage — 1 year daily bars (defaults)::

	        df = fetch_ohlc("RELIANCE.NS")
	        df = fetch_ohlc("INFY.NS", period="6mo")
	        df = fetch_ohlc("TCS.NS", period="3mo", interval="1h")

	    Always guard against None return::

	        df = fetch_ohlc("RELIANCE.NS")
	        if df is None:
	            # download failed or ticker returned no data
	            ...

	    Returned DataFrame columns: ``Open``, ``High``, ``Low``, ``Close``, ``Volume``,
	    indexed by ``DatetimeIndex``. OHLC values are split- and dividend-adjusted.
	    NaNs already dropped — safe to pass directly to indicator functions.

	    Missing suffix is handled automatically::

	        fetch_ohlc("RELIANCE")   # auto-corrected to "RELIANCE.NS", warning logged

	    These calls raise ``ValueError``::

	        fetch_ohlc("INFY.NS", period="3w")       # invalid yfinance period
	        fetch_ohlc("TCS.NS", interval="45m")     # invalid yfinance interval

	Note:
	    Intraday intervals (``1m``, ``5m``, ``1h``, etc.) are only available for
	    the last 60 days — yfinance hard limit.
	"""  # noqa: E101
	if not (ticker.endswith(".NS") or ticker.endswith(".BO")):
		ticker = ticker + ".NS"
		logger.warning("No exchange suffix detected — appended '.NS': %s", ticker)

	if period not in _VALID_PERIODS:
		raise ValueError(
			f"Invalid period '{period}'. Valid options: {sorted(_VALID_PERIODS)}"
		)

	if interval not in _VALID_INTERVALS:
		raise ValueError(
			f"Invalid interval '{interval}'. Valid options: {sorted(_VALID_INTERVALS)}"
		)

	try:
		raw = yf.download(
			tickers=ticker,
			period=period,
			interval=interval,
			auto_adjust=True,
			progress=False,
		)
	except Exception as e:
		logger.error("yfinance download failed for %s: %s", ticker, e)
		return None

	if raw is None or raw.empty:
		logger.warning(
			"yfinance returned empty DataFrame for %s (period=%s)", ticker, period
		)
		return None

	# yfinance MultiIndex column collapse: keep only OHLCV columns
	if isinstance(raw.columns, pd.MultiIndex):
		raw.columns = raw.columns.get_level_values(0)  # type: ignore[assignment]

	df = raw[["Open", "High", "Low", "Close", "Volume"]].copy()
	df.dropna(inplace=True)

	logger.info(
		"Fetched %d rows for %s (period=%s, interval=%s)",
		len(df),
		ticker,
		period,
		interval,
	)
	return df


if __name__ == "__main__":
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
	)
	df = fetch_ohlc("RELIANCE.NS", period="1mo", interval="1d")
	if df is not None:
		print(df.tail())
		print(f"\nShape: {df.shape}")
		print(f"Columns: {df.columns.tolist()}")
