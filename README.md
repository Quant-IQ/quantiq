# QuantIQ
> End-to-end algorithmic trading system | NSE Indian equity market | Python

![Status](https://shields.io)
![Python](https://shields.io)
![License](https://shields.io)

## Team

| Name | Role |
| :--- | :--- |
| Rohan | Project Lead |
| [TBD] | Co-Lead |
| Guneet | Quant / Strategy |
| [TBD] | Dev / Infra |
| [TBD] | Data Engineer |
| [TBD] | Analyst / Docs |

## What We Are Building
A working paper-trading bot targeting NSE equity stocks using the Dhan API. Built collaboratively over 12 weeks as a learning and portfolio project.

## Project Status
**Phase 0 — Onboarding (Week 1) — In Progress**

## Setup
```bash
# 1. Clone the repo and enter the directory
git clone https://github.com/QuantIQ-Team/quantiq.git
cd quantiq

# ==========================================
# ⚠️ CRITICAL: PYTHON VERSION CHECK ⚠️
# Do NOT use Python 3.13 or 3.14. It will fail to install our data libraries.
# You must have Python 3.11 or 3.12 installed.
# ==========================================
python --version 

# 2. Set up the virtual environment (Run the command for your OS)
# Mac/Linux:
python3.12 -m venv venv
# Windows:
py -3.12 -m venv venv

# 3. Activate the virtual environment
source venv/bin/activate           # Mac/Linux
venv\Scripts\activate              # Windows (Command Prompt)
source venv/Scripts/activate       # Windows (Git Bash)

# 4. Install dependencies (This should take < 30 seconds, no C++ building!)
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Set up your local environment variables
cp .env.example .env
# Open .env in VSCode and fill in your Dhan API credentials

# Verify .env is safely ignored by Git (it should NOT be listed here)
git status

# 6. Create your member profile and open your first PR
# Replace 'yourname' with your actual first name (e.g., members/roy)
git checkout -b members/yourname

# Create the file members/yourname.md and fill in your details
git add members/yourname.md
git commit -m "docs: add yourname profile file"
git push origin members/yourname

# GitHub will print a URL in the terminal — click it to open the PR form!
```

## Stack
**Python 3.12** · **pandas** · **numpy** · **yfinance** · **ta** · **vectorbt** · **Streamlit** · **Dhan API**

---
*Last updated: Week 1 — README expands after each phase.*
