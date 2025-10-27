"""
LA Metro (Los Angeles County Metropolitan Transportation Authority) Configuration
Los Angeles, California
"""

CONFIG = {
    'name': 'LA Metro',
    'agency': 'LA Metro',
    'region': 'Los Angeles',
    'requires_api_key': False,
    'api_key_url': None,
    'api_key_header': None,

    'feeds': {
        'vehicle_positions': {
            'url': 'https://api.metro.net/agencies/lametro/vehicles/',
            'routes': ['Red', 'Purple', 'Blue', 'Expo', 'Green', 'Gold', 'Orange', 'Silver'],
            'type': 'vehicle_positions',
        },
        'trip_updates': {
            'url': 'https://api.metro.net/agencies/lametro/tripupdates/',
            'routes': ['Red', 'Purple', 'Blue', 'Expo', 'Green', 'Gold', 'Orange', 'Silver'],
            'type': 'trip_updates',
        },
        'alerts': {
            'url': 'https://api.metro.net/agencies/lametro/alerts/',
            'routes': [],
            'type': 'alerts',
        },
    }
}
