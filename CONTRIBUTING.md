# Contributing to QuantIQ

First off, thank you for contributing to QuantIQ! Git is how we collaborate without overwriting each other, and GitHub is where our work lives in the cloud.

## Quick Reference / TL;DR

**Before you start:**

1. Check the GitHub Issues board — is the task already assigned?
2. If not, create an Issue and assign it to yourself.
3. Pull latest main: `git pull origin main`

**Branch naming:** `feature/description` | `fix/description` | `data/description` | `docs/description` | `backtest/description` | `members/your-name`

**Commit format:** `type: short description` (max 50 chars, lowercase)
Types: `feat` `fix` `data` `docs` `test` `refactor` `chore`

**PR rules:** Fill template fully · Write "Closes #N" · Assign reviewer · Never merge your own PR · Address all comments before merging

**Never commit:** `.env` files | API tokens | Hardcoded credentials | `logs/*.csv`

**Questions?** Post in Discord **#dev**. Tag **@co-lead**/**@lead** if blocked for more than 24 hours.

---

## The Daily Workflow

Every piece of work follows this exact loop. Memorize it. There are no exceptions.

```bash
# Step 1 — Get the latest main
git checkout main
git pull origin main

# Step 2 — Create a branch for your work
git checkout -b feature/your-feature-name

# Step 3 — Edit files in VS Code, save them

# Step 4 — Stage your changes
git status                  # see what changed
git add path/to/file.py     # stage one file, OR
git add .                   # stage everything
git add -p                  # stage chunks interactively (recommended for mixed changes)

# Step 5 — Commit with a clear message
git commit -m "feat: add SMA-20 to data pipeline"

# Step 6 — Push your branch to GitHub
git push origin feature/your-feature-name

# Step 7 — Open a Pull Request on GitHub.com
```

---

## Branch Naming Strategy

`main` is sacred — always working, always reviewed. Never push directly to `main`. Every change starts as a branch.

| Prefix | When to Use | Example |
| --- | --- | --- |
| `feature/` | New functionality or module | `feature/sma-crossover-strategy` |
| `fix/` | Bug fix — something is broken | `fix/api-auth-token-expiry` |
| `data/` | Data pipeline or feed work | `data/nifty50-pipeline-refactor` |
| `docs/` | README, docstrings, comments only | `docs/readme-phase2-update` |
| `backtest/` | Backtesting scripts and experiments | `backtest/rsi-mean-reversion-v2` |
| `members/` | Your Week 1 personal file ONLY | `members/your-name` |

---

## Commit Message Standards

**Format:** `type: short description` (max 50 chars, lowercase, no full stop).

```text
type: short description

# Optional body — explain WHY, not WHAT (the diff already shows what)
Added EMA because SMA reacted too slowly during volatile sessions.
Closes #14
```

### Commit Types

* `feat`: New feature or function
* `fix`: Bug fix
* `data`: Data pipeline changes
* `docs`: Documentation only
* `test`: Adding or updating tests
* `refactor`: Code restructure, no behaviour change
* `chore`: Config, deps, .gitignore

### Good vs. Bad Commits

| Status | Example |
| --- | --- |
| ✅ **GOOD** | `feat: add SMA-20 and SMA-50 overlay to chart` |
| ❌ **BAD** | `update` |
| ✅ **GOOD** | `fix: handle KeyError when ticker has no NSE data` |
| ❌ **BAD** | `fixed stuff` |
| ✅ **GOOD** | `chore: pin pandas to 2.1.0 for vectorbt compat` |
| ❌ **BAD** | `asdfgh` |

---

## Pull Request Rules

Every change enters `main` through a PR. No exceptions, even for the Project Lead.

1. **Finish on your branch:** Code runs locally. Tested. No `print()` debugging left in.
2. **Sync with main first:** `git pull origin main` then `git merge main`. Resolve conflicts before pushing.
3. **Push your branch:** `git push origin feature/your-branch-name`.
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

### I want to undo my last commit (not yet pushed)

```bash
git reset --soft HEAD~1 # keeps your changes staged
git reset HEAD~1        # keeps changes unstaged
git reset --hard HEAD~1 # DISCARDS changes (careful!)
```
