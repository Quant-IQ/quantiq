import logging

import yfinance as yf

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

def analyze_stock(ticker: str) -> None:
    """Analyze one year of stock market data.

    Args:
        ticker: Yahoo Finance ticker symbol.

    Returns:
        None
    """
    try:
        data = yf.download(
            ticker,
            period="1y",
            progress=False,
            auto_adjust=True,
        )

        if data.empty:
            logger.info(f"No data found for {ticker}")
            return

        high_price = float(data["High"].max().iloc[0])
        low_price = float(data["Low"].min().iloc[0])
        average_close = float(data["Close"].mean().iloc[0])

        start_close = float(data["Close"].iloc[0].iloc[0])
        end_close = float(data["Close"].iloc[-1].iloc[0])

        percentage_change = (
            (end_close - start_close) / start_close
        ) * 100

        logger.info(f"Ticker: {ticker}")
        logger.info(f"High: {high_price:.2f}")
        logger.info(f"Low: {low_price:.2f}")
        logger.info(f"Average Close: {average_close:.2f}")
        logger.info(f"Percentage Change: {percentage_change:.2f}%")

    except Exception as error:
        logger.error(f"Error fetching data: {error}")


if __name__ == "__main__":
    analyze_stock("^NSEI")