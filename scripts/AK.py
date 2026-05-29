import logging

import yfinance as yf

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def fetch_and_analyze(ticker: str) -> None:
	try:
		df = yf.Ticker(ticker).history(period="1y")
	except Exception as error:
		logger.error("Failed to fetch data: %s", error)
		return

	if df.empty:
		logger.warning("No data found for %s", ticker)
		return

	high = float(df["High"].max())
	low = float(df["Low"].min())
	average_close = float(df["Close"].mean())

	first_close = float(df["Close"].iloc[0])
	last_close = float(df["Close"].iloc[-1])

	percent_change = ((last_close - first_close) / first_close) * 100

	logger.info("Ticker: %s", ticker)
	logger.info("High: %.2f", high)
	logger.info("Low: %.2f", low)
	logger.info("Average Close: %.2f", average_close)
	logger.info("Percent Change: %.2f%%", percent_change)


if __name__ == "__main__":
	fetch_and_analyze("RELIANCE.NS")
