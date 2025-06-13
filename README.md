# Induct Downtime Monitoring System

A real-time monitoring system for Amazon warehouse induct operations that tracks downtime between package scans, categorizes delays, sends Slack notifications, and stores data for analysis.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Test system components
python main.py --test

# Run single scrape cycle
python main.py --single

# Run continuous monitoring
python main.py --continuous
```

## System Components

### Core Modules

- **`src/auth.py`** - Midway authentication using existing cookies
- **`src/mercury_scraper.py`** - Mercury dashboard scraper
- **`src/downtime_analyzer.py`** - Downtime calculation and categorization
- **`src/data_storage.py`** - SQLite/CSV data storage
- **`src/slack_notifier.py`** - Slack webhook notifications
- **`main.py`** - Main orchestrator with scheduling

### Key Features

- **Real-time Scraping**: Mercury dashboard every 2 minutes
- **Downtime Detection**: Tracks gaps between scans at same location
- **Smart Categorization**: 20-60s, 60-120s, 120-780s buckets
- **Slack Integration**: 30-minute reports and shift summaries
- **Data Persistence**: SQLite database with CSV backup
- **Shift Awareness**: Only operates during configured shift hours

## Configuration

Edit `config.yaml` to customize:

- Mercury URL and scraping intervals
- Valid locations (GA1-GA10) and statuses
- Downtime categories and thresholds
- Slack webhook and notification settings
- Shift schedule and break times

## Usage Examples

```bash
# Test authentication
python src/auth.py

# Test Mercury scraping
python src/mercury_scraper.py --test

# Test Slack notifications
python src/slack_notifier.py

# Test downtime analysis
python src/downtime_analyzer.py

# Run full system test
python main.py --test
```

## Data Flow

1. **Scrape** Mercury dashboard for induct scan data
2. **Filter** by valid locations (GA1-GA10) and statuses
3. **Analyze** time gaps between consecutive scans per location
4. **Categorize** downtimes and ignore breaks (>780s)
5. **Store** raw scans and downtime events in database
6. **Notify** Slack with reports and alerts

## Notifications

- **30-minute reports**: Downtime summary by location
- **Shift-end alerts**: Locations exceeding 2100s total downtime
- **Immediate alerts**: Individual downtimes ≥120s
- **System alerts**: Errors, startup/shutdown notifications

## Requirements

- Python 3.8+
- Active Midway authentication (`mwinit -o`)
- Network access to Mercury dashboard
- Slack webhook permissions

## Troubleshooting

- **Authentication fails**: Re-run `mwinit -o`
- **Scraping errors**: Check Mercury URL and cookie path
- **Slack not sending**: Verify webhook URL and network access
- **Data not storing**: Check write permissions in data/ directory

## Success Metrics

- Zero missed downtime events during shift
- 30-minute Slack reports throughout shift
- Complete data capture for trend analysis
- Operational bottleneck identification