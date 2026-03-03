# query_db CLI

Command-line tool for inspecting the `scrapes.db` SQLite database that stores all political snapshot data collected by the background scraper.

## Requirements

Must be run from inside the `app/` directory with the virtual environment's Python:

```cmd
cd app
.venv\Scripts\python.exe query_db.py <command> [options]
```

If `python` is already on your PATH and pointing to the venv:

```cmd
python query_db.py <command> [options]
```

---

## Commands

### `list`

Lists the most recent scrape entries in a summary table.

```
python query_db.py list [--limit N]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--limit N` | Number of entries to show | `20` |

**Output columns:** `ID`, `URL`, `Title`, `Created At`

**Examples:**

```cmd
python query_db.py list
python query_db.py list --limit 5
```

**Sample output:**

```
ID    URL                                  Title                                Created At
--------------------------------------------------------------------------------------------
86    political_snapshot_auto              Automated political snapshot         2026-03-03T06:17:22
85    political_snapshot_auto              Automated political snapshot         2026-03-03T06:16:15
```

---

### `get`

Shows full detail for a single entry by its ID, including paragraphs, links, and the full raw scraped data.

```
python query_db.py get <id>
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `<id>` | The integer ID of the entry (from `list`) |

**Example:**

```cmd
python query_db.py get 86
```

**Sample output:**

```
ID:          86
URL:         political_snapshot_auto
Title:       Automated political snapshot
H1:
Meta Desc:   Automated political snapshot
Created At:  2026-03-03T06:17:22.369310

Paragraphs (2):
  1. Supervisors: District 1 - Paloma Aguirre, District 2 - Joel Anderson, ...
  2. Found 0 election tables

Links (0):

Raw Data:
{
  "supervisors": [
    { "name": "District 1 - Paloma Aguirre", "title": "", "link": "..." },
    ...
  ],
  "election_results": {
    "races": []
  }
}
```

> **Note:** `raw_data` is only present on entries saved after the `raw_data` column was added. Older rows will show no Raw Data section.

---

### `latest`

Shortcut that shows the full detail of the most recently saved auto-snapshot. Equivalent to finding the highest ID with `url = political_snapshot_auto` and running `get` on it.

```
python query_db.py latest
```

**Example:**

```cmd
python query_db.py latest
```

---

### `sql`

Runs an arbitrary SQL `SELECT` statement directly against the database and prints the results as a plain table.

```
python query_db.py sql "<SQL statement>"
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `"<SQL statement>"` | Any valid SQLite SELECT statement (wrap in quotes) |

**Examples:**

```cmd
python query_db.py sql "SELECT id, title, created_at FROM scrapes ORDER BY id DESC LIMIT 10"
python query_db.py sql "SELECT COUNT(*) FROM scrapes"
python query_db.py sql "SELECT id, url FROM scrapes WHERE url LIKE 'political%'"
```

**Sample output:**

```
id  title                         created_at
------------------------------------------------------------
86  Automated political snapshot  2026-03-03T06:17:22.369310
85  Automated political snapshot  2026-03-03T06:16:15.163720
```

---

## Database Schema

The `scrapes` table contains all saved snapshots:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-incrementing primary key |
| `url` | TEXT | Source identifier (`political_snapshot_auto` for background scrapes) |
| `title` | TEXT | Entry title |
| `h1` | TEXT | H1 heading extracted from the page |
| `meta_description` | TEXT | Meta description or summary |
| `paragraphs` | TEXT | JSON array of summary paragraph strings |
| `links` | TEXT | JSON array of `{"href": ..., "text": ...}` objects |
| `raw_data` | TEXT | Full JSON blob of the scraped data (supervisors + election results) |
| `created_at` | TEXT | UTC timestamp in ISO 8601 format |

### Useful raw SQL queries

Count all entries:
```sql
SELECT COUNT(*) FROM scrapes;
```

Find entries from a specific date:
```sql
SELECT id, title, created_at FROM scrapes WHERE created_at LIKE '2026-03-03%';
```

View raw supervisor data from the latest snapshot:
```sql
SELECT raw_data FROM scrapes WHERE url LIKE 'political_snapshot_auto%' ORDER BY id DESC LIMIT 1;
```
