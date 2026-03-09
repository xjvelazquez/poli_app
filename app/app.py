from flask import Flask, render_template, redirect, url_for, flash
from storage import init_db, save_scrape, get_history, get_scrape_by_id, get_latest_by_url_prefix
from scrapers import scrape_county_political_snapshot, scrape_url
from officeholders import OFFICEHOLDERS
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
GOVT_SCRAPE_INTERVAL = int(os.environ.get('GOVT_SCRAPE_INTERVAL_SEC', str(7 * 24 * 3600)))

GOVERNMENT_BODIES = {
    'mayor': {
        'title': 'Mayor',
        'subtitle': 'Chief Executive of the City of San Diego',
        'description': 'Directly elected citywide. Strong-mayor system since 2006.',
        'facts': [
            'Manages day-to-day city operations',
            'Proposes the annual city budget',
            'Has veto power over City Council legislation',
            'Current mayor: Todd Gloria (elected 2020, re-elected 2024)',
        ],
        'scrape_url': 'https://www.sandiego.gov/mayor',
    },
    'city-council': {
        'title': 'City Council',
        'subtitle': 'San Diego City Council',
        'description': '9 members elected by district. Sets policy, approves the budget, and passes ordinances.',
        'facts': [
            '9 members representing Districts 1–9',
            '4-year terms with a 2-term limit',
            'Approves the annual city budget',
            'Passes city ordinances and resolutions',
        ],
        'scrape_url': 'https://www.sandiego.gov/city-clerk/elected',
    },
    'city-attorney': {
        'title': 'City Attorney',
        'subtitle': 'Office of the San Diego City Attorney',
        'description': 'Independently elected citywide. Provides legal counsel to the city and prosecutes misdemeanors.',
        'facts': [
            'Independently elected citywide',
            'Provides legal counsel to city departments and the City Council',
            'Prosecutes misdemeanor violations of city ordinances',
        ],
        'scrape_url': 'https://www.sandiego.gov/city-attorney',
    },
    'city-auditor': {
        'title': 'City Auditor',
        'subtitle': 'Office of the San Diego City Auditor',
        'description': 'Independently elected. Conducts performance and financial audits of city operations.',
        'facts': [
            'Independently elected citywide',
            'Conducts performance audits of city programs',
            'Conducts financial audits to ensure proper use of public funds',
            'Reports findings to the City Council and the public',
        ],
        'scrape_url': 'https://www.sandiego.gov/auditor',
    },
    'coo': {
        'title': 'City Chief Operating Officer',
        'subtitle': 'Office of the Chief Operating Officer',
        'description': 'Appointed by the Mayor. Oversees city departments operationally.',
        'facts': [
            'Appointed by and serves at the pleasure of the Mayor',
            'Oversees the day-to-day operations of city departments',
            'Coordinates implementation of the Mayor\'s policy priorities',
        ],
        'scrape_url': 'https://www.sandiego.gov/city-manager',
    },
    'county-board': {
        'title': 'County Board of Supervisors',
        'subtitle': 'San Diego County Board of Supervisors',
        'description': 'Governs San Diego County — separate from the City. 5 members representing county districts.',
        'facts': [
            '5 members, each representing a county supervisorial district',
            'Governs unincorporated county areas and provides county-wide services',
            'Oversees public health, social services, courts, and elections',
            'Separate from and independent of the City of San Diego government',
        ],
        'scrape_url': 'https://www.sandiegocounty.gov/content/sdc/general/bos.html',
    },
}

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-change-in-prod')


@app.route('/', methods=['GET'])
def index():
    entry = get_latest_by_url_prefix('political_snapshot_auto')
    if not entry:
        return render_template('index.html', snapshot=None, updated_at=None)
    snapshot = {
        'summary': entry.get('paragraphs', []),
    }
    return render_template('index.html', snapshot=snapshot, updated_at=entry.get('created_at'))


@app.route('/government/<slug>')
def government_body(slug):
    body = GOVERNMENT_BODIES.get(slug)
    if not body:
        flash('Government body not found.')
        return redirect(url_for('index'))
    entry = get_latest_by_url_prefix(f'government/{slug}')
    live_data = None
    if entry:
        live_data = {
            'paragraphs': entry.get('paragraphs', []),
            'updated_at': entry.get('created_at'),
        }
    officeholders = OFFICEHOLDERS.get(slug, [])
    return render_template('government.html', body=body, slug=slug, live_data=live_data, officeholders=officeholders)


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


def _background_govt_body_loop(interval_seconds):
    while True:
        for slug, body in GOVERNMENT_BODIES.items():
            log.info(f'Govt scraper: scraping {slug}...')
            try:
                data = scrape_url(body['scrape_url'], max_paragraphs=20)
                data['raw_data'] = {k: v for k, v in data.items() if k != 'raw_data'}
                save_scrape(f'government/{slug}', data)
                log.info(f'Govt scraper: saved {slug}')
            except Exception as e:
                log.error(f'Govt scraper failed for {slug}: {e}', exc_info=True)
        log.info(f'Govt scraper: sleeping {interval_seconds}s')
        time.sleep(interval_seconds)


def start_background_govt_scraper(interval_seconds=GOVT_SCRAPE_INTERVAL):
    t = threading.Thread(target=_background_govt_body_loop, args=(interval_seconds,), daemon=True)
    t.start()


if __name__ == '__main__':
    init_db()
    start_background_snapshot()
    start_background_govt_scraper()
    app.run(debug=True)
