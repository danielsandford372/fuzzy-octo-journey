"""
Quick status check for the MTA database.
"""
import os
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv


def get_database_status(db_path: str):
    """Display status information about the MTA database."""

    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        print("\nTo create the database, run:")
        print("  python sync.py --once")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get file size
    size_mb = os.path.getsize(db_path) / (1024 * 1024)

    print("=" * 60)
    print("MTA Train Database Status")
    print("=" * 60)
    print(f"\nDatabase: {db_path}")
    print(f"Size: {size_mb:.2f} MB")

    # Check last update
    cursor.execute("SELECT MAX(recorded_at) FROM train_positions")
    last_update = cursor.fetchone()[0]

    if last_update:
        print(f"Last Update: {last_update}")

        # Calculate age
        try:
            last_dt = datetime.strptime(last_update, '%Y-%m-%d %H:%M:%S')
            age = datetime.now() - last_dt
            print(f"Data Age: {age.seconds // 60} minutes ago")

            if age > timedelta(hours=1):
                print("⚠️  Data is more than 1 hour old")
        except:
            pass
    else:
        print("Last Update: No data yet")

    print("\n" + "-" * 60)
    print("Record Counts (Last 24 Hours)")
    print("-" * 60)

    cutoff = int((datetime.now() - timedelta(hours=24)).timestamp())

    # Train positions
    cursor.execute("""
        SELECT COUNT(*) FROM train_positions
        WHERE timestamp > ?
    """, (cutoff,))
    pos_count = cursor.fetchone()[0]
    print(f"Train Positions: {pos_count:,}")

    # Unique trips
    cursor.execute("""
        SELECT COUNT(DISTINCT trip_id) FROM train_positions
        WHERE timestamp > ?
    """, (cutoff,))
    trip_count = cursor.fetchone()[0]
    print(f"Unique Trips: {trip_count:,}")

    # Trip updates
    cursor.execute("""
        SELECT COUNT(*) FROM trip_updates
        WHERE timestamp > ?
    """, (cutoff,))
    update_count = cursor.fetchone()[0]
    print(f"Trip Updates: {update_count:,}")

    # Active alerts
    now = int(datetime.now().timestamp())
    cursor.execute("""
        SELECT COUNT(*) FROM service_alerts
        WHERE (active_period_end IS NULL OR active_period_end > ?)
    """, (now,))
    alert_count = cursor.fetchone()[0]
    print(f"Active Alerts: {alert_count}")

    print("\n" + "-" * 60)
    print("Routes with Recent Data")
    print("-" * 60)

    cursor.execute("""
        SELECT route_id, COUNT(DISTINCT trip_id) as trains
        FROM train_positions
        WHERE timestamp > ?
        GROUP BY route_id
        ORDER BY route_id
    """, (cutoff,))

    routes = cursor.fetchall()
    if routes:
        for route_id, train_count in routes:
            print(f"  {route_id:5} - {train_count:3} trains")
    else:
        print("  No recent data")

    print("\n" + "=" * 60)

    # Storage breakdown
    cursor.execute("SELECT COUNT(*) FROM train_positions")
    total_pos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM trip_updates")
    total_updates = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM service_alerts")
    total_alerts = cursor.fetchone()[0]

    print("\nTotal Records (All Time)")
    print(f"  Train Positions: {total_pos:,}")
    print(f"  Trip Updates: {total_updates:,}")
    print(f"  Service Alerts: {total_alerts:,}")

    conn.close()


def main():
    """Main entry point."""
    load_dotenv()
    db_path = os.getenv('DATABASE_PATH', 'mta_trains.db')

    get_database_status(db_path)

    print("\n💡 Tips:")
    print("  - Run 'python sync.py' to start collecting data")
    print("  - Run 'python query_examples.py' to see example queries")
    print("  - Use 'sqlite3 mta_trains.db' for direct SQL access")
    print()


if __name__ == '__main__':
    main()
