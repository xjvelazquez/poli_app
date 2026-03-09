# poli_app

Python web application that displays an automated San Diego County political snapshot. A background thread periodically scrapes county data and stores it; the home page always shows the most recent result.

## Prerequisites

- Python 3.10 or newer
- `pip` (comes with recent Python)

## Setup

PowerShell (Windows):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS / Linux (bash):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration (optional)

The app reads one environment variable:

- `SCRAPE_INTERVAL_SEC` — background snapshot interval in seconds (default: `3600`)

Set it in PowerShell:

```powershell
$env:SCRAPE_INTERVAL_SEC = "3600"
```

Or in bash:

```bash
export SCRAPE_INTERVAL_SEC=3600
```

## Run

Start the app:

```powershell
# (with venv activated)
python app.py
```

Visit http://127.0.0.1:5000 in your browser.

## Routes

| Route | Description |
|---|---|
| `/` | Latest background snapshot (supervisors, election tables) |
| `/history` | Log of all stored snapshots |
| `/history/<id>` | Detail view for a specific snapshot entry |

## Notes & next steps

- The first load may show "No snapshot available yet" until the background scraper completes its first run.
- For production use consider adding rate-limiting, HTTPS, persistent storage, and proper logging.
