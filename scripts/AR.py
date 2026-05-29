import logging

import yfinance as yf
from ta.trend import SMAIndicator

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

VALID_PERIODS = {
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


def fetch_and_analyze(ticker: str, period: str = "1y") -> None:
	"""
	Fetch historical NSE data and log market statistics.

	Args:
	    ticker: NSE ticker with .NS suffix.
	    period: Yahoo Finance lookback period.

	Returns:
	    None
	"""
	if not ticker.endswith(".NS"):
		logger.warning(
			"Ticker %s missing .NS suffix. NSE tickers require .NS.",
			ticker,
		)
		return

	if period not in VALID_PERIODS:
		logger.warning("Invalid period: %s", period)
		return

	logger.info("Fetching %s | period=%s", ticker, period)

	try:
		df = yf.Ticker(ticker).history(
			period=period,
			auto_adjust=True,
		)
	except Exception as error:
		logger.error(
			"Failed to fetch data for %s: %s",
			ticker,
			error,
		)
		return

	if df.empty:
		logger.warning("No data returned for %s", ticker)
		return

	df["SMA20"] = SMAIndicator(
		close=df["Close"],
		window=20,
	).sma_indicator()

	df["SMA50"] = SMAIndicator(
		close=df["Close"],
		window=50,
	).sma_indicator()

	df.dropna(inplace=True)

	if df.empty:
		logger.warning(
			"%s has insufficient data for SMA50 calculation",
			ticker,
		)
		return

	period_high = float(df["High"].max())
	period_low = float(df["Low"].min())
	average_close = float(df["Close"].mean())

	sma20 = float(df["SMA20"].iloc[-1])
	sma50 = float(df["SMA50"].iloc[-1])

	first_close = float(df["Close"].iloc[0])
	last_close = float(df["Close"].iloc[-1])

	percent_change = ((last_close - first_close) / first_close) * 100

	average_volume = float(df["Volume"].mean())

	signal = "SMA20 > SMA50 → BULLISH" if sma20 > sma50 else "SMA20 < SMA50 → BEARISH"

	logger.info("--- %s Analysis Results ---", ticker)
	logger.info("Period:        %s", period)
	logger.info("High (INR):    %.2f", period_high)
	logger.info("Low (INR):     %.2f", period_low)
	logger.info("Avg Close:     %.2f INR", average_close)
	logger.info("SMA20:         %.2f INR", sma20)
	logger.info("SMA50:         %.2f INR", sma50)
	logger.info("Signal:        %s", signal)
	logger.info("Change (%%):    %.2f%%", percent_change)
	logger.info(
		"Last Date:     %s",
		df.index[-1].strftime("%Y-%m-%d"),
	)
	logger.info(
		"Avg Volume:    %s",
		f"{average_volume:,.0f}",
	)


if __name__ == "__main__":
	tickers = [
		"RELIANCE.NS",
		"TCS.NS",
		"INFY.NS",
		"HDFCBANK.NS",
		"ICICIBANK.NS",
	]

	for ticker in tickers:
		fetch_and_analyze(ticker)
