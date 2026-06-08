"""
Visualisation utilities for OHLC market data.

Provides Plotly candlestick charts with optional overlays:
- SMA
- EMA
- Bollinger Bands
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


def plot_ohlc(
	df: pd.DataFrame,
	sma_window: int = 20,
	ema_window: int = 20,
	bb_window: int = 20,
	show_sma: bool = True,
	show_ema: bool = True,
	show_bollinger: bool = True,
) -> go.Figure:
	"""
	Create an interactive Plotly candlestick chart.

	Args:
	    df (pd.DataFrame):
	        DataFrame containing Open, High, Low and Close columns.

	    sma_window (int):
	        Window size for SMA overlay.

	    ema_window (int):
	        Window size for EMA overlay.

	    bb_window (int):
	        Window size for Bollinger Bands.

	    show_sma (bool):
	        Whether to display SMA.

	    show_ema (bool):
	        Whether to display EMA.

	    show_bollinger (bool):
	        Whether to display Bollinger Bands.

	Returns:
	    go.Figure:
	        Plotly figure object.
	"""
	if df.empty:
		raise ValueError("Input DataFrame cannot be empty")
	required_columns = {"Open", "High", "Low", "Close"}

	missing_columns = required_columns - set(df.columns)
	if missing_columns:
		raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

	chart_df = df.copy()

	fig = go.Figure()

	fig.add_trace(
		go.Candlestick(
			x=chart_df.index,
			open=chart_df["Open"],
			high=chart_df["High"],
			low=chart_df["Low"],
			close=chart_df["Close"],
			name="OHLC",
		)
	)

	if show_sma:
		chart_df["SMA"] = chart_df["Close"].rolling(window=sma_window).mean()

		fig.add_trace(
			go.Scatter(
				x=chart_df.index,
				y=chart_df["SMA"],
				mode="lines",
				name=f"SMA {sma_window}",
			)
		)

	if show_ema:
		chart_df["EMA"] = chart_df["Close"].ewm(span=ema_window, adjust=False).mean()

		fig.add_trace(
			go.Scatter(
				x=chart_df.index,
				y=chart_df["EMA"],
				mode="lines",
				name=f"EMA {ema_window}",
			)
		)

	if show_bollinger:
		rolling_mean = chart_df["Close"].rolling(window=bb_window).mean()

		rolling_std = chart_df["Close"].rolling(window=bb_window).std()

		upper_band = rolling_mean + (2 * rolling_std)
		lower_band = rolling_mean - (2 * rolling_std)

		fig.add_trace(
			go.Scatter(
				x=chart_df.index,
				y=upper_band,
				mode="lines",
				name="BB Upper",
			)
		)

		fig.add_trace(
			go.Scatter(
				x=chart_df.index,
				y=lower_band,
				mode="lines",
				name="BB Lower",
			)
		)

	fig.update_layout(
		title="OHLC Candlestick Chart",
		xaxis_title="Date",
		yaxis_title="Price",
		xaxis_rangeslider_visible=False,
		template="plotly_white",
	)

	return fig
