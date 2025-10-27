"""
CTA (Chicago Transit Authority) Configuration
Chicago, Illinois
"""

CONFIG = {
    'name': 'CTA',
    'agency': 'CTA',
    'region': 'Chicago',
    'requires_api_key': False,
    'api_key_url': None,
    'api_key_header': None,

    'feeds': {
        'train_positions': {
            'url': 'https://www.transitchicago.com/downloads/sch_data/google_transit.zip',
            'routes': ['Red', 'Blue', 'Brown', 'Green', 'Orange', 'Pink', 'Purple', 'Yellow'],
            'type': 'vehicle_positions',
            'note': 'CTA uses Train Tracker API - GTFS-RT implementation may vary',
        },
        'bus_positions': {
            'url': 'http://www.ctabustracker.com/bustime/api/v2/getgtfsrt',
            'routes': [],
            'type': 'vehicle_positions',
        },
    }
}
