# Transit Tracker - Quick Start Guide

Track multiple transit systems in 5 minutes!

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Get API Keys

Choose which systems you want to track and get the required API keys:

- **MTA (NYC)**: https://api.mta.info/ (required)
- **BART (SF)**: https://api.bart.gov/docs/overview/index.aspx (required)
- **MBTA (Boston)**: https://api-v3.mbta.com/ (required)
- **WMATA (DC)**: https://developer.wmata.com/ (required)
- **CTA (Chicago)**: No key needed!
- **LA Metro**: No key needed!

## 3. Configure

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
MTA_NYC_API_KEY=your_key_here
BART_API_KEY=your_key_here
# ... etc
```

## 4. List Available Systems

```bash
python tracker.py --list-systems
```

## 5. Start Tracking!

Track all configured systems:
```bash
python tracker.py
```

Track specific systems only:
```bash
python tracker.py --systems mta_nyc,bart
```

One-time sync:
```bash
python tracker.py --once
```

## 6. Query the Data

Check database:
```bash
python status.py
```

Query directly:
```bash
sqlite3 transit_tracker.db
sqlite> SELECT system, COUNT(*) FROM train_positions GROUP BY system;
```

## Common Commands

**List systems:**
```bash
python tracker.py --list-systems
```

**Track NYC only:**
```bash
python tracker.py --systems mta_nyc
```

**Track Chicago and LA (no API key needed!):**
```bash
python tracker.py --systems cta,la_metro
```

**Change update interval:**
```bash
python tracker.py --interval 60
```

**Clean up old data:**
```bash
python tracker.py --cleanup
```

## Next Steps

- Check `README.md` for complete documentation
- See `releases/` for single-system trackers
- Review database schema for query ideas
- Set up continuous sync as a service

That's it! You're now tracking transit data!
