"""
WMATA (Washington Metropolitan Area Transit Authority) Configuration
Washington DC Metro Area
"""

CONFIG = {
    'name': 'WMATA Metro',
    'agency': 'WMATA',
    'region': 'Washington DC',
    'requires_api_key': True,
    'api_key_url': 'https://developer.wmata.com/',
    'api_key_header': 'api_key',

    'feeds': {
        'gtfs_rt': {
            'url': 'https://api.wmata.com/gtfs/rail-gtfsrt-vehiclepositions.pb',
            'routes': ['Red', 'Orange', 'Silver', 'Blue', 'Yellow', 'Green'],
            'type': 'vehicle_positions',
        },
        'trip_updates': {
            'url': 'https://api.wmata.com/gtfs/rail-gtfsrt-tripupdates.pb',
            'routes': ['Red', 'Orange', 'Silver', 'Blue', 'Yellow', 'Green'],
            'type': 'trip_updates',
        },
        'alerts': {
            'url': 'https://api.wmata.com/gtfs/rail-gtfsrt-alerts.pb',
            'routes': [],
            'type': 'alerts',
        },
    }
}
