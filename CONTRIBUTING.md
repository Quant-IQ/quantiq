# Contributing to QuantIQ

First off, thank you for contributing to QuantIQ! Git is how we collaborate without overwriting each other, and GitHub is where our work lives in the cloud.

## Quick Reference / TL;DR

**Before you start:**

1. Check the GitHub Issues board — is the task already assigned?
2. If not, create an Issue and assign it to yourself.
3. Pull latest main: `git pull origin main`

**Branch naming:** `feat(scope)/description` | `fix(scope)/description` | `data(scope)/description` | `docs/description` | `backtest/description`

**Commit format:** `type(scope): short description` (max 72 chars, lowercase)
Types: `feat` `fix` `docs` `style` `refactor` `test` `build` `chore`
Scopes: `data` `broker` `strategy` `backtest` `dashboard` `bot`

**PR rules:** Fill template fully · Write "Closes #N" · Assign reviewer · Never merge your own PR · Address all comments before merging

**Never commit:** `.env` files | API tokens | Hardcoded credentials | `logs/*.csv`

**Questions?** Post in Discord **#dev**. Tag **@co-lead**/**@lead** if blocked for more than 24 hours.

---

## File Placement

Put work in the right directory from the start — wrong location = PR blocked.

| Phase | What | Where | File pattern |
| ----- | ---- | ------ | ------------ |
| 3 | Strategy backtest | `backtest/` | `strategy_v1.ipynb` |
| 3+ | Production data pipeline | `src/data/` | `fetch.py`, `indicators.py`, `validate.py` |
| 3+ | Signal generation | `src/strategy/` | `base.py`, `sma_crossover.py`, `signals.py` |
| 4 | Live bot + order management | `src/execution/` | `dhan_client.py`, `order_manager.py`, etc. |
| 5 | Dashboard | `src/dashboard/` | `app.py` |
| All | Trade signal log (gitignored) | `logs/` | `trades.csv` |

`scripts/`, `notebooks/`, `members/` (Phase 0–2 scaffolding) removed once no longer needed for the app to function. All new code goes in `src/`.

---

## The Daily Workflow

Every piece of work follows this exact loop. Memorize it. There are no exceptions.

```bash
# Step 1 — Get the latest main
git checkout main
git pull origin main

# Step 2 — Create a branch for your work
git checkout -b feat(scope)/your-feature-name

# Step 3 — Edit files in VS Code, save them

# Step 4 — Stage your changes
git status                  # see what changed
git add path/to/file.py     # stage one file, OR
git add .                   # stage everything
git add -p                  # stage chunks interactively (recommended for mixed changes)

# Step 5 — Commit with a clear message
git commit -m "feat(data): add SMA-20 to data pipeline"

# Step 6 — Push your branch to GitHub
git push origin feat(scope)/your-feature-name

# Step 7 — Open a Pull Request on GitHub.com
```

---

## Branch Naming Strategy

`main` is sacred — always working, always reviewed. Never push directly to `main`. Every change starts as a branch.

| Prefix | When to Use | Example |
| --- | --- | --- |
| `feat(scope)/` | New functionality or module | `feat(strategy)/sma-crossover` |
| `fix(scope)/` | Bug fix — something is broken | `fix(broker)/api-auth-token-expiry` |
| `data(scope)/` | Data pipeline or feed work | `data(pipeline)/nifty50-refactor` |
| `docs/` | README, docstrings, comments only | `docs/readme-phase3-update` |
| `backtest/` | Backtesting scripts and experiments | `backtest/rsi-mean-reversion-v2` |

---

## Commit Message Standards

Follows [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).

**Format:** `type(scope): short description` (max 72 chars, lowercase, no full stop).

```text
type(scope): short description

# Optional body — explain WHY, not WHAT (the diff already shows what)
Added EMA because SMA reacted too slowly during volatile sessions.
Closes #14
```

### Commit Types

* `feat`: New feature or function
* `fix`: Bug fix
* `docs`: Documentation only
* `style`: Formatting, no logic change
* `refactor`: Code restructure, no behaviour change
* `test`: Adding or updating tests
* `build`: Dependency or build system changes
* `chore`: Config, .gitignore, maintenance

### Scopes

Use one of these scopes to show which area is affected:
`data` | `broker` | `strategy` | `backtest` | `dashboard` | `bot`

Omit scope only for repo-wide changes (e.g. `docs: update README`).

### Good vs. Bad Commits

| Status | Example |
| --- | --- |
| ✅ **GOOD** | `feat(strategy): add SMA-20 and SMA-50 overlay to chart` |
| ❌ **BAD** | `update` |
| ✅ **GOOD** | `fix(data): handle KeyError when ticker has no NSE data` |
| ❌ **BAD** | `fixed stuff` |
| ✅ **GOOD** | `chore: pin pandas to 2.1.0 for vectorbt compat` |
| ❌ **BAD** | `asdfgh` |

---

## Pull Request Rules

Every change enters `main` through a PR. No exceptions, even for the Project Lead.

1. **Finish on your branch:** Code runs locally. Tested. No `print()` debugging left in.
2. **Sync with main first:** `git pull origin main` then `git merge main`. Resolve conflicts before pushing.
3. **Push your branch:** `git push origin feat(scope)/your-branch-name`.
4. **Fill the PR description:** Use the auto-loaded template. Fill every section. Write "Closes #N" to link your issue.
5. **Assign a reviewer:** Right sidebar → Reviewers → pick a teammate. Never leave it blank.
6. **Post in #dev on Discord:** "PR #14 up — needs 1 review." Then leave it alone.
7. **Address feedback:** Push fixes to the same branch — the PR auto-updates. Reply "Done" to comments.
8. **Reviewer merges:** The reviewer (NOT you) clicks Merge using **Squash and merge**.

> **⚠️ NEVER MERGE YOUR OWN PR**
> Branch protection enforces this. The reviewer is the merger. Always.

---

## Code Review Standards

Reviews must be posted within 48 hours of being assigned.

### As a Reviewer

* Does it do what the PR description says?
* Does it break any existing functionality?
* Are there docstrings on every new function?
* Are there any hardcoded API tokens or paths?
* Are variable names clear and descriptive?
* Could this be written more simply?
* Are edge cases handled? (empty DataFrame, NaN, API errors)
* Does the PR description link an Issue with "Closes #N"?
* Are there any obvious test cases missing?
* Did the author confirm the code runs locally?
* **Be actionable:** Instead of "This is wrong," say "This will crash if df is empty. Add: `if df.empty: return None`".
* **Use Nit:** Prefix non-blocking cosmetic suggestions with "Nit:" (e.g., "Nit: rename 'x' to 'closing_price'"). Author can ignore.

### As an Author

* Read every comment — all of them.
* Do not take technical feedback personally.
* Reply "Done" even to small fixes so reviewers know it was addressed.
* Push fixes to the same branch — the PR auto-updates.
* Never force-push after a review has started.
* If you disagree, explain with facts, not opinion.
* Re-request review after pushing substantial changes.
* Resolve every conversation before merging.
* Do not mark threads resolved yourself unless the fix is trivial.

---

## After Your PR Is Merged — Branch Cleanup

Once your PR is merged into `main`, clean up immediately. Stale local branches accumulate fast on a 9-person team and make `git branch` unreadable.

```bash
# Step 1 — Switch back to main
git checkout main

# Step 2 — Pull the merged changes (your work is now in here)
git pull origin main

# Step 3 — Delete your local branch (it's already in main, so this is safe)
git branch -d feat(scope)/your-feature-name
# Use -D (capital) only if git refuses -d and you are sure the branch is merged
git branch -D feat(scope)/your-feature-name

# Step 4 — Prune stale remote-tracking refs
# This removes entries like "origin/feat(scope)/your-feature-name" that no longer exist on GitHub
git fetch --prune

# Step 5 — Verify your branch is gone
git branch        # local branches
git branch -r     # remote-tracking branches — your branch should not appear
```

### See All Stale Branches at Once

```bash
# Branches already merged into main (safe to delete)
git branch --merged main

# Remote branches that have been deleted on GitHub but still tracked locally
git remote prune origin --dry-run
```

### One-Liner Full Cleanup (run after any merge)

```bash
git checkout main && git pull origin main && git fetch --prune
```

> **Rule:** Delete your branch the same day your PR merges. Do not let merged branches sit around — it creates confusion about what is active work.

---

## Troubleshooting & Common Scenarios

### I committed to the wrong branch

```bash
git log --oneline -1             # copy the commit hash
git reset --soft HEAD~1          # undo the commit, keep changes
git stash                        # shelve the changes
git checkout correct-branch      # switch to the right branch
git stash pop                    # restore changes
git add . && git commit -m "..." # commit on the correct branch
```

### I need to update my branch with latest main

```bash
git checkout main
git pull origin main
git checkout your-branch
git merge main
# Resolve any conflicts, then:
git push origin your-branch
```

### I have merge conflicts

```bash
git status # lists conflicted files
# Open each in VS Code — choose Accept Current/Incoming or merge manually
git add <resolved-file>
git commit # completes the merge
```

### I committed a token / secret by mistake

DO NOT just delete it — it is still in the git history.

1. Rotate/revoke the token IMMEDIATELY in your platform settings.
2. Remove from current code:

```bash
git rm --cached .env  # untrack the file
echo ".env" >> .gitignore
git commit -m "chore: remove .env from tracking"
```

For a full history scrub, contact the Project Lead.

### My branch is far behind main (lots of conflicts expected)

```bash
# Interactive rebase onto latest main — replays your commits on top cleanly
git checkout main
git pull origin main
git checkout your-branch
git rebase main
# Resolve conflicts per commit if they appear:
#   git add <resolved-file>
#   git rebase --continue
# To abort and go back to how things were:
#   git rebase --abort
git push --force-with-lease origin your-branch  # safe force-push — only pushes if no one else pushed
```

> Use `--force-with-lease` over `--force` when you must force-push. It refuses if the remote has changes you haven't seen, preventing accidental overwrites.

### I want to undo my last commit (not yet pushed)

```bash
git reset --soft HEAD~1 # keeps your changes staged
git reset HEAD~1        # keeps changes unstaged
git reset --hard HEAD~1 # DISCARDS changes (careful!)
```

### I need to undo a commit I already pushed

```bash
git revert <commit-hash>   # creates a new commit that undoes the target commit
git push origin your-branch
```

> Use `git revert` over `git reset --hard` for pushed commits — it adds an undo commit rather than rewriting history, which is safe for shared branches.

---

## Essential Git Command Reference

### Setup & Clone

| Command | What it does |
| --- | --- |
| `git clone <url>` | Download a repo to your machine |
| `git clone <url> --branch main` | Clone a specific branch |
| `git remote -v` | Show where local repo points to |
| `git config --global user.email "x"` | Set your email for commits |
| `git config --global user.name "x"` | Set your name for commits |

### Daily Workflow

| Command | What it does |
| --- | --- |
| `git status` | See what changed since last commit |
| `git diff` | See unstaged changes line by line |
| `git diff --staged` | See what is staged ready to commit |
| `git add <file>` | Stage one specific file |
| `git add .` | Stage all changed files |
| `git add -p` | Stage chunks interactively (recommended) |
| `git commit -m "type: msg"` | Commit staged changes |
| `git commit --amend` | Edit the most recent commit message |
| `git push origin branch-name` | Upload branch to GitHub |
| `git pull origin main` | Fetch + merge latest main into current |

### Branching

| Command | What it does |
| --- | --- |
| `git checkout -b feat(scope)/name` | Create + switch to new branch |
| `git checkout main` | Switch to main branch |
| `git branch` | List all local branches |
| `git branch -d feat(scope)/name` | Delete a branch locally after merge |
| `git merge main` | Merge latest main into current branch |

### History & Undo

| Command | What it does |
| --- | --- |
| `git log --oneline` | Compact commit history |
| `git log --oneline --graph` | Branch + merge visualisation |
| `git show <commit-hash>` | See exactly what a commit changed |
| `git stash` | Temporarily shelve uncommitted changes |
| `git stash pop` | Restore stashed changes |
| `git restore <file>` | Discard uncommitted changes |
| `git revert <commit>` | Undo a commit safely (creates new commit) |

### Collaboration

| Command | What it does |
| --- | --- |
| `git fetch origin` | Download remote changes without merging |
| `git blame <file>` | See who last changed each line |
| `git shortlog -sn` | Summary: who made how many commits |

---

## Reference Documentation

Canonical docs for every tool, standard, and regulation used in QuantIQ. Read the relevant section before submitting PRs that touch those areas.

---

### Broker API

| Resource | URL |
| --- | --- |
| DhanHQ API Docs v2 (primary) | <https://dhanhq.co/docs/v2/> |
| DhanHQ Orders & Rate Limits | <https://dhanhq.co/docs/v2/orders/> |
| DhanHQ Market Quote / LTP | <https://dhanhq.co/docs/v2/market-quote/> |
| DhanHQ Option Chain | <https://dhanhq.co/docs/v2/option-chain/> |
| DhanHQ Python SDK (GitHub) | <https://github.com/dhan-oss/DhanHQ-py> |
| DhanHQ SDK README | <https://github.com/dhan-oss/DhanHQ-py/blob/main/README.md> |
| DhanHQ SDK Releases (breaking changes) | <https://github.com/dhan-oss/DhanHQ-py/releases> |
| Dhan API Rate Limit FAQ | <https://dhan.co/support/platforms/dhanhq-api/how-many-orders-can-i-placed-using-dhan-api/> |
| NSE Market Data Portal | <https://www.nseindia.com/market-data/live-equity-market> |

> **Hard constraints:**
>
> * Access tokens expire every **24 hours** (SEBI mandate). Regenerate daily before 9:15 AM IST.
> * Order rate limit: **≤10 orders/sec/exchange/client**. Exceeding this requires NSE algo registration.
> * Pin SDK version: `dhanhq==2.1.x` in `requirements.txt`. Do not auto-upgrade — v2.2.0 contains breaking changes.

---

### Python Libraries

| Library | Docs | GitHub | PyPI |
| --- | --- | --- | --- |
| pandas | <https://pandas.pydata.org/docs/> | <https://github.com/pandas-dev/pandas> | <https://pypi.org/project/pandas/> |
| numpy | <https://numpy.org/doc/stable/> | <https://github.com/numpy/numpy> | <https://pypi.org/project/numpy/> |
| yfinance | <https://ranaroussi.github.io/yfinance/> | <https://github.com/ranaroussi/yfinance> | <https://pypi.org/project/yfinance/> |
| ta (indicators) | <https://technical-analysis-library-in-python.readthedocs.io/en/latest/> | <https://github.com/bukosabino/ta> | <https://pypi.org/project/ta/> |
| vectorbt (backtesting) | <https://vectorbt.dev/> | <https://github.com/polakowo/vectorbt> | <https://pypi.org/project/vectorbt/> |
| python-dotenv | <https://github.com/theskumar/python-dotenv> | <https://github.com/theskumar/python-dotenv> | <https://pypi.org/project/python-dotenv/> |
| streamlit | <https://docs.streamlit.io/> | <https://github.com/streamlit/streamlit> | <https://pypi.org/project/streamlit/> |
| plotly | <https://plotly.com/python/> | <https://github.com/plotly/plotly.py> | <https://pypi.org/project/plotly/> |

> **Known issues contributors must read:**
>
> * `yfinance` + NSE: all tickers **must** be suffixed `.NS` (e.g. `RELIANCE.NS`). Unsuffixed tickers silently return US equities. See [issue #825](https://github.com/ranaroussi/yfinance/issues/825).
> * `ta` library has **no built-in daily VWAP**. Implement manually: `(Volume * Typical_Price).cumsum() / Volume.cumsum()`.
> * `vectorbt` open-source is `0.28.x` — pin `vectorbt==0.28.2`. Do NOT write `vectorbt>=1.0` (that is the paid VectorBT PRO product).
> * Python version: pin `>=3.11,<3.13` for stable Numba/vectorbt wheel compatibility.

---

### Code Style & Standards

| Standard | URL |
| --- | --- |
| PEP 8 — Style Guide | <https://peps.python.org/pep-0008/> |
| PEP 257 — Docstring Conventions | <https://peps.python.org/pep-0257/> |
| PEP 484 — Type Hints | <https://peps.python.org/pep-0484/> |
| Google Python Style Guide (docstrings) | <https://google.github.io/styleguide/pyguide.html> |
| Python `logging` module | <https://docs.python.org/3/library/logging.html> |
| Logging HOWTO | <https://docs.python.org/3/howto/logging.html> |

> QuantIQ uses Google-style docstrings (`Args:`, `Returns:`, `Raises:`). See §3.8 of the Google Style Guide.

---

### Version Control & Git

| Resource | URL |
| --- | --- |
| Conventional Commits v1.0.0 | <https://www.conventionalcommits.org/en/v1.0.0/> |
| Semantic Versioning | <https://semver.org/> |
| Git Official Docs | <https://git-scm.com/doc> |
| Pro Git Book (free) | <https://git-scm.com/book/en/v2> |
| GitHub Docs | <https://docs.github.com/> |
| GitHub Actions | <https://docs.github.com/en/actions> |
| GitHub Branch Protection | <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches> |
| Learn Git Branching (interactive) | <https://learngitbranching.js.org/> |

---

### Regulatory Reference (India)

> **All contributors must read the Feb 2025 SEBI circular before working on the Phase 4 trading bot.**

| Document | URL | Date |
| --- | --- | --- |
| SEBI: Safer Participation of Retail Investors in Algo Trading | <https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html> | 4 Feb 2025 |
| SEBI: Extension of implementation timeline | <https://www.sebi.gov.in/legal/circulars/sep-2025/extension-of-timeline-for-implementation-of-sebi-circular-dated-february-04-2025-on-safer-participation-of-retail-investors-in-algorithmic-trading-_96979.html> | Sep 2025 |
| SEBI: Discussion Paper (precursor) | <https://www.sebi.gov.in/reports-and-statistics/reports/dec-2024/participation-of-retail-investors-in-algorithmic-trading_89837.html> | Dec 2024 |
| SEBI Circular Index (algo trading) | <https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListingAll=yes&search=Algorithmic> | Live |
| NSE Exchange Circulars | <https://www.nseindia.com/resources/exchange-communication-circulars#href-0> | Live |

---

### Learning Resources

| Resource | URL |
| --- | --- |
| Zerodha Varsity (all modules) | <https://zerodha.com/varsity/modules/> |
| Varsity — Technical Analysis | <https://zerodha.com/varsity/module/technical-analysis/> |
| CS50P — Harvard Python (free) | <https://cs50.harvard.edu/python/> |
| QuantInsti Blog | <https://blog.quantinsti.com/> |
| Real Python — REST APIs | <https://realpython.com/api-integration-in-python/> |
| Investopedia — Technical Analysis | <https://www.investopedia.com/technical-analysis-4689657> |
| freeCodeCamp Git Crash Course | <https://www.youtube.com/watch?v=mAFoROnOfHs> |
| Google Technical Writing One | <https://developers.google.com/tech-writing/one> |
