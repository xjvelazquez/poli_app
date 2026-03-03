import sqlite3
import json
import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / 'scrapes.db'


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS scrapes (
            id INTEGER PRIMARY KEY,
            url TEXT,
            title TEXT,
            h1 TEXT,
            meta_description TEXT,
            paragraphs TEXT,
            links TEXT,
            raw_data TEXT,
            created_at TEXT
        )
        '''
    )
    # migrate existing databases that predate the raw_data column
    existing = {row[1] for row in c.execute('PRAGMA table_info(scrapes)')}
    if 'raw_data' not in existing:
        c.execute('ALTER TABLE scrapes ADD COLUMN raw_data TEXT')
    conn.commit()
    conn.close()


def save_scrape(url, data):
    conn = get_conn()
    c = conn.cursor()
    paragraphs_json = json.dumps(data.get('paragraphs', []), ensure_ascii=False)
    links_json = json.dumps(data.get('links', []), ensure_ascii=False)
    raw_data_json = json.dumps(data.get('raw_data'), ensure_ascii=False) if data.get('raw_data') is not None else None
    created_at = datetime.datetime.utcnow().isoformat()
    c.execute(
        'INSERT INTO scrapes (url, title, h1, meta_description, paragraphs, links, raw_data, created_at) VALUES (?,?,?,?,?,?,?,?)',
        (url, data.get('title'), data.get('h1'), data.get('meta_description'), paragraphs_json, links_json, raw_data_json, created_at),
    )
    conn.commit()
    rowid = c.lastrowid
    conn.close()
    return rowid


def get_history(limit=50):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, url, title, h1, meta_description, paragraphs, links, raw_data, created_at FROM scrapes ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    entries = []
    for r in rows:
        entries.append({
            'id': r[0],
            'url': r[1],
            'title': r[2],
            'h1': r[3],
            'meta_description': r[4],
            'paragraphs': json.loads(r[5]) if r[5] else [],
            'links': json.loads(r[6]) if r[6] else [],
            'raw_data': json.loads(r[7]) if r[7] else None,
            'created_at': r[8],
        })
    return entries


def get_scrape_by_id(item_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, url, title, h1, meta_description, paragraphs, links, raw_data, created_at FROM scrapes WHERE id = ?', (item_id,))
    r = c.fetchone()
    conn.close()
    if not r:
        return None
    return {
        'id': r[0],
        'url': r[1],
        'title': r[2],
        'h1': r[3],
        'meta_description': r[4],
        'paragraphs': json.loads(r[5]) if r[5] else [],
        'links': json.loads(r[6]) if r[6] else [],
        'raw_data': json.loads(r[7]) if r[7] else None,
        'created_at': r[8],
    }


def get_latest_by_url_prefix(prefix):
    """Return the most recent scrape row where url starts with prefix."""
    conn = get_conn()
    c = conn.cursor()
    like = f"{prefix}%"
    c.execute('SELECT id, url, title, h1, meta_description, paragraphs, links, raw_data, created_at FROM scrapes WHERE url LIKE ? ORDER BY id DESC LIMIT 1', (like,))
    r = c.fetchone()
    conn.close()
    if not r:
        return None
    return {
        'id': r[0],
        'url': r[1],
        'title': r[2],
        'h1': r[3],
        'meta_description': r[4],
        'paragraphs': json.loads(r[5]) if r[5] else [],
        'links': json.loads(r[6]) if r[6] else [],
        'raw_data': json.loads(r[7]) if r[7] else None,
        'created_at': r[8],
    }
