# poli_app

Simple Python web application that scrapes a provided URL and displays extracted data. It also includes a small political snapshot feature for San Diego County and a history view of saved scrapes.

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

The app reads a few environment variables:

- `ADMIN_USER` — admin username for saving political snapshots (default: `admin`)
- `ADMIN_PASS` — admin password for saving political snapshots (default: `pass`)
- `SCRAPE_INTERVAL_SEC` — background snapshot interval in seconds (default: `3600`)

Set them in PowerShell:

```powershell
$env:ADMIN_USER = "youruser"
$env:ADMIN_PASS = "yourpass"
$env:SCRAPE_INTERVAL_SEC = "3600"
```

Or in bash:

```bash
export ADMIN_USER=youruser
export ADMIN_PASS=yourpass
export SCRAPE_INTERVAL_SEC=3600
```

## Run

Start the app:

```powershell
# (with venv activated)
python app.py
```

Visit http://127.0.0.1:5000 in your browser.

## Usage

- Home page: paste a URL and click "Scrape" to extract and view content.
- History: visit `/history` to see saved scrapes.
- Political snapshot: visit `/political` for a live snapshot. To persist a snapshot, POST to `/political/save` with HTTP Basic auth using the admin credentials.

## Examples

Scrape a URL using `curl` (form POST):

```bash
curl -X POST -F "url=https://example.com" http://127.0.0.1:5000/scrape
```

Save a political snapshot (uses basic auth). Defaults are `admin:pass` unless you set env vars:

```bash
curl -u admin:pass -X POST http://127.0.0.1:5000/political/save
```

View the latest saved history in the browser at `/history`.

## Notes & next steps

- This project is a demo. When scraping third-party sites, respect `robots.txt` and the site's terms of service.
- For production use consider adding input validation, rate-limiting, persistent credentials management, HTTPS, and proper logging.

If you'd like, I can also add a short example script that posts a URL and prints the result.
Simple Python webapp that scrapes a provided URL and displays extracted data.

Setup (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run (PowerShell):

```powershell
python app.py
```

Open http://127.0.0.1:5000 in your browser, enter a URL, and click "Scrape".

Notes:
- This is a minimal demo. Respect website robots.txt and terms of service when scraping.
- For production use, add rate-limiting, caching, and error handling.
