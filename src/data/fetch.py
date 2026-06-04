import logging
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

_CACHE_DIR = Path(__file__).parent / "cache" / "tickers"

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

_INTRADAY_INTERVALS = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}


def _cache_path(ticker: str, period: str, interval: str) -> Path:
	"""Return parquet cache path for a ticker/period/interval combination."""
	safe = ticker.replace("/", "_")
	return _CACHE_DIR / f"{safe}__{period}__{interval}.parquet"


def _is_stale(path: Path, interval: str) -> bool:
	"""Return True if cache file is missing or older than the staleness threshold.

	Args:
		path (Path): Cache file path to check.
		interval (str): yfinance interval string — used to pick staleness threshold.

	Returns:
		bool: True if cache is absent or stale.
	"""
	if not path.exists():
		return True
	age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
	threshold = timedelta(hours=1) if interval in _INTRADAY_INTERVALS else timedelta(days=1)
	return age > threshold


def fetch_ohlc(
	ticker: str,
	period: str = "1y",
	interval: str = "1d",
	use_cache: bool = True,
) -> pd.DataFrame | None:
	"""Fetch OHLCV data for an NSE/BSE ticker via yfinance, with optional parquet cache.

	Validates the ticker suffix, checks the local parquet cache (if enabled),
	downloads adjusted OHLCV data on a miss, writes the result to cache, and
	returns a clean DataFrame ready for indicator calculation.

	Args:
		ticker (str): NSE ticker with `.NS` suffix (e.g. ``"RELIANCE.NS"``).
			BSE tickers use ``.BO``. Index tickers use ``^`` prefix (e.g. ``"^NSEI"``).
			An unsuffixed ticker is auto-corrected to ``.NS`` with a warning.
		period (str): Lookback window accepted by yfinance. One of:
			``1d 5d 1mo 3mo 6mo 1y 2y 5y 10y ytd max``. Defaults to ``"1y"``.
		interval (str): Bar size accepted by yfinance. One of:
			``1m 2m 5m 15m 30m 60m 90m 1h 1d 5d 1wk 1mo 3mo``.
			Sub-minute intervals (``1m``, ``2m``) are limited to ~7 days. Hourly
			intervals (``1h``) empirically return up to 3+ months.
			Defaults to ``"1d"``.
		use_cache (bool): Load from / write to local parquet cache. Staleness
			threshold: 1 hour for intraday intervals, 1 day for daily+.
			Defaults to ``True``.

	Returns:
		pd.DataFrame | None: DataFrame indexed by datetime with columns
		``Open``, ``High``, ``Low``, ``Close``, ``Volume``. OHLC values are
		split- and dividend-adjusted (``auto_adjust=True``). Returns ``None``
		on download failure or empty result.
		Index timezone: ``tz=None`` for daily/weekly bars; ``tz=Asia/Kolkata``
		for intraday bars. Zero-volume rows (NSE holiday artifacts) are not
		filtered — callers that require non-zero volume must drop them.

	Raises:
		ValueError: If ``period`` or ``interval`` is not a recognised yfinance value.

	Example:
		Basic usage::

			df = fetch_ohlc("RELIANCE.NS")
			df = fetch_ohlc("INFY.NS", period="6mo")
			df = fetch_ohlc("TCS.NS", period="3mo", interval="1h")
			df = fetch_ohlc("RELIANCE.NS", use_cache=False)  # skip cache

		Always guard against None return::

			df = fetch_ohlc("RELIANCE.NS")
			if df is None:
				...

	Note:
		Sub-minute intervals (``1m``, ``2m``) are limited to ~7 days. Hourly
		intervals (``1h``) empirically return up to 3+ months. Yahoo Finance
		enforces these limits server-side; they may change without notice.
		Cache is stored at ``src/data/cache/tickers/<ticker>__<period>__<interval>.parquet``.
	"""  # noqa: E101
	if not ticker.startswith("^") and not (
		ticker.endswith(".NS") or ticker.endswith(".BO")
	):
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

	# Cache check
	cache_file = _cache_path(ticker, period, interval)
	if use_cache and not _is_stale(cache_file, interval):
		try:
			df = pd.read_parquet(cache_file)
			logger.info(
				"Cache hit for %s (period=%s, interval=%s) — %d rows",
				ticker, period, interval, len(df),
			)
			return df
		except Exception as e:
			logger.warning("Cache read failed for %s, re-downloading: %s", ticker, e)

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

	if use_cache:
		try:
			_CACHE_DIR.mkdir(parents=True, exist_ok=True)
			df.to_parquet(cache_file)
		except Exception as e:
			logger.warning("Cache write failed for %s: %s", ticker, e)

	logger.info(
		"Fetched %d rows for %s (period=%s, interval=%s)",
		len(df), ticker, period, interval,
	)
	return df


def fetch_batch(
	tickers: list[str],
	period: str = "1y",
	interval: str = "1d",
	use_cache: bool = True,
) -> dict[str, pd.DataFrame | None]:
	"""Fetch OHLCV data for multiple tickers, using cache where available.

	Splits tickers into cache hits and misses. Hits are loaded from parquet.
	Misses are downloaded in a single ``yf.download`` call and written to cache.
	Failed tickers return ``None`` in the result dict — they do not raise.

	Args:
		tickers (list[str]): List of NSE/BSE tickers (e.g. ``["RELIANCE.NS", "TCS.NS"]``).
			Unsuffixed tickers are auto-corrected to ``.NS`` with a warning.
		period (str): Lookback window — same options as ``fetch_ohlc``. Defaults to ``"1y"``.
		interval (str): Bar size — same options as ``fetch_ohlc``. Defaults to ``"1d"``.
		use_cache (bool): Check cache before downloading; write cache after download.
			Defaults to ``True``.

	Returns:
		dict[str, pd.DataFrame | None]: Mapping of normalised ticker → DataFrame.
		Failed or empty tickers map to ``None``. Filter misses with::

			clean = {k: v for k, v in result.items() if v is not None}

	Raises:
		ValueError: If ``period`` or ``interval`` is not a recognised yfinance value.

	Example:
		::

			batch = fetch_batch(["RELIANCE.NS", "TCS.NS", "INFY.NS"], period="6mo")
			for ticker, df in batch.items():
				if df is not None:
					print(ticker, df.shape)
	"""
	if period not in _VALID_PERIODS:
		raise ValueError(
			f"Invalid period '{period}'. Valid options: {sorted(_VALID_PERIODS)}"
		)
	if interval not in _VALID_INTERVALS:
		raise ValueError(
			f"Invalid interval '{interval}'. Valid options: {sorted(_VALID_INTERVALS)}"
		)

	result: dict[str, pd.DataFrame | None] = {}
	misses: list[str] = []

	for raw_ticker in tickers:
		ticker = raw_ticker
		if not ticker.startswith("^") and not (
			ticker.endswith(".NS") or ticker.endswith(".BO")
		):
			ticker = ticker + ".NS"
			logger.warning("No exchange suffix detected — appended '.NS': %s", ticker)

		cache_file = _cache_path(ticker, period, interval)
		if use_cache and not _is_stale(cache_file, interval):
			try:
				result[ticker] = pd.read_parquet(cache_file)
				logger.info("Cache hit: %s", ticker)
				continue
			except Exception as e:
				logger.warning("Cache read failed for %s: %s", ticker, e)

		misses.append(ticker)

	if not misses:
		return result

	logger.info("Batch downloading %d tickers", len(misses))
	try:
		if len(misses) == 1:
			# Pass as string — list with one element still returns MultiIndex which
			# breaks the column slice below. String returns flat OHLCV columns.
			raw = yf.download(
				tickers=misses[0],
				period=period,
				interval=interval,
				auto_adjust=True,
				progress=False,
			)
		else:
			raw = yf.download(
				tickers=misses,
				period=period,
				interval=interval,
				auto_adjust=True,
				progress=False,
				group_by="ticker",
			)
	except Exception as e:
		logger.error("yfinance batch download failed: %s", e)
		for ticker in misses:
			result[ticker] = None
		return result

	for ticker in misses:
		try:
			if len(misses) == 1:
				df_raw = raw
			else:
				top_level = raw.columns.get_level_values(0)
				if ticker not in top_level:
					logger.warning("Ticker %s absent from batch result", ticker)
					result[ticker] = None
					continue
				df_raw = raw[ticker]

			if df_raw is None or df_raw.empty:
				logger.warning("Empty result for %s in batch download", ticker)
				result[ticker] = None
				continue

			if isinstance(df_raw.columns, pd.MultiIndex):
				df_raw.columns = df_raw.columns.get_level_values(0)  # type: ignore[assignment]

			df = df_raw[["Open", "High", "Low", "Close", "Volume"]].copy()
			df.dropna(inplace=True)

			if df.empty:
				logger.warning("Empty DataFrame after dropna for %s", ticker)
				result[ticker] = None
				continue

			if use_cache:
				try:
					_CACHE_DIR.mkdir(parents=True, exist_ok=True)
					df.to_parquet(_cache_path(ticker, period, interval))
				except Exception as e:
					logger.warning("Cache write failed for %s: %s", ticker, e)

			result[ticker] = df
			logger.info("Fetched %d rows for %s", len(df), ticker)

		except Exception as e:
			logger.warning("Failed to process %s from batch result: %s", ticker, e)
			result[ticker] = None

	return result


if __name__ == "__main__":
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
	)
	df = fetch_ohlc("RELIANCE.NS", period="1mo", interval="1d")
	if df is not None:
		logger.info("Single fetch — last 5 rows:\n%s", df.tail().to_string())
		logger.info("Shape: %s", df.shape)

	batch = fetch_batch(["TCS.NS", "INFY.NS"], period="1mo", interval="1d")
	for t, d in batch.items():
		logger.info("Batch %s — %s", t, d.shape if d is not None else "None")
