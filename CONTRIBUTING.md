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

## After Your PR Is Merged — Branch Cleanup

Once your PR is merged into `main`, clean up immediately. Stale local branches accumulate fast on a 9-person team and make `git branch` unreadable.

```bash
# Step 1 — Switch back to main
git checkout main

# Step 2 — Pull the merged changes (your work is now in here)
git pull origin main

# Step 3 — Delete your local branch (it's already in main, so this is safe)
git branch -d feature/your-feature-name
# Use -D (capital) only if git refuses -d and you are sure the branch is merged
git branch -D feature/your-feature-name

# Step 4 — Prune stale remote-tracking refs
# This removes entries like "origin/feature/your-feature-name" that no longer exist on GitHub
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
| `git checkout -b feature/name` | Create + switch to new branch |
| `git checkout main` | Switch to main branch |
| `git branch` | List all local branches |
| `git branch -d feature/name` | Delete a branch locally after merge |
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
