# Transit Tracker - Release History

## Available Releases

### v2.0 - Transit Tracker (Multi-Agency) ⭐ RECOMMENDED
**Released:** October 2025
**Tag:** `v2.0`

The complete multi-agency solution supporting 6 major transit systems simultaneously.

**Supported Systems:**
- MTA (New York City)
- BART (San Francisco Bay Area)
- MBTA (Boston)
- CTA (Chicago)
- WMATA (Washington DC)
- LA Metro (Los Angeles)

**Features:**
- Track multiple cities at once
- Unified database
- System-specific filtering
- Comprehensive API

**Get Started:**
```bash
git checkout v2.0
python tracker.py --list-systems
python tracker.py --systems mta_nyc,bart,mbta
```

---

## Individual System Releases

Each transit system has a dedicated v1.0 release optimized for single-system tracking.

### v1.0-mta - MTA NYC Subway Tracker 🗽
**Location:** New York City
**Tag:** `v1.0-mta` or `v1.0` (original release)
**API Key:** Required (free from https://api.mta.info/)

**Coverage:**
- All numbered lines (1-7)
- All lettered lines (A-Z)
- Staten Island Railway

**Usage:**
```bash
git checkout v1.0-mta
python tracker.py --systems mta_nyc
```

---

### v1.0-bart - BART Tracker 🌉
**Location:** San Francisco Bay Area
**Tag:** `v1.0-bart`
**API Key:** Required (free from https://api.bart.gov/)

**Coverage:**
- All BART lines (Richmond, Warm Springs, Dublin, Millbrae, Berryessa, Airport)

**Usage:**
```bash
git checkout v1.0-bart
python tracker.py --systems bart
```

---

### v1.0-mbta - MBTA Tracker 🚇
**Location:** Boston
**Tag:** `v1.0-mbta`
**API Key:** Required (free from https://api-v3.mbta.com/)

**Coverage:**
- Red, Orange, Blue Lines
- Green Line (B, C, D, E branches)
- Mattapan Trolley

**Usage:**
```bash
git checkout v1.0-mbta
python tracker.py --systems mbta
```

---

### v1.0-cta - CTA 'L' Tracker 🌆
**Location:** Chicago
**Tag:** `v1.0-cta`
**API Key:** None required! 🎉

**Coverage:**
- Red, Blue, Brown, Green, Orange, Pink, Purple, Yellow Lines

**Usage:**
```bash
git checkout v1.0-cta
python tracker.py --systems cta
```

---

### v1.0-wmata - DC Metro Tracker 🏛️
**Location:** Washington DC
**Tag:** `v1.0-wmata`
**API Key:** Required (free from https://developer.wmata.com/)

**Coverage:**
- Red, Orange, Silver, Blue, Yellow, Green Lines

**Usage:**
```bash
git checkout v1.0-wmata
python tracker.py --systems wmata
```

---

### v1.0-la - LA Metro Tracker ☀️
**Location:** Los Angeles
**Tag:** `v1.0-la`
**API Key:** None required! 🎉

**Coverage:**
- All LA Metro rail lines (Red, Purple, Blue/A, Expo/E, Green/C, Gold/L, Orange/G, Silver)

**Usage:**
```bash
git checkout v1.0-la
python tracker.py --systems la_metro
```

---

## Which Release Should I Use?

### Use v2.0 (Multi-Agency) if:
- You want to track multiple cities
- You need a unified database across systems
- You want the latest features and updates
- You're building a multi-city application

### Use Individual System Releases (v1.0-*) if:
- You only need one specific transit system
- You want the simplest setup for a single city
- You're deploying on resource-constrained devices
- You prefer focused, streamlined code

## Release Comparison

| Feature | v2.0 Multi-Agency | v1.0-* Single System |
|---------|-------------------|----------------------|
| Systems Supported | 6 cities | 1 city |
| Database | Unified | System-specific |
| Code Complexity | Moderate | Simple |
| Setup Time | ~5 minutes | ~3 minutes |
| Dependencies | Same | Same |
| Update Frequency | Regular | As needed |
| Recommended For | Production, Multi-city | Learning, Single-city |

## Migration Guide

### From v1.0 (MTA) to v2.0
Your old MTA database will continue to work, but:
- Database schema adds `system` and `agency` fields
- Run migration or start fresh database
- Update code references from `MTADatabase` to `TransitDatabase`

### Between Individual Systems
Each v1.0-* release is independent. Simply checkout the appropriate tag for your city.

## Getting API Keys

All API keys are free for non-commercial use:

| System | Get Key From |
|--------|-------------|
| MTA (NYC) | https://api.mta.info/ |
| BART (SF) | https://api.bart.gov/docs/overview/index.aspx |
| MBTA (Boston) | https://api-v3.mbta.com/ |
| CTA (Chicago) | No key needed! |
| WMATA (DC) | https://developer.wmata.com/ |
| LA Metro | No key needed! |

## Support

For issues, questions, or feature requests:
- Check README.md for documentation
- Review QUICKSTART.md for setup help
- Open an issue on GitHub

## Changelog

### v2.0 (October 2025)
- Added 5 new transit systems (BART, MBTA, CTA, WMATA, LA Metro)
- Unified multi-agency architecture
- Enhanced database schema with system/agency fields
- New tracker.py with --systems flag
- Individual system releases
- Comprehensive documentation updates

### v1.0 (October 2025)
- Initial release with MTA NYC support only
- Real-time train positions
- Trip updates and predictions
- Service alerts
- SQLite database storage
- Continuous sync capability

---

**All releases are production-ready and actively maintained.**
