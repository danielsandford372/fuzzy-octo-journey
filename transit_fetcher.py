"""
Generic transit data fetcher supporting multiple agencies.
"""
import requests
import importlib
from google.transit import gtfs_realtime_pb2
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransitFetcher:
    """Generic fetcher for GTFS Realtime transit data."""

    AVAILABLE_SYSTEMS = ['mta_nyc', 'bart', 'mbta', 'cta', 'wmata', 'la_metro']

    def __init__(self, system: str, api_key: Optional[str] = None):
        """
        Initialize the transit fetcher.

        Args:
            system: Transit system identifier (e.g., 'mta_nyc', 'bart', 'mbta')
            api_key: API key if required by the system
        """
        if system not in self.AVAILABLE_SYSTEMS:
            raise ValueError(f"Unknown system: {system}. Available: {self.AVAILABLE_SYSTEMS}")

        self.system = system
        self.api_key = api_key

        # Load system configuration
        module = importlib.import_module(f'transit_systems.{system}')
        self.config = module.CONFIG

        # Validate API key requirement
        if self.config['requires_api_key'] and not api_key:
            logger.warning(
                f"{self.config['name']} requires an API key. "
                f"Get one at: {self.config['api_key_url']}"
            )

        # Setup headers
        self.headers = {}
        if api_key and self.config.get('api_key_header'):
            self.headers[self.config['api_key_header']] = api_key

    def fetch_feed(self, feed_name: str) -> gtfs_realtime_pb2.FeedMessage:
        """
        Fetch a GTFS Realtime feed.

        Args:
            feed_name: Name of the feed from the system config

        Returns:
            Parsed GTFS Realtime FeedMessage

        Raises:
            ValueError: If feed_name is invalid
            requests.RequestException: If API request fails
        """
        if feed_name not in self.config['feeds']:
            raise ValueError(
                f"Invalid feed name: {feed_name}. "
                f"Available: {list(self.config['feeds'].keys())}"
            )

        feed_config = self.config['feeds'][feed_name]
        url = feed_config['url']

        # Add API key as query parameter if needed
        params = {}
        if self.api_key and self.config.get('api_key_param'):
            params[self.config['api_key_param']] = self.api_key

        logger.info(f"Fetching {self.config['name']} feed: {feed_name}")

        response = requests.get(url, headers=self.headers, params=params, timeout=30)
        response.raise_for_status()

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        logger.info(
            f"Successfully fetched {len(feed.entity)} entities from "
            f"{self.config['name']} {feed_name} feed"
        )
        return feed

    def fetch_all_feeds(self) -> Dict[str, gtfs_realtime_pb2.FeedMessage]:
        """
        Fetch all available feeds for this transit system.

        Returns:
            Dictionary mapping feed names to FeedMessages
        """
        feeds = {}
        for feed_name in self.config['feeds'].keys():
            try:
                feeds[feed_name] = self.fetch_feed(feed_name)
            except Exception as e:
                logger.error(f"Failed to fetch {feed_name} feed: {e}")

        return feeds

    def parse_vehicle_positions(self, feed: gtfs_realtime_pb2.FeedMessage) -> List[Dict[str, Any]]:
        """
        Parse vehicle position data from a feed.

        Args:
            feed: GTFS Realtime FeedMessage

        Returns:
            List of dictionaries containing vehicle position data
        """
        positions = []

        for entity in feed.entity:
            if entity.HasField('vehicle'):
                vehicle = entity.vehicle

                position_data = {
                    'system': self.system,
                    'agency': self.config['agency'],
                    'trip_id': vehicle.trip.trip_id if vehicle.HasField('trip') else None,
                    'route_id': vehicle.trip.route_id if vehicle.HasField('trip') else None,
                    'train_id': entity.id,
                    'direction': vehicle.trip.direction_id if vehicle.HasField('trip') else None,
                    'current_stop_id': vehicle.stop_id if vehicle.HasField('stop_id') else None,
                    'current_status': self._get_current_status(vehicle.current_status),
                    'timestamp': vehicle.timestamp if vehicle.HasField('timestamp') else feed.header.timestamp,
                    'latitude': vehicle.position.latitude if vehicle.HasField('position') else None,
                    'longitude': vehicle.position.longitude if vehicle.HasField('position') else None,
                    'bearing': vehicle.position.bearing if vehicle.HasField('position') and vehicle.position.HasField('bearing') else None,
                    'speed': vehicle.position.speed if vehicle.HasField('position') and vehicle.position.HasField('speed') else None,
                }

                positions.append(position_data)

        return positions

    def parse_trip_updates(self, feed: gtfs_realtime_pb2.FeedMessage) -> List[Dict[str, Any]]:
        """
        Parse trip update data from a feed.

        Args:
            feed: GTFS Realtime FeedMessage

        Returns:
            List of dictionaries containing trip update data
        """
        updates = []

        for entity in feed.entity:
            if entity.HasField('trip_update'):
                trip_update = entity.trip_update

                trip_id = trip_update.trip.trip_id if trip_update.HasField('trip') else None
                route_id = trip_update.trip.route_id if trip_update.HasField('trip') else None

                for stop_time_update in trip_update.stop_time_update:
                    update_data = {
                        'system': self.system,
                        'agency': self.config['agency'],
                        'trip_id': trip_id,
                        'route_id': route_id,
                        'stop_id': stop_time_update.stop_id,
                        'arrival_time': stop_time_update.arrival.time if stop_time_update.HasField('arrival') else None,
                        'departure_time': stop_time_update.departure.time if stop_time_update.HasField('departure') else None,
                        'schedule_relationship': self._get_schedule_relationship(stop_time_update.schedule_relationship),
                        'timestamp': trip_update.timestamp if trip_update.HasField('timestamp') else feed.header.timestamp,
                    }

                    updates.append(update_data)

        return updates

    def parse_service_alerts(self, feed: gtfs_realtime_pb2.FeedMessage) -> List[Dict[str, Any]]:
        """
        Parse service alert data from a feed.

        Args:
            feed: GTFS Realtime FeedMessage

        Returns:
            List of dictionaries containing service alert data
        """
        alerts = []

        for entity in feed.entity:
            if entity.HasField('alert'):
                alert = entity.alert

                # Get header text
                header_text = None
                if alert.header_text.translation:
                    header_text = alert.header_text.translation[0].text

                # Get description
                description_text = None
                if alert.description_text.translation:
                    description_text = alert.description_text.translation[0].text

                # Get affected routes
                affected_routes = []
                for informed_entity in alert.informed_entity:
                    if informed_entity.HasField('route_id'):
                        affected_routes.append(informed_entity.route_id)

                # Get active periods
                active_period_start = None
                active_period_end = None
                if alert.active_period:
                    active_period_start = alert.active_period[0].start if alert.active_period[0].HasField('start') else None
                    active_period_end = alert.active_period[0].end if alert.active_period[0].HasField('end') else None

                alert_data = {
                    'system': self.system,
                    'agency': self.config['agency'],
                    'alert_id': entity.id,
                    'header_text': header_text,
                    'description_text': description_text,
                    'alert_type': self._get_alert_type(alert.cause),
                    'severity': self._get_severity(alert.severity_level) if alert.HasField('severity_level') else None,
                    'active_period_start': active_period_start,
                    'active_period_end': active_period_end,
                    'affected_routes': ','.join(affected_routes),
                    'timestamp': feed.header.timestamp,
                }

                alerts.append(alert_data)

        return alerts

    @staticmethod
    def _get_current_status(status: int) -> str:
        """Convert current status enum to string."""
        status_map = {
            0: 'INCOMING_AT',
            1: 'STOPPED_AT',
            2: 'IN_TRANSIT_TO',
        }
        return status_map.get(status, 'UNKNOWN')

    @staticmethod
    def _get_schedule_relationship(relationship: int) -> str:
        """Convert schedule relationship enum to string."""
        relationship_map = {
            0: 'SCHEDULED',
            1: 'SKIPPED',
            2: 'NO_DATA',
        }
        return relationship_map.get(relationship, 'SCHEDULED')

    @staticmethod
    def _get_alert_type(cause: int) -> str:
        """Convert alert cause enum to string."""
        cause_map = {
            1: 'UNKNOWN_CAUSE',
            2: 'OTHER_CAUSE',
            3: 'TECHNICAL_PROBLEM',
            4: 'STRIKE',
            5: 'DEMONSTRATION',
            6: 'ACCIDENT',
            7: 'HOLIDAY',
            8: 'WEATHER',
            9: 'MAINTENANCE',
            10: 'CONSTRUCTION',
            11: 'POLICE_ACTIVITY',
            12: 'MEDICAL_EMERGENCY',
        }
        return cause_map.get(cause, 'UNKNOWN')

    @staticmethod
    def _get_severity(severity: int) -> str:
        """Convert severity level enum to string."""
        severity_map = {
            1: 'UNKNOWN_SEVERITY',
            2: 'INFO',
            3: 'WARNING',
            4: 'SEVERE',
        }
        return severity_map.get(severity, 'UNKNOWN')

    @classmethod
    def list_systems(cls) -> List[Dict[str, str]]:
        """
        Get list of available transit systems.

        Returns:
            List of dictionaries with system information
        """
        systems = []
        for system_id in cls.AVAILABLE_SYSTEMS:
            module = importlib.import_module(f'transit_systems.{system_id}')
            config = module.CONFIG
            systems.append({
                'id': system_id,
                'name': config['name'],
                'agency': config['agency'],
                'region': config['region'],
                'requires_api_key': config['requires_api_key'],
            })
        return systems
