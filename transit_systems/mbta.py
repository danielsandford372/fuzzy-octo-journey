"""
MBTA (Massachusetts Bay Transportation Authority) Configuration
Boston, Massachusetts
"""

CONFIG = {
    'name': 'MBTA',
    'agency': 'MBTA',
    'region': 'Boston',
    'requires_api_key': True,
    'api_key_url': 'https://api-v3.mbta.com/',
    'api_key_header': 'x-api-key',

    'feeds': {
        'vehicle_positions': {
            'url': 'https://cdn.mbta.com/realtime/VehiclePositions.pb',
            'routes': ['Red', 'Orange', 'Blue', 'Green-B', 'Green-C', 'Green-D', 'Green-E', 'Mattapan'],
            'type': 'vehicle_positions',
        },
        'trip_updates': {
            'url': 'https://cdn.mbta.com/realtime/TripUpdates.pb',
            'routes': ['Red', 'Orange', 'Blue', 'Green-B', 'Green-C', 'Green-D', 'Green-E', 'Mattapan'],
            'type': 'trip_updates',
        },
        'alerts': {
            'url': 'https://cdn.mbta.com/realtime/Alerts.pb',
            'routes': [],
            'type': 'alerts',
        },
    }
}
