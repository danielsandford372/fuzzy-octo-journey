"""
MTA (New York City) Transit Configuration
"""

CONFIG = {
    'name': 'MTA NYC Subway',
    'agency': 'MTA',
    'region': 'New York City',
    'requires_api_key': True,
    'api_key_url': 'https://api.mta.info/',
    'api_key_header': 'x-api-key',

    'feeds': {
        'ACE': {
            'url': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace',
            'routes': ['A', 'C', 'E'],
        },
        'BDFM': {
            'url': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm',
            'routes': ['B', 'D', 'F', 'M'],
        },
        'G': {
            'url': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g',
            'routes': ['G'],
        },
        'JZ': {
            'url': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz',
            'routes': ['J', 'Z'],
        },
        'NQRW': {
            'url': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw',
            'routes': ['N', 'Q', 'R', 'W'],
        },
        'L': {
            'url': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l',
            'routes': ['L'],
        },
        '1234567': {
            'url': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs',
            'routes': ['1', '2', '3', '4', '5', '6', '7'],
        },
        'SIR': {
            'url': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si',
            'routes': ['SIR'],
        },
    }
}
