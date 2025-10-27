"""
Example queries for the MTA train database.

This module demonstrates how to query and analyze the stored MTA data.
"""
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv


class MTAQuery:
    """Helper class for querying MTA train data."""

    def __init__(self, db_path: str = "mta_trains.db"):
        """Initialize connection to the database."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_active_trains(self, route_id: str = None) -> List[Dict[str, Any]]:
        """
        Get currently active trains (last 5 minutes).

        Args:
            route_id: Optional filter by route (e.g., '1', 'A', 'L')

        Returns:
            List of train positions
        """
        cursor = self.conn.cursor()
        cutoff = int((datetime.now() - timedelta(minutes=5)).timestamp())

        if route_id:
            query = """
                SELECT DISTINCT ON (trip_id)
                    trip_id, route_id, train_id, current_stop_id,
                    current_status, timestamp, latitude, longitude
                FROM train_positions
                WHERE timestamp > ? AND route_id = ?
                ORDER BY trip_id, timestamp DESC
            """
            cursor.execute(query, (cutoff, route_id))
        else:
            query = """
                SELECT DISTINCT ON (trip_id)
                    trip_id, route_id, train_id, current_stop_id,
                    current_status, timestamp, latitude, longitude
                FROM train_positions
                WHERE timestamp > ?
                ORDER BY trip_id, timestamp DESC
            """
            cursor.execute(query, (cutoff,))

        return [dict(row) for row in cursor.fetchall()]

    def get_train_history(self, trip_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get position history for a specific trip.

        Args:
            trip_id: Trip ID to track
            limit: Maximum number of records

        Returns:
            List of positions ordered by time
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM train_positions
            WHERE trip_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (trip_id, limit))

        return [dict(row) for row in cursor.fetchall()]

    def get_upcoming_arrivals(self, stop_id: str, minutes: int = 30) -> List[Dict[str, Any]]:
        """
        Get upcoming train arrivals at a specific stop.

        Args:
            stop_id: MTA stop ID
            minutes: Look ahead this many minutes

        Returns:
            List of upcoming arrivals
        """
        cursor = self.conn.cursor()
        now = int(datetime.now().timestamp())
        future = now + (minutes * 60)

        cursor.execute("""
            SELECT
                route_id, trip_id, stop_id,
                arrival_time, departure_time,
                datetime(arrival_time, 'unixepoch', 'localtime') as arrival_datetime
            FROM trip_updates
            WHERE stop_id = ?
            AND arrival_time BETWEEN ? AND ?
            ORDER BY arrival_time ASC
        """, (stop_id, now, future))

        return [dict(row) for row in cursor.fetchall()]

    def get_route_statistics(self, route_id: str, hours: int = 24) -> Dict[str, Any]:
        """
        Get statistics for a specific route.

        Args:
            route_id: Route ID (e.g., '1', 'A', 'L')
            hours: Look back this many hours

        Returns:
            Dictionary with statistics
        """
        cursor = self.conn.cursor()
        cutoff = int((datetime.now() - timedelta(hours=hours)).timestamp())

        # Count unique trains
        cursor.execute("""
            SELECT COUNT(DISTINCT trip_id) as train_count
            FROM train_positions
            WHERE route_id = ? AND timestamp > ?
        """, (route_id, cutoff))
        train_count = cursor.fetchone()[0]

        # Count position updates
        cursor.execute("""
            SELECT COUNT(*) as update_count
            FROM train_positions
            WHERE route_id = ? AND timestamp > ?
        """, (route_id, cutoff))
        update_count = cursor.fetchone()[0]

        # Get average speed (if available)
        cursor.execute("""
            SELECT AVG(speed) as avg_speed
            FROM train_positions
            WHERE route_id = ? AND timestamp > ? AND speed IS NOT NULL
        """, (route_id, cutoff))
        avg_speed = cursor.fetchone()[0]

        return {
            'route_id': route_id,
            'unique_trains': train_count,
            'position_updates': update_count,
            'average_speed': avg_speed,
            'time_period_hours': hours
        }

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """
        Get currently active service alerts.

        Returns:
            List of active alerts
        """
        cursor = self.conn.cursor()
        now = int(datetime.now().timestamp())

        cursor.execute("""
            SELECT
                alert_id, header_text, description_text,
                severity, affected_routes,
                datetime(active_period_start, 'unixepoch', 'localtime') as start_time,
                datetime(active_period_end, 'unixepoch', 'localtime') as end_time
            FROM service_alerts
            WHERE (active_period_start IS NULL OR active_period_start <= ?)
            AND (active_period_end IS NULL OR active_period_end >= ?)
            ORDER BY severity DESC, timestamp DESC
        """, (now, now))

        return [dict(row) for row in cursor.fetchall()]

    def get_stop_frequency(self, stop_id: str, hours: int = 24) -> int:
        """
        Get number of trains that stopped at a station.

        Args:
            stop_id: MTA stop ID
            hours: Look back this many hours

        Returns:
            Number of trains
        """
        cursor = self.conn.cursor()
        cutoff = int((datetime.now() - timedelta(hours=hours)).timestamp())

        cursor.execute("""
            SELECT COUNT(DISTINCT trip_id) as train_count
            FROM train_positions
            WHERE current_stop_id = ?
            AND current_status = 'STOPPED_AT'
            AND timestamp > ?
        """, (stop_id, cutoff))

        return cursor.fetchone()[0]

    def get_all_routes(self) -> List[str]:
        """
        Get list of all routes in the database.

        Returns:
            List of unique route IDs
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT route_id
            FROM train_positions
            ORDER BY route_id
        """)

        return [row[0] for row in cursor.fetchall()]

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Example usage of the query methods."""
    load_dotenv()
    db_path = os.getenv('DATABASE_PATH', 'mta_trains.db')

    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Please run sync.py first to populate the database")
        return

    query = MTAQuery(db_path)

    print("=== MTA Train Database Query Examples ===\n")

    # Example 1: Get all routes
    print("1. Available Routes:")
    routes = query.get_all_routes()
    print(f"   Found {len(routes)} routes: {', '.join(routes)}\n")

    # Example 2: Get active trains
    print("2. Currently Active Trains (last 5 minutes):")
    active = query.get_active_trains()
    print(f"   {len(active)} trains currently tracked")
    for train in active[:5]:  # Show first 5
        print(f"   - Route {train['route_id']}: Trip {train['trip_id']} at {train['current_stop_id']} ({train['current_status']})")
    print()

    # Example 3: Get statistics for a route
    if routes:
        route = routes[0]
        print(f"3. Statistics for Route {route} (last 24 hours):")
        stats = query.get_route_statistics(route)
        print(f"   - Unique trains: {stats['unique_trains']}")
        print(f"   - Position updates: {stats['position_updates']}")
        if stats['average_speed']:
            print(f"   - Average speed: {stats['average_speed']:.2f} m/s")
        print()

    # Example 4: Get active alerts
    print("4. Active Service Alerts:")
    alerts = query.get_active_alerts()
    if alerts:
        for alert in alerts[:3]:  # Show first 3
            print(f"   - [{alert['severity']}] {alert['header_text']}")
            print(f"     Routes: {alert['affected_routes']}")
    else:
        print("   No active alerts")
    print()

    query.close()


if __name__ == '__main__':
    main()
