"""
Main sync script for pulling MTA train data into the database.
"""
import os
import time
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
import schedule

from mta_fetcher import MTAFetcher
from database import MTADatabase

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MTADataSync:
    """Manages synchronization of MTA data to database."""

    def __init__(self, api_key: str, db_path: str):
        """
        Initialize the sync manager.

        Args:
            api_key: MTA API key
            db_path: Path to SQLite database
        """
        self.fetcher = MTAFetcher(api_key)
        self.db = MTADatabase(db_path)

    def sync_feed(self, feed_name: str):
        """
        Sync a single feed to the database.

        Args:
            feed_name: Name of the feed to sync
        """
        try:
            logger.info(f"Syncing {feed_name} feed...")

            # Fetch the feed
            feed = self.fetcher.fetch_feed(feed_name)

            # Store feed metadata
            self.db.insert_feed_metadata(
                feed_name=feed_name,
                version=feed.header.gtfs_realtime_version,
                timestamp=feed.header.timestamp
            )

            # Parse and store vehicle positions
            positions = self.fetcher.parse_vehicle_positions(feed)
            for position in positions:
                self.db.insert_train_position(position)

            logger.info(f"Stored {len(positions)} vehicle positions from {feed_name}")

            # Parse and store trip updates
            trip_updates = self.fetcher.parse_trip_updates(feed)
            for update in trip_updates:
                self.db.insert_trip_update(update)

            logger.info(f"Stored {len(trip_updates)} trip updates from {feed_name}")

            # Parse and store service alerts
            alerts = self.fetcher.parse_service_alerts(feed)
            for alert in alerts:
                self.db.insert_service_alert(alert)

            logger.info(f"Stored {len(alerts)} service alerts from {feed_name}")

        except Exception as e:
            logger.error(f"Error syncing {feed_name} feed: {e}", exc_info=True)

    def sync_all_feeds(self):
        """Sync all available MTA feeds."""
        logger.info("Starting sync of all MTA feeds...")
        start_time = time.time()

        for feed_name in MTAFetcher.FEED_URLS.keys():
            self.sync_feed(feed_name)

        elapsed = time.time() - start_time
        logger.info(f"Completed sync of all feeds in {elapsed:.2f} seconds")

    def cleanup_old_data(self, days_to_keep: int = 7):
        """Remove data older than specified days."""
        logger.info(f"Cleaning up data older than {days_to_keep} days...")
        rows_deleted = self.db.cleanup_old_data(days_to_keep)
        logger.info(f"Deleted {rows_deleted} old records")

    def run_continuous(self, interval_seconds: int = 30):
        """
        Run continuous sync at specified interval.

        Args:
            interval_seconds: Seconds between syncs (MTA recommends 30+ seconds)
        """
        logger.info(f"Starting continuous sync every {interval_seconds} seconds")
        logger.info("Press Ctrl+C to stop")

        # Schedule the sync job
        schedule.every(interval_seconds).seconds.do(self.sync_all_feeds)

        # Schedule daily cleanup (keep last 7 days)
        schedule.every().day.at("03:00").do(self.cleanup_old_data)

        # Run first sync immediately
        self.sync_all_feeds()

        # Keep running scheduled jobs
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping sync...")
            self.db.close()

    def close(self):
        """Clean up resources."""
        self.db.close()


def main():
    """Main entry point for the sync script."""
    parser = argparse.ArgumentParser(description='Sync MTA train data to database')
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run sync once and exit (default: continuous mode)'
    )
    parser.add_argument(
        '--feed',
        type=str,
        help='Sync specific feed only (e.g., ACE, BDFM, 1234567)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Sync interval in seconds for continuous mode (default: 30, min recommended: 30)'
    )
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up old data and exit'
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    api_key = os.getenv('MTA_API_KEY')
    if not api_key:
        logger.error("MTA_API_KEY not found in environment variables")
        logger.error("Please copy .env.example to .env and add your API key")
        return 1

    db_path = os.getenv('DATABASE_PATH', 'mta_trains.db')

    # Initialize sync manager
    sync_manager = MTADataSync(api_key, db_path)

    try:
        if args.cleanup:
            # Just cleanup and exit
            sync_manager.cleanup_old_data()

        elif args.once:
            # Single sync
            if args.feed:
                sync_manager.sync_feed(args.feed)
            else:
                sync_manager.sync_all_feeds()

        else:
            # Continuous mode
            if args.interval < 30:
                logger.warning("MTA recommends polling intervals of 30+ seconds")

            sync_manager.run_continuous(args.interval)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

    finally:
        sync_manager.close()

    return 0


if __name__ == '__main__':
    exit(main())
