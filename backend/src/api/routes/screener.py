import logging
from typing import Dict, Any

from fastapi import APIRouter
from src.data.fetch import fetch_batch
from src.data.ticker_map import TICKER_MAP

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/screener")
def get_screener_data() -> Dict[str, Any]:
    """Fetches real data for all mapped tickers using the scripting team's fetch_batch."""
    # We use 5d interval to ensure we have a previous day for change_pct calculation
    # fetch_batch handles appending .NS internally, but returns keys with .NS
    tickers_to_fetch = list(TICKER_MAP.keys())
    batch_data = fetch_batch(tickers_to_fetch, period="5d", interval="1d", use_cache=True)
    
    response_data = []
    
    for ticker_name, df in batch_data.items():
        original_name = ticker_name.replace(".NS", "").replace(".BO", "")
        if df is None or df.empty or len(df) < 2:
            logger.warning(f"Could not get enough data for {original_name}")
            continue
            
        try:
            latest = df.iloc[-1]
            previous = df.iloc[-2]
            
            ltp = float(latest["Close"])
            prev_close = float(previous["Close"])
            change_pct = ((ltp - prev_close) / prev_close) * 100 if prev_close != 0 else 0
            
            response_data.append({
                "symbol": original_name,
                "ltp": round(ltp, 2),
                "change_pct": round(change_pct, 2),
                "day_high": round(float(latest["High"]), 2),
                "day_low": round(float(latest["Low"]), 2),
                "volume": int(latest["Volume"])
            })
        except Exception as e:
            logger.error(f"Error parsing data for {original_name}: {e}")
            continue
            
    return {"data": response_data}
