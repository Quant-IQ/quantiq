#!/bin/bash

echo "Starting issue generation for QuantIQ..."

# ==========================================
# PHASE 0: Onboarding & Setup
# ==========================================
echo "Creating Phase 0 issues..."


gh issue create --title "[PHASE-0] Post intro in Discord #introductions" --body "Name, role, one sentence on what you want to learn. Then reply Acknowledged in #rules-and-norms thread." --label "phase-0,role:all"
gh issue create --title "[PHASE-0] Set up Discord server & channels" --body "Create all channels and roles per the pre-launch roadmap. Pin ground rules in #rules-and-norms." --label "phase-0,role:co-lead" --assignee "Rohansri006"
gh issue create --title "[PHASE-0] Create Notion workspace" --body "Set up Home, Weekly Log, Meeting Notes, Architecture, Decisions Log, Roles, Resources pages. Invite team." --label "phase-0,role:co-lead" --assignee "Rohansri006"
gh issue create --title "[PHASE-0] Send onboarding DMs to all members" --body "Personalise and send Message 3 from the Discord welcome PDF to each confirmed member within 24hrs of them joining." --label "phase-0,role:co-lead" --assignee "Rohansri006"

sleep 2

# ==========================================
# PHASE 1: Foundations
# ==========================================
echo "Creating Phase 1 issues..."

gh issue create --title "[PHASE-1] Start CS50P — lectures 0 to 4" --body "cs50.harvard.edu/python/2022. Lectures 0–4 minimum for all. Full course for Dev/Data/Quant." --label "phase-1,role:all"
gh issue create --title "[PHASE-1] Complete Varsity Module 1 fully" --body "All remaining videos from Module 1. Core market literacy baseline before moving to indicators." --label "phase-1,role:all"
gh issue create --title "[PHASE-1] Install project Python libraries" --body "pip install pandas numpy matplotlib plotly yfinance dhanhq ta vectorbt streamlit python-dotenv jupyter" --label "phase-1,role:all"
gh issue create --title "[PHASE-1] Watch Varsity Module 2 — first 5 videos" --body "Candlesticks, trends, support and resistance. This is the minimum market knowledge for everyone." --label "phase-1,role:all"
gh issue create --title "[PHASE-1] Week 4 analysis script (Quant)" --body "Write analysis/yourname_basic.py: download 3 months NIFTY data via yfinance. Print: high, low, avg close, % change. Open PR." --label "phase-1,role:quant"
gh issue create --title "[PHASE-1] Week 4 analysis script (Dev)" --body "Write analysis/yourname_basic.py: download 3 months NIFTY data via yfinance. Print: high, low, avg close, % change. Open PR." --label "phase-1,role:dev"
gh issue create --title "[PHASE-1] Week 4 analysis script (Data)" --body "Write analysis/yourname_basic.py: download 3 months NIFTY data via yfinance. Print: high, low, avg close, % change. Open PR." --label "phase-1,role:data"
gh issue create --title "[PHASE-1] Write Notion log — Weeks 2 & 3" --body "Notion Weekly Log. Each entry: what the team did, one screenshot, one problem and how it was solved." --label "phase-1,role:docs"
gh issue create --title "[PHASE-1] Review 2 PRs per week" --body "Read every PR diff. Check: docstrings present, no hardcoded secrets, clear commit message. Leave at least one comment." --label "phase-1,role:co-lead"
gh issue create --title "[PHASE-1] Set up .env for team" --body "Create .env.example with placeholder keys. Add .env to .gitignore. Write setup instructions in CONTRIBUTING.md." --label "phase-1,role:dev"

sleep 2

# ==========================================
# PHASE 2: Data & Analysis
# ==========================================
echo "Creating Phase 2 issues..."

gh issue create --title "[PHASE-2] Learn pandas fundamentals" --body "Corey Schafer pandas YouTube series — all 10 videos. Code along with real data." --label "phase-2,role:data"
gh issue create --title "[PHASE-2] Build data fetch pipeline" --body "src/data/fetch.py: function fetch_ohlc(ticker, period) that returns a clean DataFrame. Docstring required." --label "phase-2,role:data"
gh issue create --title "[PHASE-2] Add SMA-20 and SMA-50 indicators" --body "src/data/indicators.py: calculate_sma(df, window). Use ta library or implement from scratch. Add to DataFrame." --label "phase-2,role:data"
gh issue create --title "[PHASE-2] Add RSI and MACD indicators" --body "Extend indicators.py. RSI with default period 14. MACD with default 12/26/9 params. Docstrings required." --label "phase-2,role:data"
gh issue create --title "[PHASE-2] Build plotly candlestick chart" --body "src/data/visualise.py: function plot_ohlc(df) that returns interactive plotly candlestick with SMA overlay." --label "phase-2,role:data"
gh issue create --title "[PHASE-2] Contribute section to market_analysis.ipynb" --body "Pick any NIFTY50 stock. Add: price chart with one indicator, 3 sentences of observations. PR into notebooks/." --label "phase-2,role:all"
gh issue create --title "[PHASE-2] Add correlation heatmap to notebook" --body "Select 5 NIFTY50 stocks. Plot a correlation heatmap of their closing prices. Interpret the output in a comment." --label "phase-2,role:quant"
gh issue create --title "[PHASE-2] Write Notion log — Weeks 5, 6, 7" --body "Three weekly log entries. Include: what was built, one chart screenshot per week, one team learning." --label "phase-2,role:docs"
gh issue create --title "[PHASE-2] Update README — Phase 2 progress" --body "Add screenshot of best chart from the group notebook. Update status table. Expand setup instructions." --label "phase-2,role:docs"
gh issue create --title "[PHASE-2] Learn Streamlit basics" --body "30 Days of Streamlit — Days 1 to 15. Build a toy app locally: one chart, one metric, one table." --label "phase-2,role:docs"

sleep 2

# ==========================================
# PHASE 3: Strategy & Backtesting
# ==========================================
echo "Creating Phase 3 issues..."

gh issue create --title "[PHASE-3] Write strategy spec document" --body "Plain-English doc in docs/strategy_v1.md: entry signal, exit signal, position size, stop-loss rule, target instrument." --label "phase-3,role:quant"
gh issue create --title "[PHASE-3] Implement SMA crossover strategy" --body "src/strategy/sma_crossover.py: generate_signals(df) returns DataFrame with BUY/SELL/HOLD column." --label "phase-3,role:dev"
gh issue create --title "[PHASE-3] Prepare clean backtest data feed" --body "1 year of daily NIFTY data. No missing dates (handle holidays). All indicators pre-calculated. Saved to backtest/." --label "phase-3,role:data"
gh issue create --title "[PHASE-3] Run backtest with vectorbt" --body "Use vectorbt Portfolio.from_signals(). Run on 1yr NIFTY. Output: Sharpe ratio, max drawdown, total return, win rate." --label "phase-3,role:quant"
gh issue create --title "[PHASE-3] Add realistic costs to backtest" --body "Add Rs 20 brokerage per trade and 0.1% slippage. Re-run backtest. Compare results with and without costs." --label "phase-3,role:dev"
gh issue create --title "[PHASE-3] Document backtest results" --body "Write backtest/results_v1.md: strategy description, equity curve image, key metrics table, interpretation." --label "phase-3,role:docs"
gh issue create --title "[PHASE-3] Update README — backtest results" --body "Add Results section to README. Paste equity curve chart. Add metrics table. This is the portfolio centrepiece." --label "phase-3,role:docs"
gh issue create --title "[PHASE-3] Write Decisions Log — strategy choices" --body "Log at least 3 strategy decisions in Notion Decisions Log. Why SMA over RSI? Why NIFTY? Why daily bars?" --label "phase-3,role:co-lead"

sleep 2

# ==========================================
# PHASE 4: Paper Trading
# ==========================================
echo "Creating Phase 4 issues..."

gh issue create --title "[PHASE-4] Open Dhan account + generate API token" --body "dhan.co → open account (free, instant KYC). Profile → DhanHQ APIs → Generate Access Token. Valid 30 days." --label "phase-4,role:all"
gh issue create --title "[PHASE-4] Dhan API authentication" --body "src/execution/dhan_client.py: authenticate with client_id and token from .env. Fetch LTP for RELIANCE.NS. Print it." --label "phase-4,role:dev"
gh issue create --title "[PHASE-4] Build WebSocket live tick connection" --body "Connect to Dhan WebSocket. Subscribe to NIFTY50 instruments. Print live LTP to console. Handle reconnect on drop." --label "phase-4,role:dev"
gh issue create --title "[PHASE-4] Build signal execution loop" --body "src/execution/bot.py: fetch price every 60s, calculate indicator, check signal, log to logs/trades.csv." --label "phase-4,role:dev"
gh issue create --title "[PHASE-4] Build trade log (CSV)" --body "logs/trades.csv: timestamp, ticker, signal (BUY/SELL/HOLD), price, indicator values. Append-only, never overwrite." --label "phase-4,role:dev"
gh issue create --title "[PHASE-4] Discord webhook alert on signal" --body "When a BUY or SELL signal fires, send a Discord webhook message to #standup with: signal, price, timestamp." --label "phase-4,role:dev"
gh issue create --title "[PHASE-4] Run 3 live paper trading sessions" --body "Coordinate 3 market-hours bot runs. Log any anomalies. Confirm no real orders placed. Share log summary with team." --label "phase-4,role:co-lead"
gh issue create --title "[PHASE-4] Build Streamlit dashboard" --body "src/dashboard/app.py: live price metric, current signal badge, last 20 trades table. Run locally first." --label "phase-4,role:docs"
gh issue create --title "[PHASE-4] Validate live signals vs backtest" --body "Compare paper trading signals with what the backtest predicted. Document any discrepancies in Notion." --label "phase-4,role:quant"
gh issue create --title "[PHASE-4] Write Notion log — Weeks 10 & 11" --body "Include: screenshot of bot running, screenshot of trade log CSV, screenshot of dashboard, one anomaly found." --label "phase-4,role:docs"

sleep 2

# ==========================================
# PHASE 5: Ship It
# ==========================================
echo "Creating Phase 5 issues..."

gh issue create --title "[PHASE-5] Final code clean-up — add all docstrings" --body "Every function in the codebase must have a docstring. Review your own code first. Then review one teammate's." --label "phase-5,role:all"
gh issue create --title "[PHASE-5] Final README — all sections complete" --body "Project name, description, team, setup, structure, results (with equity curve), dashboard screenshot, What We Learned." --label "phase-5,role:docs"
gh issue create --title "[PHASE-5] Deploy Streamlit dashboard" --body "Push dashboard to Streamlit Cloud (free tier). Share the public URL. Add the link to README." --label "phase-5,role:docs"
gh issue create --title "[PHASE-5] Run public repo checklist" --body "Audit for secrets, check commit history, confirm README stands alone, get team thumbs-up, change repo to Public." --label "phase-5,role:co-lead" --assignee "Rohansri006"
gh issue create --title "[PHASE-5] Record 2-minute demo video" --body "Screen record: show the live bot run, the equity curve, and the Streamlit dashboard. Upload to Google Drive, link in README." --label "phase-5,role:all"
gh issue create --title "[PHASE-5] Write LinkedIn wrap post draft" --body "Draft the project wrap post in the shared Google Doc. Include: what was built, team credits, GitHub link, key metric." --label "phase-5,role:docs"
gh issue create --title "[PHASE-5] Notion final project summary" --body "A final Notion page summarising the full 12 weeks: timeline, what worked, what did not, what each person learned." --label "phase-5,role:docs"

echo "Done! All 55 issues have been deployed to the board."
