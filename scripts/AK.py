import logging

import yfinance as yf

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_and_analyze(ticker: str) -> None:

	try:
		stock_data = yf.Ticker(ticker).history(period="1y")

		if stock_data.empty:
			logger.warning("No data found for %s", ticker)
			return

		high = float(stock_data["High"].max())
		low = float(stock_data["Low"].min())
		average_close = float(stock_data["Close"].mean())

		start_close = float(stock_data["Close"].iloc[0])
		end_close = float(stock_data["Close"].iloc[-1])

		percent_change = ((end_close - start_close) / start_close) * 100

		logger.info("")
		logger.info("--- %s Analysis Results ---", ticker)
		logger.info("Period:        1y")
		logger.info("High (INR):    %.2f", high)
		logger.info("Low (INR):     %.2f", low)
		logger.info("Avg Close:     %.2f INR", average_close)
		logger.info("Change (%%):    %.2f%%", percent_change)
		logger.info(
			"Last Date:     %s",
			stock_data.index[-1].strftime("%Y-%m-%d"),
		)

	except Exception as error:
		logger.error("Failed to fetch data for %s: %s", ticker, error)


if __name__ == "__main__":
	tickers = [
		"RELIANCE.NS",
		"HINDUNILVR.NS",
		"ASIANPAINT.NS",
		"MARUTI.NS",
		"SUNPHARMA.NS",
	]

	for ticker in tickers:
		fetch_and_analyze(ticker)
