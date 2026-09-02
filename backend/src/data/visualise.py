"""
Technical Analysis Visualization Module
Contributors: AR (Dev Lead) | Phase 3 Target Module

Design Decision Rationale (CLAUDE.md Compliance):
Utilizes purely interactive Plotly chart structures to satisfy dynamic notebook
rendering limits without introducing unapproved matplotlib state dependencies.
"""

import logging
import re

import pandas as pd
import plotly.graph_objects as go
from ta.momentum import RSIIndicator

logger = logging.getLogger(__name__)


def macd_chart(df: pd.DataFrame) -> go.Figure | None:
	"""Generates an interactive Plotly chart containing MACD line, signal line, and histogram.

	Args:
	    df (pd.DataFrame): Dataframe containing pre-calculated tracking columns:
	        'MACD', 'MACD_signal', and 'MACD_diff'.

	Returns:
	    go.Figure | None: A Plotly chart object populated with the indicator subplot traces,
	        or None if input is invalid or required columns are missing.
	"""
	if df is None:
		logger.error(
			"macd_chart() received None — pass a DataFrame from indicators.macd()"
		)
		return None

	required_columns = ["MACD", "MACD_signal", "MACD_diff"]
	for col in required_columns:
		if col not in df.columns:
			logger.error(
				"macd_chart() missing required column '%s' — run indicators.macd() first",
				col,
			)
			return None

	fig = go.Figure()

	fig.add_trace(
		go.Scatter(
			x=df.index,
			y=df["MACD"],
			mode="lines",
			name="MACD",
			line=dict(color="#2196F3", width=1.5),
		)
	)

	fig.add_trace(
		go.Scatter(
			x=df.index,
			y=df["MACD_signal"],
			mode="lines",
			name="Signal",
			line=dict(color="#FF9800", width=1.5),
		)
	)

	colors = ["#26C26A" if val >= 0 else "#EF5350" for val in df["MACD_diff"]]

	fig.add_trace(
		go.Bar(x=df.index, y=df["MACD_diff"], name="Histogram", marker_color=colors)
	)

	fig.update_layout(
		title="MACD Oscillator Subplot Dashboard",
		xaxis_title="Date",
		yaxis_title="Value",
		template="plotly_dark",
		hovermode="x unified",
	)

	return fig


def rsi_chart(df: pd.DataFrame) -> go.Figure | None:
	"""Generates an interactive Plotly RSI chart.

	Args:
	    df (pd.DataFrame): DataFrame containing a pre-calculated ``RSI`` column.

	Returns:
	    go.Figure | None: Plotly figure displaying the RSI indicator,
	        or None if validation fails.
	"""
	if df is None:
		logger.error(
			"rsi_chart() received None — pass a DataFrame from indicators.rsi()"
		)
		return None

	if df.empty:
		logger.error("rsi_chart() received an empty DataFrame")
		return None

	if "RSI" not in df.columns:
		logger.error(
			"rsi_chart() missing required column 'RSI' — run indicators.rsi() first"
		)
		return None

	if not isinstance(df.index, pd.DatetimeIndex):
		try:
			df = df.copy()
			df.index = pd.to_datetime(df.index)
		except Exception as e:
			logger.error(
				"Failed to convert DataFrame index to DatetimeIndex: %s",
				e,
			)
			return None

	fig = go.Figure()

	fig.add_trace(
		go.Scatter(
			x=df.index,
			y=df["RSI"],
			mode="lines",
			name="RSI",
			line=dict(color="#9C27B0", width=2),
		)
	)

	fig.add_hline(
		y=70,
		line_dash="dash",
		line_color="#EF5350",
		annotation_text="Overbought (70)",
	)

	fig.add_hline(
		y=30,
		line_dash="dash",
		line_color="#26C26A",
		annotation_text="Oversold (30)",
	)

	fig.update_layout(
		title="Relative Strength Index (RSI 14)",
		xaxis_title="Date",
		yaxis_title="RSI",
		yaxis=dict(
			range=[0, 100],
			rangemode="tozero",
		),
		template="plotly_dark",
		hovermode="x unified",
	)

	return fig


def volume_chart(df: pd.DataFrame) -> go.Figure | None:
	"""Generates an interactive Plotly chart showing volume bars with a 20-day rolling average overlay.

	Args:
	    df (pd.DataFrame): Dataframe containing at minimum a 'Volume' column with historical data.

	Returns:
	    go.Figure | None: A Plotly chart object populated with the volume bar and line overlay traces,
	        or None if input is invalid or the 'Volume' column is missing.
	"""
	if df is None:
		logger.error(
			"volume_chart() received None — pass a DataFrame from fetch_ohlc()"
		)
		return None

	if "Volume" not in df.columns:
		logger.error("volume_chart() missing required 'Volume' column")
		return None

	avg_vol = df["Volume"].rolling(window=20).mean()

	fig = go.Figure()

	fig.add_trace(
		go.Bar(x=df.index, y=df["Volume"], name="Volume", marker_color="#42A5F5")
	)

	fig.add_trace(
		go.Scatter(
			x=avg_vol.index,
			y=avg_vol,
			mode="lines",
			name="20-day Avg Volume",
			line=dict(color="#FFD54F", width=2),
		)
	)

	fig.update_layout(
		title="Historical Trading Volume & 20-day Moving Average",
		xaxis_title="Date",
		yaxis_title="Volume",
		template="plotly_dark",
		hovermode="x unified",
	)

	return fig


def candlestick_chart(
	df: pd.DataFrame,
	ema_windows: list[int] | None = None,
) -> go.Figure | None:
	"""Generates an interactive Plotly candlestick chart with optional EMA overlays.

	EMA columns must be pre-calculated and present in df before calling this function.
	Expected column names follow the pattern ``EMA{window}`` (e.g. ``EMA20``, ``EMA50``).

	Args:
	    df (pd.DataFrame): DataFrame containing OHLCV columns (Open, High, Low, Close)
	        and pre-calculated EMA columns matching each requested window.
	    ema_windows (list[int] | None): EMA periods to overlay (e.g. [20, 50]).
	        Each window requires a corresponding ``EMA{window}`` column in df.
	        Defaults to ``[20, 50]``.

	Returns:
	    go.Figure | None: Plotly figure with candlestick body and EMA line overlays,
	        or None if df is None, required OHLC columns are missing, or any requested
	        EMA column is absent.
	"""
	if ema_windows is None:
		ema_windows = [20, 50]

	if df is None:
		logger.error(
			"candlestick_chart() received None — pass a DataFrame with OHLCV columns"
		)
		return None

	required_ohlc = ["Open", "High", "Low", "Close"]
	for col in required_ohlc:
		if col not in df.columns:
			logger.error("candlestick_chart() missing required column '%s'", col)
			return None

	ema_colors = ["#FFD700", "#00E5FF", "#FF9800", "#E040FB", "#69FF47"]
	for window in ema_windows:
		col = f"EMA{window}"
		if col not in df.columns:
			logger.error(
				"candlestick_chart() missing EMA column '%s' — "
				"run indicators.ema() with window=%d first",
				col,
				window,
			)
			return None

	fig = go.Figure()

	fig.add_trace(
		go.Candlestick(
			x=df.index,
			open=df["Open"],
			high=df["High"],
			low=df["Low"],
			close=df["Close"],
			name="OHLC",
			increasing_line_color="#26C26A",
			decreasing_line_color="#EF5350",
		)
	)

	for i, window in enumerate(ema_windows):
		col = f"EMA{window}"
		fig.add_trace(
			go.Scatter(
				x=df.index,
				y=df[col],
				mode="lines",
				name=f"EMA{window}",
				line=dict(color=ema_colors[i % len(ema_colors)], width=1.5),
			)
		)

	fig.update_layout(
		title="Candlestick Chart with EMA Overlays",
		xaxis_title="Date",
		yaxis_title="Price (₹)",
		template="plotly_dark",
		hovermode="x unified",
		xaxis_rangeslider_visible=False,
	)

	return fig


def bollinger_chart(df: pd.DataFrame) -> go.Figure | None:
	"""Generates an interactive Plotly chart showing Bollinger Bands with close price.

	Bollinger Bands consist of a middle SMA line and upper/lower bands at ±2 standard
	deviations. The band area between upper and lower is rendered as a filled region.
	All BB columns must be pre-calculated before calling this function (e.g. via
	``ta.volatility.BollingerBands``). Expected column names: ``BB_upper``,
	``BB_mid``, ``BB_lower``, ``Close``.

	Args:
	    df (pd.DataFrame): DataFrame containing pre-calculated Bollinger Band columns:
	        ``BB_upper``, ``BB_mid``, ``BB_lower``, and ``Close``.

	Returns:
	    go.Figure | None: Plotly figure with close price line, SMA mid-band, and
	        filled upper/lower band area, or None if df is None or any required
	        column is missing.
	"""
	if df is None:
		logger.error(
			"bollinger_chart() received None — pass a DataFrame with BB columns"
		)
		return None

	required_columns = ["BB_upper", "BB_mid", "BB_lower", "Close"]
	for col in required_columns:
		if col not in df.columns:
			logger.error(
				"bollinger_chart() missing required column '%s' — "
				"run ta.volatility.BollingerBands first",
				col,
			)
			return None

	fig = go.Figure()

	# Upper band — rendered first; lower band fills down to this trace
	fig.add_trace(
		go.Scatter(
			x=df.index,
			y=df["BB_upper"],
			mode="lines",
			name="Upper Band",
			line=dict(color="#546E7A", width=1),
			showlegend=True,
		)
	)

	# Lower band — fill="tonexty" shades the region between lower and upper
	fig.add_trace(
		go.Scatter(
			x=df.index,
			y=df["BB_lower"],
			mode="lines",
			name="Lower Band",
			line=dict(color="#546E7A", width=1),
			fill="tonexty",
			fillcolor="rgba(84, 110, 122, 0.15)",
			showlegend=True,
		)
	)

	# Middle band (SMA20)
	fig.add_trace(
		go.Scatter(
			x=df.index,
			y=df["BB_mid"],
			mode="lines",
			name="SMA20 (Mid)",
			line=dict(color="#FFD54F", width=1.5, dash="dot"),
		)
	)

	# Close price on top
	fig.add_trace(
		go.Scatter(
			x=df.index,
			y=df["Close"],
			mode="lines",
			name="Close",
			line=dict(color="#00E5FF", width=1.5),
		)
	)

	fig.update_layout(
		title="Bollinger Bands (20, 2σ)",
		xaxis_title="Date",
		yaxis_title="Price (₹)",
		template="plotly_dark",
		hovermode="x unified",
	)

	return fig


def plot_ohlc(df: pd.DataFrame) -> go.Figure | None:
	"""
	Build an interactive Plotly candlestick chart with toggleable technical indicators.

	Expects a pandas DataFrame indexed by Datetime with specific baseline metrics
	already calculated by the technical indicator pipeline.

	Args:
	    df (pd.DataFrame): Financial time series containing 'Open', 'High',
	                       'Low', 'Close' and indicator columns.

	Returns:
	    go.Figure | None: A fully configured Plotly figure object, or None
	                      if critical price columns are missing or empty.
	"""
	try:
		# Check for critical price columns before attempting to map visual traces
		required_cols = ["Open", "High", "Low", "Close"]
		if not all(col in df.columns for col in required_cols):
			logger.error(
				"Data integrity failure: Missing core OHLC columns in DataFrame."
			)
			return None

		if df.empty:
			logger.warning("Empty DataFrame passed to plot_ohlc pipeline.")
			return None

		# Synchronize datetime indexing
		if not isinstance(df.index, pd.DatetimeIndex):
			df.index = pd.to_datetime(df.index)

		fig = go.Figure()

		# 1. Base Candlestick Layer (Always Visible index tracking: 0)
		fig.add_trace(
			go.Candlestick(
				x=df.index,
				open=df["Open"],
				high=df["High"],
				low=df["Low"],
				close=df["Close"],
				name="OHLC Price",
			)
		)

		# Technical Indicator Overlays — Checks column mapping safely.
		# indicators.py names columns SMA<window>/EMA<window> (e.g. SMA20,
		# EMA50) and lowercase BB_upper/BB_lower — match those, not bare
		# "SMA"/"EMA"/"BB_Upper"/"BB_Lower", which indicators.py never emits.
		sma_cols = sorted(c for c in df.columns if re.fullmatch(r"SMA\d+", c))
		for sma_col in sma_cols:
			fig.add_trace(
				go.Scatter(
					x=df.index,
					y=df[sma_col],
					mode="lines",
					line=dict(color="orange", width=1.5),
					name=sma_col,
					visible=True,
				)
			)

		ema_cols = sorted(c for c in df.columns if re.fullmatch(r"EMA\d+", c))
		for ema_col in ema_cols:
			fig.add_trace(
				go.Scatter(
					x=df.index,
					y=df[ema_col],
					mode="lines",
					line=dict(color="#1f77b4", width=1.5),
					name=ema_col,
					visible=True,
				)
			)

		if "BB_upper" in df.columns and "BB_lower" in df.columns:
			fig.add_trace(
				go.Scatter(
					x=df.index,
					y=df["BB_upper"],
					mode="lines",
					line=dict(color="rgba(231, 76, 60, 0.5)", width=1, dash="dash"),
					name="BB Upper",
					visible=True,
				)
			)
			fig.add_trace(
				go.Scatter(
					x=df.index,
					y=df["BB_lower"],
					mode="lines",
					line=dict(color="rgba(231, 76, 60, 0.5)", width=1, dash="dash"),
					name="BB Lower",
					visible=True,
				)
			)

		# 2. Layout & Button Toggle Settings (Plotly Dark Theme Match)
		total_traces = len(fig.data)

		fig.update_layout(
			title="QuantIQ | Dynamic Price Action & Technical Overlays",
			yaxis_title="Stock Price (INR)",
			xaxis_title="Timeline / Date",
			xaxis_rangeslider_visible=True,
			template="plotly_dark",
			height=700,
			width=1000,
			legend=dict(
				orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
			),
			updatemenus=[
				dict(
					type="buttons",
					direction="right",
					active=0,
					x=0.01,
					y=1.12,
					buttons=list(
						[
							dict(
								label="Show All Overlays",
								method="update",
								args=[{"visible": [True] * total_traces}],
							),
							dict(
								label="Price Action Only",
								method="update",
								args=[
									{"visible": [True] + [False] * (total_traces - 1)}
								],
							),
						]
					),
				)
			],
		)
		return fig

	except Exception as e:
		logger.error("Visualisation crash caught inside plot_ohlc module: %s", e)
		return None


if __name__ == "__main__":
	import sys

	import yfinance as yf

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	TICKER = "RELIANCE.NS"
	logger.info("Fetching 6 months of daily data for %s...", TICKER)

	raw = yf.download(
		TICKER, period="6mo", interval="1d", auto_adjust=True, progress=False
	)
	if raw is None or raw.empty:
		logger.error("No data returned for %s — check ticker or network", TICKER)
		sys.exit(1)

	# Flatten MultiIndex columns if present (yfinance batch download)
	if isinstance(raw.columns, pd.MultiIndex):
		raw.columns = raw.columns.get_level_values(0)

	df = raw[["Open", "High", "Low", "Close", "Volume"]].copy()
	df.dropna(inplace=True)

	close_s = df["Close"]

	# EMA columns (normally from indicators.ema())
	df["EMA20"] = close_s.ewm(span=20, adjust=False).mean()
	df["EMA50"] = close_s.ewm(span=50, adjust=False).mean()

	# MACD columns (normally from indicators.macd())
	fast_ema = close_s.ewm(span=12, adjust=False).mean()
	slow_ema = close_s.ewm(span=26, adjust=False).mean()
	macd_line = fast_ema - slow_ema
	df["MACD"] = macd_line
	df["MACD_signal"] = macd_line.ewm(span=9, adjust=False).mean()
	df["MACD_diff"] = df["MACD"] - df["MACD_signal"]

	# RSI column (normally from indicators.rsi())
	df["RSI"] = RSIIndicator(close=close_s, window=14).rsi()

	logger.info(
		"Data ready: %d rows (%s → %s)",
		len(df),
		df.index[0].date(),
		df.index[-1].date(),
	)

	logger.info("Rendering candlestick chart with EMA20/EMA50...")
	fig_candle = candlestick_chart(df, ema_windows=[20, 50])
	if fig_candle:
		fig_candle.update_layout(title=f"{TICKER} — Candlestick + EMA20/50")
		fig_candle.show()

	logger.info("Rendering MACD chart...")
	fig_macd = macd_chart(df)
	if fig_macd:
		fig_macd.update_layout(title=f"{TICKER} — MACD")
		fig_macd.show()

	logger.info("Rendering RSI chart...")
	fig_rsi = rsi_chart(df)
	if fig_rsi:
		fig_rsi.update_layout(title=f"{TICKER} — RSI (14)")
		fig_rsi.show()

	logger.info("Rendering volume chart...")
	fig_vol = volume_chart(df)
	if fig_vol:
		fig_vol.update_layout(title=f"{TICKER} — Volume & 20-day Avg")
		fig_vol.show()

	# Bollinger Bands columns (normally from ta.volatility.BollingerBands)
	rolling_mean = close_s.rolling(window=20).mean()
	rolling_std = close_s.rolling(window=20).std()
	df["BB_mid"] = rolling_mean
	df["BB_upper"] = rolling_mean + 2 * rolling_std
	df["BB_lower"] = rolling_mean - 2 * rolling_std
	df.dropna(inplace=True)

	logger.info("Rendering Bollinger Bands chart...")
	fig_bb = bollinger_chart(df)
	if fig_bb:
		fig_bb.update_layout(title=f"{TICKER} — Bollinger Bands (20, 2σ)")
		fig_bb.show()
