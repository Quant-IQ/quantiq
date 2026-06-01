import logging
import pandas as pd
import yfinance as yf
import vectorbt as vbt
from ta.trend import SMAIndicator
logging.basicConfig(
    level=logging.INFO ,
    format=" %(asctime)s | %(levelname)s |%(name)s | %(message)s" ,
)
logger = logging.getLogger(__name__)

def crossover_strategy(
    ticker: str, duration: str, Fast_days: int, Slow_days: int
) -> vbt.Portfolio | None:
    """Executes a complete Moving Average Crossover System calculation pipeline.

    Args:
        ticker: The string financial identifier of the target asset (e.g., "INFY.NS").
        duration: The historical lookback timeframe duration to download.
        Fast_days: The sliding window size for the short-term trend line.
        Slow_days: The sliding window size for the long-term trend line.

    Returns:
        A vectorbt Portfolio simulation object containing the complete backtest
        historical ledger, or None if an ingestion failure occurs.
    """

    logger.info(f"Initializing pipeline matrix for ticker: {ticker}")

    # Step 1: INGESTION of data

    try:
        df: pd.DataFrame | None = yf.download(
            ticker, period=duration, interval="1d", auto_adjust=True
        )
        if df is None or df.empty:
            logger.error(f"Pipeline error: Empty frame returned for {ticker}")
            return None
    except Exception as e:
        logger.error(f"Critical failure during network data ingestion: {e}")
        return None
    # checking if array is 1D or 2D

    if isinstance(df.columns , pd.MultiIndex):
        close_vector = df['Close'][ticker].squeeze()
    else:
        close_vector = df['Close'].squeeze()
    # Step 2: engineering sliding window feature
    # computing fast_SMA and slow_SMA
    logger.info(f" Computing sliding windows: Fast ({Fast_days} days) vs Slow ({Slow_days} days)...")
    fast_sma = SMAIndicator(close=pd.Series(close_vector), window=Fast_days).sma_indicator()
    slow_sma = SMAIndicator(close=pd.Series(close_vector), window=Slow_days).sma_indicator()
    # Step 3: SIGNALS: Conditional Logics
    entry_signals = fast_sma > slow_sma
    exit_signals = fast_sma < slow_sma

    # initializing cold start by by cleaning out uninitialized NaN cells

    entry_signals = entry_signals.fillna(False)
    exit_signals = exit_signals.fillna(False)

    if isinstance(df.columns, pd.MultiIndex):
        high_vector = df["High"][ticker].squeeze()
        low_vector = df["Low"][ticker].squeeze()
        volume_vector = df["Volume"][ticker].squeeze()
    else:
        high_vector = df["High"].squeeze()
        low_vector = df["Low"].squeeze()
        volume_vector = df["Volume"].squeeze()


    period_high = df["High"].max()
    period_low = df["Low"].min()
    avg_close = df["Close"].mean()
    avg_vol = df["Volume"].mean()
    sma_fast_val = float(fast_sma.iloc[-1])
    sma_slow_val = float(slow_sma.iloc[-1])
    first_close = df["Close"].iloc[0]
    last_close = df["Close"].iloc[-1]
    pct_change = ((last_close - first_close) / first_close) * 100
    signal = "Fast SMA > Slow SMA → BULLISH" if sma_fast_val > sma_slow_val else "Fast SMA < Slow SMA → BEARISH"

    logger.info("--- %s Analysis Results ---", ticker)
    logger.info("Period:        %s", duration)
    logger.info("High (INR):    %.2f", period_high)
    logger.info("Low (INR):     %.2f", period_low)
    logger.info("Avg Close:     %.2f INR", avg_close)


    logger.info("Fast SMA (%d):  %.2f INR", Fast_days, sma_fast_val)
    logger.info("Slow SMA (%d):  %.2f INR", Slow_days, sma_slow_val)

    logger.info("Signal:        %s", signal)
    logger.info("Change (%%):    %.2f%%", pct_change)
    logger.info("Last Date:     %s", str(df.index[-1].strftime("%Y-%m-%d")))
    logger.info("Avg Volume:    %s", f"{float(avg_vol):,.0f}")

    # Step 4: simulatioon Engine (PORTFOLIO)
    logger.info(f" Routing state signals into vectorbt simulation engine")
    Portfolio = vbt.Portfolio.from_signals(
        close = close_vector,
        entries = entry_signals,
        exits = exit_signals,
        init_cash = 1000000.0, # Base capital
        fees = 0.001, # Brokerage
        freq = "1D"
        )
    return Portfolio

if __name__ == "__main__":
    target_asset = "INFY.NS"
    data_period = "2y"
    fast_window = 20
    slow_window = 50
    backtest_results = crossover_strategy(target_asset, data_period, fast_window, slow_window)
    if backtest_results is not None:
        logger.info("Strategy simulation performance metric sheet:")
        logger.info("=" * 50)
        logger.info(backtest_results.stats())  # Safe to execute stats tracking
        logger.info("=" * 50)
    else:
        logger.error("Pipeline execution failed. Unable to display metrics.")
