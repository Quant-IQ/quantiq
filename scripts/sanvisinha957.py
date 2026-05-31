import logging

import pandas as pd
import yfinance as yf
from ta.trend import SMAIndicator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

NIFTY50_PICKS = ["WIPRO.NS", "BAJFINANCE.NS", "INFY.NS", "SUNPHARMA.NS", "AXISBANK.NS"]


def validate_inputs(ticker: str, period: str) -> bool:
    """Validate ticker format and period before fetching data.

    Args:
        ticker: NSE ticker symbol, must end with '.NS'.
        period: Lookback period string.

    Returns:
        True if inputs are valid, False otherwise.
    """
    valid_periods = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}

    if not ticker.endswith(".NS"):
        logger.warning("Skipping %s — NSE tickers must end with .NS", ticker)
        return False

    if period not in valid_periods:
        logger.warning("Invalid period '%s'. Choose from: %s", period, ", ".join(sorted(valid_periods)))
        return False

    return True


def compute_statistics(df: pd.DataFrame) -> dict[str, float]:
    """Compute summary statistics from OHLCV data.

    Args:
        df: DataFrame with Close, High, Low, Volume, SMA20, SMA50 columns.

    Returns:
        Dictionary containing period_high, period_low, avg_close,
        avg_volume, sma20, sma50, pct_change.
    """
    first_close: float = float(df["Close"].iloc[0])
    last_close: float = float(df["Close"].iloc[-1])

    return {
        "period_high": float(df["High"].max()),
        "period_low": float(df["Low"].min()),
        "avg_close": float(df["Close"].mean()),
        "avg_volume": float(df["Volume"].mean()),
        "sma20": float(df["SMA20"].iloc[-1]),
        "sma50": float(df["SMA50"].iloc[-1]),
        "pct_change": ((last_close - first_close) / first_close) * 100,
    }


def analyse_ticker(ticker: str, period: str = "1y") -> None:
    """Fetch and analyse historical data for a single NSE ticker.

    Args:
        ticker: Yahoo Finance ticker symbol ending with '.NS'.
        period: Lookback period, defaults to '1y'.
    """
    if not validate_inputs(ticker, period):
        return

    logger.info("Analysing %s | period=%s", ticker, period)

    try:
        df: pd.DataFrame = yf.Ticker(ticker).history(period=period)
    except Exception as e:
        logger.error("Failed to fetch data for %s: %s", ticker, e)
        return

    if df.empty:
        logger.warning("No data returned for %s.", ticker)
        return

    df["SMA20"] = SMAIndicator(close=df["Close"], window=20).sma_indicator()
    df["SMA50"] = SMAIndicator(close=df["Close"], window=50).sma_indicator()
    df.dropna(inplace=True)

    if df.empty:
        logger.warning("%s: not enough data — need at least 50 trading days.", ticker)
        return

    stats = compute_statistics(df)
    trend = "BULLISH" if stats["sma20"] > stats["sma50"] else "BEARISH"

    logger.info("-" * 40)
    logger.info("  %s — %s", ticker, df.index[-1].strftime("%Y-%m-%d"))
    logger.info("-" * 40)
    logger.info("  High       : INR %.2f", stats["period_high"])
    logger.info("  Low        : INR %.2f", stats["period_low"])
    logger.info("  Avg Close  : INR %.2f", stats["avg_close"])
    logger.info("  SMA20      : INR %.2f", stats["sma20"])
    logger.info("  SMA50      : INR %.2f", stats["sma50"])
    logger.info("  Trend      : %s", trend)
    logger.info("  Change     : %.2f%%", stats["pct_change"])
    logger.info("  Avg Volume : %s", f"{stats['avg_volume']:,.0f}")
    logger.info("-" * 40)


if __name__ == "__main__":
    for ticker in NIFTY50_PICKS:
        analyse_ticker(ticker)
