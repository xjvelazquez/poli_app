# Backlog — San Diego Local Government App

> Solo project. Stories are written in BMAD format.
> Status: `todo` | `in-progress` | `done` | `blocked`

---

## How to Use

- Add new stories under the appropriate epic section below.
- Move items between status sections by updating the `status` field.
- For larger stories, create a dedicated file in `_bmad-output/implementation-artifacts/` and link it here.

---

## Epics

### 🏛️ Epic 1 — Government Information Display

| ID | Title | Status | Notes |
|----|-------|--------|-------|
| E1-001 | Display San Diego local government overview on home page | `done` | City Council, Mayor, Attorney, Auditor, COO, County Board, Key Facts |
| E1-002 | Add individual pages per government body (e.g. /mayor, /city-council) | `done` | `/government/<slug>` routes; shared template; weekly scraper; cards linked from home |
| E1-003 | Add current officeholder data (names, terms, contact) | `todo` | Could be static JSON or scraped |
| E1-004 | Add San Diego County Board of Supervisors detail page | `todo` | 5 districts, current supervisors |

---

### 🕷️ Epic 2 — Scrapers & Live Data

| ID | Title | Status | Notes |
|----|-------|--------|-------|
| E2-001 | Fix election races returning 0 results in background snapshot | `todo` | Background snapshot logs warning — investigate scraper |
| E2-002 | Scrape current City Council member roster | `todo` | sandiego.gov/city-clerk/elected |
| E2-003 | Scrape County Supervisors roster | `todo` | sandiegocounty.gov |
| E2-004 | Schedule and persist scraped officeholder data to DB | `todo` | Extend storage.py |

---

### 🖥️ Epic 3 — UI / UX

| ID | Title | Status | Notes |
|----|-------|--------|-------|
| E3-001 | Add favicon | `todo` | Currently returns 404 |
| E3-002 | Improve home page layout and styling | `in-progress` | Grid cards added; may need mobile responsiveness pass |
| E3-003 | Add navigation header/sidebar across all pages | `todo` | Currently only index has a History link |
| E3-004 | Make government cards linkable to detail pages | `todo` | Depends on E1-002 |

---

### 🗄️ Epic 4 — Infrastructure & Quality

| ID | Title | Status | Notes |
|----|-------|--------|-------|
| E4-001 | Add basic test coverage for scrapers.py | `todo` | |
| E4-002 | Add basic test coverage for storage.py | `todo` | |
| E4-003 | Externalize app secret key to environment variable | `done` | Uses `FLASK_SECRET_KEY` env var; falls back to dev value |
| E4-004 | Add proper error pages (404, 500) | `todo` | |

---

## Done Archive

| ID | Title | Completed |
|----|-------|-----------|
| E1-001 | Display San Diego local government overview on home page | 2026-03-08 |
| E4-003 | Externalize app secret key to environment variable | 2026-03-08 |
| E1-002 | Add individual pages per government body | 2026-03-08 |
