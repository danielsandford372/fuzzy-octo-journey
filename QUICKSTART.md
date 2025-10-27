# Quick Start Guide

Get up and running with MTA Train Data Sync in 5 minutes!

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Get an API Key

1. Go to https://api.mta.info/
2. Sign up (it's free!)
3. Create an API key

## 3. Configure

```bash
cp .env.example .env
```

Edit `.env` and add your key:
```
MTA_API_KEY=your_key_here
```

## 4. Start Syncing

```bash
python sync.py
```

That's it! Data is now being collected into `mta_trains.db`

## 5. Query the Data

Check database status:
```bash
python status.py
```

Run example queries:
```bash
python query_examples.py
```

Use SQL directly:
```bash
sqlite3 mta_trains.db
sqlite> SELECT route_id, COUNT(*) FROM train_positions GROUP BY route_id;
```

## Common Commands

**Single sync (no continuous loop):**
```bash
python sync.py --once
```

**Sync only specific lines:**
```bash
python sync.py --once --feed ACE
```

**Change update interval:**
```bash
python sync.py --interval 60
```

See `README.md` for full documentation!
