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
