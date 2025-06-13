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

## Implementation Details
See ROADMAP.md for complete implementation plan, architecture, and step-by-step instructions.