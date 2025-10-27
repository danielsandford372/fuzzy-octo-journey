# Transit Tracker - Individual System Releases

This directory contains streamlined, single-system versions of Transit Tracker.

Each release is a standalone script optimized for tracking a specific transit agency.

## Available Releases

### MTA NYC Subway Tracker (v1.0-mta)
**Location:** New York City
**Lines:** All NYC Subway lines (1-7, A-Z, SIR)
**Requirements:** MTA API Key (free from https://api.mta.info/)
**File:** `mta_tracker.py`

### BART Tracker (v1.0-bart)
**Location:** San Francisco Bay Area
**Lines:** All BART lines
**Requirements:** BART API Key (free from https://api.bart.gov/)
**File:** `bart_tracker.py`

### MBTA Tracker (v1.0-mbta)
**Location:** Boston
**Lines:** Red, Orange, Blue, Green (all branches), Mattapan
**Requirements:** MBTA API Key (free from https://api-v3.mbta.com/)
**File:** `mbta_tracker.py`

### CTA Tracker (v1.0-cta)
**Location:** Chicago
**Lines:** All CTA 'L' train lines
**Requirements:** None (public feeds)
**File:** `cta_tracker.py`

### WMATA Metro Tracker (v1.0-wmata)
**Location:** Washington DC
**Lines:** Red, Orange, Silver, Blue, Yellow, Green
**Requirements:** WMATA API Key (free from https://developer.wmata.com/)
**File:** `wmata_tracker.py`

### LA Metro Tracker (v1.0-la)
**Location:** Los Angeles
**Lines:** All LA Metro rail lines
**Requirements:** None (public feeds)
**File:** `la_tracker.py`

## Quick Start (Any System)

1. Download the specific tracker script
2. Install dependencies: `pip install gtfs-realtime-bindings requests python-dotenv`
3. Get an API key if required (see links above)
4. Run: `python <tracker_name>.py --api-key YOUR_KEY`

## Features

All streamlined trackers include:
- Real-time vehicle positions
- Trip updates and predictions
- Service alerts
- SQLite database storage
- Continuous or one-time sync modes
- Automatic data cleanup

## Full Multi-Agency Version

For tracking multiple transit systems simultaneously, use the main Transit Tracker in the parent directory.
