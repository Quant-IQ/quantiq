import logging
from typing import Dict, Any
from fastapi import APIRouter
from src.data.fetch import fetch_batch

logger = logging.getLogger(__name__)
router = APIRouter()

# Map the yfinance index symbols to display names
INDEX_MAPPING = {
    "^NSEI": "NIFTY 50",
    "^BSESN": "SENSEX",
    "^NSEBANK": "NIFTY BANK"
}

@router.get("/dashboard/indices")
def get_dashboard_indices() -> Dict[str, Any]:
    """Fetches real-time index data using the scripting team's fetch_batch function."""
    symbols = list(INDEX_MAPPING.keys())
    batch_data = fetch_batch(symbols, period="5d", interval="1d", use_cache=True)
    
    response_data = []
    
    for symbol, df in batch_data.items():
        if df is None or df.empty or len(df) < 2:
            logger.warning(f"Could not get enough data for index {symbol}")
            continue
            
        try:
            latest = df.iloc[-1]
            previous = df.iloc[-2]
            
            ltp = float(latest["Close"])
            prev_close = float(previous["Close"])
            change = ltp - prev_close
            change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
            
            response_data.append({
                "name": INDEX_MAPPING.get(symbol, symbol),
                "value": round(ltp, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2)
            })
        except Exception as e:
            logger.error(f"Error parsing index data for {symbol}: {e}")
            continue
            
    return {"indices": response_data}
