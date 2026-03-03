refactor: remove manual URL scraper, add political snapshot dashboard

- Removed manual URL scrape form, /scrape route, /political (live), /political/save,
  and /political/cached routes from app.py
- Removed ADMIN_USER/ADMIN_PASS config; scraper-bot User-Agent replaced with realistic
  Chrome browser headers to fix sandiegocounty.gov blocking/timeouts
- fetch_soup() timeout increased from 10s to 20s
- Default scrape interval changed from 3600s to 60s (still overridable via SCRAPE_INTERVAL_SEC)
- Home page (/) now displays the latest background auto-snapshot instead of a scrape form
- Added structured logging to background snapshot loop: start, success counts, warnings
  on empty results, and full stack traces on exceptions (replaces silent except: pass)
- Added raw_data column to scrapes table storing full JSON scrape payload
  (supervisors + election_results); init_db() auto-migrates existing databases via
  ALTER TABLE without data loss
- Added query_db.py CLI tool with four commands:
    list [--limit N]  — tabular summary of recent entries
    get <id>          — full detail including raw_data JSON
    latest            — shortcut for most recent auto-snapshot
    sql '<SQL>'       — run arbitrary SELECT against the database
- Added app/docs/query_db.md with full CLI reference, schema documentation,
  and useful SQL query examples
- Updated README: removed generic scraper description, curl examples, and
  ADMIN_USER/ADMIN_PASS config; added routes table and first-load note
- Updated templates: index.html rewritten as snapshot dashboard with last-updated
  timestamp; history.html and entry.html updated to match new context
