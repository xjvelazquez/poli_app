from flask import Flask, render_template, redirect, url_for, flash
from storage import init_db, save_scrape, get_history, get_scrape_by_id, get_latest_by_url_prefix
from scrapers import scrape_county_political_snapshot
import os
import threading
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
log = logging.getLogger(__name__)

SCRAPE_INTERVAL = int(os.environ.get('SCRAPE_INTERVAL_SEC', '60'))

app = Flask(__name__)
app.secret_key = "dev-secret"


@app.route('/', methods=['GET'])
def index():
    entry = get_latest_by_url_prefix('political_snapshot_auto')
    if not entry:
        return render_template('index.html', snapshot=None, updated_at=None)
    snapshot = {
        'summary': entry.get('paragraphs', []),
    }
    return render_template('index.html', snapshot=snapshot, updated_at=entry.get('created_at'))


@app.route('/history')
def history():
    entries = get_history(100)
    return render_template('history.html', entries=entries)


@app.route('/history/<int:item_id>')
def history_entry(item_id):
    entry = get_scrape_by_id(item_id)
    if not entry:
        flash('Entry not found.')
        return redirect(url_for('history'))
    return render_template('entry.html', entry=entry)


def _background_snapshot_loop(interval_seconds):
    while True:
        log.info('Background snapshot: starting scrape...')
        try:
            data = scrape_county_political_snapshot()
            title = 'Automated political snapshot'
            paragraphs = []
            sup_names = [s.get('name') for s in data.get('supervisors', [])][:10]
            if sup_names:
                paragraphs.append('Supervisors: ' + ', '.join(sup_names))
            else:
                log.warning('Background snapshot: no supervisors returned')
            races = data.get('election_results', {}).get('races', [])
            if races:
                paragraphs.append(f'Found {len(races)} election tables')
            else:
                log.warning('Background snapshot: no election races returned')
            record = {
                'title': title,
                'h1': '',
                'meta_description': 'Automated political snapshot',
                'paragraphs': paragraphs,
                'links': [],
                'raw_data': data,
            }
            save_scrape('political_snapshot_auto', record)
            log.info(f'Background snapshot: saved — supervisors={len(sup_names)}, races={len(races)}')
        except Exception as e:
            log.error(f'Background snapshot failed: {e}', exc_info=True)
        log.info(f'Background snapshot: sleeping {interval_seconds}s')
        time.sleep(interval_seconds)


def start_background_snapshot(interval_seconds=SCRAPE_INTERVAL):
    t = threading.Thread(target=_background_snapshot_loop, args=(interval_seconds,), daemon=True)
    t.start()


if __name__ == '__main__':
    init_db()
    # start background scheduler
    start_background_snapshot()
    app.run(debug=True)
