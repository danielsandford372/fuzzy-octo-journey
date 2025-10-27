# Transit Tracker

Real-time transit data tracking for major North American transit systems. Pull live train/subway locations, trip updates, and service alerts into an easy-to-use SQLite database.

## Supported Transit Systems

| System | Location | API Key Required |
|--------|----------|------------------|
| **MTA** | New York City | Yes (free) |
| **BART** | San Francisco Bay Area | Yes (free) |
| **MBTA** | Boston | Yes (free) |
| **CTA** | Chicago | No ✓ |
| **WMATA** | Washington DC | Yes (free) |
| **LA Metro** | Los Angeles | No ✓ |

## Features

- ✨ Multi-agency support - track multiple cities simultaneously
- 🚇 Real-time vehicle positions and speeds
- 📍 Trip updates with arrival/departure predictions
- 🚨 Service alerts and disruptions
- 💾 SQLite database with automatic cleanup
- 🔄 Continuous or one-time sync modes

## Quick Links

- **Installation:** See `QUICKSTART.md`
- **Releases:** See `RELEASES.md` for version info
- **API Keys:** All free from respective transit agencies

## Usage

```bash
# List available systems
python tracker.py --list-systems

# Track all configured systems
python tracker.py

# Track specific systems
python tracker.py --systems mta_nyc,bart,cta
```

## Documentation

- `QUICKSTART.md` - 5-minute setup guide
- `RELEASES.md` - Version history and individual system releases
- `.env.example` - Configuration template

## License

MIT License - free to use for any purpose.

---

**Note:** This is an unofficial tool not affiliated with any transit agency.
