# CLAUDE.md — QuantIQ Project Context

> Read this file in full at the start of every session. It is the authoritative reference for project
> architecture, conventions, team structure, and AI behaviour rules. Do not infer from the codebase
> alone — this file explains intent, not just structure.

---

## 1. Project Overview

**QuantIQ** is a 12-week collaborative algorithmic trading project targeting NSE Indian equity stocks.
It is simultaneously a learning vehicle, a team collaboration exercise, and a portfolio piece.

| Attribute        | Value                                                        |
| ---------------- | ------------------------------------------------------------ |
| Target market    | NSE (National Stock Exchange, India)                         |
| Instruments      | Equity + F&O (paper trading only until team consensus)       |
| Broker / API     | Dhan API via `dhanhq` Python SDK (free tier)                 |
| Language         | Python 3.12 (3.11 minimum; 3.13+ breaks data libraries)      |
| Primary goal     | End-to-end paper trading system: data → signal → execution   |
| Secondary goal   | Learning vehicle for a mixed-skill team                      |
| Tertiary goal    | Portfolio piece for tech and finance internship applications |
| Project duration | 12 weeks, 5 phases                                           |
| Repo visibility  | Private until Phase 3 (~Week 8), then public                 |

**Do not suggest going live with real capital.** Paper trading only until all members agree and
at least 2–3 weeks of paper logs have been reviewed.

---

## 2. Repository Structure

```text
quantiq/
├── CLAUDE.md                        # This file — AI context
├── README.md                        # Public-facing project description
├── CONTRIBUTING.md                  # PR rules, branch naming, commit format
├── requirements.txt                 # Pinned exact versions — always pip freeze after adding
├── .env.example                     # Template — never commit .env
├── .gitignore                       # Python + .env + logs/*.csv excluded
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
│       ├── task.md
│       └── bug.md
├── src/
│   ├── data/                        # Market data ingestion and indicator calculation
│   │   ├── fetch.py                 # yfinance + Dhan API data fetching
│   │   ├── indicators.py            # SMA, EMA, RSI, MACD, VWAP, ATR via ta library
│   │   └── validate.py              # Gap detection, holiday handling, bad tick filtering
│   ├── strategy/                    # Signal generation — entry and exit logic only
│   │   ├── base.py                  # Abstract base class all strategies inherit from
│   │   ├── sma_crossover.py         # Phase 3 primary strategy
│   │   └── signals.py               # Signal dataclass definitions
│   ├── execution/                   # Dhan API integration and order management
│   │   ├── dhan_client.py           # Authenticated Dhan client wrapper
│   │   ├── order_manager.py         # Order placement, cancellation, status checks
│   │   ├── websocket_feed.py        # Live tick data via Dhan WebSocket
│   │   └── logger.py               # Trade signal logging to logs/trades.csv
│   └── dashboard/                   # Streamlit UI
│       └── app.py                   # Live price + current signal + trade log view
├── scripts/                         # Phase 1 individual analysis scripts + general utilities
│   └── <handle>.py                  # One file per member — fetch NSE data, print stats
├── backtest/
│   └── strategy_v1.ipynb            # vectorbt backtest — SMA crossover on NIFTY 1yr
├── notebooks/
│   └── market_analysis.ipynb        # Phase 2 group notebook — NIFTY50 analysis
├── members/                         # One markdown file per team member
│   └── [name].md
├── logs/
│   └── trades.csv                   # Paper trade signal log — gitignored
└── docs/
    └── architecture.md              # Plain-English system architecture explanation
```

**All `src/` directories are scaffolded with `.gitkeep` files. `src/` implementation begins Phase 3.**
**All `src/` files listed above are planned targets, not current files.**
**Phase 1 work goes in `scripts/` — see §7. `scripts/` may be cleaned up before the repo goes public (Phase 5).**
Do not add files outside this structure without discussing with the Project Lead (RS).

---

## 3. Tech Stack

### Production Dependencies

| Library         | Version (pin in requirements.txt) | Purpose                                     |
| --------------- | --------------------------------- | ------------------------------------------- |
| `pandas`        | latest stable                     | DataFrames, time series, data wrangling     |
| `numpy`         | latest stable                     | Array operations, vectorised maths          |
| `yfinance`      | latest stable                     | Historical OHLCV data for NSE tickers       |
| `ta`            | latest stable                     | Technical indicators (SMA, EMA, RSI, MACD)  |
| `vectorbt`      | latest stable                     | Backtesting engine                          |
| `dhanhq`        | latest stable                     | Dhan broker API — orders, market data       |
| `plotly`        | latest stable                     | Interactive charts (prefer over matplotlib) |
| `streamlit`     | latest stable                     | Dashboard UI                                |
| `python-dotenv` | latest stable                     | Load `.env` credentials                     |
| `requests`      | latest stable                     | HTTP calls where dhanhq doesn't wrap        |
| `websockets`    | latest stable                     | Dhan WebSocket live feed                    |

### Dev Dependencies (not in production requirements.txt)

| Library   | Purpose                                  |
| --------- | ---------------------------------------- |
| `jupyter` | Notebooks for analysis and backtest      |
| `pytest`  | Unit tests (add as project matures)      |
| `black`   | Code formatter — run before every commit |
| `ruff`    | Linter + import sorter (replaces flake8) |

### Tool Philosophy — FOSS First

Always recommend free and open-source alternatives over proprietary or paid tools. This is a
non-negotiable project default. Specifically:

- Editor: VS Code (standing exception to FOSS rule — team uses VS Code, not VSCodium)
- Workspace: AppFlowy (not Notion)
- Broker API: Dhan (not Zerodha Kite — Rs 2000/month)
- Charts: Plotly (not paid charting libs)
- Dashboard deploy: Streamlit Cloud free tier (not Vercel or Heroku)
- Python learning: CS50P Harvard (not paid Udemy unless already purchased)

---

## 4. Environment Setup

```bash
# Python 3.12 preferred — 3.13+ breaks data libraries
py -3.12 -m venv venv

# Activate — Windows CMD
venv\Scripts\activate

# Activate — Windows Git Bash / macOS / Linux
source venv/Scripts/activate        # Git Bash Windows
source venv/bin/activate            # macOS / Linux

# Install all dependencies
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env — fill in Dhan CLIENT_ID and ACCESS_TOKEN

# Verify
python --version   # 3.11 or 3.12
pip --version
git --version
```

### Required `.env` Variables

```dotenv
DHAN_CLIENT_ID=your_client_id_here
DHAN_ACCESS_TOKEN=your_access_token_here
```

**Never hardcode credentials. Never commit `.env`. Always load via `os.getenv()` or `python-dotenv`.**

Dhan access tokens expire every **24 hours** (SEBI hard cap) and must be manually regenerated from the Dhan profile page daily.

---

## 5. Coding Standards

### Docstrings — Mandatory on Every Function

Every function in `src/` must have a docstring. This is non-negotiable — it is what separates
a student project from a professional one, and the Docs role reviews for this on every PR.

```python
def calculate_sma(data: pd.Series, window: int) -> pd.Series:
    """
    Calculate simple moving average for a price series.

    Args:
        data (pd.Series): Closing price series indexed by datetime.
        window (int): Number of periods for the rolling average.

    Returns:
        pd.Series: SMA values with the same index as input.
                   First (window - 1) values will be NaN.

    Raises:
        ValueError: If window is larger than len(data).
    """
    if window > len(data):
        raise ValueError(f"Window {window} exceeds data length {len(data)}")
    return data.rolling(window).mean()
```

### Error Handling — Wrap Every External Call

APIs fail. Data feeds have gaps. NSE has holidays. Code must not crash on these.

```python
import logging

logger = logging.getLogger(__name__)

def fetch_ltp(security_id: int) -> float | None:
    """Fetch last traded price from Dhan API. Returns None on failure.

    Args:
        security_id (int): Integer security ID (e.g. 1333 for HDFC Bank NSE_EQ).
                           Find IDs via dhan.fetch_security_list("compact").

    Returns:
        float | None: Last traded price, or None on API failure.
    """
    try:
        response = dhan.quote_data({"NSE_EQ": [security_id]})
        return response["data"]["NSE_EQ"][str(security_id)]["last_price"]
    except KeyError as e:
        logger.error("Unexpected response structure for security_id %s: %s", security_id, e)
        return None
    except Exception as e:
        logger.error("Dhan API call failed for security_id %s: %s", security_id, e)
        return None
```

### Logging — Use `logging`, Not `print()`

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/quantiq.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)
```

Use `logger.info()` for normal events, `logger.warning()` for unexpected but recoverable states,
`logger.error()` for failures. Remove all `print()` statements before opening a PR.

### Type Hints — Required in `src/`

```python
# Correct
def get_signal(prices: pd.Series, short: int = 20, long: int = 50) -> str:

# Wrong — no hints
def get_signal(prices, short, long):
```

### NSE Ticker Format

Always append `.NS` suffix for yfinance NSE tickers:

```python
# Correct
yf.download("RELIANCE.NS", period="1y", interval="1d")

# Wrong
yf.download("RELIANCE", ...)
```

### Dhan API Ticker Format

Dhan uses **integer security IDs**, not ISIN strings:

```python
# Correct — integer security IDs
dhan.quote_data({"NSE_EQ": [11536, 1333]})   # Reliance, HDFC Bank

# DO NOT USE — ISIN strings silently fail in v2
dhan.quote_data({"NSE_EQ": ["INE002A01018"]})  # WRONG
```

Find integer IDs via `dhan.fetch_security_list("compact")`.
Maintain a `src/data/ticker_map.py` mapping common names to both yfinance and Dhan formats.

### pandas — Key Patterns

```python
# Always check for NaN after rolling operations
df["SMA20"] = df["Close"].rolling(20).mean()
df.dropna(inplace=True)                         # Drop NaN rows before backtest

# NSE data has weekend/holiday gaps — check for missing dates
expected = pd.date_range(start=df.index[0], end=df.index[-1], freq="B")
missing = expected.difference(df.index)
if not missing.empty:
    logger.warning("Missing %d trading days", len(missing))

# Resample intraday to daily
daily = df.resample("1D").agg({
    "Open": "first",
    "High": "max",
    "Low": "min",
    "Close": "last",
    "Volume": "sum",
})

# Boolean filter — rows where price is above SMA
above_sma = df[df["Close"] > df["SMA20"]]
```

### Rate Limiting — Dhan API

10 orders/sec per exchange per client (SEBI/NSE mandate — hard cap). Track and throttle:

```python
import time

MAX_ORDERS_PER_SEC = 8  # Stay well under 10/sec SEBI hard limit
_order_timestamps: list[float] = []

def rate_limited_order(order_params: dict) -> dict:
    """Place order with rate limiting."""
    now = time.time()
    _order_timestamps[:] = [t for t in _order_timestamps if now - t < 1.0]
    if len(_order_timestamps) >= MAX_ORDERS_PER_SEC:
        time.sleep(1.0 - (now - _order_timestamps[0]))
    _order_timestamps.append(time.time())
    return dhan.place_order(**order_params)
```

---

## 6. Git and GitHub Workflow

### Branch Naming

```text
feature/short-description        # New functionality
fix/short-description            # Bug fixes
data/short-description           # Data pipeline changes
docs/short-description           # Documentation only
backtest/short-description       # Backtesting scripts
members/your-name                # Phase 0 onboarding commit
```

### Commit Format

Follows [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).

```text
type(scope): short description (max 72 chars, lowercase)

Types:  feat | fix | docs | style | refactor | test | build | chore
Scopes: data | broker | strategy | backtest | dashboard | bot

# Omit scope only for repo-wide changes (e.g. docs: update README)

Examples:
feat(data): add RSI indicator to data pipeline
fix(strategy): handle NaN values in SMA crossover signal
feat(broker): add daily token refresh scheduler
docs: update README with backtest results
refactor(data): extract order logging to separate module
chore: pin dependency versions in requirements.txt
```

### PR Rules — Non-Negotiable

1. Never push directly to `main`
2. Never merge your own PR — always needs one reviewer
3. Write `Closes #N` in PR description to auto-close the linked Issue
4. Fill the PR template completely — do not delete sections
5. Remove all `print()` statements and debug code before opening
6. All functions must have docstrings — reviewer will block merge if missing
7. No hardcoded credentials — reviewer will block merge immediately
8. Add `Closes #N` for every Issue the PR resolves
9. Reviewer must post within **48 hours** of being assigned — post in #dev if you cannot
10. Reviewer uses **Squash and merge** — enables auto-delete of the head branch

### Issue Structure

Every task lives as a GitHub Issue. Use the provided templates:

- **Task template**: for planned work
- **Bug template**: for defects

Labels in use: `phase-0` through `phase-5`, `data`, `dev`, `docs`, `quant`, `co-lead`, `blocked`, `good-first-issue`

---

## 7. Project Phases and Current State

### Phase Map

| Phase | Weeks | Core Deliverable                                           | Status      |
| ----- | ----- | ---------------------------------------------------------- | ----------- |
| 0     | 1     | Every member: first commit (`members/name.md`)             | Complete    |
| 1     | 2–4   | `scripts/<handle>.py` — fetch NSE data, SMA20/50 stats     | Active      |
| 2     | 5–7   | `notebooks/market_analysis.ipynb` — group NIFTY50 analysis | Not started |
| 3     | 8–9   | `backtest/strategy_v1.ipynb` — Sharpe, drawdown, win rate  | Not started |
| 4     | 10–11 | Live bot — paper trading across 3+ sessions via Dhan API   | Not started |
| 5     | 12    | Public repo — clean code, full README, Streamlit deployed  | Not started |

### Current Phase: Phase 1 — Foundations (Week 2)

**Active tasks this week:**

- All members: post Monday standup in Discord `#standup`
- NS, AJ, AD (pending members): complete Phase 0 catch-up by Thursday 15 May
- GT (Quant): start Varsity Module 2, Investopedia entries for SMA/EMA/RSI/MACD
- AV (Data): NumPy quickstart + yfinance, fetch RELIANCE.NS locally
- AR (Dev): CS50P lectures 5–8, REST APIs in Python (Real Python)
- RT (Quant): start Varsity Module 2, Investopedia entries for SMA/EMA/RSI/MACD (support GT)
- EB (Docs): chase standups Tuesday evening, DM anyone who hasn't posted

### Target Architecture (Full System — Phases 1–5)

```text
                    ┌─────────────────┐
                    │   yfinance      │  Historical OHLCV (backtest + init)
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  src/data/      │  fetch.py → indicators.py → validate.py
                    │  fetch.py       │  Output: clean DataFrame with OHLCV + indicators
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────▼──────┐  ┌────▼────┐  ┌────▼─────────────┐
    │  backtest/     │  │strategy/│  │ execution/        │
    │  vectorbt      │  │ signals │  │ dhan_client.py    │
    │  Phase 3       │  │ Phase 2+│  │ order_manager.py  │
    └────────────────┘  └────┬────┘  │ websocket_feed.py │
                             │       │ logger.py         │
                             │       └────────┬──────────┘
                             │                │
                    ┌────────▼────────────────▼──┐
                    │     logs/trades.csv         │
                    │     Signal log (gitignored) │
                    └────────────────┬────────────┘
                                     │
                    ┌────────────────▼────────────┐
                    │     dashboard/app.py         │
                    │     Streamlit — Phase 5      │
                    └─────────────────────────────┘
```

---

## 8. Team Structure

Roles assigned for Phase 1 on **17 May 2026**. Will be reviewed again at end of Phase 1 or start of Phase 2 based on actual performance. Roles marked (P) primary, (S) secondary.

| Handle | Role (P / S) — Phase 1 | Role Colour | Owns |
| --- | --- | --- | --- |
| RS | Project Lead / All | `#F0C040` | Repo, Discord, AppFlowy, decisions, unblocking |
| EB | Analyst / Docs (P) / Dev / Infra (S) | `#FF7B9C` | README, AppFlowy log, Streamlit dashboard |
| GT | Quant / Strategy (P) / Analyst / Docs (S) | `#F0883E` | Strategy design, backtesting, indicator research |
| AV | Quant / Strategy (P) / Data Engineering (S) | `#F0883E` | Strategy support, indicator work |
| AR | Data Engineering (P) / Dev / Infra (S) | `#BC8CFF` | Data pipelines, indicator work, data validation |
| RT | Quant / Strategy (P) / Dev / Infra (S) | `#F0883E` | Strategy design, backtesting, indicator research |
| NS | Dev / Infra (P) / Data Engineering (S) | `#58A6FF` | Dev / Infra support, data pipeline — introduced at 17 May sync |
| AJ | Data Engineering (P) / Quant / Strategy (S) | `#BC8CFF` | Data pipelines, indicator work, strategy research support |
| SS | Quant / Strategy (P) / Analyst / Docs (S) | `#F0883E` | Strategy research, documentation support |
| SmS | Data Engineering (P) / Analyst / Docs (S) | `#BC8CFF` | Data pipeline support, AppFlowy log, README |
| AK | Dev / Infra (P) / Data Engineering (S) | `#58A6FF` | Bot engine support, data pipeline |
| ShS | Analyst / Docs (P) / Dev / Infra (S) | `#FF7B9C` | README, AppFlowy log, dev support |

**Team size:** 12 active members. AD departed before Phase 1. HG departed Week 2 Phase 1. Roles reviewed end of Phase 1 / start of Phase 2. Target: 12–14 active members, natural attrition expected to stabilise at 8–12 by Phase 4.

**Co-Lead role:** Vacant. To be assigned end of Phase 1 or Phase 2 as team scales. Sub-team structure planned for 14+ members: Project Lead → Co-Lead (Quant / Strategy + Data Engineering) + Co-Lead (Dev / Infra + Analyst / Docs).

**Attrition rule:** Two consecutive missed standups with no explanation = voluntary exit.

---

## 9. Communication and Workflow Norms

### Standup Format — Discord `#standup`, Every Monday

```text
WEEK [n] — [Name] — [Role]
Did:      What you completed last week
Next:     What you are working on this week
Blocked:  Anything stopping you (or 'Nothing')
```

RS posts first every Monday. EB chases anyone who hasn't posted by Tuesday evening via DM (private DM only — no public call-outs).

**Accountability escalation:** Late by Tuesday evening → Co-Lead DMs. Missed 2 weeks in a row → Co-Lead alerts RS. Missed 2+ weeks with no commits → treated as voluntary exit. No exceptions.

### Task Lifecycle

```text
Issue created → assigned to one person → moves to "This Week" on Kanban
→ member creates branch → opens PR with "Closes #N"
→ reviewer approves → merged → Issue auto-closes → card moves to Done
```

**One owner per task.** Two assignees = no one is responsible.
**One week per task maximum.** If it spans longer, break it into sub-Issues.
**Blocked tasks:** add `blocked` label within 24 hours of getting stuck. Co-Lead unblocks.

### Tool Usage

| Tool           | Purpose                                | Notes                                        |
| -------------- | -------------------------------------- | -------------------------------------------- |
| Discord        | Primary team communication             | All project discussions here                 |
| WhatsApp       | Urgent human messages only             | "Are you alive?" — not project tracking      |
| GitHub         | Code, PRs, Issues, Projects Kanban     | Code-linked tasks only                       |
| AppFlowy Cloud | Docs, weekly log, team Kanban overview | FOSS. Shared via <quantiq.team@quant-iq.net> |
| VS Code        | Code editor                            | Standing exception to FOSS-first rule        |

AppFlowy workspace is shared via company email `quantiq.team@quant-iq.net` (domain: `quant-iq.net`).
This email is for AppFlowy Cloud login and shared project comms only — it does not replace Discord.

---

## 10. Key Design Decisions — Rationale

| #   | Decision                              | Reason                                                   |
| --- | ------------------------------------- | -------------------------------------------------------- |
| 1   | Dhan API over Zerodha Kite            | Free vs Rs 2000/month                                    |
| 2   | Python as project language            | Best library ecosystem for data + trading                |
| 3   | AppFlowy over Notion                  | FOSS, self-hostable, no vendor lock-in                   |
| 4   | Private repo until Phase 3 (~Week 8)  | Build first, show when results exist                     |
| 5   | vectorbt over backtrader              | Simpler API for this use case, faster for param sweeps   |
| 6   | `ta` library over TA-Lib              | No C compiler required — easier team install             |
| 7   | yfinance for historical data          | Free, reliable for NSE with `.NS` suffix                 |
| 8   | Plotly over matplotlib                | Interactive charts, better for finance visualization     |
| 9   | Streamlit Cloud for dashboard deploy  | Free tier, in existing stack, no DevOps knowledge needed |
| 10  | CS50P over paid Udemy courses         | Free, equivalent quality, no cost barrier for team       |
| 11  | Paper trade only until team consensus | Never touch real capital without full team agreement     |
| 12  | RT assigned Quant / Strategy          | Co-assigned with GT for strategy and backtesting         |
| 13  | EB primary Docs, secondary Data       | Owns README, AppFlowy log, Streamlit dashboard           |
| 14  | Co-Lead vacant — end of Phase 1 or 2  | Roles and strengths being established; team scaling      |
| 15  | Dual-role model (P/S) for all members | Primary = ownership; secondary = support / cross-train   |
| 16  | Second recruitment wave — up to 6 new | All who pass interview treated as full members           |

---

## 11. Strategy Specification (Phase 3 Target)

### SMA Crossover — Primary Strategy

```txt
Entry signal:  SMA-20 crosses ABOVE SMA-50  →  BUY
Exit signal:   SMA-20 crosses BELOW SMA-50  →  SELL
Position size: Fixed lot (to be determined in Phase 3)
Stop loss:     ATR-based trailing stop
Universe:      NIFTY50 constituents — start with top 5 by liquidity
Timeframe:     Daily bars
Backtest on:   1 year of NIFTY data (vectorbt)
```

**Backtest metrics to report:**

- Total return vs NIFTY buy-and-hold benchmark
- Sharpe ratio (target > 1.0)
- Maximum drawdown (target < 20%)
- Win rate (target > 50%)
- Number of trades
- Calmar ratio

**Cost assumptions:**

- Brokerage: Rs 20/trade (Dhan intraday)
- Slippage: 0.1% per trade
- STT, exchange fees: include actual NSE rates

### Alternative Strategies to Research (Phase 3 Extended)

- RSI mean-reversion (buy below 30, sell above 70)
- Opening range breakout (ORB) on 15-minute bars
- Momentum — top N NIFTY50 stocks by 20-day return

---

## 12. Dhan API — Reference

### Authentication

```python
from dhanhq.dhanhq import dhanhq as DhanHQ
import os
from dotenv import load_dotenv

load_dotenv()

dhan = DhanHQ(
    client_id=os.getenv("DHAN_CLIENT_ID"),
    access_token=os.getenv("DHAN_ACCESS_TOKEN"),
)
```

### Fetch Live Quote (LTP)

```python
# NSE equity — use integer security ID (not ISIN string format)
# Find security IDs via: dhan.fetch_security_list("compact")
# 1333 = HDFC Bank, 11536 = Reliance Industries (NSE_EQ segment)
response = dhan.quote_data({"NSE_EQ": [1333, 11536]})
print(response)

# For OHLC snapshot:
response = dhan.ohlc_data({"NSE_EQ": [1333]})

# For just the ticker (LTP only, lower payload):
response = dhan.ticker_data({"NSE_EQ": [1333]})
```

### Place Paper Order (log only — do not execute in Phase 1–3)

```python
# Log to CSV — never call place_order until Phase 4 paper trading confirmed
import csv
from datetime import datetime

def log_signal(ticker: str, signal: str, price: float, reason: str) -> None:
    """Log a trade signal to the paper trade CSV."""
    with open("logs/trades.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            ticker,
            signal,         # "BUY" or "SELL"
            price,
            reason,         # e.g. "SMA20 crossed above SMA50"
        ])
```

### WebSocket Live Feed (Phase 4)

```python
from dhanhq import marketfeed

async def on_tick(tick: dict) -> None:
    """Handle incoming tick. Called for every price update."""
    logger.info("Tick received: %s", tick)
    # Pass tick to signal generator

# Subscription example
instruments = [
    (marketfeed.NSE, "1333", marketfeed.Full),  # HDFC Bank
]
```

**API constraints:**

- Access token expires every **24 hours** (SEBI cap) — must regenerate daily from Dhan profile
- Rate limit: 10 orders/second (SEBI/NSE hard cap) — always throttle, never exceed
- No paper-trading sandbox — log signals to CSV only; use vectorbt for simulation
- Never commit your access token — load from `.env` only

---

## 13. Security Rules

These are absolute. No exceptions regardless of context.

1. **Never commit `.env`** — it is in `.gitignore`. If a token is committed, rotate it immediately.
2. **Never hardcode credentials** — no `token = "abc123"` anywhere in `src/`
3. **Audit before going public** — search entire repo for `token`, `key`, `secret`, `password` before
   switching repo to public in Week 8–9
4. **`.env.example` only** — this file has placeholder values, never real credentials
5. **Logs are gitignored** — `logs/*.csv` must never be committed (may contain price data + signal patterns)
6. **No team member shares their Dhan token** — every member generates their own from their Dhan account
7. **Static IP whitelisting mandatory** (SEBI Feb 2025) — set via `DhanLogin.set_ip()` before any live
   order. 7-day cooldown after setting; cannot modify within that window.
8. **OAuth + TOTP 2FA mandatory** — all other auth methods discontinued per SEBI Feb 2025 circular.
   Use TOTP or OAuth flow (see §12 Authentication). Never generate code that bypasses 2FA.
9. **Daily session logout required** — no persistent sessions across trading days. Bot must log out
   after market close (15:30 IST) and re-authenticate before 09:15 IST next session.

---

## 14. Documentation Strategy

Documentation is layered across four levels. Each level has a specific owner.

| Layer | Location               | Owner      | Updated When                     |
| ----- | ---------------------- | ---------- | -------------------------------- |
| 1     | `README.md`            | EB (Docs)  | End of each phase                |
| 2     | AppFlowy Weekly Log    | EB (Docs)  | Every Sunday night               |
| 3     | Docstrings in `src/`   | All coders | On every function before PR open |
| 4     | `docs/architecture.md` | RS + EB    | When system design changes       |

### README Build Schedule

- **Week 1**: Project name, one-paragraph description, team credits, "In Progress" status
- **Week 4**: Setup instructions + first stock chart screenshot
- **Week 9**: Backtest results — equity curve image, Sharpe, drawdown, win rate
- **Week 12**: Architecture diagram, demo GIF, "What We Learned" section, Streamlit link

---

## 15. LinkedIn Posting Schedule

Post when output exists. Never post about intent.

| Week | Post                                                             |
| ---- | ---------------------------------------------------------------- |
| 1    | Nothing — settle the team first                                  |
| 4–5  | First stock analysis chart — what you built and what you learned |
| 9    | Backtest equity curve + results — Sharpe, drawdown, win rate     |
| 12   | Project wrap — what was built, who built it, GitHub link         |

Maintain a shared draft doc in AppFlowy where teammates review LinkedIn posts before publishing.

---

## 16. Going Public — Week 8–9 Checklist

Before switching the repo from private to public:

- [ ] Search entire repo for `token`, `key`, `secret`, `password` — zero results
- [ ] `git log` audit — no sensitive data in any historical commit
- [ ] `.env` not present anywhere in the repo or commit history
- [ ] `logs/*.csv` not present in repo (gitignored correctly)
- [ ] README stands alone — a stranger can read it and understand the project
- [ ] Backtest results are in the repo — at minimum one equity curve and a results table
- [ ] All functions in `src/` have docstrings
- [ ] All team members have posted a thumbs-up in `#announcements`
- [ ] **Then**: GitHub → Settings → Danger Zone → Change visibility → Public

---

## 17. AI Behaviour Rules for Claude Code

These rules apply to every interaction in this codebase. Read them before generating any code.

### Always

- Use `python-dotenv` and `os.getenv()` for all credentials — never hardcode
- Write docstrings on every function in `src/` — no exceptions
- Use type hints in all `src/` function signatures
- Wrap every Dhan API call in `try/except`
- Use `logging` module — not `print()`
- Use `plotly` for charts — not `matplotlib` (unless explicitly asked)
- Recommend FOSS tools in every tool suggestion
- Add `.NS` suffix to all NSE tickers used with yfinance
- `dropna()` after every rolling window calculation before backtesting
- Run `pip freeze > requirements.txt` after adding any new package
- Follow the branch naming convention when creating branches
- Reference `Closes #N` in commit/PR messages when resolving Issues
- Use `TimedRotatingFileHandler` with `backupCount=1825` for all audit logs (SEBI 5-year retention)

### Never

- Suggest Zerodha Kite API (Rs 2000/month — Dhan is the chosen broker)
- Suggest Notion (AppFlowy is the chosen workspace tool)
- Recommend Python 3.13+ (breaks vectorbt and other data libraries)
- Push directly to `main`
- Merge a PR without a reviewer
- Hardcode any credential, token, or secret
- Use `print()` in `src/` — use `logging`
- Call `dhan.place_order()` in Phases 1–3 — log signals only
- Recommend a paid tool when a free equivalent exists and is fit for purpose
- Generate code that can exceed 10 orders/sec — always rate-limit with `MAX_ORDERS_PER_SEC = 8`
- Assume `paper_trade=True` sandbox exists in Dhan SDK — no sandbox documented; use vectorbt

### When Generating New Modules

**Phase 1 scripts go in `scripts/<handle>.py` — not in `src/`.** Lower bar applies:
no mandatory docstrings or type hints, no `if __name__ == "__main__"` required.
Still required: `.NS` suffix on NSE tickers, no hardcoded credentials, `logging` not `print()`.

For `src/` modules (Phase 3+):

1. Create the file under the correct `src/` subdirectory
2. Add module-level docstring: what it does, who owns it, phase it becomes active
3. Add all functions with full docstrings and type hints
4. Add `if __name__ == "__main__":` block with a minimal smoke test
5. Update `requirements.txt` if new dependencies were added

### When Generating Notebooks

1. First cell: markdown with notebook title, purpose, author (role), and week number
2. Second cell: all imports
3. Third cell: configuration (tickers, date range, parameters)
4. Add markdown cells between code sections explaining what each section does
5. Last cell: summary of findings in plain English (for the Docs role to copy to AppFlowy)

### When Suggesting Tools or Libraries

Check this order before recommending:

1. Is it already in `requirements.txt`? Use it.
2. Is there a FOSS alternative to the paid tool being considered? Recommend the FOSS one.
3. Does it require a C compiler to install? If yes, is there a pure-Python alternative? (e.g. `ta` over `TA-Lib`)
4. Is it compatible with Python 3.12? Check before recommending.

---

## 18. Dhan API — Key References

- **Python SDK**: <https://github.com/dhan-oss/DhanHQ-py>
- **API Docs**: <https://dhanhq.co/docs/v2/>
- **Rate limit**: 10 orders/second (SEBI/NSE hard cap — never exceed)
- **Token refresh**: Every **24 hours** (SEBI hard cap) — manual, from Dhan profile
- **Paper trading**: No sandbox in Dhan SDK. Use vectorbt `Portfolio.from_signals()` for simulation.

## 19. External Resources (Pinned)

| Resource                        | URL                                               | Phase |
| ------------------------------- | ------------------------------------------------- | ----- |
| Zerodha Varsity — All Modules   | <https://zerodha.com/varsity>                     | 1–4   |
| CS50P — Python                  | <https://cs50.harvard.edu/python/2022>            | 1–2   |
| vectorbt Documentation          | <https://vectorbt.dev>                            | 3     |
| DhanHQ SDK GitHub               | <https://github.com/dhan-oss/DhanHQ-py>           | 4     |
| Streamlit Docs                  | <https://docs.streamlit.io>                       | 5     |
| QuantInsti Blog                 | <https://blog.quantinsti.com>                     | 2–4   |
| Investopedia Technical Analysis | <https://www.investopedia.com/technical-analysis> | 2–3   |
| Learn Git Branching             | <https://learngitbranching.js.org>                | 1     |
| NSE India Market Data           | <https://www.nseindia.com/market-data>            | 2+    |
| TradingView India               | <https://www.tradingview.com>                     | 2+    |

---

*Last updated: Week 2, Phase 1. Update this file whenever architecture, team, or decisions change.*
*Owner: RS (Project Lead). Changes via PR — do not edit directly on main.*

---

## 20. External Documentation & Constraints

This section is the authoritative reference for Claude Code. When generating code for QuantIQ, always consult the relevant docs below before producing any implementation. Constraints listed here are non-negotiable.

---

### 20.1 Broker Integration — DhanHQ

- **SDK:** `dhanhq==2.0.2` (pin exactly). v2.2.0 has breaking import changes — do not upgrade without checking <https://github.com/dhan-oss/DhanHQ-py/releases>
- **API Docs v2:** <https://dhanhq.co/docs/v2/>
- **Orders reference:** <https://dhanhq.co/docs/v2/orders/>
- **Market Quote / LTP:** <https://dhanhq.co/docs/v2/market-quote/>
- **Option Chain:** <https://dhanhq.co/docs/v2/option-chain/>
- **SDK GitHub:** <https://github.com/dhan-oss/DhanHQ-py>
- **SDK README:** <https://github.com/dhan-oss/DhanHQ-py/blob/main/README.md>

**Hard constraints — never violate:**

1. Access tokens are valid for **24 hours only** (SEBI mandate). The bot must regenerate the token daily before 9:15 AM IST market open. Never document or assume 30-day or permanent token validity.
2. Order rate limit: **≤10 orders/second/exchange/client**. Never generate code that exceeds this without explicit rate-limiting.
3. All order placement must log: timestamp, symbol, order type, quantity, price, order ID, response status.
4. Static-IP whitelisting is mandatory (SEBI Feb 2025 circular). Use `DhanLogin.set_ip()` / `modify_ip()` / `get_ip()` from the SDK.
5. DhanHQ has **no documented paper-trading sandbox**. Never generate code that assumes a sandbox endpoint exists. Use vectorbt `Portfolio.from_signals()` for paper simulation.
6. Security IDs are **integers** (e.g. `1333` = HDFC Bank NSE_EQ). Never use ISIN strings with `quote_data` / `ohlc_data` / `ticker_data`. Find IDs via `dhan.fetch_security_list("compact")`.

**Confirmed SDK methods (dhanhq v2.x):**

```python
# Market data — integer security IDs required
dhan.quote_data({"NSE_EQ": [1333, 11536]})          # real-time snapshot
dhan.ohlc_data({"NSE_EQ": [1333]})                   # OHLC quote
dhan.ticker_data({"NSE_EQ": [1333]})                 # LTP only (lower payload)
dhan.intraday_minute_data(security_id, exchange_segment, instrument_type)
dhan.historical_daily_data(security_id, exchange_segment, instrument_type, expiry_code, from_date, to_date)

# Security master — find integer IDs
dhan.fetch_security_list("compact")

# Orders (Phase 4 only)
dhan.place_order(...)
dhan.modify_order(order_id, ...)
dhan.cancel_order(order_id)

# Portfolio
dhan.get_positions()
dhan.get_holdings()
dhan.get_fund_limits()
dhan.get_order_list()
```

---

### 20.2 Market Data — yfinance

- **Docs:** <https://ranaroussi.github.io/yfinance/>
- **API reference:** <https://ranaroussi.github.io/yfinance/reference/index.html>
- **GitHub:** <https://github.com/ranaroussi/yfinance>
- **NSE ticker issue:** <https://github.com/ranaroussi/yfinance/issues/825>

**Hard constraints:**

1. All NSE tickers must be suffixed `.NS` (e.g. `RELIANCE.NS`, `INFY.NS`). BSE tickers use `.BO`. Never fetch an unsuffixed Indian ticker — it silently returns US equity data.
2. Always validate ticker suffix at the data-layer entry point before passing to yfinance.

**Correct usage:**

```python
# download() — multiple tickers
yf.download(
    tickers="RELIANCE.NS TCS.NS",  # space-separated string or list
    period="1y",                    # 1d 5d 1mo 3mo 6mo 1y 2y 5y 10y ytd max
    interval="1d",                  # 1m 2m 5m 15m 30m 60m 90m 1h 1d 5d 1wk 1mo 3mo
    auto_adjust=True,               # adjusts OHLC for splits/dividends
)

# Ticker.history() — single ticker
ticker = yf.Ticker("RELIANCE.NS")
df = ticker.history(period="1y", interval="1d")
# Columns: Open, High, Low, Close, Volume, Dividends, Stock Splits
```

Intraday intervals available for last 60 days only. yfinance is unofficial — Yahoo ToS limits commercial use.

---

### 20.3 Technical Indicators — `ta` library

- **Docs:** <https://technical-analysis-library-in-python.readthedocs.io/en/latest/>
- **API reference:** <https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html>
- **GitHub:** <https://github.com/bukosabino/ta>

**Hard constraint:** `ta` does NOT include a daily VWAP. When VWAP is required, implement manually:

```python
# VWAP — manual implementation, do NOT rely on ta.volume.VolumeWeightedAveragePrice for daily VWAP
typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
df["VWAP"] = (typical_price * df["Volume"]).cumsum() / df["Volume"].cumsum()
```

**Correct indicator usage:**

```python
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange, BollingerBands

df["SMA20"] = SMAIndicator(close=df["Close"], window=20).sma_indicator()
df["EMA20"] = EMAIndicator(close=df["Close"], window=20).ema_indicator()
df["RSI"]   = RSIIndicator(close=df["Close"], window=14).rsi()

macd = MACD(close=df["Close"], window_slow=26, window_fast=12, window_sign=9)
df["MACD"]        = macd.macd()
df["MACD_signal"] = macd.macd_signal()
df["MACD_diff"]   = macd.macd_diff()

df["ATR"] = AverageTrueRange(
    high=df["High"], low=df["Low"], close=df["Close"], window=14
).average_true_range()

bb = BollingerBands(close=df["Close"], window=20, window_dev=2)
df["BB_upper"] = bb.bollinger_hband()
df["BB_mid"]   = bb.bollinger_mavg()
df["BB_lower"] = bb.bollinger_lband()

df.dropna(inplace=True)  # always after rolling ops, before backtest
```

---

### 20.4 Backtesting — vectorbt

- **Docs:** <https://vectorbt.dev/>
- **GitHub:** <https://github.com/polakowo/vectorbt>
- **Python compat issue:** <https://github.com/polakowo/vectorbt/issues/807>

**Hard constraints:**

1. Use `vectorbt==1.0.0` — pin exactly. v1.0.0 is open-source (went free in 2025). Do not upgrade without testing Numba compatibility.
2. Python compatibility: `>=3.11,<3.13`. Do not generate code or CI configs targeting Python 3.13+ until Numba wheel availability is confirmed.

**Correct usage:**

```python
import vectorbt as vbt

pf = vbt.Portfolio.from_signals(
    close=df["Close"],
    entries=entries,    # pd.Series of bool — True = buy
    exits=exits,        # pd.Series of bool — True = sell
    init_cash=100_000,
    fees=0.001,         # 0.1% per trade (slippage + brokerage)
    freq="1D",
)

print(pf.total_return())     # cumulative return
print(pf.sharpe_ratio())     # risk-adjusted return (target > 1.0)
print(pf.max_drawdown())     # largest peak-to-trough (target < 20%)
print(pf.trades.win_rate())  # % profitable trades (target > 50%)
print(pf.stats())            # full summary table
```

---

### 20.5 Dashboard — Streamlit

- **Docs:** <https://docs.streamlit.io/>
- **API reference:** <https://docs.streamlit.io/develop/api-reference>
- **Secrets management:** <https://docs.streamlit.io/develop/concepts/connections/secrets-management>

**Hard constraints:**

1. Store `DHAN_CLIENT_ID` and `DHAN_ACCESS_TOKEN` in `.streamlit/secrets.toml` locally. Never hardcode credentials.
2. `.streamlit/secrets.toml` must be in `.gitignore`. Never commit it.
3. For Streamlit Community Cloud deployment, credentials are pasted into "Advanced settings → Secrets" — never stored in the repo.

---

### 20.6 Charting — Plotly

- **Docs:** <https://plotly.com/python/>
- **API reference:** <https://plotly.com/python-api-reference/>
- **Figure reference:** <https://plotly.com/python/reference/>

Always use Plotly over matplotlib. Interactive charts are a project requirement.

---

### 20.7 Data Manipulation

| Library | Docs | Quickstart |
| --- | --- | --- |
| pandas | <https://pandas.pydata.org/docs/> | <https://pandas.pydata.org/docs/user_guide/10min.html> |
| numpy | <https://numpy.org/doc/stable/> | <https://numpy.org/doc/stable/user/quickstart.html> |

---

### 20.8 Environment Variables — python-dotenv

- **GitHub / Docs:** <https://github.com/theskumar/python-dotenv>
- **Version:** `python-dotenv==1.2.2`, requires Python `>=3.10`

**Hard constraint:** Never generate code that reads API credentials directly from environment without `load_dotenv()` or Streamlit secrets.

---

### 20.9 Code Style

Always generate code conforming to:

- **PEP 8:** <https://peps.python.org/pep-0008/>
- **PEP 257:** <https://peps.python.org/pep-0257/>
- **PEP 484 (type hints):** <https://peps.python.org/pep-0484/>
- **Google Python Style Guide (docstrings):** <https://google.github.io/styleguide/pyguide.html>

Use Google-style docstrings exclusively (`Args:`, `Returns:`, `Raises:`).

---

### 20.10 Regulatory Compliance (India)

- **SEBI Master Circular (Feb 2025):** <https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html>
- **SEBI Extension (Sep 2025):** <https://www.sebi.gov.in/legal/circulars/sep-2025/extension-of-timeline-for-implementation-of-sebi-circular-dated-february-04-2025-on-safer-participation-of-retail-investors-in-algorithmic-trading-_96979.html>
- **SEBI Circular Index:** <https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListingAll=yes&search=Algorithmic>

**Hard constraints for Phase 4 bot:**

1. Order rate: ≤10 orders/sec. Never generate a loop that can exceed this.
2. Daily session logout must be implemented — no persistent session across trading days.
3. All algo activity must be audit-logged with ≥5-year retention capability (file rotation acceptable; use Python `logging` with `TimedRotatingFileHandler`).
4. Static-IP whitelisting must be set via DhanHQ SDK before any live order is placed.

---

### 20.11 Version Control

- **Conventional Commits:** <https://www.conventionalcommits.org/en/v1.0.0/>
- **Semantic Versioning:** <https://semver.org/>

When generating commit messages, branch names, or PR templates, always follow Conventional Commits format:
`<type>(<scope>): <description>` — e.g. `feat(data): add NSE ticker validator`
