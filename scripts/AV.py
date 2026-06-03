import logging
import pandas as pd
import requests
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def fetch_multi_market_summary(
    tickers: list[str] = [
        "ITC.NS",
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS",
        "ICICIBANK.NS",
    ]
) -> dict[str, dict[str, float | str]]:
    """Download one year of market data for multiple tickers and compute summaries.

    Uses a custom requests session with proper browser headers to prevent Yahoo Finance
    from throwing a JSONDecodeError / rate-limiting blocks.
    """
    # Clean and validate tickers
    cleaned_tickers = [ticker.strip().upper() for ticker in tickers]
    for ticker in cleaned_tickers:
        if not ticker.endswith(".NS"):
            raise ValueError(
                f"All NSE tickers must include the '.NS' suffix: {ticker!r}"
            )

    logger.info("Fetching data for: %s | period=1y", ", ".join(cleaned_tickers))

    # --- BOT PROTECTION LAYER ---
    # Setup a fake browser session identity to mask python's requests footprint
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    )

    # Download one year of daily market data safely through our session
    try:
        data = yf.download(
            cleaned_tickers,
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=True,
            group_by="ticker",
            session=session,  # Bypasses "Expecting value" API walls
        )
    except Exception as exc:
        logger.exception("Failed to download market data from Yahoo Finance: %s", exc)
        raise

    if data is None or data.empty:
        raise ValueError(
            "No market data returned. Your IP might be temporarily rate-limited by Yahoo."
        )

    all_summaries = {}

    # Process each ticker
    for ticker in cleaned_tickers:
        try:
            # Safely extract sub-dataframe for the specific ticker
            if len(cleaned_tickers) > 1:
                if ticker not in data.columns.levels[0]:
                    logger.warning(
                        "Ticker %s not found in downloaded data headers. Skipping.",
                        ticker,
                    )
                    continue
                ticker_df = data[ticker].dropna()
            else:
                ticker_df = data.copy()
                if isinstance(ticker_df.columns, pd.MultiIndex):
                    ticker_df.columns = ticker_df.columns.get_level_values(0)
                ticker_df = ticker_df.dropna()

            if len(ticker_df) < 50:
                logger.warning(
                    "Not enough rows (%d) to calculate indicators for %s. Skipping.",
                    len(ticker_df),
                    ticker,
                )
                continue

            # Calculate metrics using .squeeze()
            high: float = float(ticker_df["High"].max().squeeze())
            low: float = float(ticker_df["Low"].min().squeeze())
            avg_close: float = float(ticker_df["Close"].mean().squeeze())

            # Calculate Moving Averages
            sma20: float = float(
                ticker_df["Close"].rolling(window=20).mean().iloc[-1].squeeze()
            )
            sma50: float = float(
                ticker_df["Close"].rolling(window=50).mean().iloc[-1].squeeze()
            )

            first_close: float = float(ticker_df["Close"].iloc[0].squeeze())
            last_close: float = float(ticker_df["Close"].iloc[-1].squeeze())

            pct_change: float = ((last_close - first_close) / first_close) * 100
            avg_volume: float = float(ticker_df["Volume"].mean().squeeze())

            signal: str = "BULLISH" if sma20 > sma50 else "BEARISH"

            # Save metrics
            all_summaries[ticker] = {
                "high": high,
                "low": low,
                "avg_close": avg_close,
                "sma20": sma20,
                "sma50": sma50,
                "pct_change": pct_change,
                "avg_volume": avg_volume,
                "signal": signal,
            }

            # Print individual terminal results cleanly
            logger.info("\n--- %s Analysis Results ---", ticker)
            logger.info("High (INR):      %.2f", all_summaries[ticker]["high"])
            logger.info("Low (INR):       %.2f", all_summaries[ticker]["low"])
            logger.info("Avg Close:       %.2f INR", all_summaries[ticker]["avg_close"])
            logger.info("SMA20 | SMA50:   %.2f | %.2f", sma20, sma50)
            logger.info(
                "Signal:          %s (SMA20 %s SMA50)",
                signal,
                ">" if sma20 > sma50 else "<",
            )
            logger.info("Change (1Y):     %.2f%%", all_summaries[ticker]["pct_change"])
            logger.info("Avg Volume:      {_vol:,.0f}".format(_vol=avg_volume))

        except KeyError as ke:
            logger.error("Missing expected column mapping data for %s: %s", ticker, ke)
            continue
        except Exception as e:
            logger.error("Unexpected error processing data for %s: %s", ticker, e)
            continue

    return all_summaries


if __name__ == "__main__":
    my_stocks = [
        "ITC.NS",
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS",
        "ICICIBANK.NS",
    ]
    fetch_multi_market_summary(tickers=my_stocks)
