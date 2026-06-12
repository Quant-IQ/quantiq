"""
Technical Analysis Visualization Module
Contributors: AR (Dev Lead) | Phase 2 Core Graphics Support

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


if __name__ == "__main__":
	# Internal Smoke Test / Sanity Check to confirm execution integrity
	logging.basicConfig(level=logging.INFO)
	logger.info("Running custom macd_chart internal smoke test pipeline...")

	# Instantiating clean mock tracking datasets
	mock_index = pd.date_range(start="2026-06-01", periods=5, freq="D")
	mock_df = pd.DataFrame(
		{
			"MACD": [1.2, 1.5, 1.4, 1.1, 0.9],
			"MACD_signal": [1.0, 1.1, 1.2, 1.2, 1.1],
			"MACD_diff": [
				0.2,
				0.4,
				0.2,
				-0.1,
				-0.2,
			],  # Mix of positive and negative numbers
		},
		index=mock_index,
	)

	# Execute the chart compiler pipeline
	test_fig = macd_chart(mock_df)
	logger.info(
		"Smoke test complete. Visual graph engine successfully returned: %s",
		type(test_fig),
	)
