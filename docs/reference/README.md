# QuantIQ Master Reference Binder

**File:** `QuantIQ-Master-Reference-Doc.pdf`
**Version:** 1.0
**Date:** 2026-05-19
**Pages:** ~311 KB · est. 320–430 printed pages
**Owner:** RS (Project Lead)

A print-ready A4 reference binder covering every tool, standard, and regulation used in QuantIQ. Read the relevant module before writing code that touches that area.

---

## Module Index

| # | Module | Contents | Est. Pages |
| --- | --- | --- | --- |
| 0 | Master Index & Usage Guide | TOC, how to use the binder, quick-find tables, colour coding legend | 8–12 |
| 1 | DhanHQ v2 — Broker API | Auth, orders, portfolio, market quote, option chain, historical data, WebSocket, rate limits, releases | 60–80 |
| 2 | Python Data Stack | pandas quickstart, numpy quickstart, yfinance complete reference | 40–50 |
| 3 | Technical Analysis — `ta` library | All indicators, parameters, examples, VWAP workaround | 25–35 |
| 4 | Backtesting — vectorbt | Getting started, Portfolio API, signals, indicators, plotting | 40–50 |
| 5 | Dashboard — Streamlit | Core API, widgets, secrets, layouts, deployment | 35–45 |
| 6 | Charting — Plotly Python | Express, graph_objects, figure reference, common chart types | 30–40 |
| 7 | Python Standards | PEP 8, PEP 257, PEP 484, Google Style Guide (docstrings), logging | 30–40 |
| 8 | Version Control & DevOps | Conventional Commits, SemVer, Git essentials, GitHub Actions, branch protection | 20–30 |
| 9 | Regulatory — SEBI & NSE | Feb 2025 circular full text, Sept 2025 extension, NSE technical standards, compliance checklist | 20–30 |
| 10 | Environment & Tooling | python-dotenv, pip/venv, requirements pinning, `.gitignore` patterns | 10–15 |

---

## Per-Module Structure

Each module contains:

* Cover page (title, module number, version date, page count)
* Module-level TOC
* Quick reference card (1–2 pages cheat-sheet)
* Full content with consistent section hierarchy
* Constraint callouts in shaded boxes (e.g. "10 orders/sec hard limit")
* Code examples in monospace blocks
* Back cover with "see also" cross-references to other modules

---

## Regenerating

To produce an updated binder, open a Claude Code session and run:

```text
/pdf — regenerate QuantIQ-Master-Reference-Doc.pdf from CLAUDE.md + CONTRIBUTING.md
```

Then replace the PDF in this folder and update the **Version** and **Date** fields above.

---

## Related Files

* [`CLAUDE.md`](../../CLAUDE.md) — §20 External Documentation & Constraints (authoritative URL list)
* [`CONTRIBUTING.md`](../../CONTRIBUTING.md) — Reference Documentation section (contributor-facing link table)
* [`docs/architecture.md`](../architecture.md) — Live system architecture doc
