# CLAUDE.md — QuantIQ Project Context

> Read full at session start. Authoritative reference for architecture, conventions, team structure, AI behaviour rules. Don't infer from codebase alone — explains intent, not just structure.
> **Session start checklist:** (1) Read `.claude/todo.md` for open tasks. (2) Read relevant memory files. (3) Check GitHub for open/closed issues relevant to current phase. (4) Report open items to RS before asking what to work on. At session end: update `.claude/todo.md`.

---

## 1. Project Overview

**QuantIQ** — 12-week collaborative algorithmic trading project targeting NSE Indian equity stocks. Learning vehicle, team collaboration exercise, portfolio piece.

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

**Do not suggest going live with real capital.** Paper trading only until all members agree and at least 2–3 weeks of paper logs reviewed.

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

**All `src/` directories scaffolded with `.gitkeep`. `src/` implementation begins Phase 3.**
**All `src/` files above: planned targets, not current files.**
**Phase 1 work goes in `scripts/` — see §7. `scripts/` may be cleaned before repo goes public (Phase 5).**
No files outside this structure without discussing with Project Lead (RS).

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

Always recommend free and open-source alternatives over proprietary or paid tools. Non-negotiable project default. Specifically:

- Editor: VS Code (standing exception to FOSS rule — team uses VS Code, not VSCodium)
- Workspace: Notion (free tier, 10 collaborators — switched from AppFlowy which caps at 2)
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

Dhan access tokens expire every **24 hours** (SEBI hard cap) — must be manually regenerated from Dhan profile page daily.

---

## 5. Coding Standards

### Docstrings — Mandatory on Every Function

Every function in `src/` must have docstring. Non-negotiable — separates student project from professional one. Docs role reviews on every PR.

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

Use `logger.info()` for normal events, `logger.warning()` for unexpected but recoverable states, `logger.error()` for failures. Remove all `print()` before opening PR.

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

Find integer IDs via `dhan.fetch_security_list("compact")`. Maintain `src/data/ticker_map.py` mapping common names to both yfinance and Dhan formats.

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
2. Never merge own PR — always needs one reviewer
3. Write `Closes #N` in PR description to auto-close linked Issue
4. Fill PR template completely — do not delete sections
5. Remove all `print()` and debug code before opening
6. All functions must have docstrings — reviewer blocks merge if missing
7. No hardcoded credentials — reviewer blocks merge immediately
8. Add `Closes #N` for every Issue PR resolves
9. Reviewer must post within **48 hours** of assignment — post in #dev if unable
10. Reviewer uses **Squash and merge** — enables auto-delete of head branch

### PR Description Template

Every PR must use this template. Use `/quantiq-pr-description` to generate it automatically.

```markdown
## What does this PR do?
<!-- One or two sentences. What changed and why. -->

## How to test it
<!-- Steps to verify: e.g. "run python src/data/fetch.py — should print OHLCV table" -->

## Screenshots / Output
<!-- Paste a terminal output, chart screenshot, or test result if relevant. -->

## Checklist
- [ ] My code runs without errors locally
- [ ] I have added docstrings to all new functions
- [ ] No API tokens, .env values, or hardcoded paths in this PR
- [ ] Variable names are clear and descriptive (no x, temp, stuff)
- [ ] I have pulled latest main and resolved any conflicts
- [ ] I have linked the related Issue below

## Related Issue
Closes #[Issue number]

## Notes for reviewer
<!-- Anything you want the reviewer to pay special attention to. -->
```

### Issue Structure

Every task lives as GitHub Issue. Use provided templates:

- **Task template**: planned work
- **Bug template**: defects

Labels: `phase-0` through `phase-5`, `data`, `dev`, `docs`, `quant`, `co-lead`, `blocked`, `good-first-issue`

---

## 7. Project Phases and Current State

### Phase Map

| Phase | Weeks  | Due Date    | Core Deliverable                                           | Status      |
| ----- | ------ | ----------- | ---------------------------------------------------------- | ----------- |
| 0     | 1      | —           | Every member: first commit (`members/name.md`)             | Complete    |
| 1     | 2–4    | —           | `scripts/<handle>.py` — fetch NSE data, SMA20/50 stats     | Complete    |
| 2     | 4–5    | 14 Jun 2026 | `notebooks/market_analysis.ipynb` — group NIFTY50 analysis | Active      |
| 3     | 6–8    | 5 Jul 2026  | `src/` build — data, screener, watchlists, strategy        | Not started |
| 4     | 9–10   | 19 Jul 2026 | Execution layer + paper trading via Dhan API               | Not started |
| 5     | 11–12  | 2 Aug 2026  | Dashboard, deploy, public repo, full README                | Not started |

### Current Phase: Phase 2 — Market Analysis (Week 4, started 1 June 2026)

Phase 2 deliverable: `notebooks/market_analysis.ipynb` — group NIFTY50 analysis. Phase 2 sync held **1 June 2026**. Sub-team leads and Co-Lead confirmed at sync. Deadline: **14 Jun 2026**.

### GitHub Issues Snapshot — 7 Jun 2026: 197 total | 101 open | 96 closed

### Open Issues — Phase 2 (27 open)

| # | Title | Assignee | Notes |
| --- | ----- | -------- | ----- |
| 21 | [PHASE-2] Learn pandas fundamentals | RS | |
| 23 | [PHASE-2] Add SMA and EMA indicators | RS | |
| 25 | [PHASE-2] Build plotly candlestick chart | GT | |
| 26 | [PHASE-2] Contribute section to market_analysis.ipynb | RS | |
| 27 | [PHASE-2] Add correlation heatmap to notebook | RT | section 13 |
| 28 | [PHASE-2] Write Notion log — Weeks 4 & 5 | unassigned | |
| 29 | [PHASE-2] Update README — Phase 2 progress | unassigned | |
| 30 | [PHASE-2] Learn Streamlit basics | unassigned | |
| 114 | Pandas/RS | RS | |
| 115 | [PHASE-2] Add SMA indicators | RS | |
| 116 | [PHASE-2] Add EMA indicators | AV | |
| 117 | SMA/RS | RS | |
| 118 | Plotly/GT | GT | |
| 119 | EMA/AV | AV | |
| 121 | Analysis/RS | RS | |
| 122 | Correlation\RT | unassigned | ⚠ should be RS+GT |
| 124 | README/EB | EB | |
| 125 | [PHASE-2] Week5 Notion/ShS | ShS | |
| 126 | [PHASE-2] Varsity Module 2/SS | SS | |
| 127 | [PHASE-2] Add RSI indicators | RT | |
| 128 | [PHASE-2] Add MACD indicator | AV | |
| 190 | [PHASE-2] Analysis/GT | GT | |
| 191 | [PHASE-2] Pandas/SS | SS | |
| 192 | [PHASE-2] SMA/SS | SS | |
| 196 | [PHASE-2] README/ShS | ShS | |
| 261 | RSI/RT | unassigned | ⚠ RT's notebook section |
| 265 | RSI/SS | SS | |

### Open Issues — Phase 3 Backlog (35 open)

| # | Title | Assignee |
| --- | ----- | -------- |
| 31 | Write strategy spec document | GT |
| 32 | Implement SMA crossover strategy | GT |
| 34 | Run backtest with vectorbt | AV |
| 35 | Add realistic costs to backtest | AV |
| 36 | Document backtest results | EB |
| 37 | Update README — backtest results | EB |
| 38 | Write Decisions Log — strategy choices | RS |
| 200 | indicators.py — EMA, RSI, MACD, ATR, VWAP | AV |
| 201 | validate.py — gap detection, holiday handling, bad ticks | GT |
| 202 | ticker_map.py — NIFTY50 name→yfinance+DhanID | RS |
| 203 | visualise.py — interactive chart helpers | GT |
| 204 | screener/engine.py — AND/OR filter composition | AR |
| 205 | screener/runner.py — load config, fetch, run engine | AR |
| 206 | screener/config.py — ScreenerConfig dataclass | GT |
| 207 | screener/cache.py — JSON cache keyed by config+date | SmS |
| 208 | screener/filters — technical and fundamental | AV |
| 209 | watchlist system — static, dynamic, persistence | AR |
| 210 | strategy/base.py and signals.py — ABC and Signal dataclass | AV |
| 211 | strategy/rsi_mean_reversion.py | AV |
| 212 | strategy/runner.py — run strategy against tickers | GT |
| 221 | {PHASE-3} EMA indicator/AV | AV |
| 222 | {PHASE-3} RSI indicator/AV | AV |
| 223 | {PHASE-3} MACD indicator/AV | AV |
| 224 | {PHASE-3} ATR indicator/AV | AV |
| 225 | {PHASE-3} VWAP indicator/AV | AV |
| 226 | {PHASE-3} holiday_calendar/GT | GT |
| 227 | {PHASE-3} gap_detection/AR | AR |
| 228 | {PHASE-3} bad_tick_filter/AR | AR |
| 229 | {PHASE-3} stale_data_check/AR | AR |
| 230 | {PHASE-3} candlestick_ema/AR | AR |
| 231 | {PHASE-3} macd_subplot/AR | AR |
| 232 | {PHASE-3} rsi_subplot/AR | AR |
| 233 | {PHASE-3} volume_chart/AR | AR |
| 234 | {PHASE-3} technical_filters/AV | AV |
| 235 | {PHASE-3} fundamental_filters/AV | AV |
| 236 | {PHASE-3} strategy_base/GT | GT |
| 237 | {PHASE-3} signals_dataclass/AV | AV |
| 238 | {PHASE-3} static_watchlist/SmS | SmS |
| 239 | {PHASE-3} dynamic_watchlist/SmS | SmS |
| 240 | {PHASE-3} watchlist_persistence/SmS | SmS |
| 241 | {PHASE-3} watchlist_manager/AR | AR |
| 263 | SMA/GT | GT |

### Open Issues — Phase 4 Backlog (13 open)

| # | Title | Assignee |
| --- | ----- | -------- |
| 39 | Open Dhan account + generate API token | unassigned |
| 40 | Dhan API authentication | unassigned |
| 41 | Build WebSocket live tick connection | unassigned |
| 42 | Build signal execution loop | unassigned |
| 43 | Build trade log (CSV) | unassigned |
| 44 | Discord webhook alert on signal | unassigned |
| 45 | Run 3 live paper trading sessions | unassigned |
| 46 | Build Streamlit dashboard | unassigned |
| 47 | Validate live signals vs backtest | unassigned |
| 48 | Write Notion log — Weeks 10 & 11 | unassigned |
| 213 | dhan_client.py — authenticated Dhan wrapper + rate limit | AR |
| 214 | websocket_feed.py — live tick feed with auto-reconnect | AR |
| 215 | logger.py — paper trade signal log to CSV | AR |
| 216 | order_manager.py — v0.0.2 scaffold | AR |
| 217 | integration test scaffold — end-to-end signal pipeline | RS |

### Open Issues — Phase 5 Backlog (16 open)

| # | Title | Assignee |
| --- | ----- | -------- |
| 49 | Final code clean-up — add all docstrings | unassigned |
| 50 | Final README — all sections complete | unassigned |
| 51 | Deploy Streamlit dashboard | unassigned |
| 52 | Run public repo checklist | RS |
| 53 | Record 2-minute demo video | unassigned |
| 54 | Write LinkedIn wrap post draft | unassigned |
| 55 | Notion final project summary | unassigned |
| 218 | dashboard/app.py — 5-page Streamlit skeleton | EB |
| 219 | docs/architecture.md — full system diagram | EB |
| 220 | Streamlit Cloud deploy + public repo checklist | RS |
| 242 | {PHASE-5} screener_page/EB | EB |
| 243 | {PHASE-5} watchlists_page/EB | EB |
| 244 | {PHASE-5} strategy_page/EB | EB |
| 245 | {PHASE-5} backtest_page/EB | EB |
| 246 | {PHASE-5} live_feed_page/EB | EB |
| 247 | {PHASE-5} streamlit_deploy/EB | EB |
| 248 | {PHASE-5} public_repo_checklist/RS | RS |

### Closed Issues — Summary (96 closed)

| Phase | Count | Notes |
| ----- | ----- | ----- |
| Phase-0 | ~65 | Per-member onboarding — clone, git, varsity, discord, branch creation |
| Phase-1 | ~17 | Setup, scripts, analysis, webhook, GitHub Pages, housekeeping |
| Phase-2 | 3 | Fetch/RS (#120), notebook skeleton (#199), Varsity 1/EB (#123) |
| Misc | 1 | RSI/RT (#260) duplicate, closed |

**⚠ Attention items:**

- `#122 Correlation\RT` — unassigned; should be RS+GT per notebook plan (section 13)
- `#261 RSI/RT` — unassigned; RT's notebook section needs assignment
- `#28`, `#29`, `#30` — all unassigned docs tasks (Notion log, README, Streamlit basics)

### Notebook Section Order — `notebooks/market_analysis.ipynb`

Sector-grouped. RS + GT own section 13 (correlation heatmap).

| # | Sector | Ticker | Member |
| --- | ------ | ------ | ------ |
| 1 | Energy/Conglomerate | RELIANCE.NS | AJ |
| 2 | IT | TCS.NS | AV |
| 3 | IT | INFY.NS | AK |
| 4 | IT | HCLTECH.NS | SS |
| 5 | Banking | HDFCBANK.NS | AR |
| 6 | Banking | ICICIBANK.NS | EB |
| 7 | Banking | AXISBANK.NS | ShS |
| 8 | Auto | TVS.NS | RS |
| 9 | Auto | M&M.NS | GT |
| 10 | Infrastructure | LT.NS | RT |
| 11 | Consumer | TITAN.NS | NS |
| 12 | Defense | APOLLO.NS | SmS |
| 13 | Cross-sector | Correlation heatmap | RS + GT |

**Member section template:** fetch → summary stats → candlestick + EMA20/50 → MACD → RSI → volume. Fundamentals via `yf.Ticker.info` with None-guards: P/E, EPS growth, D/E, Cash/Debt, ICR, PEG (5Y+1Y), reserve & surplus, promoter%, pledged shares%, dividend yield. End with 3–5 sentence observation.

---

### Target Architecture (Full System — Phases 1–5)

```text
                    ┌─────────────────�
                    │   yfinance      │  Historical OHLCV (backtest + init)
                    └────────┬────────┘
                             │
                    ┌────────▼────────�
                    │  src/data/      │  fetch.py → indicators.py → validate.py
                    │  fetch.py       │  Output: clean DataFrame with OHLCV + indicators
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────�
              │              │              │
    ┌─────────▼──────�  ┌────▼────�  ┌────▼─────────────�
    │  backtest/     │  │strategy/│  │ execution/        │
    │  vectorbt      │  │ signals │  │ dhan_client.py    │
    │  Phase 3       │  │ Phase 2+│  │ order_manager.py  │
    └────────────────┘  └────┬────┘  │ websocket_feed.py │
                             │       │ logger.py         │
                             │       └────────┬──────────┘
                             │                │
                    ┌────────▼────────────────▼──�
                    │     logs/trades.csv         │
                    │     Signal log (gitignored) │
                    └────────────────┬────────────┘
                                     │
                    ┌────────────────▼────────────�
                    │     dashboard/app.py         │
                    │     Streamlit — Phase 5      │
                    └─────────────────────────────┘
```

---

## 8. Team Structure

Roles confirmed at Phase 2 sync on **1 June 2026**. Sub-team leads assigned. Roles marked (P) primary, (S) secondary.

| Handle | Role (P / S) — Phase 2 | Sub-team Lead | Role Colour | Owns |
| --- | --- | --- | --- | --- |
| RS | Project Lead / All | — | `#F0C040` | Repo, Discord, Notion, decisions, unblocking |
| GT | Quant / Strategy (P) / Analyst / Docs (S) | **Co-Lead (whole team)** | `#6AC074` | Co-lead all tracks until Dev/Docs co-lead assigned; strategy design, backtesting |
| EB | Analyst / Docs (P) / Dev / Infra (S) | **Docs lead** | `#2EC4B6` | README, Notion log, Streamlit dashboard |
| AV | Quant / Strategy (P) / Data Engineering (S) | **Quant lead** | `#2EC4B6` | Quant track ownership, NIFTY50 analysis, indicator work |
| AR | Data Engineering (P) / Dev / Infra (S) | **Dev lead** | `#2EC4B6` | Dev/Infra track ownership, data pipelines, data validation |
| SmS | Data Engineering (P) / Analyst / Docs (S) | **Data lead** | `#2EC4B6` | Data pipeline ownership, Notion log, README |
| RT | Quant / Strategy (P) / Dev / Infra (S) | — | `#F0883E` | Strategy design, backtesting, indicator research |
| NS | Dev / Infra (P) / Data Engineering (S) | — | `#58A6FF` | Dev / Infra support, data pipeline |
| AJ | Data Engineering (P) / Quant / Strategy (S) | — | `#BC8CFF` | Data pipelines, indicator work, strategy research support |
| SS | Quant / Strategy (P) / Analyst / Docs (S) | — | `#F0883E` | Strategy research, documentation support |
| AK | Dev / Infra (P) / Data Engineering (S) | — | `#58A6FF` | Bot engine support, data pipeline |
| ShS | Analyst / Docs (P) / Dev / Infra (S) | — | `#FF7B9C` | README, Notion log, dev support |

**Team size:** 12 active members. AD departed before Phase 1. HG departed Week 2 Phase 1.

**Co-Lead:** GT assigned Co-Lead for whole team (1 June 2026). Covers all tracks until second Co-Lead for Dev/Infra + Analyst/Docs track assigned. Sub-team structure: Project Lead → Co-Lead (GT) → Sub-team leads (AV: Quant, SmS: Data, AR: Dev, EB: Docs).

**Attrition rule:** Two consecutive missed standups with no explanation = voluntary exit.

---

## 9. Communication and Workflow Norms

### Standup Format — Discord `#standup`, Any day (hard deadline Sunday night)

```text
WEEK [n] — [Name] — [Role]
Did:      What you completed last week
Next:     What you are working on this week
Blocked:  Anything stopping you (or 'Nothing')
```

RS posts first (flexible — no fixed day). Week runs Monday–Sunday. Hard deadline: Sunday night. EB chases anyone who hasn't posted by Thursday night via DM (private DM only — no public call-outs).

**Accountability escalation:** Missing by Thursday night → EB DMs. Missed Sunday deadline → Co-Lead DMs. Missed 2 weeks in a row → Co-Lead alerts RS. Missed 2+ weeks with no commits → treated as voluntary exit. No exceptions.

### Task Lifecycle

```text
Issue created → assigned to one person → moves to "This Week" on Kanban
→ member creates branch → opens PR with "Closes #N"
→ reviewer approves → merged → Issue auto-closes → card moves to Done
```

**One owner per task.** Two assignees = no one responsible.
**One week per task max.** Spans longer → break into sub-Issues.
**Blocked tasks:** add `blocked` label within 24 hours of getting stuck. Co-Lead unblocks.

### Tool Usage

| Tool           | Purpose                                | Notes                                        |
| -------------- | -------------------------------------- | -------------------------------------------- |
| Discord        | Primary team communication             | All project discussions here                 |
| WhatsApp       | Urgent human messages only             | "Are you alive?" — not project tracking      |
| GitHub         | Code, PRs, Issues, Projects Kanban     | Code-linked tasks only                       |
| Notion Cloud | Docs, weekly log, team Kanban overview | FOSS. Shared via <quantiq.team@quant-iq.net> |
| VS Code        | Code editor                            | Standing exception to FOSS-first rule        |

Notion workspace shared via company email `quantiq.team@quant-iq.net` (domain: `quant-iq.net`). Email for Notion Cloud login and shared project comms only — does not replace Discord.

---

## 10. Key Design Decisions — Rationale

| #   | Decision                              | Reason                                                   |
| --- | ------------------------------------- | -------------------------------------------------------- |
| 1   | Dhan API over Zerodha Kite            | Free vs Rs 2000/month                                    |
| 2   | Python as project language            | Best library ecosystem for data + trading                |
| 3   | Notion over AppFlowy                  | AppFlowy free tier caps at 2 collaborators; Notion free supports 10 |
| 4   | Private repo until Phase 3 (~Week 8)  | Build first, show when results exist                     |
| 5   | vectorbt over backtrader              | Simpler API for this use case, faster for param sweeps   |
| 6   | `ta` library over TA-Lib              | No C compiler required — easier team install             |
| 7   | yfinance for historical data          | Free, reliable for NSE with `.NS` suffix                 |
| 8   | Plotly over matplotlib                | Interactive charts, better for finance visualization     |
| 9   | Streamlit Cloud for dashboard deploy  | Free tier, in existing stack, no DevOps knowledge needed |
| 10  | CS50P over paid Udemy courses         | Free, equivalent quality, no cost barrier for team       |
| 11  | Paper trade only until team consensus | Never touch real capital without full team agreement     |
| 12  | RT assigned Quant / Strategy          | Co-assigned with GT for strategy and backtesting         |
| 13  | EB primary Docs, secondary Data       | Owns README, Notion log, Streamlit dashboard           |
| 14  | GT assigned Co-Lead (1 June 2026)     | Whole-team co-lead; second Co-Lead (Dev/Docs) TBD        |
| 15  | Dual-role model (P/S) for all members | Primary = ownership; secondary = support / cross-train   |
| 16  | Second recruitment wave — up to 6 new | All who pass interview treated as full members           |

---

## 11. Product Vision — Full System

Full QuantIQ system (v1 shippable by Week 12, v2+ post-project) — four layers:

### Layer 1 — Data
- `fetch.py` — OHLCV via yfinance (NSE/BSE, single + batch)
- `indicators.py` — SMA, EMA, RSI, MACD, ATR, VWAP
- `validate.py` — gap detection, holiday handling, bad tick filtering
- **Fundamental data** — balance sheets, P&L, cash flows via BSE/NSE official filings or yfinance `.financials` / `.balance_sheet` / `.cashflow` (reliability TBD — research task assigned GT + AV)

### Layer 2 — Screener + Watchlists
- **Dynamic screener engine** — add/remove filters per run. Filter types: technical (price action, momentum, volatility), fundamental (P/E, P/B, ROE, D/E, earnings growth, FCF), quantitative (statistical)
- **Named screeners** — save screener configs with description; re-run on demand
- **Watchlists** — two types:
  - *Static*: manually curated, hand-picked stocks
  - *Dynamic*: linked to screener, auto-updates when screener runs
- Cache screener output keyed by screener name + run date

### Layer 3 — Strategy Engine
- **Strategy builder** — define entry/exit triggers using technical, fundamental, quantitative conditions
- **Execution modes** — run any strategy against:
  - Watchlist (static or dynamic)
  - Manual stock selection
  - Full market universe
- **Modes**: backtest (vectorbt) → paper trade (Dhan, signal log only) → live (Dhan, real capital — team consensus required)

### Layer 4 — Dashboard (Streamlit)
- Screener creation UI
- Watchlist management
- Strategy configuration
- Live signal feed + trade log
- Backtest results viewer

---

### v0.0.1 — Week 12 Deliverable

Legend: ✅ full  🔧 basic  🔨 very basic  🔜 v0.0.2

**Data**
| ID | Task | Version |
|----|------|---------|
| D1 | `fetch.py` single ticker OHLCV | ✅ |
| D2 | `fetch.py` batch fetch | ✅ |
| D3 | `fetch.py` caching | ✅ |
| D4 | `indicators.py` — SMA, EMA, RSI, MACD, ATR, VWAP + more as added | ✅ |
| D5 | `validate.py` — gaps, holidays, bad ticks | ✅ |
| D6 | Fundamental data source research | ✅ |
| D7 | Fundamental data fetcher | ✅ |
| D8 | Financial statement scraper | 🔨 very basic |
| D9 | Stock universe manager | 🔧 basic |
| D10 | Data pipeline scheduler | 🔜 v0.0.2 |

**Screener**
| ID | Task | Version |
|----|------|---------|
| S1 | Technical filters | ✅ |
| S2 | Fundamental filters | ✅ |
| S3 | Quantitative filters (beta, vol percentile, z-score) | 🔜 v0.0.2 |
| S4 | Screener engine (AND/OR filter logic) | ✅ |
| S5 | Save/load named screener configs | ✅ |
| S6 | Screener runner | ✅ |
| S7 | Screener output cache | ✅ |
| S8 | Profitability scoring / ranking | 🔜 v0.0.2 |
| S9 | Screener builder UI (graphical) | 🔧 basic |

**Watchlists**
| ID | Task | Version |
|----|------|---------|
| W1 | Static watchlist | ✅ |
| W2 | Dynamic watchlist (linked to screener) | ✅ |
| W3 | Watchlist persistence | ✅ |
| W4 | Watchlist manager (list/edit/delete) | 🔧 basic |
| W5 | Watchlist UI in dashboard | 🔨 very basic |

**Strategy**
| ID | Task | Version |
|----|------|---------|
| ST1 | Strategy spec format (config-driven) | ✅ |
| ST2 | Crossover strategy (EMA preferred over SMA — better for plots) | 🔨 very basic |
| ST3 | RSI mean-reversion strategy | ✅ |
| ST4 | Combined technical + fundamental strategy | 🔜 v0.0.2 |
| ST5 | Strategy runner (on watchlist / manual / full market) | ✅ |
| ST6 | Position sizing module | 🔜 v0.0.2 (paper trade only in v1) |
| ST7 | Risk management (stop loss, max drawdown breaker) | 🔧 basic |
| ST8 | Strategy builder UI | 🔧 basic (near-hardcoded; polish in v0.0.2) |

**Backtest + Execution**
| ID | Task | Version |
|----|------|---------|
| B1 | Backtest engine (vectorbt) | ✅ |
| B2 | Backtest metrics (Sharpe, drawdown, win rate, Calmar) | ✅ |
| B3 | Cost model (brokerage, slippage, STT) | 🔧 basic |
| B4 | Paper trade execution (signal log to CSV) | ✅ |
| B5 | Live trade execution (Dhan `place_order`) | 🔜 v0.0.2 |
| B6 | Order manager | 🔜 v0.0.2 |
| B7 | Trade logger (SEBI 5yr CSV) | 🔜 v0.0.2 |
| B8 | Backtest results viewer in dashboard | ✅ |

**Execution Infrastructure**
| ID | Task | Version |
|----|------|---------|
| E1 | Dhan client wrapper (auth, rate-limit) | ✅ |
| E2 | WebSocket live feed | ✅ |
| E3 | Session manager (daily login/logout) | ✅ |
| E4 | Discord webhook alerts | ✅ |
| E5 | Static IP whitelisting | ✅ |

**Dashboard**
| ID | Task | Version |
|----|------|---------|
| UI1 | App skeleton + routing | ✅ |
| UI2 | Live price widget | 🔧 basic |
| UI3 | Current signal display | ✅ |
| UI4 | Trade log (paper only; "Coming Soon" under Live tab) | 🔧 basic |
| UI5 | Screener runner + results table | ✅ |
| UI6 | Watchlist viewer / manager | ✅ |
| UI7 | Backtest results viewer | 🔨 very basic |
| UI8 | Streamlit Cloud deployment | ✅ |
| UI9 | Strategy config UI | ✅ |
| UI10 | Screener builder UI (graphical) | 🔧 basic |

**Docs**
| ID | Task | Version |
|----|------|---------|
| DOC1 | `docs/architecture.md` updated | ✅ |
| DOC2 | `CONTEXT.md` domain glossary | ✅ |
| DOC3 | README (screenshots + backtest + final) | ✅ |
| DOC4 | Notion weekly logs (Weeks 5–12) | ✅ |
| DOC5 | LinkedIn posts | ✅ |
| DOC6 | Public repo checklist | ✅ done (GitHub branch protection) |

**SMA Crossover — Phase 3 Backtest (learning vehicle)**

```txt
Entry signal:  SMA-20 crosses ABOVE SMA-50  →  BUY
Exit signal:   SMA-20 crosses BELOW SMA-50  →  SELL
Position size: Fixed lot (to be determined in Phase 3)
Stop loss:     ATR-based trailing stop
Universe:      Dynamic watchlist from screener (replaces hardcoded NIFTY50 top 5)
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

### v2+ Scope — Post Week 12

- Full dynamic screener UI (add/remove filters graphically)
- Fundamental analysis layer (once reliable NSE data source confirmed)
- Strategy builder UI in dashboard
- Full market universe screening
- Live deployment with real capital (team consensus + 2–3 weeks paper log review)

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

- Access token expires every **24 hours** (SEBI cap) — must regenerate daily before 9:15 AM IST
- Rate limit: 10 orders/second (SEBI/NSE hard cap) — always throttle, never exceed
- No paper-trading sandbox — log signals to CSV only; use vectorbt for simulation
- Never commit access token — load from `.env` only

---

## 13. Security Rules

Absolute. No exceptions regardless of context.

1. **Never commit `.env`** — in `.gitignore`. Token committed → rotate immediately.
2. **Never hardcode credentials** — no `token = "abc123"` anywhere in `src/`
3. **Audit before going public** — search entire repo for `token`, `key`, `secret`, `password` before switching to public in Week 8–9
4. **`.env.example` only** — placeholder values, never real credentials
5. **Logs gitignored** — `logs/*.csv` must never be committed (may contain price data + signal patterns)
6. **No member shares Dhan token** — every member generates own from their Dhan account
7. **Static IP whitelisting mandatory** (SEBI Feb 2025) — set via `DhanLogin.set_ip()` before any live order. 7-day cooldown after setting; cannot modify within that window.
8. **OAuth + TOTP 2FA mandatory** — all other auth methods discontinued per SEBI Feb 2025 circular. Use TOTP or OAuth flow (see §12 Authentication). Never generate code that bypasses 2FA.
9. **Daily session logout required** — no persistent sessions across trading days. Bot must log out after market close (15:30 IST) and re-authenticate before 09:15 IST next session.

---

## 14. Documentation Strategy

Layered across four levels. Each level has specific owner.

| Layer | Location               | Owner      | Updated When                     |
| ----- | ---------------------- | ---------- | -------------------------------- |
| 1     | `README.md`            | EB (Docs)  | End of each phase                |
| 2     | Notion Weekly Log    | EB (Docs)  | Every Sunday night               |
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

Maintain shared draft doc in Notion where teammates review LinkedIn posts before publishing.

---

## 16. Going Public — Week 8–9 Checklist

Before switching repo from private to public:

- [ ] Search entire repo for `token`, `key`, `secret`, `password` — zero results
- [ ] `git log` audit — no sensitive data in any historical commit
- [ ] `.env` not present anywhere in repo or commit history
- [ ] `logs/*.csv` not present in repo (gitignored correctly)
- [ ] README stands alone — stranger can read it and understand the project
- [ ] Backtest results in repo — at minimum one equity curve and results table
- [ ] All functions in `src/` have docstrings
- [ ] All team members posted thumbs-up in `#announcements`
- [ ] **Then**: GitHub → Settings → Danger Zone → Change visibility → Public

---

## 17. AI Behaviour Rules for Claude Code

Apply to every interaction in this codebase. Read before generating any code.

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
- Follow branch naming convention when creating branches
- Reference `Closes #N` in commit/PR messages when resolving Issues
- Use `TimedRotatingFileHandler` with `backupCount=1825` for all audit logs (SEBI 5-year retention)

### Never

- Suggest Zerodha Kite API (Rs 2000/month — Dhan is chosen broker)
- Suggest AppFlowy (Notion is chosen workspace — AppFlowy free tier limited to 2 collaborators)
- Recommend Python 3.13+ (breaks vectorbt and other data libraries)
- Push directly to `main`
- Merge PR without reviewer
- Hardcode any credential, token, or secret
- Use `print()` in `src/` — use `logging`
- Call `dhan.place_order()` in Phases 1–3 — log signals only
- Recommend paid tool when free equivalent exists and fits
- Generate code that can exceed 10 orders/sec — always rate-limit with `MAX_ORDERS_PER_SEC = 8`
- Assume `paper_trade=True` sandbox exists in Dhan SDK — no sandbox documented; use vectorbt
- Make any changes to the GitHub repo (PRs, comments, merges, labels, issue updates) without explicit RS permission — always describe what needs to be done and let RS execute manually

### GitHub Interaction Rules

Claude Code must not interact with the GitHub repo directly. No `gh` commands that write state (create PR, post comment, merge, label, assign, close issue) unless RS explicitly says "go ahead and do it" in the same conversation turn.

**Correct behaviour:**
- Review a PR → write findings as markdown files in `temp/`, report back to RS
- Identify what comment to post → show the text, let RS copy-paste it
- Identify a branch to merge → say which branch and why, let RS do the merge

**Why:** RS reviews all GitHub-facing communication before it goes public. Team members see everything posted to the repo. Claude posting directly bypasses that review step.

### PR Review Output Format

When reviewing a PR, write all findings to `d:\Work\quantiq\temp\` as markdown files. RS copy-pastes into GitHub manually.

**File structure:**

```
temp/
├── review_master.md          ← overall decision, scope violations, summary table
└── review_<filename>.md      ← one file per changed file reviewed
```

**Naming:** `review_` + filename with `/` replaced by `_`. Example: `src/strategy/base.py` → `review_src_strategy_base_py.md`.

**Per-file format:**

```markdown
# Review — `path/to/file.py`

## Issue 1 — BLOCKING: short title
[problem description]
[code block showing problem]
[code block showing fix]

## Issue 2 — CONCERN: short title
...

## Issue 3 — MINOR: short title
...
```

**Master file format:**

```markdown
# PR #N — Master Review Comment

**Decision: Approve / Request Changes**

[Overall summary — scope violations, structural blockers, recommended next steps]

## File-level issues summary

| File | Blockers | Concerns |
|------|----------|----------|
| ... | N | N |
```

Severity tags: `BLOCKING` (merge must not proceed), `CONCERN` (needs discussion before merge), `MINOR` (fix before merge or note for follow-up).

### When Generating New Modules

**Phase 1 scripts go in `scripts/<handle>.py` — not in `src/`.** Lower bar applies: no mandatory docstrings or type hints, no `if __name__ == "__main__"` required. Still required: `.NS` suffix on NSE tickers, no hardcoded credentials, `logging` not `print()`.

For `src/` modules (Phase 3+):

1. Create file under correct `src/` subdirectory
2. Add module-level docstring: what it does, who owns it, phase it becomes active
3. Add all functions with full docstrings and type hints
4. Add `if __name__ == "__main__":` block with minimal smoke test
5. Update `requirements.txt` if new dependencies added

### When Generating Notebooks

1. First cell: markdown with notebook title, purpose, author (role), week number
2. Second cell: all imports
3. Third cell: configuration (tickers, date range, parameters)
4. Add markdown cells between code sections explaining what each section does
5. Last cell: summary of findings in plain English (for Docs role to copy to Notion)

### When Suggesting Tools or Libraries

Check this order before recommending:

1. Already in `requirements.txt`? Use it.
2. FOSS alternative to paid tool being considered? Recommend FOSS.
3. Requires C compiler to install? Pure-Python alternative? (e.g. `ta` over `TA-Lib`)
4. Compatible with Python 3.12? Check before recommending.

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

*Last updated: Week 4, Phase 2 (5 June 2026). Update when architecture, team, or decisions change.*
*Owner: RS (Project Lead). Changes via PR — do not edit directly on main.*

---

## 20. External Documentation & Constraints

Authoritative reference for Claude Code. When generating code for QuantIQ, always consult relevant docs below before producing any implementation. Constraints listed here are non-negotiable.

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

1. Access tokens valid **24 hours only** (SEBI mandate). Bot must regenerate daily before 9:15 AM IST. Never document or assume 30-day or permanent token validity.
2. Order rate limit: **≤10 orders/second/exchange/client**. Never generate code exceeding this without explicit rate-limiting.
3. All order placement must log: timestamp, symbol, order type, quantity, price, order ID, response status.
4. Static-IP whitelisting mandatory (SEBI Feb 2025 circular). Use `DhanLogin.set_ip()` / `modify_ip()` / `get_ip()` from SDK.
5. DhanHQ has **no documented paper-trading sandbox**. Never generate code assuming sandbox endpoint exists. Use vectorbt `Portfolio.from_signals()` for paper simulation.
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

1. All NSE tickers must be suffixed `.NS` (e.g. `RELIANCE.NS`, `INFY.NS`). BSE tickers use `.BO`. Never fetch unsuffixed Indian ticker — silently returns US equity data.
2. Always validate ticker suffix at data-layer entry point before passing to yfinance.

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

**Hard constraint:** `ta` does NOT include daily VWAP. When VWAP required, implement manually:

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
2. Python compatibility: `>=3.11,<3.13`. Do not generate code or CI configs targeting Python 3.13+ until Numba wheel availability confirmed.

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
3. For Streamlit Community Cloud deployment, credentials pasted into "Advanced settings → Secrets" — never stored in repo.

---

### 20.6 Charting — Plotly

- **Docs:** <https://plotly.com/python/>
- **API reference:** <https://plotly.com/python-api-reference/>
- **Figure reference:** <https://plotly.com/python/reference/>

Always use Plotly over matplotlib. Interactive charts are project requirement.

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

**Hard constraint:** Never generate code reading API credentials from environment without `load_dotenv()` or Streamlit secrets.

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

1. Order rate: ≤10 orders/sec. Never generate loop that can exceed this.
2. Daily session logout must be implemented — no persistent session across trading days.
3. All algo activity must be audit-logged with ≥5-year retention capability (file rotation acceptable; use Python `logging` with `TimedRotatingFileHandler`).
4. Static-IP whitelisting must be set via DhanHQ SDK before any live order placed.

---

### 20.11 Version Control

- **Conventional Commits:** <https://www.conventionalcommits.org/en/v1.0.0/>
- **Semantic Versioning:** <https://semver.org/>

When generating commit messages, branch names, or PR templates, always follow Conventional Commits format: `<type>(<scope>): <description>` — e.g. `feat(data): add NSE ticker validator`
