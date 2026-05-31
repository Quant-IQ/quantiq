import yfinance as yf
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def analyze_stock(ticker: str = "RELIANCE.NS") -> Dict[str, float]:
    """
    Download 1 year stock data and calculate key metrics.

    Args:
        ticker (str): NSE stock ticker with .NS suffix.

    Returns:
        Dict[str, float]: Stock metrics including high, low, avg close,
        percent change, volatility, and trading days.
    """
    try:
        data = yf.download(ticker, period="1y")

        if data.empty:
            raise ValueError("No data fetched for ticker")

        # Basic metrics
        high_price = float(data["High"].max())
        low_price = float(data["Low"].min())
        avg_close = float(data["Close"].mean())

        start_price = float(data["Close"].iloc[0])
        end_price = float(data["Close"].iloc[-1])

        percent_change = ((end_price - start_price) / start_price) * 100

        # Extra (safe enhancement)
        volatility = float(data["Close"].pct_change().std()) * 100
        trading_days = len(data)

        result = {
            "ticker": ticker,
            "high": high_price,
            "low": low_price,
            "avg_close": avg_close,
            "percent_change": percent_change,
            "volatility": volatility,
            "trading_days": trading_days,
        }

        logger.info("=== STOCK ANALYSIS ===")
        logger.info(f"Ticker: {ticker}")
        logger.info(f"High: {high_price:.2f}")
        logger.info(f"Low: {low_price:.2f}")
        logger.info(f"Avg Close: {avg_close:.2f}")
        logger.info(f"% Change: {percent_change:.2f}%")
        logger.info(f"Volatility: {volatility:.2f}%")
        logger.info(f"Trading Days: {trading_days}")

        return result

    except Exception as e:
        logger.error(f"Error fetching stock data: {e}")
        return {}


def main() -> None:
    analyze_stock("RELIANCE.NS")


if __name__ == "__main__":
    main()