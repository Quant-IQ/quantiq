"""
Technical Analysis Visualization Module
Contributors: AR (Dev Lead) | Phase 3 Target Module

Design Decision Rationale (CLAUDE.md Compliance):
Utilizes purely interactive Plotly chart structures to satisfy dynamic notebook
rendering limits without introducing unapproved matplotlib state dependencies.
"""

import logging

import pandas as pd
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


def macd_chart(df: pd.DataFrame) -> go.Figure:
	"""Generates an interactive Plotly chart containing MACD line, signal line, and histogram.

	Args:
	    df (pd.DataFrame): Dataframe containing pre-calculated tracking columns:
	        'MACD', 'MACD_signal', and 'MACD_diff'.

	Returns:
	    go.Figure: A Plotly chart object populated with the indicator subplot traces.

	Raises:
	    KeyError: If any of the required MACD metric vector streams are missing.
	"""
	# 1. Validation check for required data columns
	required_columns = ["MACD", "MACD_signal", "MACD_diff"]
	for col in required_columns:
		if col not in df.columns:
			logger.error(
				"Missing required metric column for chart compilation: %s", col
			)
			raise KeyError(f"DataFrame must contain a pre-calculated '{col}' column.")

	# 2. Instantiate the figure frame container
	fig = go.Figure()

	# 3. Add trend-following vector tracking line traces
	fig.add_trace(
		go.Scatter(
			x=df.index,
			y=df["MACD"],
			mode="lines",
			name="MACD",
			line=dict(color="blue", width=1.5),
		)
	)

	fig.add_trace(
		go.Scatter(
			x=df.index,
			y=df["MACD_signal"],
			mode="lines",
			name="Signal",
			line=dict(color="orange", width=1.5),
		)
	)

	# 4. Fix Acceptance Criteria #2: Map colors safely to handle positive/negative bars
	# This avoids the list comprehension object iteration bug present in the issue draft
	colors = ["green" if val >= 0 else "red" for val in df["MACD_diff"]]

	# 5. Add the momentum histogram bar trace layout
	fig.add_trace(
		go.Bar(x=df.index, y=df["MACD_diff"], name="Histogram", marker_color=colors)
	)

	# 6. Clean up layout canvas metadata with a clean dark theme
	fig.update_layout(
		title="MACD Oscillator Subplot Dashboard",
		xaxis_title="Date",
		yaxis_title="Value",
		template="plotly_dark",
		hovermode="x unified",
	)

	return fig


def volume_chart(df: pd.DataFrame) -> go.Figure:
	"""Generates an interactive Plotly chart showing volume bars with a 20-day rolling average overlay.

	Args:
	    df (pd.DataFrame): Dataframe containing at minimum a 'Volume' column with historical data.

	Returns:
	    go.Figure: A Plotly chart object populated with the volume bar and line overlay traces.

	Raises:
	    KeyError: If the required 'Volume' column is missing from the input DataFrame.
	"""
	# 1. Defensive programming validation
	if "Volume" not in df.columns:
		logger.error("Missing required 'Volume' column for chart compilation.")
		raise KeyError("DataFrame must contain a 'Volume' column.")

	# 2. Calculate the 20-day rolling average volume safely
	# min_periods=1 ensures that we still get an average even if the dataset has fewer than 20 rows
	avg_vol = df["Volume"].rolling(window=20, min_periods=1).mean()

	# 3. Instantiate the figure frame container
	fig = go.Figure()

	# 4. Add the base volume bars trace (Acceptance Criteria #1)
	fig.add_trace(
		go.Bar(x=df.index, y=df["Volume"], name="Volume", marker_color="lightblue")
	)

	# 5. Add the 20-day rolling average overlay line trace (Acceptance Criteria #2)
	fig.add_trace(
		go.Scatter(
			x=avg_vol.index,
			y=avg_vol,
			mode="lines",
			name="20-day Avg Volume",
			line=dict(color="navy", width=2),
		)
	)

	# 6. Clean up layout canvas metadata with a dark theme consistent with the app
	fig.update_layout(
		title="Historical Trading Volume & 20-day Moving Average",
		xaxis_title="Date",
		yaxis_title="Volume",
		template="plotly_dark",
		hovermode="x unified",
	)

	return fig


if __name__ == "__main__":
	# Internal Smoke Test / Sanity Check to confirm execution integrity
	logging.basicConfig(level=logging.INFO)
	logger.info("Running custom visualization engine internal smoke test pipelines...")

	# Instantiating clean mock tracking datasets (25 days to satisfy the 20-day rolling window)
	mock_index = pd.date_range(start="2026-05-01", periods=25, freq="D")

	# Generating a mock matrix sequence
	mock_df = pd.DataFrame(
		{
			"MACD": [1.0 + (i * 0.02) for i in range(25)],
			"MACD_signal": [1.1 + (i * 0.01) for i in range(25)],
			"MACD_diff": [((1.0 + (i * 0.02)) - (1.1 + (i * 0.01))) for i in range(25)],
			"Volume": [
				1000 + (i * 150) if i % 2 == 0 else 1200 - (i * 50) for i in range(25)
			],
		},
		index=mock_index,
	)

	# Execute and verify the MACD chart pipeline
	macd_fig = macd_chart(mock_df)
	logger.info("MACD chart validation successful: %s", type(macd_fig))

	# Execute and verify the Volume chart pipeline
	vol_fig = volume_chart(mock_df)
	logger.info("Volume chart validation successful: %s", type(vol_fig))
	logger.info("All visualization module smoke tests completed successfully!")
