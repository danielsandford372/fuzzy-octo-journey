"""
BART (Bay Area Rapid Transit) Configuration
San Francisco Bay Area, California
"""

CONFIG = {
    'name': 'BART',
    'agency': 'BART',
    'region': 'San Francisco Bay Area',
    'requires_api_key': True,
    'api_key_url': 'https://api.bart.gov/docs/overview/index.aspx',
    'api_key_header': None,  # BART uses query parameter
    'api_key_param': 'key',

    'feeds': {
        'gtfs_rt': {
            'url': 'https://api.bart.gov/gtfsrt/tripupdate.aspx',
            'routes': ['01-Richmond', '03-Warm Springs/South Fremont', '05-Dublin/Pleasanton',
                      '07-Millbrae', '11-Berryessa/North San Jose', '19-Oakland Airport'],
            'type': 'trip_updates',
        },
        'alerts': {
            'url': 'https://api.bart.gov/gtfsrt/alerts.aspx',
            'routes': [],
            'type': 'alerts',
        },
    }
}
