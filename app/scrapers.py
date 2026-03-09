import re
import json
import requests
from bs4 import BeautifulSoup


def scrape_url(url, max_paragraphs=10):
    resp = requests.get(url, timeout=10, headers={'User-Agent': 'scraper-bot/1.0'})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    title = ''
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    h1 = soup.find('h1')
    h1_text = h1.get_text(strip=True) if h1 else ''

    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')][:max_paragraphs]

    links = []
    for a in soup.find_all('a', href=True)[:20]:
        href = a['href']
        text = a.get_text(strip=True)
        links.append({'href': href, 'text': text})

    meta_desc = ''
    meta = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
    if meta and meta.get('content'):
        meta_desc = meta['content'].strip()

    return {
        'title': title,
        'h1': h1_text,
        'meta_description': meta_desc,
        'paragraphs': paragraphs,
        'links': links,
    }


BROWSER_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/122.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def fetch_soup(url, timeout=20):
    """Fetch URL and return BeautifulSoup object (raises on HTTP errors)."""
    resp = requests.get(url, timeout=timeout, headers=BROWSER_HEADERS)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, 'html.parser')


def scrape_people_list(url, container_selector='body', name_selector='h3, h2, .name, a',
                      title_selector=None, link_selector='a'):
    """Generic helper: given a container selector, extract person name, title and link.

    Returns a list of dicts: {'name':..., 'title':..., 'link':...}.
    """
    soup = fetch_soup(url)
    containers = soup.select(container_selector)
    results = []
    for c in containers:
        name_elem = c.select_one(name_selector)
        if not name_elem:
            # try to find any strong or bold name inside
            name_elem = c.select_one('strong, b')
        if not name_elem:
            continue
        name = name_elem.get_text(strip=True)
        title = ''
        if title_selector:
            t = c.select_one(title_selector)
            if t:
                title = t.get_text(strip=True)
        link = ''
        l = c.select_one(link_selector)
        if l and l.has_attr('href'):
            link = l['href']
        results.append({'name': name, 'title': title, 'link': link})
    return results


def get_county_supervisors(url=None):
    """Try to extract San Diego County supervisors from a page.

    If `url` is None a best-guess County page is used. This function uses a few
    heuristic selectors and returns an array of {'name','title','link'}.
    """
    if not url:
        url = 'https://www.sandiegocounty.gov/content/sdc/general/bos.html'

    # candidate container selectors to try in order (heuristics)
    candidates = [
        ('.supervisor, .supervisors, .member, .board-member', 'h3, h2, .name, a', '.title', 'a'),
        ('section.people, .people, .staff-list', 'h3, h2, a', '.role, .title', 'a'),
        ('table tr', 'td:first-child, a, strong', 'td:nth-child(2)', 'a'),
        ('article, main, .content', 'h3, h2, a', None, 'a'),
    ]

    for container, name_sel, title_sel, link_sel in candidates:
        try:
            items = scrape_people_list(url, container_selector=container,
                                      name_selector=name_sel,
                                      title_selector=title_sel,
                                      link_selector=link_sel)
            if items:
                return items
        except Exception:
            # try next heuristic
            continue

    # as a fallback, try to extract any links with 'supervisor' in text
    try:
        soup = fetch_soup(url)
        found = []
        for a in soup.find_all('a', href=True):
            text = a.get_text(strip=True)
            if 'supervisor' in text.lower() or 'district' in text.lower():
                found.append({'name': text, 'title': '', 'link': a['href']})
        return found
    except Exception:
        return []


def get_election_results(url, container_selector=None):
    """Attempt to extract recent election results from a county page.

    Returns a dict with keys found on the page: titles, tables converted to list-of-rows.
    If `container_selector` is provided it will be used to narrow the search.
    """
    soup = fetch_soup(url)
    root = soup.select_one(container_selector) if container_selector else soup
    results = {'tables': [], 'text_blocks': []}

    # extract HTML tables into list-of-rows
    for tbl in root.find_all('table'):
        rows = []
        for tr in tbl.find_all('tr'):
            cols = [td.get_text(strip=True) for td in tr.find_all(['th', 'td'])]
            if cols:
                rows.append(cols)
        if rows:
            results['tables'].append(rows)

    # also capture prominent headings + following paragraphs
    for h in root.find_all(['h1', 'h2', 'h3']):
        text = h.get_text(strip=True)
        following = []
        sib = h.find_next_sibling()
        count = 0
        while sib and count < 6:
            if sib.name == 'p':
                following.append(sib.get_text(strip=True))
            sib = sib.find_next_sibling()
            count += 1
        if text or following:
            results['text_blocks'].append({'heading': text, 'paragraphs': following})

    return results


def scrape_sdvote_results(url=None):
    """Scrape San Diego Registrar past election records from sdvote.com.

    The page embeds election data as a JSON string inside a commented-out JS
    variable. We extract and parse it directly rather than looking for HTML
    tables (which are JS-rendered and empty in static HTML).

    Returns: {'races': [ {'id', 'date', 'title', 'result_url', 'result_title',
                           'canvass_url', 'canvass_title'}, ... ] }
    """
    if not url:
        url = 'https://www.sdvote.com/content/rov/en/past-election-info.html'
    try:
        soup = fetch_soup(url)
    except Exception:
        return {'races': []}

    races = []
    for script in soup.find_all('script'):
        text = script.string or ''
        # The page embeds: //var electionData = JSON.stringify([{...}])
        # or: var electionData = JSON.stringify([{...}])
        match = re.search(r'electionData\s*=\s*JSON\.stringify\((\[.+\])\)', text, re.DOTALL)
        if match:
            try:
                # The page uses JS hex escapes (\x22, \x26, etc.) which are not
                # valid in JSON. Convert them to literal characters first.
                raw = match.group(1)
                cleaned = re.sub(r'\\x([0-9a-fA-F]{2})',
                                 lambda m: chr(int(m.group(1), 16)), raw)
                records = json.loads(cleaned)
                for rec in records:
                    races.append({
                        'id': rec.get('id', ''),
                        'date': rec.get('Election_Date', ''),
                        'title': rec.get('Election_Title', ''),
                        'result_url': rec.get('Result', ''),
                        'result_title': rec.get('Result_Title', ''),
                        'canvass_url': rec.get('Canvass', ''),
                        'canvass_title': rec.get('Canvass_Title', ''),
                    })
            except (json.JSONDecodeError, ValueError):
                pass
            break  # only one electionData block expected

    return {'races': races}


def scrape_county_political_snapshot():
    """Convenience function returning supervisors + sdvote results together."""
    supervisors = get_county_supervisors()
    sdvote = scrape_sdvote_results()
    return {'supervisors': supervisors, 'election_results': sdvote}
