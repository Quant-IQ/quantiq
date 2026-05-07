# Contributing to QuantIQ

## Before you start
1. Check the GitHub Issues board — is the task already assigned?
2. If not, create an Issue and assign it to yourself.
3. Pull latest main: `git pull origin main`

## Branch naming
`feature/description` | `fix/description` | `data/description`
`docs/description` | `backtest/description` | `members/your-name`

## Commit format
`type: short description` (max 50 chars, lowercase)
Types: `feat` `fix` `data` `docs` `test` `refactor` `chore`

## Pull Request rules
- Fill the PR template fully — every section
- Write "Closes #N" in the description
- Assign at least one reviewer
- Never merge your own PR
- Address all review comments before merging

## Never commit
`.env` files | API tokens | Hardcoded credentials | `logs/*.csv`

## Questions?
Post in Discord **#dev**. Tag **@co-lead** if blocked for more than 24 hours.