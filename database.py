"""
Database schema and management for MTA train location data.
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Any
import os


class MTADatabase:
    """Manages SQLite database for MTA train location data."""

    def __init__(self, db_path: str = "mta_trains.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def create_tables(self):
        """Create database tables for storing train location data."""
        cursor = self.conn.cursor()

        # Table for train positions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS train_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id TEXT NOT NULL,
                route_id TEXT NOT NULL,
                train_id TEXT,
                direction TEXT,
                current_stop_id TEXT,
                current_status TEXT,
                timestamp INTEGER NOT NULL,
                latitude REAL,
                longitude REAL,
                bearing REAL,
                speed REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_trip_id (trip_id),
                INDEX idx_route_id (route_id),
                INDEX idx_timestamp (timestamp),
                INDEX idx_recorded_at (recorded_at)
            )
        """)

        # Table for trip updates (arrival/departure predictions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trip_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id TEXT NOT NULL,
                route_id TEXT NOT NULL,
                stop_id TEXT NOT NULL,
                arrival_time INTEGER,
                departure_time INTEGER,
                schedule_relationship TEXT,
                timestamp INTEGER NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_trip_update_trip_id (trip_id),
                INDEX idx_trip_update_stop_id (stop_id),
                INDEX idx_trip_update_timestamp (timestamp)
            )
        """)

        # Table for alerts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE NOT NULL,
                header_text TEXT,
                description_text TEXT,
                alert_type TEXT,
                severity TEXT,
                active_period_start INTEGER,
                active_period_end INTEGER,
                affected_routes TEXT,
                timestamp INTEGER NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_alert_id (alert_id),
                INDEX idx_alert_timestamp (timestamp)
            )
        """)

        # Table for feed metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feed_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_name TEXT NOT NULL,
                gtfs_realtime_version TEXT,
                timestamp INTEGER NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_feed_timestamp (timestamp)
            )
        """)

        self.conn.commit()

    def insert_train_position(self, position_data: Dict[str, Any]) -> int:
        """Insert a train position record."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO train_positions (
                trip_id, route_id, train_id, direction,
                current_stop_id, current_status, timestamp,
                latitude, longitude, bearing, speed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            position_data.get('trip_id'),
            position_data.get('route_id'),
            position_data.get('train_id'),
            position_data.get('direction'),
            position_data.get('current_stop_id'),
            position_data.get('current_status'),
            position_data.get('timestamp'),
            position_data.get('latitude'),
            position_data.get('longitude'),
            position_data.get('bearing'),
            position_data.get('speed')
        ))
        self.conn.commit()
        return cursor.lastrowid

    def insert_trip_update(self, update_data: Dict[str, Any]) -> int:
        """Insert a trip update record."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO trip_updates (
                trip_id, route_id, stop_id,
                arrival_time, departure_time,
                schedule_relationship, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            update_data.get('trip_id'),
            update_data.get('route_id'),
            update_data.get('stop_id'),
            update_data.get('arrival_time'),
            update_data.get('departure_time'),
            update_data.get('schedule_relationship'),
            update_data.get('timestamp')
        ))
        self.conn.commit()
        return cursor.lastrowid

    def insert_service_alert(self, alert_data: Dict[str, Any]) -> int:
        """Insert or update a service alert record."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO service_alerts (
                alert_id, header_text, description_text,
                alert_type, severity,
                active_period_start, active_period_end,
                affected_routes, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert_data.get('alert_id'),
            alert_data.get('header_text'),
            alert_data.get('description_text'),
            alert_data.get('alert_type'),
            alert_data.get('severity'),
            alert_data.get('active_period_start'),
            alert_data.get('active_period_end'),
            alert_data.get('affected_routes'),
            alert_data.get('timestamp')
        ))
        self.conn.commit()
        return cursor.lastrowid

    def insert_feed_metadata(self, feed_name: str, version: str, timestamp: int):
        """Insert feed metadata."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO feed_metadata (feed_name, gtfs_realtime_version, timestamp)
            VALUES (?, ?, ?)
        """, (feed_name, version, timestamp))
        self.conn.commit()

    def get_latest_positions(self, route_id: str = None, limit: int = 100) -> List[Dict]:
        """Get the latest train positions, optionally filtered by route."""
        cursor = self.conn.cursor()

        if route_id:
            cursor.execute("""
                SELECT * FROM train_positions
                WHERE route_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (route_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM train_positions
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def get_recent_alerts(self, limit: int = 50) -> List[Dict]:
        """Get recent service alerts."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM service_alerts
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def cleanup_old_data(self, days_to_keep: int = 7):
        """Remove data older than specified days."""
        cursor = self.conn.cursor()
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)

        cursor.execute("DELETE FROM train_positions WHERE timestamp < ?", (cutoff_date,))
        cursor.execute("DELETE FROM trip_updates WHERE timestamp < ?", (cutoff_date,))
        cursor.execute("DELETE FROM service_alerts WHERE timestamp < ?", (cutoff_date,))
        cursor.execute("DELETE FROM feed_metadata WHERE timestamp < ?", (cutoff_date,))

        self.conn.commit()
        return cursor.rowcount

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
