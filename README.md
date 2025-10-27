# Transit Tracker

A comprehensive Python application for tracking real-time transit data from major North American transit agencies. Pull live train/subway locations, trip updates, and service alerts into an easy-to-use SQLite database.

## Supported Transit Systems

| System | Location | API Key Required | Lines Covered |
|--------|----------|------------------|---------------|
| **MTA** | New York City | Yes (free) | All NYC Subway lines (1-7, A-Z, SIR) |
| **BART** | San Francisco Bay Area | Yes (free) | All BART lines |
| **MBTA** | Boston | Yes (free) | Red, Orange, Blue, Green, Mattapan |
| **CTA** | Chicago | No | All CTA 'L' train lines |
| **WMATA** | Washington DC | Yes (free) | Red, Orange, Silver, Blue, Yellow, Green |
| **LA Metro** | Los Angeles | No | All LA Metro rail lines |

## Features

- **Multi-Agency Support**: Track multiple transit systems simultaneously
- **Real-Time Data**: Vehicle positions, speeds, and current status
- **Trip Predictions**: Arrival and departure times for all stops
- **Service Alerts**: Real-time disruption notifications
- **Historical Storage**: SQLite database with automatic cleanup
- **Flexible Querying**: Easy-to-use Python API and direct SQL access
- **Continuous Sync**: Configurable update intervals
- **Streamlined Releases**: Individual standalone scripts for each system

## Quick Start

### 1. Installation

```bash
git clone <repository-url>
cd fuzzy-octo-journey
pip install -r requirements.txt
```

### 2. Configuration

```bash
cp .env.example .env
```

Edit `.env` and add API keys for the systems you want to track:

```bash
# Example: Track NYC and Boston
MTA_NYC_API_KEY=your_mta_key_here
MBTA_API_KEY=your_mbta_key_here
```

Get API keys:
- **MTA (NYC)**: https://api.mta.info/
- **BART (SF)**: https://api.bart.gov/docs/overview/index.aspx
- **MBTA (Boston)**: https://api-v3.mbta.com/
- **WMATA (DC)**: https://developer.wmata.com/
- **CTA & LA Metro**: No key needed!

### 3. List Available Systems

```bash
python tracker.py --list-systems
```

### 4. Start Tracking

Track all configured systems:
```bash
python tracker.py
```

Track specific systems only:
```bash
python tracker.py --systems mta_nyc,bart,mbta
```

Single sync (no continuous loop):
```bash
python tracker.py --once
```

## Usage Examples

### Continuous Tracking

```bash
# Track all configured systems every 30 seconds
python tracker.py

# Custom interval (60 seconds)
python tracker.py --interval 60
```

### One-Time Sync

```bash
# Sync all configured systems once
python tracker.py --once

# Sync specific systems
python tracker.py --once --systems mta_nyc,bart
```

### Data Cleanup

```bash
# Remove data older than 7 days
python tracker.py --cleanup
```

## Querying Data

### Using Python

```python
from database import TransitDatabase

db = TransitDatabase('transit_tracker.db')

# Get active trains for MTA
positions = db.get_latest_positions(system='mta_nyc', limit=50)

for pos in positions:
    print(f"{pos['route_id']} train at {pos['current_stop_id']}")

db.close()
```

### Using SQL

```bash
sqlite3 transit_tracker.db
```

```sql
-- Get all active trains across all systems
SELECT system, agency, route_id, COUNT(*) as trains
FROM train_positions
WHERE timestamp > strftime('%s', 'now', '-5 minutes')
GROUP BY system, agency, route_id
ORDER BY system, route_id;

-- Get upcoming arrivals at a specific stop
SELECT system, route_id,
       datetime(arrival_time, 'unixepoch', 'localtime') as arrival
FROM trip_updates
WHERE stop_id = 'your_stop_id'
AND arrival_time > strftime('%s', 'now')
ORDER BY arrival_time
LIMIT 10;

-- View active service alerts
SELECT agency, header_text, severity, affected_routes
FROM service_alerts
WHERE active_period_end > strftime('%s', 'now')
OR active_period_end IS NULL
ORDER BY severity DESC;
```

## Database Schema

### train_positions
Real-time vehicle location data

| Column | Type | Description |
|--------|------|-------------|
| system | TEXT | System identifier (e.g., 'mta_nyc') |
| agency | TEXT | Agency name (e.g., 'MTA') |
| trip_id | TEXT | Unique trip identifier |
| route_id | TEXT | Route/line identifier |
| current_stop_id | TEXT | Current or next stop ID |
| current_status | TEXT | STOPPED_AT, IN_TRANSIT_TO, INCOMING_AT |
| latitude/longitude | REAL | GPS coordinates (when available) |
| speed/bearing | REAL | Vehicle speed and direction |
| timestamp | INTEGER | Unix timestamp |

### trip_updates
Arrival and departure predictions

| Column | Type | Description |
|--------|------|-------------|
| system | TEXT | System identifier |
| trip_id | TEXT | Trip identifier |
| stop_id | TEXT | Stop identifier |
| arrival_time | INTEGER | Predicted arrival (unix timestamp) |
| departure_time | INTEGER | Predicted departure (unix timestamp) |
| schedule_relationship | TEXT | SCHEDULED, SKIPPED, NO_DATA |

### service_alerts
Service disruptions and notifications

| Column | Type | Description |
|--------|------|-------------|
| system | TEXT | System identifier |
| alert_id | TEXT | Unique alert identifier |
| header_text | TEXT | Alert headline |
| description_text | TEXT | Detailed description |
| severity | TEXT | INFO, WARNING, SEVERE |
| affected_routes | TEXT | Comma-separated route list |
| active_period_start/end | INTEGER | Alert time window |

## Individual System Releases

For tracking a single transit system, check out the `releases/` directory which contains streamlined standalone scripts optimized for each agency:

- `releases/mta_tracker.py` - NYC Subway only
- `releases/bart_tracker.py` - BART only
- `releases/mbta_tracker.py` - Boston only
- `releases/cta_tracker.py` - Chicago only
- `releases/wmata_tracker.py` - DC Metro only
- `releases/la_tracker.py` - LA Metro only

These are self-contained and perfect for single-system deployments.

## Architecture

```
┌──────────────────────────────────────────┐
│     Multiple GTFS-RT Feed Sources        │
│  (MTA, BART, MBTA, CTA, WMATA, LA Metro) │
└─────────────────┬────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│       transit_fetcher.py                │
│  (Generic GTFS-RT parser & fetcher)    │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│          tracker.py                     │
│  (Multi-agency orchestration)          │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│         database.py                     │
│  (SQLite storage layer)                │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│      transit_tracker.db                 │
│  (Unified multi-agency database)       │
└─────────────────────────────────────────┘
```

## Performance

- **Sync Time**: ~5-15 seconds for all 6 agencies
- **Database Growth**: ~20-40 MB per day (all agencies combined)
- **Recommended Interval**: 30+ seconds (per GTFS-RT best practices)
- **Auto-Cleanup**: Keeps last 7 days by default

## Project Structure

```
transit-tracker/
├── tracker.py              # Main multi-agency sync script
├── transit_fetcher.py      # Generic GTFS-RT fetcher
├── database.py             # Database management
├── requirements.txt        # Python dependencies
├── .env.example           # Configuration template
├── transit_systems/       # Agency-specific configurations
│   ├── mta_nyc.py
│   ├── bart.py
│   ├── mbta.py
│   ├── cta.py
│   ├── wmata.py
│   └── la_metro.py
├── releases/              # Standalone single-system trackers
│   └── README.md
├── sync.py               # Legacy MTA-only script (deprecated)
├── mta_fetcher.py        # Legacy MTA-only fetcher (deprecated)
├── query_examples.py     # Example queries
└── status.py             # Database status checker
```

## Troubleshooting

### "No transit systems configured"
- Check that API keys are set in `.env`
- Use `--systems` flag to specify systems explicitly
- Use `--list-systems` to see what's available

### "Failed to fetch feed"
- Verify API key is correct and active
- Check internet connection
- Some feeds may have brief outages - retry later

### Missing GPS coordinates
- Not all agencies provide lat/lon in all feeds
- Trip updates and stop information are always available
- Check the specific agency's GTFS-RT documentation

## Contributing

Contributions welcome! To add a new transit system:

1. Create config in `transit_systems/new_system.py`
2. Add to `AVAILABLE_SYSTEMS` in `transit_fetcher.py`
3. Document in README
4. Test with real API
5. Submit PR

## License

MIT License - free to use for any purpose.

## Credits

Built using:
- GTFS Realtime specification by Google
- Official transit agency APIs
- Python gtfs-realtime-bindings

## Resources

- [GTFS Realtime Reference](https://gtfs.org/realtime/)
- [MTA Developer Resources](https://api.mta.info/)
- [BART API Documentation](https://api.bart.gov/)
- [MBTA V3 API](https://api-v3.mbta.com/)
- [CTA Developer Center](https://www.transitchicago.com/developers/)
- [WMATA API](https://developer.wmata.com/)
- [LA Metro Developer](https://developer.metro.net/)

---

**Note:** This is an unofficial tool not affiliated with any transit agency.
