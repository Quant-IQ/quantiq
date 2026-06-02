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
    Fetches historical OHLCV data for an NSE ticker and logs key statistics.

    Calculates SMA20, SMA50, period high/low, average close,
    percentage change, average volume, and a directional signal
    based on SMA crossover.

    Args:
        ticker (str): Yahoo Finance ticker symbol.
            Must end with '.NS' for NSE equities.
        period (str): Lookback period.

    Returns:
        None
    """

    if not ticker.endswith(".NS"):
        logger.warning(
            "Ticker %s missing .NS suffix — skipping.",
            ticker,
        )
        return

    if period not in VALID_PERIODS:
        logger.warning(
            "Invalid period '%s'.",
            period,
        )
        return

    logger.info("\nFetching %s | period=%s", ticker, period)

    try:
        df = yf.Ticker(ticker).history(period=period)

    except Exception as error:
        logger.error(
            "yfinance fetch failed for %s: %s",
            ticker,
            error,
        )
        return

    if df.empty:
        logger.warning(
            "No data returned for %s.",
            ticker,
        )
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
            "%s: insufficient data after dropna.",
            ticker,
        )
        return

    period_high = df["High"].max()
    period_low = df["Low"].min()
    avg_close = df["Close"].mean()
    avg_volume = df["Volume"].mean()

    sma20 = df["SMA20"].iloc[-1]
    sma50 = df["SMA50"].iloc[-1]

    first_close = df["Close"].iloc[0]
    last_close = df["Close"].iloc[-1]

    pct_change = (
        (last_close - first_close)
        / first_close
    ) * 100

    signal = (
        "SMA20 > SMA50 → BULLISH"
        if sma20 > sma50
        else "SMA20 < SMA50 → BEARISH"
    )

    logger.info("--- %s Analysis Results ---", ticker)
    logger.info("Period: %s", period)
    logger.info("High (INR): %.2f", period_high)
    logger.info("Low (INR): %.2f", period_low)
    logger.info("Avg Close: %.2f INR", avg_close)
    logger.info("SMA20: %.2f INR", sma20)
    logger.info("SMA50: %.2f INR", sma50)
    logger.info("Signal: %s", signal)
    logger.info("Change (%%): %.2f%%", pct_change)
    logger.info(
        "Avg Volume: {:,.0f}".format(avg_volume),
    )


if __name__ == "__main__":
    tickers = [
        "RELIANCE.NS",
        "HDFCBANK.NS",
        "TCS.NS",
        "INFY.NS",
        "ICICIBANK.NS",
    ]

    for stock in tickers:
        fetch_and_analyze(stock)