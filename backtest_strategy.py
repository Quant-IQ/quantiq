import os
import pandas as pd
import vectorbt as vbt
from dotenv import load_dotenv
from dhanhq import dhanhq

# 1. ENVIRONMENT VARIABLES SE KEYS LOAD KARNA
load_dotenv()

# Setup Dhan API Connection
dhan = dhanhq(
    client_id=os.getenv("DHAN_CLIENT_ID"), 
    access_token=os.getenv("DHAN_ACCESS_TOKEN")
)

print("🛰️ Connecting to Dhan API & Pulling Historical Data...")

# 2. DHAN API SE DATA FETCH KARNA
try:
    # FIXED: Used official dhanhq method 'historical_data' instead of 'get_historical_data'
    raw_data = dhan.historical_data(
        security_id="1333",          # Reliance Industries on NSE
        exchange_segment="NSE_EQ",    
        instrument_type="EQUITY",
        expiry_code=0,
        from_date="2026-01-01",      
        to_date="2026-05-27",        
        data_period="15"             # 15-minute intervals
    )
    
    # Data ko tabular DataFrame mein convert karna
    df = pd.DataFrame(raw_data['data'])
    df['start_Time'] = pd.to_datetime(df['start_Time'])
    df.set_index('start_Time', inplace=True)
    print(f"✅ Data loaded successfully from Dhan! Total records: {len(df)}")

except Exception as e:
    print(f"⚠️ API Connection Issue: {e}")
    print("🔄 Falling back to a robust mock data system for execution testing...")
    import numpy as np
    range_dates = pd.date_range(start="2026-01-01", end="2026-05-27", freq="15min")
    mock_close = 2500 + np.cumsum(np.random.normal(0.1, 3.0, len(range_dates)))
    df = pd.DataFrame(index=range_dates, data={'close': mock_close})

# 3. CORE STRATEGY LOGIC DEFINITION
price_series = df['close']

# Calculating the two moving averages via VectorBT
fast_ma = vbt.MA.run(price_series, window=9).ma
slow_ma = vbt.MA.run(price_series, window=21).ma

# FIXED: Replaced '.vbt.crosses_above' with clean matrix boolean comparisons to avoid Vbt_SRAccessor crashes
# ENTRY (BUY): Fast MA cuts or stays above Slow MA
buy_signals = fast_ma > slow_ma

# EXIT (SELL): Fast MA cuts or stays below Slow MA
sell_signals = fast_ma < slow_ma

# 4. RUNNING THE VECTORBT SIMULATION ENGINE
print("🚀 Simulating trades over the timeline...")
portfolio = vbt.Portfolio.from_signals(
    close=price_series,
    entries=buy_signals,
    exits=sell_signals,
    init_cash=100000,   # Starting with 1 Lakh INR capital
    fees=0.0005         # 0.05% brokerage/slippage simulation cost
)

# 5. PRINT THE PERFORMANCE RESULTS
print("\n" + "="*45)
print("📊 SIMPLIFIED BACKTEST PERFORMANCE REPORT")
print("="*45)
print(portfolio.stats())
print("="*45)