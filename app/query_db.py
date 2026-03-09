"""
CLI tool to query the scrapes SQLite database.

Usage:
    python query_db.py list [--limit N]
    python query_db.py get <id>
    python query_db.py sql "<SQL statement>"
    python query_db.py latest

Examples:
    python query_db.py list
    python query_db.py list --limit 5
    python query_db.py get 3
    python query_db.py latest
    python query_db.py sql "SELECT id, title, created_at FROM scrapes ORDER BY id DESC LIMIT 10"
"""

import sys
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'scrapes.db'


def get_conn():
    if not DB_PATH.exists():
        print(f'[error] Database not found at {DB_PATH}')
        sys.exit(1)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def cmd_list(limit=20):
    conn = get_conn()
    rows = conn.execute(
        'SELECT id, url, title, created_at FROM scrapes ORDER BY id DESC LIMIT ?',
        (limit,)
    ).fetchall()
    conn.close()
    if not rows:
        print('No entries found.')
        return
    col_w = [4, 35, 35, 26]
    header = f"{'ID':<{col_w[0]}}  {'URL':<{col_w[1]}}  {'Title':<{col_w[2]}}  {'Created At':<{col_w[3]}}"
    print(header)
    print('-' * len(header))
    for r in rows:
        url = (r['url'] or '')[:col_w[1]]
        title = (r['title'] or '')[:col_w[2]]
        print(f"{r['id']:<{col_w[0]}}  {url:<{col_w[1]}}  {title:<{col_w[2]}}  {r['created_at']}")


def cmd_get(entry_id):
    conn = get_conn()
    row = conn.execute(
        'SELECT * FROM scrapes WHERE id = ?', (entry_id,)
    ).fetchone()
    conn.close()
    if not row:
        print(f'[error] No entry with id={entry_id}')
        return
    print(f"ID:          {row['id']}")
    print(f"URL:         {row['url']}")
    print(f"Title:       {row['title']}")
    print(f"H1:          {row['h1']}")
    print(f"Meta Desc:   {row['meta_description']}")
    print(f"Created At:  {row['created_at']}")
    paragraphs = json.loads(row['paragraphs']) if row['paragraphs'] else []
    print(f"\nParagraphs ({len(paragraphs)}):")
    for i, p in enumerate(paragraphs, 1):
        print(f"  {i}. {p}")
    links = json.loads(row['links']) if row['links'] else []
    print(f"\nLinks ({len(links)}):")
    for i, l in enumerate(links, 1):
        print(f"  {i}. {l.get('text', '')}  ->  {l.get('href', '')}")
    raw = json.loads(row['raw_data']) if row['raw_data'] else None
    if raw:
        print(f"\nRaw Data:")
        print(json.dumps(raw, indent=2))


def cmd_latest():
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM scrapes WHERE url LIKE 'political_snapshot_auto%' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if not row:
        print('No auto snapshot found.')
        return
    cmd_get(row['id'])


def cmd_sql(query):
    conn = get_conn()
    try:
        cursor = conn.execute(query)
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        print(f'[error] {e}')
        conn.close()
        return
    conn.close()
    if not rows:
        print('No results.')
        return
    keys = rows[0].keys()
    print('  '.join(f'{k}' for k in keys))
    print('-' * 60)
    for r in rows:
        print('  '.join(str(r[k]) if r[k] is not None else 'NULL' for k in keys))


def usage():
    print(__doc__)
    sys.exit(0)


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        usage()

    cmd = args[0].lower()

    if cmd == 'list':
        limit = 20
        if '--limit' in args:
            idx = args.index('--limit')
            try:
                limit = int(args[idx + 1])
            except (IndexError, ValueError):
                print('[error] --limit requires an integer value')
                sys.exit(1)
        cmd_list(limit)

    elif cmd == 'get':
        if len(args) < 2:
            print('[error] Usage: query_db.py get <id>')
            sys.exit(1)
        try:
            cmd_get(int(args[1]))
        except ValueError:
            print('[error] id must be an integer')
            sys.exit(1)

    elif cmd == 'latest':
        cmd_latest()

    elif cmd == 'sql':
        if len(args) < 2:
            print('[error] Usage: query_db.py sql "<SQL>"')
            sys.exit(1)
        cmd_sql(args[1])

    else:
        print(f'[error] Unknown command: {cmd}')
        usage()
