# QuantIQ Master Reference Binder

> **Version:** 18 May 2026 | **Repository:** github.com/Quant-IQ/quantiq | **Total pages:** 212

> This document combines all 11 binder modules into a single searchable reference.

---

## Table of Contents

- [M0 — Master Index & Usage Guide](#m0) (10 pp)
- [M1 — DhanHQ v2 — Broker API](#m1) (35 pp)
- [M2 — Python Data Stack (pandas, numpy, yfinance)](#m2) (20 pp)
- [M3 — Technical Analysis — ta library](#m3) (20 pp)
- [M4 — Backtesting — vectorbt](#m4) (20 pp)
- [M5 — Dashboard — Streamlit](#m5) (21 pp)
- [M6 — Charting — Plotly Python](#m6) (21 pp)
- [M7 — Python Standards (PEP 8/257/484, Google Style, logging)](#m7) (18 pp)
- [M8 — Version Control & DevOps](#m8) (15 pp)
- [M9 — Regulatory — SEBI & NSE](#m9) (13 pp)
- [M10 — Environment & Tooling](#m10) (19 pp)

---


# M0 — Master Index & Usage Guide


## Hard Constraints — Master List

Every rule below is non-negotiable in QuantIQ. Code that violates any item here is broken by definition.


### API & Broker

| # | Constraint | Source |
| --- | --- | --- |
| A1 | Dhan access token expires every 24 hours. Bot must regenerate daily before 09:15 IST. | SEBI / M1 §3 |
| A2 | Order rate must never exceed 10 orders/sec/exchange/client. | SEBI Feb 2025 / M1 §10 |
| A3 | Static IP must be whitelisted before any live order. Use DhanLogin.set_ip(). | SEBI / M1 §3 |
| A4 | No paper-trading sandbox in Dhan SDK. Use vectorbt for simulation. | M1 §3 / M4 |
| A5 | Pin dhanhq==2.0.2. v2.2.0 has breaking import changes — do not upgrade without checking releases. | Dhan releases / M1 §1 |


### Data & Libraries

| # | Constraint | Source |
| --- | --- | --- |
| D1 | yfinance tickers for NSE must be suffixed .NS. Unsuffixed = US ticker. | M2 §4 |
| D2 | ta library has NO VWAP. Use manual cumulative formula. | M3 §5 |
| D3 | vectorbt: pin vectorbt==1.0.0. v1.0.0 is open-source (went free 2025). Do not auto-upgrade. | M4 §1 |
| D4 | Python version: pin >=3.11,<3.13 in pyproject.toml. | M10 §4 |
| D5 | python-dotenv >=1.2.2 requires Python >=3.10. | M10 §2 |


### Security & Credentials

| # | Constraint | Source |
| --- | --- | --- |
| S1 | .streamlit/secrets.toml and .env must be in .gitignore. | M5 §6 / M10 §3 |
| S2 | No hardcoded API keys, client IDs, or tokens anywhere in repo. | M10 §2 |
| S3 | Streamlit secrets are pasted into Community Cloud UI, not committed. | M5 §7 |
| S4 | OAuth 2FA mandatory for Dhan login (per SEBI Feb 2025). | M9 §3 |


### Operational (Phase 4 live trading)

| # | Constraint | Source |
| --- | --- | --- |
| O1 | Daily session logout. No persistent session across trading days. | M9 §3 |
| O2 | Audit log retention >=5 years. Use TimedRotatingFileHandler. | M9 §3 / M7 §6 |
| O3 | All algo activity tagged with algo-ID for exchange reporting. | M9 §3 |
| O4 | Backtest before any strategy goes live. Use vectorbt Portfolio. | M4 |


## Module Map

| # | Title | Contents | ~Pages |
| --- | --- | --- | --- |
| M0 | Master Index & Usage Guide | - | 10 |
| M1 | DhanHQ v2 — Broker API | - | 35 |
| M2 | Python Data Stack (pandas, numpy, yfinance) | - | 20 |
| M3 | Technical Analysis — ta library | - | 20 |
| M4 | Backtesting — vectorbt | - | 20 |
| M5 | Dashboard — Streamlit | - | 21 |
| M6 | Charting — Plotly Python | - | 21 |
| M7 | Python Standards (PEP 8/257/484, Google Style, logging) | - | 18 |
| M8 | Version Control & DevOps | - | 15 |
| M9 | Regulatory — SEBI & NSE | - | 13 |
| M10 | Environment & Tooling | - | 19 |


## Quick-Find Index

Key terms and where to find them in this document:

| Term | Location |
| --- | --- |
| Access token (Dhan) | M1 §3 — Authentication |
| ADX indicator | M3 §6 — Trend Indicators |
| ATR indicator | M3 §5 — Volatility Indicators |
| Bollinger Bands | M3 §5 — Volatility Indicators |
| Candlestick chart | M6 §3 |
| Conventional Commits | M8 §2 |
| Dhan API rate limits | M1 §1 Quick Reference |
| Dhan order placement | M1 §4 — Orders |
| Dhan WebSocket | M1 §7 — Live Market Feed |
| Google-style docstrings | M7 §4 |
| Historical data (Dhan) | M1 §8 |
| MACD indicator | M3 §3 — Momentum Indicators |
| NSE ticker (.NS suffix) | M2 §7 — yfinance |
| Option chain (Dhan) | M1 §9 |
| Order rate limit (10/sec) | M9 §1 / M1 §1 |
| pandas DataFrame | M2 §2 |
| PEP 8 | M7 §2 |
| Plotly candlestick | M6 §3 |
| Portfolio metrics | M4 §7 |
| RSI indicator | M3 §3 — Momentum Indicators |
| SEBI Feb 2025 circular | M9 §3 |
| Secrets (Streamlit) | M5 §10 |
| Semantic Versioning | M8 §3 |
| Static IP whitelisting | M9 §1 / M1 §3 |
| Streamlit widgets | M5 §6 |
| vectorbt installation | M4 §2 |
| VWAP workaround | M3 §8 / M2 §5 |
| yfinance NSE ticker | M2 §7 |

---


# M1 — DhanHQ v2 — Broker API

> **Source:** dhanhq.co/docs/v2/ (DhanHQ v2.5, captured 18 May 2026)  
> **SDK:** `pip install dhanhq` (pin: `dhanhq==2.0.2`)  
> **Hard constraints:** 10 orders/sec, 24-hour token, static IP mandatory


## Quick Reference


### Base URL

```
https://api.dhan.co/v2/
```


### Headers (every request)

| Header | Value |
| --- | --- |
| Content-Type | application/json |
| access-token | JWT from generateAccessToken |
| client-id | dhanClientId (Quote APIs only) |


### Rate Limits

| Window | Order APIs | Data APIs | Quote APIs | Non Trading |
| --- | --- | --- | --- | --- |
| per second | 10 | 5 | 1 | 20 |
| per minute | 250 | — | Unlimited | Unlimited |
| per hour | 1,000 | — | Unlimited | Unlimited |
| per day | 7,000 | 100,000 | Unlimited | Unlimited |

> Order Modifications: max 25 per order. Option Chain: 1 unique request per 3 seconds.


### Python SDK quickstart

```python
pip install dhanhq

from dhanhq import dhanhq
dhan = dhanhq("client_id", "access_token")

# Place market order
dhan.place_order(
    security_id="11536",
    exchange_segment=dhan.NSE,
    transaction_type=dhan.BUY,
    quantity=5,
    order_type=dhan.MARKET,
    product_type=dhan.INTRA,
    price=0
)
```


### Endpoint Cheat Sheet

| Method | Path | Purpose |
| --- | --- | --- |
| POST | /orders | Place new order |
| PUT | /orders/{id} | Modify pending order |
| DELETE | /orders/{id} | Cancel pending order |
| GET | /orders | Get day's order book |
| GET | /trades | Get day's trade book |
| GET | /holdings | Demat holdings |
| GET | /positions | Open positions |
| DELETE | /positions | Exit all positions |
| GET | /fundlimit | Available funds |
| POST | /margincalculator | Pre-trade margin check |
| POST | /marketfeed/ltp | Up to 1000 LTPs |
| POST | /marketfeed/ohlc | Up to 1000 OHLC |
| POST | /marketfeed/quote | Quote with depth |
| POST | /charts/historical | Daily candles |
| POST | /charts/intraday | Min candles (90d) |
| POST | /optionchain | Full option chain |
| POST | /optionchain/expirylist | Active expiries |
| GET | /profile | User profile / token validity |


## Authentication

Two access methods: (a) direct access token from Dhan Web (24-hour), (b) API key + secret OAuth flow (12-month key, 24-hour token).


### Generate Access Token via API (TOTP)

```
POST https://auth.dhan.co/app/generateAccessToken
?dhanClientId=1000000001&pin=111111&totp=000000
```


### Renew Token

```
GET https://api.dhan.co/v2/RenewToken
# Renews active token for another 24 hours. Cannot renew expired tokens.
```


### OAuth Flow (3 steps)

```
# Step 1 — Generate Consent
POST https://auth.dhan.co/app/generate-consent?client_id={dhanClientId}
Headers: app_id, app_secret
Returns: consentAppId (max 25/day)

# Step 2 — Browser Login
https://auth.dhan.co/login/consentApp-login?consentAppId={...}
# User enters credentials + 2FA; redirects to redirect_URL?tokenId={...}

# Step 3 — Consume Consent
POST https://auth.dhan.co/app/consumeApp-consent?tokenId={tokenId}
Headers: app_id, app_secret
Returns: accessToken
```


### Static IP Whitelisting (MANDATORY — SEBI)

```python
# Set IP (mandatory before any order)
POST https://api.dhan.co/v2/ip/setIP
{
  "dhanClientId": "1000000001",
  "ip": "10.200.10.10",
  "ipFlag": "PRIMARY"    # or "SECONDARY"
}
# 7-day cooldown after setting. Cannot modify within 7 days.

# Get current whitelisted IPs
GET https://api.dhan.co/v2/ip/getIP

# Modify IP (after 7-day cooldown)
PUT https://api.dhan.co/v2/ip/modifyIP
```


### User Profile (startup check)

```python
GET https://api.dhan.co/v2/profile
# Returns: dhanClientId, tokenValidity, activeSegment, ddpi, mtf, dataPlan

# Recommended first call on bot startup to verify token validity
```


## Orders


### Place Order

```python
POST /orders
{
    "dhanClientId": "1000000003",
    "correlationId": "123abc678",
    "transactionType": "BUY",       # BUY or SELL
    "exchangeSegment": "NSE_EQ",    # see Annexure
    "productType": "INTRADAY",      # CNC, INTRADAY, MARGIN, MTF, CO, BO
    "orderType": "MARKET",          # LIMIT, MARKET, STOP_LOSS, STOP_LOSS_MARKET
    "validity": "DAY",              # DAY or IOC
    "securityId": "11536",
    "quantity": "5",
    "price": "",
    "triggerPrice": "",
    "afterMarketOrder": false
}
# Returns: {"orderId": "112111182198", "orderStatus": "PENDING"}
```


### Modify Order

```python
PUT /orders/{order-id}
{
    "dhanClientId": "1000000009",
    "orderId": "112111182045",
    "orderType": "LIMIT",
    "quantity": "40",       # TOTAL quantity, not pending (v2 breaking change)
    "price": "3345.8",
    "validity": "DAY"
}
# Max 25 modifications per order
```


### Order Status Values

| Status | Meaning |
| --- | --- |
| TRANSIT | Did not reach exchange |
| PENDING | Awaiting execution |
| REJECTED | Rejected by broker or exchange |
| CANCELLED | Cancelled by user |
| PART_TRADED | Partial fill |
| TRADED | Fully executed |
| EXPIRED | Validity elapsed |


## Portfolio & Positions

```python
GET /holdings        # Demat holdings (delivered positions)
GET /positions       # Open positions (current day)
POST /positions/convert  # Convert INTRADAY <-> CNC
DELETE /positions    # EXIT ALL positions + cancel open orders (kill switch)
```


## Market Quote

```python
# LTP only (up to 1000 instruments, 1 req/sec)
POST /marketfeed/ltp
{"NSE_EQ": [11536], "NSE_FNO": [49081]}

# OHLC + LTP
POST /marketfeed/ohlc

# Full quote with 5-level depth + OI
POST /marketfeed/quote
# Returns: last_price, volume, oi, depth (5 levels bid/ask), circuit limits, OHLC
```


## Live Market Feed (WebSocket)

```python
# Connect
wss://api-feed.dhan.co?version=2&token={JWT}&clientId={clientId}&authType=2
# Max 5 connections per user. Up to 5,000 instruments per connection.

# Subscribe (send JSON over open connection)
{"RequestCode": 15, "InstrumentCount": 2,
 "InstrumentList": [{"ExchangeSegment": "NSE_EQ", "SecurityId": "1333"}]}

# Request codes: 15/16=Ticker sub/unsub, 17/18=Quote, 21/22=Full, 23/24=FullDepth
# Response is binary Little Endian. 8-byte header + payload.
# Response codes: 2=Ticker, 4=Quote, 8=Full, 5=OI, 6=PrevClose, 50=Disconnect
```


## Historical Data

```python
# Daily candles (full history)
POST /charts/historical
{
  "securityId": "1333",
  "exchangeSegment": "NSE_EQ",
  "instrument": "EQUITY",
  "fromDate": "2022-01-08",
  "toDate": "2022-02-08",
  "oi": false
}
# Returns column-oriented parallel arrays: open[], high[], low[], close[], volume[], timestamp[]

# Intraday (interval: 1, 5, 15, 25, 60 minutes — max 90 days per call, 5yr history)
POST /charts/intraday
{"securityId": "1333", "exchangeSegment": "NSE_EQ",
 "instrument": "EQUITY", "interval": "5",
 "fromDate": "2024-09-11 09:30:00", "toDate": "2024-09-15 13:00:00"}
```

```python
# Convert DhanHQ response to DataFrame
import pandas as pd
df = pd.DataFrame(response)
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', utc=True).dt.tz_convert('Asia/Kolkata')
df = df.set_index('timestamp')
```


## Option Chain

```python
POST /optionchain
{"UnderlyingScrip": 13, "UnderlyingSeg": "IDX_I", "Expiry": "2024-10-31"}
# Returns: last_price (spot), oc: {strike: {ce: {...}, pe: {...}}}
# Per strike: last_price, volume, oi, iv, greeks (delta, gamma, theta, vega),
#             top_bid_price, top_ask_price, security_id

POST /optionchain/expirylist
{"UnderlyingScrip": 13, "UnderlyingSeg": "IDX_I"}
# Returns list of expiry dates in YYYY-MM-DD format
```


## Annexure — Enums


### Exchange Segment

| Enum | Exchange | Segment |
| --- | --- | --- |
| NSE_EQ | NSE | Equity Cash |
| NSE_FNO | NSE | Futures & Options |
| BSE_EQ | BSE | Equity Cash |
| MCX_COMM | MCX | Commodity |
| NSE_CURRENCY | NSE | Currency |
| IDX_I | Index | Index Value |


### Product Type

| Enum | Description |
| --- | --- |
| CNC | Cash & Carry (delivery) |
| INTRADAY | Intraday |
| MARGIN | Carry-forward F&O |
| MTF | Margin Trading Facility |
| CO | Cover Order (SL mandatory) |
| BO | Bracket Order (target + SL) |


### Error Codes

| Code | Type |
| --- | --- |
| DH-901 | Invalid auth (token/client ID expired) |
| DH-902 | Invalid access (subscription/segment) |
| DH-904 | Rate limit breached |
| DH-905 | Input exception (missing fields) |
| DH-906 | Order error |
| DH-908 | Internal server error |


## Release Notes (v2.0 — v2.5)

| Version | Date | Key Changes |
| --- | --- | --- |
| v2.5 | Feb 09 2026 | Conditional Trigger Orders, P&L exit (Trader's Control), TOTP-based token gen via API |
| v2.4 | Sep 22 2025 | API Key+Secret login (12-month key). BREAKING: token now 24-hour. Static IP mandatory. |
| v2.3 | Sep 08 2025 | Full Market Depth (200-level) on WebSocket. Historical Options Data. Order rate = 10/sec. |
| v2.2 | Mar 07 2025 | Super Orders. User Profile API. Intraday history extended to 5 years. |
| v2.1 | Jan 06 2025 | 20-level Market Depth. Option Chain API with Greeks. |
| v2.0 | Sep 15 2024 | Market Quote API. Forever Orders. BREAKING: quantity=total in modify, epoch timestamps. |

---


# M2 — Python Data Stack (pandas, numpy, yfinance)

> **Libraries:** pandas, numpy, yfinance  
> **Install:** `pip install pandas numpy yfinance`  
> **Docs:** pandas.pydata.org | numpy.org | ranaroussi.github.io/yfinance


## Quick Reference


### Imports

```python
import pandas as pd
import numpy as np
import yfinance as yf
```


### pandas — Most-Used One-Liners

| Expression | What it does |
| --- | --- |
| pd.DataFrame(data) | Create DataFrame |
| pd.read_csv('f.csv', parse_dates=['date']) | Load CSV |
| df.head(n) / df.tail(n) | First/last n rows |
| df.info() | Schema: dtypes, non-null counts |
| df.describe() | Stats: mean, std, min, quartiles, max |
| df['col'] | Select column (Series) |
| df[['a','b']] | Select multiple columns (DataFrame) |
| df.loc[row, col] | Label-based indexing |
| df.iloc[i, j] | Integer-position indexing |
| df[df['col'] > x] | Boolean filter |
| df.sort_values('col') | Sort by column |
| df.groupby('col').agg({'v':'mean'}) | Group + aggregate |
| df.merge(df2, on='key') | SQL-style join |
| df.fillna(method='ffill') | Forward-fill NaN |
| df.dropna() | Drop rows with NaN |
| df.resample('W').mean() | Downsample time series weekly |
| df['col'].rolling(20).mean() | 20-period rolling mean |
| df['col'].pct_change() | Period-over-period % change |


### yfinance — Most-Used One-Liners

| Expression | What it does |
| --- | --- |
| yf.download('RELIANCE.NS', period='1y') | Daily OHLCV, 1 year |
| yf.download('TCS.NS', start='2024-01-01', end='2025-01-01') | Custom date range |
| yf.download('INFY.NS', interval='5m', period='5d') | 5-min bars, last 5 days |
| yf.Ticker('HDFC.NS').history(period='6mo') | Via Ticker object |
| yf.download(['TCS.NS','INFY.NS'], period='1y') | Multiple tickers — MultiIndex |

> **NSE suffix rules:** NSE stocks → `.NS` | BSE stocks → `.BO` | Nifty 50 → `^NSEI` | Bank Nifty → `^NSEBANK`


## pandas — Core Concepts


### Creating DataFrames

```python
# From dict
df = pd.DataFrame({'open':[100,102], 'close':[101,104], 'volume':[1e6,2e6]})

# From CSV
df = pd.read_csv('data.csv', parse_dates=['date'], index_col='date')

# From yfinance (already a DataFrame)
df = yf.download('RELIANCE.NS', period='1y')
```


### Selecting Data

```python
close = df['Close']                          # Single column -> Series
ohlc  = df[['Open','High','Low','Close']]   # Multiple -> DataFrame
val   = df.loc['2024-01-15', 'Close']       # Label-based
sli   = df.loc['2024-01':'2024-03']         # Date slice
first = df.iloc[0]                           # Integer position
big_vol  = df[df['Volume'] > 1_000_000]     # Boolean filter
green    = df[df['Close'] > df['Open']]
```


## pandas — Time Series


### DatetimeIndex

```python
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')

# NSE trading hours filter (IST)
df.index = df.index.tz_convert('Asia/Kolkata')
session = df.between_time('09:15', '15:30')
```


### Resampling

```python
# 1-min bars -> 5-min OHLCV
ohlcv_5m = df.resample('5T').agg({
    'Open':'first', 'High':'max', 'Low':'min', 'Close':'last', 'Volume':'sum'
})
```


### Rolling and EWM

```python
df['SMA20'] = df['Close'].rolling(20).mean()
df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
df['Volatility'] = df['Returns'].rolling(20).std() * (252**0.5)
```


## Trading Patterns


### Load DhanHQ Historical Data into DataFrame

```python
def dhan_to_df(response: dict) -> pd.DataFrame:
    df = pd.DataFrame({
        'Open':   response['open'],
        'High':   response['high'],
        'Low':    response['low'],
        'Close':  response['close'],
        'Volume': response['volume'],
    }, index=pd.to_datetime(response['timestamp'], unit='s', utc=True).tz_convert('Asia/Kolkata'))
    df.index.name = 'Date'
    return df
```


### VWAP — Manual Implementation (ta library has no VWAP)

```python
def vwap(df: pd.DataFrame) -> pd.Series:
    typical = (df['High'] + df['Low'] + df['Close']) / 3
    return (typical * df['Volume']).cumsum() / df['Volume'].cumsum()

df['VWAP'] = vwap(df)
```


### Sharpe Ratio

```python
def sharpe(returns: pd.Series, risk_free=0.065, periods=252) -> float:
    rf_daily = risk_free / periods
    excess   = returns - rf_daily
    return (excess.mean() / excess.std()) * (periods ** 0.5)
```


## yfinance — NSE Data Fetching

> **Critical:** All NSE tickers MUST be suffixed `.NS`. Unsuffixed tickers silently return US equity data. No error is raised. See [GitHub issue #825](https://github.com/ranaroussi/yfinance/issues/825).

```python
# Always validate suffix
def nse(symbol: str) -> str:
    if not symbol.endswith(('.NS', '.BO')):
        return symbol + '.NS'
    return symbol

# Download with date range
df = yf.download('RELIANCE.NS', start='2024-01-01', end='2025-01-01', auto_adjust=True)

# Intraday (1m=7d max, 5m/15m=60d max, 1h=730d max)
df = yf.download('INFY.NS', period='5d', interval='5m', auto_adjust=True)

# Multiple tickers
data = yf.download(['TCS.NS','INFY.NS'], period='1y', auto_adjust=True)
tcs_close = data['Close']['TCS.NS']
```


### NSE Index Tickers

| Index | Ticker |
| --- | --- |
| Nifty 50 | ^NSEI |
| Bank Nifty | ^NSEBANK |
| Sensex | ^BSESN |

---


# M3 — Technical Analysis — ta library

> **Install:** `pip install ta`  
> **Docs:** technical-analysis-library-in-python.readthedocs.io  
> **CRITICAL:** ta has **NO VWAP**. See §VWAP below for manual implementation.


## Install & Import

```python
pip install ta

from ta import add_all_ta_features
from ta.utils import dropna
from ta.momentum  import RSIIndicator, MACD, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.trend     import SMAIndicator, EMAIndicator, ADXIndicator
from ta.volume    import OnBalanceVolumeIndicator, MFIIndicator
```


## All 42 Indicators at a Glance

| Category | Indicators |
| --- | --- |
| Momentum (11) | RSI, MACD, Stochastic, StochRSI, ROC, Williams %R, Awesome Oscillator, KAMA, PPO, TSI, Ultimate Oscillator |
| Volume (8) | OBV, Chaikin MF, Force Index, EoM, VPT, MFI, NVI, PVO |
| Volatility (5) | Bollinger Bands, ATR, Keltner Channel, Donchian Channel, Ulcer Index |
| Trend (12) | SMA, EMA, WMA, DEMA, TEMA, TRIX, Mass Index, CCI, DPO, KST, Ichimoku, PSAR, STC, ADX |
| Others (3) | Daily Return, Daily Log Return, Cumulative Return |


## Momentum Indicators


### RSI

```python
from ta.momentum import RSIIndicator
ind = RSIIndicator(close=df['Close'], window=14)
df['RSI'] = ind.rsi()
# Overbought: RSI > 70 | Oversold: RSI < 30
```


### MACD

```python
from ta.momentum import MACD
macd = MACD(close=df['Close'], window_slow=26, window_fast=12, window_sign=9)
df['MACD']        = macd.macd()
df['MACD_signal'] = macd.macd_signal()
df['MACD_hist']   = macd.macd_diff()
```


### Stochastic Oscillator

```python
from ta.momentum import StochasticOscillator
stoch = StochasticOscillator(high=df['High'], low=df['Low'],
                              close=df['Close'], window=14, smooth_window=3)
df['Stoch_K'] = stoch.stoch()
df['Stoch_D'] = stoch.stoch_signal()
```


## Volatility Indicators


### Bollinger Bands

```python
from ta.volatility import BollingerBands
bb = BollingerBands(close=df['Close'], window=20, window_dev=2)
df['BB_upper'] = bb.bollinger_hband()
df['BB_mid']   = bb.bollinger_mavg()
df['BB_lower'] = bb.bollinger_lband()
df['BB_pct']   = bb.bollinger_pband()    # 0=lower, 1=upper
df['BB_width'] = bb.bollinger_wband()
```


### ATR — Average True Range

```python
from ta.volatility import AverageTrueRange
atr = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14)
df['ATR'] = atr.average_true_range()
# ATR-based stop loss: stop = entry - (2 * ATR)
```


## Trend Indicators


### SMA and EMA

```python
from ta.trend import SMAIndicator, EMAIndicator
df['SMA20']  = SMAIndicator(close=df['Close'], window=20).sma_indicator()
df['SMA50']  = SMAIndicator(close=df['Close'], window=50).sma_indicator()
df['EMA12']  = EMAIndicator(close=df['Close'], window=12).ema_indicator()
df['EMA26']  = EMAIndicator(close=df['Close'], window=26).ema_indicator()
```


### ADX — Average Directional Index

```python
from ta.trend import ADXIndicator
adx = ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'], window=14)
df['ADX']     = adx.adx()       # Trend strength 0-100 (>25 = strong trend)
df['ADX_pos'] = adx.adx_pos()   # +DI (bullish direction)
df['ADX_neg'] = adx.adx_neg()   # -DI (bearish direction)
```


### Parabolic SAR

```python
from ta.trend import PSARIndicator
psar = PSARIndicator(high=df['High'], low=df['Low'], close=df['Close'], step=0.02, max_step=0.2)
df['PSAR']        = psar.psar()
df['PSAR_up_ind'] = psar.psar_up_indicator()   # 1 in uptrend
```


## Volume Indicators


### OBV

```python
df['OBV'] = OnBalanceVolumeIndicator(close=df['Close'], volume=df['Volume']).on_balance_volume()
```


### MFI — Money Flow Index

```python
from ta.volume import MFIIndicator
df['MFI'] = MFIIndicator(high=df['High'], low=df['Low'],
                          close=df['Close'], volume=df['Volume'], window=14).money_flow_index()
```


## VWAP — Manual Implementation

> **WARNING:** `ta` does NOT include VWAP. `ta.volume.VolumeWeightedAveragePrice` does not exist. Use the code below.

```python
def vwap_session(df: pd.DataFrame) -> pd.Series:
    """Intraday VWAP — resets each session."""
    typical   = (df['High'] + df['Low'] + df['Close']) / 3
    cum_tp_vol = (typical * df['Volume']).cumsum()
    return cum_tp_vol / df['Volume'].cumsum()

# Multi-day VWAP (resets daily)
def add_vwap(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['Date'] = df.index.date
    df['TP']   = (df['High'] + df['Low'] + df['Close']) / 3
    df['VWAP'] = (
        df.groupby('Date')['TP'].transform(lambda x: (x * df.loc[x.index,'Volume']).cumsum()) /
        df.groupby('Date')['Volume'].cumsum()
    )
    return df.drop(columns=['Date','TP'])
```


## Add All Indicators at Once

```python
from ta import add_all_ta_features
from ta.utils import dropna

df = dropna(df)   # required first
df = add_all_ta_features(df, open='Open', high='High',
                          low='Low', close='Close', volume='Volume')
# Adds ~60 columns: momentum_rsi, volatility_atr, trend_sma_fast, etc.
```


## QuantIQ Standard Indicator Pipeline

```python
from ta.utils     import dropna
from ta.momentum  import RSIIndicator, MACD
from ta.volatility import BollingerBands, AverageTrueRange
from ta.trend     import SMAIndicator, EMAIndicator, ADXIndicator
from ta.volume    import OnBalanceVolumeIndicator

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = dropna(df.copy())
    df['SMA20']   = SMAIndicator(df['Close'], 20).sma_indicator()
    df['SMA50']   = SMAIndicator(df['Close'], 50).sma_indicator()
    df['EMA12']   = EMAIndicator(df['Close'], 12).ema_indicator()
    df['EMA26']   = EMAIndicator(df['Close'], 26).ema_indicator()
    adx = ADXIndicator(df['High'], df['Low'], df['Close'], 14)
    df['ADX']     = adx.adx()
    df['RSI']     = RSIIndicator(df['Close'], 14).rsi()
    m = MACD(df['Close'])
    df['MACD']    = m.macd()
    df['MACD_s']  = m.macd_signal()
    df['MACD_h']  = m.macd_diff()
    bb = BollingerBands(df['Close'], 20, 2)
    df['BB_h']    = bb.bollinger_hband()
    df['BB_l']    = bb.bollinger_lband()
    df['BB_pct']  = bb.bollinger_pband()
    df['ATR']     = AverageTrueRange(df['High'],df['Low'],df['Close'],14).average_true_range()
    df['OBV']     = OnBalanceVolumeIndicator(df['Close'],df['Volume']).on_balance_volume()
    return df.dropna()
```

---


# M4 — Backtesting — vectorbt

> **Install:** `pip install vectorbt==1.0.0`  
> **Docs:** vectorbt.dev  
> **CRITICAL:** `vectorbt==1.0.0` is the open-source version. `>=1.0` is the paid VectorBT PRO. Never pin `>=1.0`.


## Quick Reference

```python
pip install vectorbt==1.0.0

import vectorbt as vbt

# Minimal backtest — 3 lines
pf = vbt.Portfolio.from_signals(close, entries, exits)
print(pf.stats())
pf.plot().show()
```


### from_signals() Key Parameters

| Parameter | Type | Default | Purpose |
| --- | --- | --- | --- |
| close | Series/DF | required | Price series for valuation |
| entries | bool Series/DF | required | True = open long position |
| exits | bool Series/DF | required | True = close long position |
| init_cash | float | 100 | Starting capital |
| size | float | inf | Order size (shares or fraction) |
| size_type | str | 'amount' | 'amount','value','percent','percent_of_equity' |
| fees | float | 0.0 | Fee per trade (0.001 = 0.1%) |
| slippage | float | 0.0 | Slippage per trade (fraction) |
| sl_stop | float | None | Stop-loss % of entry (0.05 = 5%) |
| tp_stop | float | None | Take-profit % of entry |
| ts_stop | float | None | Trailing stop % from peak |
| freq | str | None | '1D','5T','1H' — required for annualised stats |
| direction | str | 'longonly' | 'longonly','shortonly','both' |


## Installation & Version Constraints

```python
# Pin exactly to open-source version
pip install vectorbt==1.0.0

# pyproject.toml
requires-python = ">=3.11,<3.13"

# requirements.txt
vectorbt==1.0.0
numba>=0.57,<0.61
llvmlite>=0.40,<0.44
```


### Numba Warm-up (add to bot startup)

```python
def warmup_vbt():
    dummy = pd.Series(range(100), dtype=float)
    entries = pd.Series([True if i%10==0 else False for i in range(100)])
    exits   = pd.Series([True if i%10==5 else False for i in range(100)])
    vbt.Portfolio.from_signals(dummy, entries, exits)
    print('vectorbt warmed up.')
```


## from_signals() — Full Example

```python
import vectorbt as vbt, yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend    import SMAIndicator

df      = yf.download('RELIANCE.NS', period='2y', auto_adjust=True)
close   = df['Close']
rsi     = RSIIndicator(close, 14).rsi()
sma50   = SMAIndicator(close, 50).sma_indicator()

entries = (rsi < 30) & (close > sma50)
exits   = rsi > 70

pf = vbt.Portfolio.from_signals(
    close, entries, exits,
    init_cash=100_000,
    fees=0.001,
    slippage=0.001,
    freq='1D'
)
print(pf.stats())
```


### Position Sizing Patterns

```python
# All available cash (default)
pf = vbt.Portfolio.from_signals(close, entries, exits)

# Fixed INR value per trade
pf = vbt.Portfolio.from_signals(close, entries, exits,
                                 size=10_000, size_type='value')

# ATR-based position sizing
atr    = AverageTrueRange(df['High'], df['Low'], close, 14).average_true_range()
size   = (100_000 * 0.01 / (2 * atr)).clip(lower=1).astype(int)
pf = vbt.Portfolio.from_signals(close, entries, exits,
                                 size=size, size_type='amount')

# With stop-loss and trailing stop
pf = vbt.Portfolio.from_signals(
    close, entries, exits,
    high=df['High'], low=df['Low'],
    sl_stop=0.05, sl_trail=True, tp_stop=0.15,
    freq='1D'
)
```


## Performance Stats

| Method | Description |
| --- | --- |
| pf.stats() | Full stats summary |
| pf.total_return() | Total return fraction |
| pf.sharpe_ratio() | Annualised Sharpe (requires freq) |
| pf.sortino_ratio() | Downside Sharpe |
| pf.max_drawdown() | Max drawdown fraction |
| pf.max_drawdown_duration() | Duration of worst drawdown |
| pf.trades.records_readable | DataFrame of all trades |
| pf.trades.win_rate() | Win rate |
| pf.trades.count() | Total trades |
| pf.value() | Equity curve time series |
| pf.returns() | Period returns time series |


## Parameter Sweeps

```python
import numpy as np

# RSI window sweep
windows = np.arange(5, 31)
rsi_matrix = pd.DataFrame({w: RSIIndicator(close, w).rsi() for w in windows})

pf = vbt.Portfolio.from_signals(
    close, rsi_matrix < 30, rsi_matrix > 70,
    fees=0.001, freq='1D'
)

results = pd.DataFrame({
    'sharpe':   pf.sharpe_ratio(),
    'return':   pf.total_return(),
    'drawdown': pf.max_drawdown(),
    'n_trades': pf.trades.count(),
}, index=windows)

print(results.sort_values('sharpe', ascending=False).head(5))
```

---


# M5 — Dashboard — Streamlit

> **Install:** `pip install streamlit`  
> **Run:** `streamlit run app.py`  
> **Docs:** docs.streamlit.io  
> **CRITICAL:** Never commit `.streamlit/secrets.toml`


## All Core Functions at a Glance

| Function | Purpose |
| --- | --- |
| st.title('text') | Large page title |
| st.header('text') | Section header (H1) |
| st.write(value) | Smart display: text, df, dict, fig |
| st.markdown('**bold**') | Markdown text |
| st.code('snippet', language='python') | Syntax-highlighted code |
| st.dataframe(df) | Interactive scrollable DataFrame |
| st.metric('label', value, delta) | KPI card with delta arrow |
| st.plotly_chart(fig) | Interactive Plotly figure |
| st.button('Click me') | Button — returns True when clicked |
| st.selectbox('label', options) | Dropdown selector |
| st.multiselect('label', options) | Multi-select dropdown |
| st.slider('label', min, max, value) | Numeric slider |
| st.text_input('label') | Single-line text input |
| st.number_input('label', min_value=0) | Numeric input |
| st.date_input('label') | Date picker |
| st.checkbox('label') | Checkbox — returns bool |
| col1, col2 = st.columns(2) | Two equal columns |
| tab1, tab2 = st.tabs(['A','B']) | Tab containers |
| st.sidebar.selectbox(...) | Put widget in sidebar |
| with st.expander('Show more'): | Collapsible section |
| st.success('Done!') | Green success banner |
| st.error('Failed!') | Red error banner |
| st.warning('Check this') | Yellow warning banner |
| with st.spinner('Loading...'): | Loading spinner |
| st.session_state['key'] | Per-session persistent state |
| @st.cache_data | Cache function returning data |
| @st.cache_resource | Cache shared resource (connection) |
| st.rerun() | Force script rerun |
| st.secrets['KEY'] | Read from .streamlit/secrets.toml |


## App Structure

```python
import streamlit as st

# Page config (must be FIRST st call)
st.set_page_config(
    page_title='QuantIQ Dashboard',
    page_icon='chart_with_upwards_trend',
    layout='wide',
)

with st.sidebar:
    symbol = st.selectbox('Symbol', ['RELIANCE.NS','TCS.NS'])
    period = st.selectbox('Period', ['1mo','3mo','6mo','1y'])
    if st.button('Refresh', type='primary'):
        st.cache_data.clear()
        st.rerun()
```


## Caching

```python
@st.cache_data(ttl='1h')
def load_price_data(symbol: str, period: str) -> pd.DataFrame:
    return yf.download(symbol, period=period, auto_adjust=True, progress=False)

@st.cache_resource
def get_dhan_client():
    from dhanhq import dhanhq
    return dhanhq(st.secrets['DHAN_CLIENT_ID'], st.secrets['DHAN_ACCESS_TOKEN'])

# Clear cache manually (e.g., on Refresh button)
load_price_data.clear()    # this function only
st.cache_data.clear()      # all data caches
```


## Secrets Management

```toml
# .streamlit/secrets.toml — LOCAL ONLY, NEVER COMMIT
DHAN_CLIENT_ID    = "1000000001"
DHAN_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9..."

# Access in code
client_id    = st.secrets['DHAN_CLIENT_ID']
access_token = st.secrets['DHAN_ACCESS_TOKEN']
```

```
# .gitignore — add immediately
.streamlit/secrets.toml
.env
```

**Community Cloud:** paste secrets.toml content into App Settings → Secrets in the web UI. Never store in repo.


## QuantIQ Dashboard Pattern

```python
# dashboard/app.py
import streamlit as st, pandas as pd
import plotly.graph_objects as go, yfinance as yf
from ta.utils import dropna
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

st.set_page_config(page_title='QuantIQ', layout='wide')

with st.sidebar:
    st.title('QuantIQ')
    symbol = st.selectbox('Symbol',
        ['RELIANCE.NS','TCS.NS','INFY.NS','HDFCBANK.NS'])
    period = st.selectbox('Period', ['3mo','6mo','1y','2y'])
    if st.button('Refresh', type='primary'):
        load_data.clear(); st.rerun()

@st.cache_data(ttl='30m')
def load_data(sym, per):
    df = yf.download(sym, period=per, auto_adjust=True, progress=False)
    df = dropna(df)
    df['RSI'] = RSIIndicator(df['Close'], 14).rsi()
    bb = BollingerBands(df['Close'], 20, 2)
    df['BB_u'] = bb.bollinger_hband()
    df['BB_l'] = bb.bollinger_lband()
    return df

df   = load_data(symbol, period)
last = df['Close'].iloc[-1]
prev = df['Close'].iloc[-2]
chg  = (last - prev) / prev

k1, k2, k3, k4 = st.columns(4)
k1.metric(symbol, f'INR {last:,.2f}', f'{chg:+.2%}')
k2.metric('RSI', f"{df['RSI'].iloc[-1]:.1f}")
k3.metric('52W High', f"INR {df['High'].max():,.2f}")
k4.metric('52W Low',  f"INR {df['Low'].min():,.2f}")

fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df.index, open=df['Open'], high=df['High'],
    low=df['Low'], close=df['Close'], name='OHLC'))
fig.update_layout(xaxis_rangeslider_visible=False, height=450)
st.plotly_chart(fig, use_container_width=True)

t1, t2 = st.tabs(['Raw Data', 'RSI'])
with t1:
    st.dataframe(df.tail(20), use_container_width=True)
with t2:
    st.line_chart(df[['RSI']])
```

---


# M6 — Charting — Plotly Python

> **Install:** `pip install plotly`  
> **Docs:** plotly.com/python  
> **Rule:** Use `go` (graph_objects) for all financial charts. Use `px` (Express) for quick exploration only.


## Imports

```python
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
```


## Candlestick Chart

```python
fig = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df['Open'], high=df['High'],
    low=df['Low'],   close=df['Close'],
    name='RELIANCE.NS',
    increasing_line_color='#3FB950',   # QuantIQ green
    decreasing_line_color='#F85149',   # QuantIQ red
    increasing_fillcolor='#3FB950',
    decreasing_fillcolor='#F85149',
)])
fig.update_layout(
    title='RELIANCE.NS',
    xaxis_rangeslider_visible=False,   # always False for trading charts
    height=500,
    hovermode='x unified'
)
fig.show()
```


## Standard 3-Panel Chart: Price + Volume + RSI

```python
import numpy as np

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    row_heights=[0.6, 0.2, 0.2],
    vertical_spacing=0.03,
    subplot_titles=('Price', 'Volume', 'RSI (14)')
)

# Row 1: Candlestick
fig.add_trace(go.Candlestick(
    x=df.index, open=df['Open'], high=df['High'],
    low=df['Low'], close=df['Close'], name='OHLC',
    increasing_line_color='#3FB950', decreasing_line_color='#F85149'
), row=1, col=1)

# Row 2: Volume
vol_colors = np.where(df['Close'] >= df['Open'], '#3FB950', '#F85149')
fig.add_trace(go.Bar(
    x=df.index, y=df['Volume'], marker_color=vol_colors,
    name='Volume', showlegend=False
), row=2, col=1)

# Row 3: RSI with overbought/oversold lines
fig.add_trace(go.Scatter(
    x=df.index, y=df['RSI'],
    line=dict(color='#BC8CFF', width=1.2), name='RSI'
), row=3, col=1)
fig.add_hline(y=70, line_dash='dot', line_color='red',   row=3, col=1)
fig.add_hline(y=30, line_dash='dot', line_color='green', row=3, col=1)

fig.update_layout(height=700, xaxis_rangeslider_visible=False, showlegend=True)
fig.update_yaxes(range=[0, 100], row=3, col=1)
fig.show()
```


## QuantIQ Dark Theme Template

```python
QUANTIQ_LAYOUT = dict(
    paper_bgcolor='#0D1117',
    plot_bgcolor='#161B22',
    font=dict(color='#E6EDF3', size=12),
    xaxis=dict(gridcolor='#30363D', rangeslider=dict(visible=False)),
    yaxis=dict(gridcolor='#30363D'),
    legend=dict(bgcolor='rgba(13,17,23,0.7)', bordercolor='#30363D'),
    hovermode='x unified',
    hoverlabel=dict(bgcolor='#161B22', font_color='#E6EDF3')
)
fig.update_layout(**QUANTIQ_LAYOUT)
```


## QuantIQ Chart Patterns


### Equity Curve vs Benchmark

```python
equity = pf.value().rename('Strategy')
bh     = pf_bh.value().rename('Buy & Hold')

fig = go.Figure()
fig.add_trace(go.Scatter(x=equity.index, y=equity, name='Strategy',
                          line=dict(color='#3FB950', width=2)))
fig.add_trace(go.Scatter(x=bh.index, y=bh, name='Buy & Hold',
                          line=dict(color='#58A6FF', width=1.5, dash='dot')))
fig.update_layout(title='Portfolio vs Buy-and-Hold',
                   yaxis_title='Value (INR)', height=400, **QUANTIQ_LAYOUT)
st.plotly_chart(fig, use_container_width=True)
```


### Drawdown Chart

```python
equity       = pf.value()
rolling_max  = equity.cummax()
drawdown     = (equity - rolling_max) / rolling_max * 100

fig = go.Figure()
fig.add_trace(go.Scatter(x=drawdown.index, y=drawdown,
    fill='tozeroy', fillcolor='rgba(248,81,73,0.2)',
    line=dict(color='#F85149', width=1), name='Drawdown'))
fig.update_layout(yaxis_title='Drawdown (%)', height=250, **QUANTIQ_LAYOUT)
```


### Export

```python
fig.write_html('chart.html')          # interactive (no dependencies)
fig.write_image('chart.png')          # static (requires kaleido)
# pip install kaleido   <- required for PNG/SVG/PDF export
```

---


# M7 — Python Standards

> **Sources:** peps.python.org | google.github.io/styleguide/pyguide.html  
> **Convention:** QuantIQ uses Google-style docstrings, Black formatter (88 chars), Ruff linter.


## Naming Conventions

| Type | Convention | Example |
| --- | --- | --- |
| Module / package | lower_snake_case | data_pipeline |
| Class | UpperCamelCase | DhanClient |
| Function / method | lower_snake_case | fetch_ohlcv |
| Variable | lower_snake_case | rsi_window |
| Constant | UPPER_SNAKE_CASE | MAX_ORDER_SIZE |
| Private | _leading_underscore | _validate_token |
| Type alias | UpperCamelCase | ClosePrice = pd.Series |


## Formatting Rules (PEP 8)

| Rule | Value |
| --- | --- |
| Indentation | Tabs. Enforced by Ruff (`indent-style = "tab"` in pyproject.toml). |
| Max line length | 88 characters (Black default) |
| Blank lines | 2 between top-level defs; 1 between class methods |
| Imports | One per line. stdlib → third-party → local. Alphabetical within groups. |
| Strings | Double quotes (QuantIQ standard) |
| Trailing commas | Use on multi-line sequences |
| Semicolons | Never. |


### Imports (correct order)

```python
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from ta.momentum import RSIIndicator

from quantiq.data import loader
```


### Comparisons (correct)

```python
# Good
if value is None: ...
if isinstance(obj, pd.DataFrame): ...
if not my_list: ...

# Bad
if value == None: ...
if type(obj) == pd.DataFrame: ...
if len(my_list) == 0: ...
```


## Google-Style Docstrings (PEP 257 + Google §3.8)

```python
def fetch_ohlcv(
    symbol: str,
    from_date: str,
    to_date: str,
    interval: str = "day",
) -> pd.DataFrame:
    """Fetch historical OHLCV data from DhanHQ.

    Args:
        symbol: DhanHQ security ID (e.g. "11536" for RELIANCE).
        from_date: Start date in "YYYY-MM-DD" format.
        to_date: End date in "YYYY-MM-DD" format (exclusive).
        interval: Bar interval. One of "day", "1", "5", "15", "25", "60".

    Returns:
        DataFrame indexed by datetime with columns Open, High, Low, Close, Volume.

    Raises:
        ValueError: If from_date >= to_date.
        DhanAPIError: If the API returns DH-90x error code.
    """
    ...
```


## Type Hints (PEP 484)

```python
from __future__ import annotations
import pandas as pd
import numpy as np

# Variable annotations
symbol: str = "RELIANCE.NS"
quantity: int = 100
price: float | None = None

# Function signatures
def buy(symbol: str, quantity: int, price: float, stop: float | None = None) -> dict[str, str]: ...
def log_trade(trade: dict) -> None: ...

# Common QuantIQ types
ClosePrice  = pd.Series
OHLCVData   = pd.DataFrame
SecurityId  = str
OrderId     = str
```


## stdlib logging

```python
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# Module-level logger (every module)
logger = logging.getLogger(__name__)

# Setup once at entry point
def setup_logging(log_dir: str = "logs") -> None:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter(
        "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    # File handler — rotates daily, keeps 5 years (SEBI requirement)
    fh = TimedRotatingFileHandler(
        filename=f"{log_dir}/quantiq.log",
        when="midnight", interval=1,
        backupCount=1825,  # 5 years
        encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(fh)
```


### Structured Trade Audit Log (SEBI compliance)

```python
import json
from datetime import datetime

audit_logger = logging.getLogger("quantiq.audit")

def log_order_event(event_type: str, order_id: str, symbol: str,
                     side: str, quantity: int, price: float) -> None:
    record = {
        "ts": datetime.now().isoformat(),
        "event": event_type,  # PLACED, FILLED, CANCELLED, REJECTED
        "order_id": order_id,
        "symbol": symbol,
        "side": side,
        "qty": quantity,
        "price": price,
        "algo_id": "QUANTIQ_v1",
    }
    audit_logger.info(json.dumps(record))
```

---


# M8 — Version Control & DevOps

> **Sources:** conventionalcommits.org | docs.github.com  
> **Repo:** github.com/Quant-IQ/quantiq


## Conventional Commits


### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```


### Commit Types + SemVer Bumps

| Type | Purpose | SemVer bump |
| --- | --- | --- |
| feat | New feature | MINOR |
| fix | Bug fix | PATCH |
| docs | Documentation only | none |
| style | Formatting (no logic) | none |
| refactor | Restructure (no fix/feature) | none |
| perf | Performance improvement | PATCH |
| test | Add/fix tests | none |
| build | Build system, deps | none |
| ci | CI/CD configuration | none |
| chore | Maintenance | none |
| revert | Revert a commit | PATCH |
| BREAKING CHANGE | Breaking API change (footer) | MAJOR |


### QuantIQ Scopes

| Scope | Area |
| --- | --- |
| data | Data ingestion, yfinance, DhanHQ historical |
| broker | DhanHQ orders, auth, WebSocket |
| strategy | Signal generation, indicators |
| backtest | vectorbt simulation |
| dashboard | Streamlit app |
| bot | Phase 4 live trading bot |


### Good Commit Examples

```
feat(broker): add daily token refresh scheduler
fix(data): append .NS suffix when fetching NSE tickers from yfinance
docs: add CONTRIBUTING.md with PR workflow and coding standards
build(deps): upgrade vectorbt from 0.28.1 to 0.28.2
ci: add pytest job to pull request workflow

# Breaking change:
feat(strategy): change signal API to return (entries, exits) tuple

BREAKING CHANGE: generate_signals() now returns a tuple.
Callers must unpack: entries, exits = generate_signals(df)
```


## Semantic Versioning (SemVer)

```
MAJOR.MINOR.PATCH   e.g. 1.2.3
```

| Part | Increment when |
| --- | --- |
| MAJOR | Breaking API change — callers must update code |
| MINOR | New backward-compatible feature added |
| PATCH | Backward-compatible bug fix |


## Git Essentials


### Core Commands

| Command | Purpose |
| --- | --- |
| git status | Check working tree |
| git add -p | Interactively stage hunks (recommended) |
| git commit -m 'feat(data): ...' | Commit with Conventional Commits message |
| git push origin feat/data/nse-validator | Push feature branch |
| git pull --rebase origin main | Sync with main |
| git log --oneline -20 | Last 20 commits compact |
| git stash / git stash pop | Shelve/restore changes |
| git restore <file> | Discard unstaged changes |
| git reset HEAD~1 | Undo last commit (keep changes) |
| git revert <hash> | Safe undo on shared branches |


### Feature Branch Workflow

```bash
# 1. Create branch from main
git switch main && git pull --rebase origin main
git switch -c feat/data/nse-ticker-validator

# 2. Work — commit often
git add -p
git commit -m 'feat(data): add NSE ticker suffix validation'

# 3. Keep in sync
git fetch origin && git rebase origin/main

# 4. Push and open PR
git push -u origin feat/data/nse-ticker-validator

# 5. After merge — clean up
git switch main && git pull --rebase origin main
git branch -d feat/data/nse-ticker-validator
```


## GitHub Actions — CI Workflow

```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: pip install -r requirements.txt && pip install black ruff pytest
      - name: Black check
        run: black --check --diff .
      - name: Ruff lint
        run: ruff check .
      - name: Tests
        run: pytest tests/ -v --tb=short
```


## Branch Protection (main branch)

| Setting | Value |
| --- | --- |
| Require pull request before merging | ON |
| Required approving reviews | 1 |
| Require status checks to pass | ON (CI: lint-and-test) |
| Require branches up to date | ON |
| Allow force pushes | OFF |
| Allow deletions | OFF |

---


# M9 — Regulatory — SEBI & NSE

> **Primary source:** SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/0000013 (4 Feb 2025)  
> **NSE source:** NSE/INVG/67858 (5 May 2025)  
> **Full framework mandatory:** 1 April 2026 (all brokers)

> ⚠️ **READ THIS BEFORE TOUCHING ANY LIVE ORDER CODE**


## Hard Constraints — Regulatory

| Rule | Detail |
| --- | --- |
| THRESHOLD: 10 OPS | Orders Per Second per exchange per client. Below 10 OPS = no algo registration needed. Above = must register with NSE/BSE through Dhan. |
| Static IP mandatory | One primary static IP (+ optional secondary) whitelisted before any order. 7-day cooldown after setting. |
| OAuth + 2FA only | All other auth discontinued. TOTP or equivalent required on every login. |
| 24-hour token expiry | Regenerate before 09:15 IST daily. Cannot refresh after expiry. |
| Algo tagging | Every algo order must carry exchange-assigned algo ID if above threshold. |
| Daily session logout | No persistent sessions across trading days. |
| Audit trail 5 years | All orders/trades logged. TimedRotatingFileHandler at backupCount=1825. |
| Kill switch | Exchange can halt algo ID at any time. Bot must handle rejection gracefully. |


## Regulatory Timeline

| Date | Event |
| --- | --- |
| 9 Dec 2021 | SEBI publishes discussion paper on retail algo trading. |
| 4 Feb 2025 | SEBI issues binding circular SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/0000013. |
| 5 May 2025 | NSE issues implementation standards NSE/INVG/67858 (OPS=10, static IP, 2FA, audit). |
| 1 Apr 2026 | FULL FRAMEWORK mandatory for all brokers. Now fully live. |


## SEBI Feb 2025 Circular — Key Provisions

**Circular:** SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/0000013  
**URL:** sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html

| Section | Rule | Engineering Implication |
| --- | --- | --- |
| I(a) | Broker = principal; Algo Provider = agent. | Dhan bears compliance responsibility. |
| I(b) | All algo orders tagged with exchange-unique ID. | Dhan SDK handles; requires registration if >10 OPS. |
| I(c) | Self-developed retail algos need registration only if above OPS threshold. | Stay under 10 OPS — no registration needed. |
| I(d)(ii) | No open APIs. Unique vendor-client API key + static IP mandatory. | DhanLogin.set_ip() before first order. |
| I(d)(iii) | OAuth-based authentication only. | Use TOTP or OAuth flow (see M1 §3). |
| I(d)(iv) | Two-factor authentication mandatory. | TOTP or OAuth includes 2FA. |


## NSE/INVG/67858 — OPS Rate Limiter (copy-paste ready)

```python
import time
import threading
from collections import deque

class OPSRateLimiter:
    """Token bucket rate limiter: max 10 orders/sec per SEBI/NSE mandate."""
    MAX_OPS: int = 10

    def __init__(self) -> None:
        self._window: deque = deque()
        self._lock = threading.Lock()

    def can_place_order(self) -> bool:
        now = time.monotonic()
        with self._lock:
            while self._window and now - self._window[0] >= 1.0:
                self._window.popleft()
            if len(self._window) >= self.MAX_OPS:
                return False
            self._window.append(now)
            return True

    def wait_and_place(self) -> None:
        while not self.can_place_order():
            time.sleep(0.05)

# Usage
rate_limiter = OPSRateLimiter()
rate_limiter.wait_and_place()   # blocks if at limit
response = dhan.place_order(...)
```


## Compliance Checklist (tick before Phase 4 live)

**Authentication & Access**

- [ ] Static IP set via DhanLogin.set_ip() — primary IP documented

- [ ] OAuth + TOTP configured in Dhan account

- [ ] Daily token regeneration before 09:15 IST implemented

- [ ] Token stored in secrets.toml (not committed to git)

- [ ] Bot verifies token via /profile on startup

**Order Rate Control**

- [ ] OPS rate limiter implemented (max 10/sec)

- [ ] Rate limiter tested under load

- [ ] Bot handles DH-904 gracefully (never crashes)

**Audit Logging**

- [ ] Every order logged: ts, clientId, symbol, side, qty, price, orderId, status

- [ ] TimedRotatingFileHandler with backupCount=1825 (5 years)

- [ ] Log files in .gitignore (not committed)

- [ ] Log survives bot crash (writes on each order)

**Session Management**

- [ ] Bot does NOT persist sessions across trading days

- [ ] Daily logout implemented after market close (15:30 IST)

- [ ] Bot startup: login → verify token → set IP → warmup → ready

**Risk Management**

- [ ] Daily loss limit: bot stops if P&L < -X%

- [ ] Position limit: max open positions per symbol

- [ ] Kill switch: bot can be manually stopped

- [ ] Backtest completed on 2+ years of data before live


## Key URLs

| Document | URL |
| --- | --- |
| SEBI master circular | sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html |
| NSE circulars portal | nseindia.com/resources/exchange-communication-circulars |
| SEBI circular index | sebi.gov.in/sebiweb/home/HomeAction.do?doListingAll=yes&search=Algorithmic |
| NSE securities list | nseindia.com/market-data/securities-available-for-trading |

---


# M10 — Environment & Tooling

> **Scope:** python-dotenv, venv, pip, requirements.txt, pyproject.toml, pre-commit, VS Code  
> **Python version:** >=3.11,<3.13 (QuantIQ constraint)  
> **Editor:** VS Code (not VSCodium — project standard)


## Project Setup from Scratch

```bash
# 1. Clone
git clone https://github.com/Quant-IQ/quantiq.git && cd quantiq

# 2. Virtual environment (Python 3.11)
python3.11 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit with your Dhan credentials

# 5. Pre-commit hooks
pre-commit install

# 6. Verify
python -c "import vectorbt, dhanhq, streamlit; print('OK')" 
```


## python-dotenv

```bash
pip install python-dotenv==1.2.2
```

```
# .env — local only, NEVER COMMIT
DHAN_CLIENT_ID=1000000001
DHAN_ACCESS_TOKEN=eyJhbGciOiJIUzI1NiJ9...
ENV=development
LOG_LEVEL=DEBUG
```

```python
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env from cwd

client_id    = os.getenv('DHAN_CLIENT_ID')
access_token = os.environ['DHAN_ACCESS_TOKEN']  # raises KeyError if missing

# Validation pattern (recommended)
REQUIRED = ['DHAN_CLIENT_ID', 'DHAN_ACCESS_TOKEN']
def validate_env() -> None:
    load_dotenv()
    missing = [k for k in REQUIRED if not os.getenv(k)]
    if missing:
        raise EnvironmentError(f"Missing env vars: {missing}")
```


## requirements.txt

```python
# requirements.txt — production
dhanhq==2.0.2
pandas>=2.0.0,<3.0
numpy>=1.24.0,<2.0
yfinance>=0.2.50
ta==0.11.0
vectorbt==1.0.0         # open-source — NOT >=1.0 (paid PRO)
numba>=0.57,<0.61
llvmlite>=0.40,<0.44
streamlit>=1.35.0
plotly>=5.20.0
python-dotenv==1.2.2
requests>=2.28.0
websockets>=12.0
```

```python
# requirements-dev.txt
-r requirements.txt
black>=24.0
ruff>=0.4.0
mypy>=1.8
pytest>=8.0
pytest-cov>=5.0
pre-commit>=3.7
kaleido>=0.2.1
```


## pyproject.toml

```toml
[project]
name = "quantiq"
version = "0.3.0"
description = "QuantIQ — NSE Algorithmic Trading"
requires-python = ">=3.11,<3.13"

[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["-v", "--tb=short", "--cov=quantiq"]
```


## pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-merge-conflict
      - id: debug-statements
      - id: detect-private-key
      - id: check-added-large-files
        args: ['--maxkb=500']

  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.7
    hooks:
      - id: ruff
        args: [--fix]
```


## Complete .gitignore for QuantIQ

```
# SECRETS — NEVER COMMIT
.env
.env.*
!.env.example
.streamlit/secrets.toml

# Python
__pycache__/
*.pyc
*.egg-info/
dist/
build/

# Virtual environments
.venv/
venv/
env/

# Logs (stored on server, not in repo)
logs/
*.log

# Data files
data/raw/
data/processed/
*.csv
*.parquet
!data/test/*.csv

# Testing
.pytest_cache/
.coverage
htmlcov/

# Tools
.mypy_cache/
.ruff_cache/

# IDE
.vscode/*.json
!.vscode/settings.json
!.vscode/launch.json
.idea/

# OS
.DS_Store
Thumbs.db
```


## VS Code Settings

```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "editor.formatOnSave": true,
    "editor.rulers": [88],
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true
    },
    "ruff.fixAll": true,
    "ruff.organizeImports": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"]
}
```

---

## End of QuantIQ Master Reference Binder

> Built 18 May 2026 | github.com/Quant-IQ/quantiq | quantiq.team@quant-iq.net
