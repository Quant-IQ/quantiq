from fastapi import APIRouter, HTTPException, Query
import yfinance as yf
from pydantic import BaseModel
from typing import List, Optional

from src.data.fetch import fetch_ohlc

router = APIRouter(prefix="/stock", tags=["stock"])

SYMBOL_MAP = {
    "NIFTY50": "^NSEI",
    "SENSEX": "^BSESN",
    "BANKNIFTY": "^NSEBANK"
}

class StockInfo(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    description: Optional[str] = None
    previous_close: Optional[float] = None
    current_price: Optional[float] = None

import concurrent.futures

def get_ticker_info_safe(ticker):
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(lambda: ticker.info)
            return future.result(timeout=3.0)
    except Exception:
        return {}

@router.get("/{symbol}/info", response_model=StockInfo)
def get_stock_info(symbol: str):
    try:
        # Use existing logic from fetch.py for suffixing if needed, but yf.Ticker does not auto-suffix.
        # We will assume frontend sends the raw symbol (e.g., RELIANCE) and we append .NS if missing.
        mapped_symbol = SYMBOL_MAP.get(symbol.upper(), symbol)
        ticker_sym = mapped_symbol
        if not ticker_sym.startswith("^") and not (ticker_sym.endswith(".NS") or ticker_sym.endswith(".BO")):
            ticker_sym += ".NS"

        ticker = yf.Ticker(ticker_sym)
        # fast_info is reliable but lacks detailed metadata (PE, description, etc.)
        f_info = ticker.fast_info
        # Attempt to get full info with a timeout to prevent hanging on cloud servers
        info = get_ticker_info_safe(ticker)

        return StockInfo(
            symbol=symbol,
            name=info.get("longName", symbol),
            sector=info.get("sector"),
            industry=info.get("industry"),
            market_cap=info.get("marketCap") or f_info.get("marketCap"),
            pe_ratio=info.get("trailingPE") or info.get("forwardPE"),
            dividend_yield=info.get("dividendYield"),
            fifty_two_week_high=f_info.get("yearHigh") or info.get("fiftyTwoWeekHigh"),
            fifty_two_week_low=f_info.get("yearLow") or info.get("fiftyTwoWeekLow"),
            description=info.get("longBusinessSummary"),
            previous_close=f_info.get("previousClose") or info.get("previousClose"),
            current_price=f_info.get("lastPrice") or info.get("currentPrice") or info.get("regularMarketPrice"),
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch info for {symbol}: {str(e)}")

@router.get("/{symbol}/chart")
def get_stock_chart(
    symbol: str,
    range: str = Query("1y", description="Time range (e.g. 1d, 1w, 1m, 1y, 5y)"),
    interval: str = Query(None, description="Data interval (e.g. 1m, 15m, 1d, 1wk)")
):
    # Map friendly ranges to yfinance periods and intervals
    # Defaults if interval is not explicitly provided
    if not interval:
        if range == "1d":
            period = "1d"
            interval = "5m"
        elif range == "1w":
            period = "5d"
            interval = "15m"
        elif range == "1m":
            period = "1mo"
            interval = "1d"
        elif range == "1y":
            period = "1y"
            interval = "1d"
        elif range == "5y":
            period = "5y"
            interval = "1wk"
        else:
            period = range
            interval = "1d"
    else:
        period = range

    mapped_symbol = SYMBOL_MAP.get(symbol.upper(), symbol)
    df = fetch_ohlc(mapped_symbol, period=period, interval=interval)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail=f"No chart data found for {symbol}")

    # Format data for lightweight-charts
    # lightweight-charts expects time (unix timestamp or string YYYY-MM-DD)
    # and open, high, low, close, value (volume)
    result = []

    # If index is timezone aware, convert to UTC then to timestamp
    for date, row in df.iterrows():
        # Get timestamp in seconds
        ts = int(date.timestamp())

        result.append({
            "time": ts,
            "open": row["Open"],
            "high": row["High"],
            "low": row["Low"],
            "close": row["Close"],
            "value": row["Volume"],
        })

    return {"data": result}
