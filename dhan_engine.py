# save as test.py, run: python test.py
import yfinance as yf
import pandas as pd
from ta.trend import SMAIndicator

df = yf.download("RELIANCE.NS", period="3mo", interval="1d", auto_adjust=True)
assert not df.empty, "yfinance fetch failed"

# df["SMA20"] = SMAIndicator(close=df["Close"], window=20).sma_indicator()
# This line throws an error "ValueError: Data must be 1-dimensional, got ndarray of shape (59, 1) instead" because ta library expects a 1D array, but df["Close"] is a Series (2D). We need to squeeze it to make it 1D.

df["SMA20"] = SMAIndicator(close=df["Close"].squeeze(), window=20).sma_indicator()
df.dropna(inplace=True)
assert "SMA20" in df.columns, "ta indicator failed"

print(df[["Close", "SMA20"]].tail())
print("Data + indicator pipeline OK")