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

**All `src/` directories are scaffolded with `.gitkeep` files. Implementation begins Phase 1.**
**All src/ files listed above are planned targets, not current files**
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
| `flake8`  | Linter                                   |

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

Dhan access tokens expire every 30 days and must be manually refreshed from the Dhan profile page.

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

def fetch_ltp(ticker: str) -> float | None:
    """Fetch last traded price from Dhan API. Returns None on failure."""
    try:
        response = dhan.get_ltp_data([ticker])
        return response["data"]["ltp"]
    except KeyError as e:
        logger.error("Unexpected response structure for %s: %s", ticker, e)
        return None
    except Exception as e:
        logger.error("Dhan API call failed for %s: %s", ticker, e)
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

Dhan uses a different format — security ID + exchange segment:

```python
# Dhan format for Reliance equity
"NSE_EQ|INE002A01018"

# Dhan format for Nifty50 futures
"NSE_FNO|NIFTY"
```

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

Dhan allows **25 orders/second**. Track and throttle:

```python
import time

MAX_ORDERS_PER_SEC = 20  # Stay under 25 limit with margin
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

```text
type: short description (max 72 chars)

Types: feat | fix | data | docs | test | refactor | chore

Examples:
feat: add RSI indicator to data pipeline
fix: handle NaN values in SMA crossover signal
data: add NIFTY50 constituent ticker map
docs: update README with backtest results
refactor: extract order logging to separate module
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
| 1     | 2–4   | Individual analysis scripts — fetch NSE data, print stats  | Active      |
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

| Handle | Role             | Role Colour | Owns                                                |
| ------ | ---------------- | ----------- | --------------------------------------------------- |
| RS     | Project Lead     | `#F0C040`   | Repo, Discord, AppFlowy, decisions, unblocking      |
| EB     | Analyst / Docs   | `#FF7B9C`   | README, AppFlowy log, Streamlit dashboard           |
| GT     | Quant / Strategy | `#F0883E`   | Strategy design, backtesting, indicator research    |
| AV     | Data Engineer    | `#BC8CFF`   | Data pipelines, indicator functions, backtest feeds |
| AR     | Dev / Infra      | `#58A6FF`   | Bot engine, Dhan API, execution loop                |
| RT     | Quant / Strategy | `#F0883E`   | Strategy design, backtesting, indicator research    |
| NS     | Analyst / Docs   | `#FF7B9C`   | Support — Phase 0 incomplete (catch-up pending)     |
| AJ     | Data Engineer    | `#BC8CFF`   | Support — Phase 0 incomplete (catch-up pending)     |
| AD     | Dev / Infra      | `#58A6FF`   | Support — Phase 0 incomplete (catch-up pending)     |

**Team size:** 9 confirmed. One member withdrew before Phase 1. No replacement planned.

**Attrition rule:** Two consecutive missed standups with no explanation = voluntary exit.
NS, AJ, AD are on the watch list — reliability unproven.

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
| 13  | EB assigned Analyst / Docs            | Owns README, AppFlowy log, and Streamlit dashboard       |

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
from dhanhq import dhanhq
import os
from dotenv import load_dotenv

load_dotenv()

dhan = dhanhq(
    client_id=os.getenv("DHAN_CLIENT_ID"),
    access_token=os.getenv("DHAN_ACCESS_TOKEN"),
)
```

### Fetch Live Quote (LTP)

```python
# NSE equity — use security ID format
response = dhan.get_ltp_data(["NSE_EQ|INE002A01018"])  # Reliance
print(response)
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

- Access token expires every 30 days — must refresh manually from Dhan profile
- Rate limit: 25 orders/second — always throttle
- Paper trading = log signals to CSV only, do not call `place_order`
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

### When Generating New Modules

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
- **Rate limit**: 25 orders/second
- **Token refresh**: Every 30 days — manual, from Dhan profile
- **Paper trading**: Supported natively — use `dhan.place_order()` with `paper_trade=True` in Phase 4

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

*Last updated: Week 1, Phase 0. Update this file whenever architecture, team, or decisions change.*
*Owner: RS (Project Lead). Changes via PR — do not edit directly on main.*
