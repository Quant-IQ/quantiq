# QuantIQ

> End-to-end algorithmic trading system · NSE Indian equity market · Python

![Status](https://img.shields.io/badge/Status-In%20_Progress-%20?labelColor=0d1117&color=3fb950)
![Python](https://img.shields.io/badge/Language-Python-yellow?logo=python&logoColor=rgb(52%2C%20118%2C%20169)&labelColor=ffd53d&color=rgb(52%2C%20118%2C%20169))
![Broker](https://img.shields.io/badge/Dhan-Broker?label=Broker&labelColor=ffffff&color=4fbb94)
![Repo](https://img.shields.io/badge/Visibility-Public-Green)

---

## Overview

QuantIQ is a collaborative 12-week project to build a working paper-trading bot on the NSE using the Dhan API. Equal parts learning vehicle, team collaboration exercise, and portfolio piece.

**Scope:** Strategy design → backtesting → live paper trading via Dhan API  
**Market:** NSE equity (with F&O context)  
**Timeline:** 12 weeks · 5 phases · public after Week 8

---

## Team

Phase 1 roles assigned 17 May 2026. Reviewed again at end of Phase 1. P = primary, S = secondary.

| Name | Role                                    | Status          |
| :--- | :-------------------------------------- | :-------------- |
| RS   | Project Lead                            | Active          |
| EB   | Docs (P) \| Dev (S)                     | Active          |
| GT   | Quant / Strategy (P) \| Data (S)        | Active          |
| AV   | Quant / Strategy (P) \| Data (S)        | Active          |
| AR   | Dev / Infra (P) \| Data (S)             | Active          |
| RT   | Quant / Strategy (P) \| Data (S)        | Active          |
| NS   | Docs (P) \| Dev (S)                     | Active          |
| AJ   | Quant (P) \| Data (S)                   | Phase 0 pending |
| SS   | Quant (P) \| Docs (S)                   | Phase 0 pending |
| SmS  | Docs (P) \| Data (S)                    | Active          |
| AK   | Dev (P) \| Data (S)                     | Active          |
| ShS  | Docs (P) \| Dev (S)                     | Phase 0 pending |
| HG   | Docs (P) \| Quant (S)                   | Phase 0 pending |

*Roles reviewed end of Phase 1 / start of Phase 2.*

---

## Roadmap

| Phase                   | Weeks | Deliverable                                   | Status         |
| :---------------------- | :---: | :-------------------------------------------- | :------------  |
| 0 — Onboarding          |   1   | First commit from every member                | ✅ Complete    |
| 1 — Foundations         |  2–4  | Python script: fetch + analyse NSE stock data | 🔄 In Progress |
| 2 — Data & Analysis     |  5–7  | Shared `market_analysis.ipynb` on GitHub      | ⏳ Pending     |
| 3 — Strategy & Backtest |  8–9  | Backtest report: Sharpe, drawdown, win rate   | ⏳ Pending     |
| 4 — Paper Trading       | 10–11 | Bot running across 3+ live trading sessions   | ⏳ Pending     |
| 5 — Ship It             |  12   | Portfolio-ready public GitHub repo            | ⏳ Pending     |

---

## Setup

> ⚠️ **Python version:** Use **3.12 only.** Python 3.13+ will fail to install several core data libraries.

```bash
# 1. Clone and enter the repo
git clone https://github.com/QuantIQ-Team/quantiq.git
cd quantiq

# 2. Confirm your Python version
compgen -c python | sort -u   # Must have 3.12.x (Runs only on bash)

# 3. Create a virtual environment
python3.12 -m venv venv          # Mac / Linux
py -3.12 -m venv venv            # Windows

# 4. Activate it
source venv/bin/activate          # Mac / Linux
venv\Scripts\activate             # Windows (Command Prompt)
source venv/Scripts/activate      # Windows (Git Bash)

# 5. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 6. Configure environment variables
cp .env.example .env
# Open .env and fill in your Dhan client ID and access token

# Verify .env is not tracked (it must NOT appear here)
git status

# 7. Make your first contribution
git checkout -b members/yourname
# Create members/yourname.md with your name, role, and goals
git add members/yourname.md
git commit -m "docs: add yourname profile"
git push origin members/yourname
# GitHub will print a URL in the terminal — open it to submit your PR
```

---

## Stack

| Layer       | Tools                         |
| :---------- | :---------------------------- |
| Language    | Python 3.12                   |
| Data        | `yfinance`, `pandas`, `numpy` |
| Indicators  | `ta`                          |
| Backtesting | `vectorbt`                    |
| Broker API  | `dhanhq` (Dhan)               |
| Dashboard   | `Streamlit`                   |
| Charts      | `plotly`                      |

---

## Repository Structure

```text
quantiq/
├── src/
│   ├── data/          # Data fetching and indicator calculation
│   ├── strategy/      # Entry and exit logic
│   ├── execution/     # Dhan API and order management
│   └── dashboard/     # Streamlit app
├── notebooks/         # Jupyter analysis files
├── backtest/          # Backtest results and reports
├── logs/              # Trade signal logs (CSV)
├── members/           # One profile file per team member
└── docs/              # Architecture notes
```

---

## Communication & Tools

| Tool       | Purpose                                               |
| :--------- | :---------------------------------------------------- |
| Discord    | Primary team communication — all project discussions  |
| AppFlowy   | Docs, weekly log, decisions log, Kanban overview      |
| GitHub     | Code, PRs, Issues, Projects board                     |
| WhatsApp   | Urgent personal messages only — not project tracking  |

> Discord channel guide: `#standup` (Monday standups only) · `#dev` (code + PRs) · `#markets` (strategy) · `#data` (pipelines) · `#resources` (links only)

---

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a PR. Key rules:

- Never push directly to `main`
- Never merge your own PR — all PRs require one reviewer
- Write `Closes #<issue>` in your PR description to auto-close the linked issue
- Branch naming: `feature/`, `fix/`, `data/`, `docs/`, `backtest/`, `members/`

---

## Legal

Algo trading on your own account for personal use is legal in India under SEBI guidelines. This project does not manage third-party capital and is not offered as a commercial service. Reference: [SEBI Circular — Algorithmic Trading by Retail Investors (2022)](https://www.sebi.gov.in/legal/circulars/jan-2022/algorithmic-trading-by-retail-investors_55170.html).

---

*README is a living document. Updated at the end of each phase by the Analyst / Docs role.*  
*Last updated: Week 1*
