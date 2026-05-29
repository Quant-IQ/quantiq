"""One-year market data summary using yfinance."""

from __future__ import annotations

import logging

import pandas as pd
import yfinance as yf

# Keep terminal output short and clean.
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def fetch_market_summary(ticker: str = "RELIANCE.NS") -> dict[str, float | str]:
    """Download one year of market data and compute a readable summary.

    Args:
        ticker: Yahoo Finance ticker symbol to download. Defaults to RELIANCE.NS.

    Returns:
        A dictionary containing the high, low, average close, SMA20, SMA50,
        signal, percentage change, and average volume over the downloaded
        period.

    Raises:
        ValueError: If yfinance returns no data for the requested ticker.
        Exception: If the yfinance download call fails unexpectedly.
    """
    if not ticker.endswith(".NS"):
        raise ValueError(f"NSE ticker must include the '.NS' suffix: {ticker!r}")

    # Download one year of daily market data from Yahoo Finance.
    try:
        data = yf.download(
            ticker,
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=True,
        )
    except Exception as exc:
        logger.exception("Failed to download market data for %s: %s", ticker, exc)
        raise

    if data is None:
        raise ValueError(f"No market data returned for ticker {ticker!r}.")

    if data.empty:
        raise ValueError(f"No market data returned for ticker {ticker!r}.")

    # Flatten columns if yfinance returns a MultiIndex frame.
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    if len(data) < 50:
        raise ValueError(f"Not enough data to calculate SMA20 and SMA50 for {ticker!r}.")

    # Calculate the summary values requested for Phase 1.
    high: float = float(data["High"].max())
    low: float = float(data["Low"].min())
    avg_close: float = float(data["Close"].mean())
    sma20: float = float(data["Close"].rolling(window=20).mean().iloc[-1])
    sma50: float = float(data["Close"].rolling(window=50).mean().iloc[-1])
    first_close: float = float(data["Close"].iloc[0])
    last_close: float = float(data["Close"].iloc[-1])
    pct_change: float = ((last_close - first_close) / first_close) * 100
    avg_volume: float = float(data["Volume"].mean())

    signal: str = "SMA20 > SMA50 -> BULLISH" if sma20 > sma50 else "SMA20 < SMA50 -> BEARISH"

    summary: dict[str, float | str] = {
        "high": high,
        "low": low,
        "avg_close": avg_close,
        "sma20": sma20,
        "sma50": sma50,
        "pct_change": pct_change,
        "avg_volume": avg_volume,
        "signal": signal,
    }

    # Log the results in the requested terminal-friendly format.
    logger.info("Fetching %s | period=1y", ticker)
    logger.info("--- %s Analysis Results ---", ticker)
    logger.info("Period:          1y")
    logger.info("High (INR):      %.2f", summary["high"])
    logger.info("Low (INR):       %.2f", summary["low"])
    logger.info("Avg Close:       %.2f INR", summary["avg_close"])
    logger.info("SMA20:           %.2f INR", summary["sma20"])
    logger.info("SMA50:           %.2f INR", summary["sma50"])
    logger.info("Signal:          %s", summary["signal"])
    logger.info("Change (%%):      %.2f%%", summary["pct_change"])
    logger.info("Avg Volume:      %s", f"{summary['avg_volume']:,.0f}")

    return summary


# Run the script when executed directly.
if __name__ == "__main__":
    fetch_market_summary()
