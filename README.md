# MTA Train Data Sync

A Python application that pulls live MTA (New York City Metropolitan Transportation Authority) train location data and stores it in an easy-to-use SQLite database.

## Features

- Real-time train position tracking for all NYC subway lines
- Trip updates with arrival/departure predictions
- Service alerts and notifications
- Historical data storage and querying
- Easy-to-use Python API for data analysis
- Automatic data cleanup
- Continuous sync with configurable intervals

## What Data is Collected?

### Train Positions
- Current location (latitude/longitude when available)
- Current stop and status (stopped, in transit, etc.)
- Speed and bearing
- Route and trip information

### Trip Updates
- Predicted arrival and departure times
- Stop-by-stop schedule updates
- Schedule relationship (on-time, delayed, etc.)

### Service Alerts
- Real-time service disruptions
- Planned maintenance notices
- Severity levels and affected routes
- Active time periods

## Requirements

- Python 3.7+
- MTA API key (free - get one at https://api.mta.info/)
- Internet connection

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd fuzzy-octo-journey
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Get an MTA API key:**
   - Visit https://api.mta.info/
   - Sign up for a free account
   - Generate an API key

5. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API key:
   ```
   MTA_API_KEY=your_actual_api_key_here
   DATABASE_PATH=mta_trains.db
   UPDATE_INTERVAL=30
   ```

## Usage

### Basic Usage - Continuous Sync

Run the sync script to continuously pull data every 30 seconds (MTA recommended minimum):

```bash
python sync.py
```

This will:
- Fetch data from all MTA subway feeds
- Store train positions, trip updates, and alerts
- Run continuously until stopped (Ctrl+C)
- Automatically clean up old data daily

### Single Sync

Run once and exit:

```bash
python sync.py --once
```

### Sync Specific Feed

Sync only a specific subway line group:

```bash
python sync.py --once --feed ACE
```

Available feeds:
- `ACE` - A, C, E trains
- `BDFM` - B, D, F, M trains
- `G` - G train
- `JZ` - J, Z trains
- `NQRW` - N, Q, R, W trains
- `L` - L train
- `1234567` - 1, 2, 3, 4, 5, 6, 7 trains
- `SIR` - Staten Island Railway

### Custom Sync Interval

Change the sync interval (in seconds):

```bash
python sync.py --interval 60
```

**Note:** MTA recommends polling intervals of at least 30 seconds.

### Data Cleanup

Remove old data (keeps last 7 days):

```bash
python sync.py --cleanup
```

## Querying the Data

### Using the Query Examples

Run the included example queries:

```bash
python query_examples.py
```

This demonstrates:
- Getting active trains
- Route statistics
- Active service alerts
- Stop frequencies
- And more!

### Using the Python API

```python
from database import MTADatabase

# Connect to database
db = MTADatabase('mta_trains.db')

# Get latest train positions for the 1 train
positions = db.get_latest_positions(route_id='1', limit=10)

for pos in positions:
    print(f"Train {pos['trip_id']} at stop {pos['current_stop_id']}")

# Get recent alerts
alerts = db.get_recent_alerts(limit=5)

db.close()
```

### Direct SQL Queries

You can also use any SQLite client to query the database directly:

```bash
sqlite3 mta_trains.db
```

Example queries:

```sql
-- Get all active trains on the A line
SELECT * FROM train_positions
WHERE route_id = 'A'
ORDER BY timestamp DESC
LIMIT 10;

-- Count trains by route
SELECT route_id, COUNT(DISTINCT trip_id) as train_count
FROM train_positions
WHERE timestamp > strftime('%s', 'now', '-5 minutes')
GROUP BY route_id;

-- Get upcoming arrivals at a stop
SELECT route_id,
       datetime(arrival_time, 'unixepoch', 'localtime') as arrival
FROM trip_updates
WHERE stop_id = '127N'  -- Example stop ID
AND arrival_time > strftime('%s', 'now')
ORDER BY arrival_time
LIMIT 10;

-- Active service alerts
SELECT header_text, affected_routes, severity
FROM service_alerts
WHERE active_period_end > strftime('%s', 'now')
OR active_period_end IS NULL
ORDER BY severity DESC;
```

## Database Schema

### train_positions
Stores real-time train location data.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| trip_id | TEXT | Unique trip identifier |
| route_id | TEXT | Route (e.g., '1', 'A', 'L') |
| train_id | TEXT | Train vehicle ID |
| direction | TEXT | Direction (0 or 1) |
| current_stop_id | TEXT | Current stop ID |
| current_status | TEXT | Status (STOPPED_AT, IN_TRANSIT_TO, etc.) |
| timestamp | INTEGER | Unix timestamp |
| latitude | REAL | Latitude (when available) |
| longitude | REAL | Longitude (when available) |
| bearing | REAL | Direction of travel |
| speed | REAL | Speed in m/s |
| recorded_at | TIMESTAMP | When record was inserted |

### trip_updates
Stores arrival/departure predictions.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| trip_id | TEXT | Trip identifier |
| route_id | TEXT | Route |
| stop_id | TEXT | Stop ID |
| arrival_time | INTEGER | Predicted arrival (unix timestamp) |
| departure_time | INTEGER | Predicted departure (unix timestamp) |
| schedule_relationship | TEXT | SCHEDULED, SKIPPED, NO_DATA |
| timestamp | INTEGER | Feed timestamp |
| recorded_at | TIMESTAMP | When record was inserted |

### service_alerts
Stores service disruptions and alerts.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| alert_id | TEXT | Unique alert ID |
| header_text | TEXT | Alert headline |
| description_text | TEXT | Detailed description |
| alert_type | TEXT | Type/cause of alert |
| severity | TEXT | INFO, WARNING, SEVERE |
| active_period_start | INTEGER | Start time (unix timestamp) |
| active_period_end | INTEGER | End time (unix timestamp) |
| affected_routes | TEXT | Comma-separated route list |
| timestamp | INTEGER | Feed timestamp |
| recorded_at | TIMESTAMP | When record was inserted |

### feed_metadata
Tracks feed updates and versions.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| feed_name | TEXT | Feed identifier |
| gtfs_realtime_version | TEXT | GTFS-RT version |
| timestamp | INTEGER | Feed timestamp |
| recorded_at | TIMESTAMP | When record was inserted |

## Architecture

```
┌─────────────────┐
│   MTA GTFS-RT   │  ← Real-time feeds (Protocol Buffers)
│      API        │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  mta_fetcher.py │  ← Fetches and parses GTFS-RT data
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│     sync.py     │  ← Orchestrates sync + scheduling
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   database.py   │  ← SQLite storage layer
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  mta_trains.db  │  ← SQLite database
└─────────────────┘
         │
         ↓
┌─────────────────┐
│ query_examples  │  ← Query and analyze data
└─────────────────┘
```

## Performance Considerations

- **Sync Interval:** MTA recommends 30+ second intervals to avoid rate limiting
- **Database Size:** With all feeds at 30s intervals:
  - ~10-20 MB per day
  - ~70-140 MB per week
  - Automatic cleanup keeps last 7 days by default
- **Network:** Each sync downloads ~1-2 MB across all feeds

## Troubleshooting

### "MTA_API_KEY not found"
- Make sure you created `.env` file from `.env.example`
- Verify your API key is correct
- Check that `.env` is in the same directory as `sync.py`

### "Failed to fetch feed"
- Check your internet connection
- Verify your API key is active at https://api.mta.info/
- MTA feeds occasionally have brief outages - the script will retry on next sync

### Database locked errors
- Only run one instance of `sync.py` at a time
- Close any other programs accessing the database

### No position data (lat/lon)
- Not all MTA feeds include GPS coordinates
- Some trains may not report positions at all times
- Trip updates and stop information are always available

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## License

MIT License - feel free to use this for any purpose.

## Resources

- [MTA Developer Resources](https://api.mta.info/)
- [GTFS Realtime Reference](https://gtfs.org/realtime/)
- [MTA Open Data](https://new.mta.info/developers)

## Acknowledgments

Built using:
- GTFS Realtime protocol by Google
- MTA's open data feeds
- Python gtfs-realtime-bindings

---

**Note:** This is an unofficial tool and is not affiliated with or endorsed by the MTA.
