"""
Transit Tracker - Main sync script for multiple transit agencies.
"""
import os
import time
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
import schedule

from transit_fetcher import TransitFetcher
from database import TransitDatabase

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TransitTracker:
    """Manages synchronization of transit data to database."""

    def __init__(self, db_path: str = "transit_tracker.db"):
        """
        Initialize the tracker.

        Args:
            db_path: Path to SQLite database
        """
        self.db = TransitDatabase(db_path)
        self.fetchers = {}

    def add_system(self, system: str, api_key: str = None):
        """
        Add a transit system to track.

        Args:
            system: System identifier (e.g., 'mta_nyc', 'bart')
            api_key: API key if required
        """
        try:
            fetcher = TransitFetcher(system, api_key)
            self.fetchers[system] = fetcher
            logger.info(f"Added system: {fetcher.config['name']}")
        except Exception as e:
            logger.error(f"Failed to add system {system}: {e}")

    def sync_system(self, system: str):
        """
        Sync a single transit system.

        Args:
            system: System identifier
        """
        if system not in self.fetchers:
            logger.error(f"System {system} not configured")
            return

        fetcher = self.fetchers[system]

        try:
            logger.info(f"Syncing {fetcher.config['name']}...")

            feeds = fetcher.fetch_all_feeds()

            for feed_name, feed in feeds.items():
                # Store feed metadata
                self.db.insert_feed_metadata(
                    system=system,
                    agency=fetcher.config['agency'],
                    feed_name=feed_name,
                    version=feed.header.gtfs_realtime_version,
                    timestamp=feed.header.timestamp
                )

                # Parse and store vehicle positions
                positions = fetcher.parse_vehicle_positions(feed)
                for position in positions:
                    self.db.insert_train_position(position)

                if positions:
                    logger.info(f"Stored {len(positions)} positions from {feed_name}")

                # Parse and store trip updates
                trip_updates = fetcher.parse_trip_updates(feed)
                for update in trip_updates:
                    self.db.insert_trip_update(update)

                if trip_updates:
                    logger.info(f"Stored {len(trip_updates)} trip updates from {feed_name}")

                # Parse and store service alerts
                alerts = fetcher.parse_service_alerts(feed)
                for alert in alerts:
                    self.db.insert_service_alert(alert)

                if alerts:
                    logger.info(f"Stored {len(alerts)} alerts from {feed_name}")

        except Exception as e:
            logger.error(f"Error syncing {system}: {e}", exc_info=True)

    def sync_all_systems(self):
        """Sync all configured transit systems."""
        logger.info("Starting sync of all configured systems...")
        start_time = time.time()

        for system in self.fetchers.keys():
            self.sync_system(system)

        elapsed = time.time() - start_time
        logger.info(f"Completed sync in {elapsed:.2f} seconds")

    def cleanup_old_data(self, days_to_keep: int = 7):
        """Remove data older than specified days."""
        logger.info(f"Cleaning up data older than {days_to_keep} days...")
        rows_deleted = self.db.cleanup_old_data(days_to_keep)
        logger.info(f"Deleted {rows_deleted} old records")

    def run_continuous(self, interval_seconds: int = 30):
        """
        Run continuous sync at specified interval.

        Args:
            interval_seconds: Seconds between syncs
        """
        logger.info(f"Starting continuous sync every {interval_seconds} seconds")
        logger.info("Press Ctrl+C to stop")

        # Schedule the sync job
        schedule.every(interval_seconds).seconds.do(self.sync_all_systems)

        # Schedule daily cleanup
        schedule.every().day.at("03:00").do(self.cleanup_old_data)

        # Run first sync immediately
        self.sync_all_systems()

        # Keep running scheduled jobs
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping tracker...")
            self.db.close()

    def close(self):
        """Clean up resources."""
        self.db.close()


def main():
    """Main entry point for the tracker."""
    parser = argparse.ArgumentParser(description='Transit Tracker - Multi-agency transit data sync')
    parser.add_argument(
        '--systems',
        type=str,
        help='Comma-separated list of systems to track (e.g., mta_nyc,bart,mbta)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run sync once and exit (default: continuous mode)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Sync interval in seconds for continuous mode (default: 30)'
    )
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up old data and exit'
    )
    parser.add_argument(
        '--list-systems',
        action='store_true',
        help='List available transit systems'
    )

    args = parser.parse_args()

    # List systems if requested
    if args.list_systems:
        print("\n=== Available Transit Systems ===\n")
        for system in TransitFetcher.list_systems():
            print(f"{system['id']:15} - {system['name']}")
            print(f"{'':15}   Region: {system['region']}")
            print(f"{'':15}   API Key Required: {'Yes' if system['requires_api_key'] else 'No'}")
            print()
        return 0

    # Load environment variables
    load_dotenv()

    db_path = os.getenv('DATABASE_PATH', 'transit_tracker.db')

    # Initialize tracker
    tracker = TransitTracker(db_path)

    # Determine which systems to track
    systems_to_track = []
    if args.systems:
        systems_to_track = [s.strip() for s in args.systems.split(',')]
    else:
        # Try to auto-detect from environment variables
        for system in TransitFetcher.AVAILABLE_SYSTEMS:
            env_key = f'{system.upper()}_API_KEY'
            api_key = os.getenv(env_key)
            if api_key or not TransitFetcher(system).config['requires_api_key']:
                systems_to_track.append(system)

    if not systems_to_track:
        logger.error("No transit systems configured!")
        logger.error("Either:")
        logger.error("  1. Use --systems flag: python tracker.py --systems mta_nyc,bart")
        logger.error("  2. Set API keys in .env (e.g., MTA_NYC_API_KEY=...)")
        logger.error("\nUse --list-systems to see available systems")
        return 1

    # Add systems to tracker
    for system in systems_to_track:
        env_key = f'{system.upper()}_API_KEY'
        api_key = os.getenv(env_key)
        tracker.add_system(system, api_key)

    if not tracker.fetchers:
        logger.error("No transit systems successfully configured!")
        return 1

    try:
        if args.cleanup:
            # Just cleanup and exit
            tracker.cleanup_old_data()

        elif args.once:
            # Single sync
            tracker.sync_all_systems()

        else:
            # Continuous mode
            tracker.run_continuous(args.interval)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

    finally:
        tracker.close()

    return 0


if __name__ == '__main__':
    exit(main())
