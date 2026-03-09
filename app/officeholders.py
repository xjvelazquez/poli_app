# Static officeholder data for San Diego government bodies.
# Keyed by slug matching GOVERNMENT_BODIES in app.py.
# Fields: name, title, district, term_start, url, email, photo_url
# Note: data verified as of early 2026. Update manually or replace with
# scraped data once E2-002/E2-003 scrapers are implemented.

OFFICEHOLDERS = {
    'mayor': [
        {
            'name': 'Todd Gloria',
            'title': 'Mayor',
            'district': None,
            'term_start': 'December 2020',
            'url': 'https://www.sandiego.gov/mayor',
            'email': 'mayor@sandiego.gov',
            'photo_url': None,
        },
    ],

    'city-council': [
        {
            'name': 'Jennifer Campbell',
            'title': 'Council Member',
            'district': 'District 1',
            'term_start': 'December 2018',
            'url': 'https://www.sandiego.gov/citycouncil/cd1',
            'email': 'cd1@sandiego.gov',
            'photo_url': None,
        },
        {
            'name': 'Kent Lee',
            'title': 'Council Member',
            'district': 'District 2',
            'term_start': 'December 2022',
            'url': 'https://www.sandiego.gov/citycouncil/cd2',
            'email': 'cd2@sandiego.gov',
            'photo_url': None,
        },
        {
            'name': 'Stephen Whitburn',
            'title': 'Council Member',
            'district': 'District 3',
            'term_start': 'December 2020',
            'url': 'https://www.sandiego.gov/citycouncil/cd3',
            'email': 'cd3@sandiego.gov',
            'photo_url': None,
        },
        {
            'name': 'Henry Foster III',
            'title': 'Council Member',
            'district': 'District 4',
            'term_start': 'December 2022',
            'url': 'https://www.sandiego.gov/citycouncil/cd4',
            'email': 'cd4@sandiego.gov',
            'photo_url': None,
        },
        {
            'name': 'Marni von Wilpert',
            'title': 'Council Member',
            'district': 'District 5',
            'term_start': 'December 2022',
            'url': 'https://www.sandiego.gov/citycouncil/cd5',
            'email': 'cd5@sandiego.gov',
            'photo_url': None,
        },
        {
            'name': 'Raul Campillo',
            'title': 'Council Member',
            'district': 'District 6',
            'term_start': 'December 2020',
            'url': 'https://www.sandiego.gov/citycouncil/cd6',
            'email': 'cd6@sandiego.gov',
            'photo_url': None,
        },
        {
            'name': 'Vanessa Quiroz-Carter',
            'title': 'Council Member',
            'district': 'District 7',
            'term_start': 'December 2024',
            'url': 'https://www.sandiego.gov/citycouncil/cd7',
            'email': 'cd7@sandiego.gov',
            'photo_url': None,
        },
        {
            'name': 'Vivian Moreno',
            'title': 'Council Member',
            'district': 'District 8',
            'term_start': 'December 2018',
            'url': 'https://www.sandiego.gov/citycouncil/cd8',
            'email': 'cd8@sandiego.gov',
            'photo_url': None,
        },
        {
            'name': 'Sean Elo-Rivera',
            'title': 'Council President',
            'district': 'District 9',
            'term_start': 'December 2020',
            'url': 'https://www.sandiego.gov/citycouncil/cd9',
            'email': 'cd9@sandiego.gov',
            'photo_url': None,
        },
    ],

    'city-attorney': [
        {
            'name': 'Mara Elliott',
            'title': 'City Attorney',
            'district': None,
            'term_start': 'January 2017',
            'url': 'https://www.sandiego.gov/city-attorney',
            'email': 'cityattorney@sandiego.gov',
            'photo_url': None,
        },
    ],

    'city-auditor': [
        {
            'name': 'Andy Hanau',
            'title': 'City Auditor',
            'district': None,
            'term_start': 'January 2023',
            'url': 'https://www.sandiego.gov/auditor',
            'email': 'auditor@sandiego.gov',
            'photo_url': None,
        },
    ],

    'coo': [
        {
            'name': None,
            'title': 'Chief Operating Officer',
            'district': None,
            'term_start': None,
            'url': 'https://www.sandiego.gov/city-manager',
            'email': None,
            'photo_url': None,
            '_note': 'Appointed position — verify current officeholder at sandiego.gov/city-manager',
        },
    ],

    'county-board': [
        {
            'name': 'Nora Vargas',
            'title': 'Supervisor',
            'district': 'District 1',
            'term_start': 'January 2021',
            'url': 'https://www.sandiegocounty.gov/content/sdc/bos/dist1.html',
            'email': 'bos.d1@sdcounty.ca.gov',
            'photo_url': None,
        },
        {
            'name': 'Joel Anderson',
            'title': 'Supervisor',
            'district': 'District 2',
            'term_start': 'January 2023',
            'url': 'https://www.sandiegocounty.gov/content/sdc/bos/dist2.html',
            'email': 'bos.d2@sdcounty.ca.gov',
            'photo_url': None,
        },
        {
            'name': 'Terra Lawson-Remer',
            'title': 'Supervisor',
            'district': 'District 3',
            'term_start': 'January 2021',
            'url': 'https://www.sandiegocounty.gov/content/sdc/bos/dist3.html',
            'email': 'bos.d3@sdcounty.ca.gov',
            'photo_url': None,
        },
        {
            'name': 'Monica Montgomery Steppe',
            'title': 'Supervisor / Chair',
            'district': 'District 4',
            'term_start': 'January 2021',
            'url': 'https://www.sandiegocounty.gov/content/sdc/bos/dist4.html',
            'email': 'bos.d4@sdcounty.ca.gov',
            'photo_url': None,
        },
        {
            'name': 'Jim Desmond',
            'title': 'Supervisor',
            'district': 'District 5',
            'term_start': 'January 2019',
            'url': 'https://www.sandiegocounty.gov/content/sdc/bos/dist5.html',
            'email': 'bos.d5@sdcounty.ca.gov',
            'photo_url': None,
        },
    ],
}
