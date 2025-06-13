# Induct Downtime Monitoring System - Implementation Roadmap

## Project Overview
Build a real-time monitoring system for Amazon warehouse induct operations that tracks downtime between package scans, categorizes delays, sends Slack notifications, and stores data for analysis.

## Critical Requirements
- **Deadline**: Must be operational TODAY
- **Environment**: AWS Virtual Desktop (dev-dsk-mackhun-1d-36aac158.us-east-1.amazon.com)
- **Location**: /home/mackhun/PycharmProjects/Induct-Downtime
- **Authentication**: Midway cookie at `/home/mackhun/.midway/cookie`

## Implementation Priority Order

### Phase 1: Core Data Scraping (1-2 hours)
1. **Mercury Dashboard Scraper** (`src/mercury_scraper.py`)
   ```python
   # Key fields to extract:
   - compLastScanInOrder.internalStatusCode (INDUCTED/INDUCT/STOW_BUFFER/AT_STATION only)
   - trackingId
   - Induct.destination.id (GA1-GA10 only)
   - lastScanInOrder.timestamp
   ```
   
2. **Midway Authentication** (`src/auth.py`)
   - Use existing cookie from mwinit -o
   - Implement session management with retry logic
   - Handle Mercury dashboard access

### Phase 2: Downtime Analysis Engine (1 hour)
1. **Downtime Calculator** (`src/downtime_analyzer.py`)
   - Track last scan timestamp per location (GA1-GA10)
   - Calculate time between consecutive scans at SAME location
   - Categorize: 20-60s, 60-120s, 120-780s
   - Ignore gaps >780s (breaks/shift end)
   
2. **Data Structure**:
   ```python
   location_trackers = {
       'GA1': {'last_scan': None, 'downtimes': []},
       'GA2': {'last_scan': None, 'downtimes': []},
       # ... through GA10
   }
   ```

### Phase 3: Data Storage (30 minutes)
1. **Storage Options** (`src/data_storage.py`)
   ```python
   # Option 1: SQLite (Recommended for virtual environment)
   - Database: induct_downtime.db
   - Tables: raw_scans, downtime_events, daily_summaries
   
   # Option 2: CSV Files
   - Daily files: data/raw/induct_raw_2025-06-13.csv
   - Analysis files: data/analysis/downtime_analysis_2025-06-13.csv
   ```

### Phase 4: Slack Integration (1 hour)
1. **Slack Notifier** (`src/slack_notifier.py`)
   - Webhook: `https://hooks.slack.com/triggers/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`
   
2. **Message Templates**:
   ```json
   // 30-Minute Report
   {
     "Content": "📊 Induct Downtime Report - 06:00 AM",
     "Content2": "GA1: 5 events (20-60: 3, 60-120: 1, 120-780: 1) Total: 425s\nGA2: 2 events (20-60: 2) Total: 85s\n..."
   }
   
   // Shift-End Wash (when location exceeds 2100s)
   {
     "Content": "🚨 Shift End Alert - GA5 Excessive Downtime",
     "Content2": "GA5 has exceeded 2100 seconds of downtime (Current: 2,245s)"
   }
   ```

### Phase 5: Main Orchestrator (30 minutes)
1. **Main Controller** (`main.py`)
   ```python
   # Configuration
   SCRAPE_INTERVAL = 120  # 2 minutes
   REPORT_INTERVAL = 1800  # 30 minutes
   SHIFT_START = "01:20"
   SHIFT_END = "08:30"
   BREAK_TIME = "04:55-05:30"
   ```

## File Structure
```
Induct-Downtime/
├── CLAUDE.md                    # Project context for AI assistance
├── README.md                    # Project documentation
├── main.py                      # Main orchestrator
├── requirements.txt             # Python dependencies
├── config.yaml                  # Configuration file
├── src/
│   ├── __init__.py
│   ├── mercury_scraper.py       # Mercury dashboard scraper
│   ├── auth.py                  # Midway authentication
│   ├── downtime_analyzer.py     # Downtime calculation logic
│   ├── data_storage.py          # Database/CSV operations
│   └── slack_notifier.py        # Slack notifications
├── data/
│   ├── raw/                     # Daily raw data files
│   └── analysis/                # Processed analysis files
└── logs/                        # Application logs
```

## CLAUDE.md Content
```markdown
# Induct Downtime Monitoring Project

## Purpose
Monitor warehouse induct station downtime to identify operational bottlenecks and reduce delays.

## Key Business Logic
- Downtime = Time between consecutive package scans at the SAME induct location
- Categories: 20-60s (common), 60-120s (less common), 120-780s (rare)
- Ignore gaps >780s (breaks/shift changes)
- Only track GA1-GA10 locations
- Only track INDUCTED/INDUCT/STOW_BUFFER/AT_STATION statuses

## Technical Stack
- Python 3.8+
- Selenium for Mercury scraping
- SQLite/CSV for data storage
- Requests for Slack webhooks
- Schedule for periodic tasks

## Authentication
Uses Amazon Midway authentication via mwinit -o command.
Cookie location: ~/.midway/cookie

## Shift Information
- Start: 1:20 AM
- End: 7:30-8:30 AM  
- Break: 4:55-5:30 AM
```

## Implementation Steps for Claude Code

### Step 1: Environment Setup
```bash
cd ~/PycharmProjects/Induct-Downtime
pip install selenium requests pandas sqlalchemy schedule pyyaml
```

### Step 2: Create Configuration
```yaml
# config.yaml
mercury:
  url: "https://mercury.amazon.com/getQueryResponse?ID=127de24b92c1f65c47f001541fbc6974&region=na"
  scrape_interval: 120  # seconds
  
locations:
  valid: ["GA1", "GA2", "GA3", "GA4", "GA5", "GA6", "GA7", "GA8", "GA9", "GA10"]
  
downtime:
  categories:
    - {name: "20-60", min: 20, max: 60}
    - {name: "60-120", min: 60, max: 120}
    - {name: "120-780", min: 120, max: 780}
  break_threshold: 780
  
slack:
  webhook: "https://hooks.slack.com/triggers/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"
  report_interval: 1800  # 30 minutes
  shift_end_threshold: 2100  # seconds per location
```

### Step 3: Critical Implementation Notes

1. **Selenium Setup**: 
   - Check if Chrome/Firefox and drivers are installed on virtual desktop
   - Use headless mode for efficiency

2. **Error Handling**:
   - Implement exponential backoff for Mercury requests
   - Log all errors but continue operation
   - Send Slack alert if scraping fails for >10 minutes

3. **Data Processing**:
   - Process only new records since last scrape
   - Maintain in-memory state for current shift
   - Persist to storage every scrape cycle

4. **Performance**:
   - Limit Mercury response to last 1000 rows if possible
   - Use pandas for efficient data manipulation
   - Implement connection pooling for database

## Testing Checklist
- [ ] Midway authentication works
- [ ] Mercury dashboard accessible and data parsing correct
- [ ] Downtime calculations accurate for same-location scans
- [ ] 30-minute reports sending to Slack
- [ ] Shift-end alerts trigger at 2100s per location
- [ ] Data persisting to daily files
- [ ] Handles break times (4:55-5:30 AM) correctly
- [ ] Stops notifications when all locations >780s

## Quick Start Commands
```bash
# Test authentication
python src/auth.py

# Test Mercury scraping
python src/mercury_scraper.py --test

# Run main application
python main.py

# Run in continuous mode
python main.py --continuous
```

## Troubleshooting
1. **Authentication fails**: Re-run `mwinit -o` in terminal
2. **Selenium issues**: Install Chrome driver: `sudo apt-get install chromium-chromedriver`
3. **Slack not sending**: Verify webhook URL and network access
4. **Data not storing**: Check write permissions in data/ directory

## Success Metrics
- System operational within 4 hours
- Zero missed downtime events
- Slack reports every 30 minutes during shift
- All downtime data captured for analysis
- Reduces induct downtime by identifying patterns