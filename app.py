from flask import Flask, render_template, request, redirect, url_for, flash, Response
from scrapers import scrape_url
from storage import init_db, save_scrape, get_history, get_scrape_by_id, get_latest_by_url_prefix
from scrapers import scrape_county_political_snapshot, scrape_sdvote_results
import os
import threading
import time

# simple auth config
ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'pass')
SCRAPE_INTERVAL = int(os.environ.get('SCRAPE_INTERVAL_SEC', '3600'))

app = Flask(__name__)
app.secret_key = "dev-secret"


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    if not url:
        flash('Please provide a URL.')
        return redirect(url_for('index'))
    try:
        data = scrape_url(url)
    except Exception as e:
        flash(f'Error scraping URL: {e}')
        return redirect(url_for('index'))
    # persist to DB
    try:
        record_id = save_scrape(url, data)
    except Exception as e:
        flash(f'Error saving to DB: {e}')
        record_id = None
    return render_template('result.html', url=url, data=data, record_id=record_id)


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


@app.route('/political')
def political():
    # show a live snapshot (not persisted unless user saves)
    snapshot = scrape_county_political_snapshot()
    return render_template('political.html', snapshot=snapshot)


@app.route('/political/save', methods=['POST'])
def political_save():
    # simple HTTP Basic auth check
    auth = request.authorization
    if not auth or auth.username != ADMIN_USER or auth.password != ADMIN_PASS:
        return Response('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login"'})

    # Persist a short summary of the snapshot into scrapes DB
    snapshot = scrape_county_political_snapshot()
    title = 'San Diego political snapshot'
    # create a compact paragraph summary
    paragraphs = []
    sup_names = [s.get('name') for s in snapshot.get('supervisors', [])][:10]
    if sup_names:
        paragraphs.append('Supervisors: ' + ', '.join(sup_names))
    races = snapshot.get('election_results', {}).get('races', [])
    if races:
        paragraphs.append(f'Found {len(races)} election tables')

    data = {
        'title': title,
        'h1': '',
        'meta_description': 'Political snapshot for San Diego County',
        'paragraphs': paragraphs,
        'links': [],
    }
    try:
        save_scrape('political_snapshot', data)
        flash('Snapshot saved to history')
    except Exception as e:
        flash(f'Error saving snapshot: {e}')
    return redirect(url_for('history'))


@app.route('/political/cached')
def political_cached():
    # return the most recent auto snapshot saved by scheduler
    entry = get_latest_by_url_prefix('political_snapshot_auto')
    if not entry:
        flash('No cached snapshot available')
        return redirect(url_for('political'))
    # reconstruct snapshot minimal structure
    snapshot = {
        'supervisors': [],
        'election_results': {'races': []}
    }
    # put paragraphs into a simple snapshot view
    snapshot_summary = entry.get('paragraphs', [])
    return render_template('political.html', snapshot={'supervisors': [], 'election_results': {'races': []}, 'summary': snapshot_summary})


def _background_snapshot_loop(interval_seconds):
    while True:
        try:
            data = scrape_county_political_snapshot()
            title = 'Automated political snapshot'
            paragraphs = []
            sup_names = [s.get('name') for s in data.get('supervisors', [])][:10]
            if sup_names:
                paragraphs.append('Supervisors: ' + ', '.join(sup_names))
            races = data.get('election_results', {}).get('races', [])
            if races:
                paragraphs.append(f'Found {len(races)} election tables')
            record = {
                'title': title,
                'h1': '',
                'meta_description': 'Automated political snapshot',
                'paragraphs': paragraphs,
                'links': []
            }
            save_scrape('political_snapshot_auto', record)
        except Exception:
            pass
        time.sleep(interval_seconds)


def start_background_snapshot(interval_seconds=SCRAPE_INTERVAL):
    t = threading.Thread(target=_background_snapshot_loop, args=(interval_seconds,), daemon=True)
    t.start()


if __name__ == '__main__':
    init_db()
    # start background scheduler
    start_background_snapshot()
    app.run(debug=True)
