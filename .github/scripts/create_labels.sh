#!/bin/bash

# Phase Labels
gh label create "phase-0" --color "3FB950" --description "Onboarding (Week 1)"
gh label create "phase-1" --color "58A6FF" --description "Foundations (Weeks 2–4)"
gh label create "phase-2" --color "BC8CFF" --description "Data & Analysis (Weeks 5–7)"
gh label create "phase-3" --color "F0883E" --description "Strategy & Backtesting (Weeks 8–9)"
gh label create "phase-4" --color "FF7B9C" --description "Paper Trading (Weeks 10–11)"
gh label create "phase-5" --color "7EE787" --description "Ship It (Week 12)"

# Role Labels
gh label create "role:dev" --color "58A6FF" --description "Dev / Infra role task"
gh label create "role:quant" --color "F0883E" --description "Quant / Strategy role task"
gh label create "role:data" --color "BC8CFF" --description "Data Engineer role task"
gh label create "role:docs" --color "FF7B9C" --description "Analyst / Docs role task"
gh label create "role:co-lead" --color "7EE787" --description "Co-Lead role task"
gh label create "role:all" --color "E6EDF3" --description "Required from every team member"

# Type Labels
gh label create "bug" --color "F85149" --description "Something is broken"
gh label create "enhancement" --color "3FB950" --description "New feature or improvement"
gh label create "question" --color "58A6FF" --description "Needs clarification or discussion"
gh label create "documentation" --color "BC8CFF" --description "Documentation-only change"

# Status Labels
gh label create "blocked" --color "F85149" --description "Cannot proceed — waiting on something"
gh label create "in-review" --color "F0883E" --description "PR open and under review"
gh label create "good first issue" --color "7EE787" --description "Good entry point for new members"
gh label create "wont-fix" --color "8B949E" --description "Decided not to address this"
