import logging

import yfinance as yf
from ta.trend import SMAIndicator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

VALID_PERIODS = {
    "1mo",
    "3mo",
    "6mo",
    "1y",
    "2y",
    "5y",
}


def analyze_stock(ticker: str, period: str = "1y") -> None:
    """
    Download NSE stock data and display simple trend analysis.

    Args:
        ticker (str): NSE ticker ending with '.NS'.
        period (str): Yahoo Finance lookback period.

    Returns:
        None
    """
    if not ticker.endswith(".NS"):
        logger.warning(f"⚠️ {ticker} is missing '.NS'")
        return

    if period not in VALID_PERIODS:
        logger.warning(f"⚠️ Invalid period: {period}")
        return

    logger.info(f"\n📡 Downloading data for {ticker}...\n")

    df = yf.download(
        ticker,
        period=period,
        interval="1d",
        auto_adjust=True,
    )

    if df.empty:
        logger.warning(f"❌ No data found for {ticker}")
        return

    df["SMA20"] = SMAIndicator(
        close=df["Close"].squeeze(),
        window=20,
    ).sma_indicator()

    df["SMA50"] = SMAIndicator(
        close=df["Close"].squeeze(),
        window=50,
    ).sma_indicator()

    df.dropna(inplace=True)

    high_price = float(df["High"].max().iloc[0])
    low_price = float(df["Low"].min().iloc[0])
    average_close = float(df["Close"].mean().iloc[0])

    sma20 = float(df["SMA20"].iloc[-1])
    sma50 = float(df["SMA50"].iloc[-1])

    start_close = float(df["Close"].iloc[0].iloc[0])
    end_close = float(df["Close"].iloc[-1].iloc[0])

    percent_change = ((end_close - start_close) / start_close) * 100

    if sma20 > sma50:
        trend = "🟢 Bullish"
    else:
        trend = "🔴 Bearish"

    logger.info("╔══════════════════════════════════════╗")
    logger.info(f"        📈 {ticker} Market Summary")
    logger.info("╚══════════════════════════════════════╝")

    logger.info(f"💹 52W High        : ₹{high_price:.2f}")
    logger.info(f"📉 52W Low         : ₹{low_price:.2f}")
    logger.info(f"📊 Average Close   : ₹{average_close:.2f}")

    logger.info("")

    logger.info(f"⚡ SMA20            : ₹{sma20:.2f}")
    logger.info(f"🌊 SMA50            : ₹{sma50:.2f}")

    logger.info("")

    logger.info(f"📈 Trend Signal    : {trend}")
    logger.info(f"🎯 % Change        : {percent_change:.2f}%")

    logger.info("\n✨ Analysis complete.\n")


if __name__ == "__main__":
    tickers = [
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS",
        "ICICIBANK.NS",
    ]

    for ticker in tickers:
        analyze_stock(ticker)