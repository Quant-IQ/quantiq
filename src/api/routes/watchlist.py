import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException

from src.watchlist import manager
from src.data.fetch import fetch_batch

logger = logging.getLogger(__name__)
router = APIRouter()

def _bootstrap_watchlists():
    if len(manager.list_all()) == 0:
        logger.info("No watchlists found. Bootstrapping defaults...")
        manager.create("NIFTY_BANK", ["HDFCBANK", "ICICIBANK", "AXISBANK"])
        manager.create("NIFTY_IT", ["TCS", "INFY", "HCLTECH"])
        manager.create("CORE_PORTFOLIO", ["RELIANCE", "LT", "TITAN", "TVSMOTOR", "M&M"])

@router.get("/watchlists")
def get_watchlists() -> Dict[str, List[str]]:
    _bootstrap_watchlists()
    return {"watchlists": manager.list_all()}

@router.get("/watchlists/{name}")
def get_watchlist_data(name: str) -> Dict[str, Any]:
    _bootstrap_watchlists()
    
    wl = manager.get(name)
    if not wl or not wl.tickers:
        return {"data": []}
        
    batch_data = fetch_batch(wl.tickers, period="5d", interval="1d", use_cache=True)
    response_data = []
    
    for ticker_name, df in batch_data.items():
        original_name = ticker_name.replace(".NS", "").replace(".BO", "")
        if df is None or df.empty or len(df) < 2:
            continue
            
        try:
            latest = df.iloc[-1]
            previous = df.iloc[-2]
            
            ltp = float(latest["Close"])
            prev_close = float(previous["Close"])
            change_pct = ((ltp - prev_close) / prev_close) * 100 if prev_close != 0 else 0
            
            # Extract sparkline (all Close prices in the series)
            sparkline = [round(float(val), 2) for val in df["Close"].dropna().tolist()]
            
            response_data.append({
                "symbol": original_name,
                "ltp": round(ltp, 2),
                "change_pct": round(change_pct, 2),
                "day_high": round(float(latest["High"]), 2),
                "day_low": round(float(latest["Low"]), 2),
                "volume": int(latest["Volume"]),
                "sparkline": sparkline
            })
        except Exception as e:
            logger.error(f"Error parsing data for {original_name}: {e}")
            continue
            
    return {"data": response_data}
