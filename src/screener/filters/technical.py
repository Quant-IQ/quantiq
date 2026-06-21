"""
Technical screener filters — operate on pre-computed indicator columns.

Owner: AV
File: src/screener/filters/technical.py
Phase: Phase-3

Per ADR-0002, these filters never calculate indicators themselves — they
read columns already appended by src/data/indicators.py (SMA<n>, RSI, ATR,
EMA<n>, MACD, BB_*). The caller is responsible for running indicators.py
on the df before passing it here.
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def price_above_sma(df: pd.DataFrame, window: int = 20, col: str = "Close") -> pd.Series:
	"""Boolean mask: True where price is above its SMA<window>.

	Args:
		df (pd.DataFrame): DataFrame with ``col`` and an ``SMA<window>``
			column already computed (see ``src/data/indicators.py:sma``).
		window (int): SMA window to compare against. Defaults to ``20``.
		col (str): Price column. Defaults to ``"Close"``.

	Returns:
		pd.Series: Boolean mask aligned to ``df.index``. ``False`` for
		every row if required columns are missing (fails safe, never
		raises — screener loops must keep running on bad input).
	"""
	sma_col = f"SMA{window}"
	if col not in df.columns or sma_col not in df.columns:
		logger.warning(
			"price_above_sma: missing column(s) '%s'/'%s' — returning all-False mask",
			col,
			sma_col,
		)
		return pd.Series(False, index=df.index)

	return (df[col] > df[sma_col]).fillna(False)


def rsi_oversold(df: pd.DataFrame, threshold: float = 30.0) -> pd.Series:
	"""Boolean mask: True where RSI is below ``threshold`` (oversold).

	Args:
		df (pd.DataFrame): DataFrame with an ``RSI`` column already
			computed (see ``src/data/indicators.py:rsi``).
		threshold (float): RSI level below which a row is "oversold".
			Defaults to ``30.0``.

	Returns:
		pd.Series: Boolean mask aligned to ``df.index``. All-False if
		``RSI`` column is missing.
	"""
	if "RSI" not in df.columns:
		logger.warning("rsi_oversold: missing 'RSI' column — returning all-False mask")
		return pd.Series(False, index=df.index)

	return (df["RSI"] < threshold).fillna(False)


def rsi_overbought(df: pd.DataFrame, threshold: float = 70.0) -> pd.Series:
	"""Boolean mask: True where RSI is above ``threshold`` (overbought).

	Args:
		df (pd.DataFrame): DataFrame with an ``RSI`` column already
			computed.
		threshold (float): RSI level above which a row is "overbought".
			Defaults to ``70.0``.

	Returns:
		pd.Series: Boolean mask aligned to ``df.index``. All-False if
		``RSI`` column is missing.
	"""
	if "RSI" not in df.columns:
		logger.warning("rsi_overbought: missing 'RSI' column — returning all-False mask")
		return pd.Series(False, index=df.index)

	return (df["RSI"] > threshold).fillna(False)


def atr_above_threshold(df: pd.DataFrame, threshold: float) -> pd.Series:
	"""Boolean mask: True where ATR is above ``threshold`` (high volatility).

	Args:
		df (pd.DataFrame): DataFrame with an ``ATR`` column already
			computed (see ``src/data/indicators.py:atr``).
		threshold (float): ATR level above which a row is flagged.

	Returns:
		pd.Series: Boolean mask aligned to ``df.index``. All-False if
		``ATR`` column is missing.
	"""
	if "ATR" not in df.columns:
		logger.warning("atr_above_threshold: missing 'ATR' column — returning all-False mask")
		return pd.Series(False, index=df.index)

	return (df["ATR"] > threshold).fillna(False)


if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example — fetch RELIANCE.NS, compute indicators, apply
	# every technical filter to real rows. Edge cases live in
	# tests/test_screener_filters_technical.py (pytest), not here.
	try:
		from src.data.fetch import fetch_ohlc
		from src.data.indicators import atr, rsi, sma
	except ImportError:
		sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[3]))
		from src.data.fetch import fetch_ohlc
		from src.data.indicators import atr, rsi, sma

	TICKER = "RELIANCE.NS"
	logger.info("--- Technical filters example run: %s ---", TICKER)

	df = fetch_ohlc(TICKER, period="1y", interval="1d")
	if df is None:
		logger.error("Could not fetch %s — check network connection. Exiting.", TICKER)
		sys.exit(1)

	for fn in (lambda d: sma(d, windows=[20]), rsi, atr):
		result = fn(df)
		if result is not None:
			df = result

	above_sma = price_above_sma(df, window=20)
	oversold = rsi_oversold(df)
	overbought = rsi_overbought(df)
	high_vol = atr_above_threshold(df, threshold=df["ATR"].median())

	logger.info("Latest row — Close above SMA20: %s", bool(above_sma.iloc[-1]))
	logger.info("Latest row — RSI oversold (<30): %s", bool(oversold.iloc[-1]))
	logger.info("Latest row — RSI overbought (>70): %s", bool(overbought.iloc[-1]))
	logger.info(
		"Latest row — ATR above median (%.2f): %s", df["ATR"].median(), bool(high_vol.iloc[-1])
	)
	logger.info("--- Example run complete ---")
