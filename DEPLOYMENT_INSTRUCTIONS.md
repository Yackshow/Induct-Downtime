# 🚀 Production Deployment Instructions

## Quick Deployment (Recommended)

### Step 1: Copy Files to Production Environment
```bash
# On your AWS Virtual Desktop (dev-dsk-mackhun-1d-36aac158.us-east-1.amazon.com)
mkdir -p /home/mackhun/PycharmProjects/Induct-Downtime
cd /home/mackhun/PycharmProjects/Induct-Downtime
```

### Step 2: Copy All System Files
Copy these files from the current workspace to your production directory:

**Core Files:**
- `main.py` - Main orchestrator
- `config.yaml` - Configuration
- `requirements.txt` - Dependencies
- `README.md` - Documentation

**Source Code:**
- `src/__init__.py`
- `src/auth.py` - Midway authentication
- `src/mercury_scraper.py` - Mercury dashboard scraper
- `src/downtime_analyzer.py` - Downtime analysis engine
- `src/data_storage.py` - Database operations
- `src/slack_notifier.py` - Slack notifications

**Test Files:**
- `test_with_mock_data.py` - Full system test
- `test_mock_offline.py` - Offline testing

### Step 3: Install Dependencies
```bash
cd /home/mackhun/PycharmProjects/Induct-Downtime
pip install -r requirements.txt
```

### Step 4: Setup Authentication
```bash
# Establish Midway authentication
mwinit -o
```

### Step 5: Test System
```bash
# Run comprehensive system test
python3 main.py --test
```

### Step 6: Start Monitoring
```bash
# For immediate testing
python3 main.py --single

# For continuous monitoring (start at 1:20 AM)
python3 main.py --continuous
```

## Manual Setup Instructions

### Environment Requirements
- **Python**: 3.8+ (check with `python3 --version`)
- **Location**: AWS Virtual Desktop
- **Directory**: `/home/mackhun/PycharmProjects/Induct-Downtime`
- **Network**: Access to Mercury dashboard
- **Authentication**: Midway cookies

### Dependency Installation
```bash
pip install requests>=2.25.0
pip install pandas>=1.3.0
pip install schedule>=1.1.0
pip install pyyaml>=6.0
pip install sqlalchemy>=1.4.0
pip install selenium>=4.0.0
pip install beautifulsoup4>=4.9.0
pip install python-dateutil>=2.8.0
```

### Directory Structure
```
/home/mackhun/PycharmProjects/Induct-Downtime/
├── main.py                      # Main orchestrator
├── config.yaml                  # Configuration
├── requirements.txt             # Dependencies
├── README.md                    # Documentation
├── src/
│   ├── __init__.py
│   ├── auth.py                  # Authentication
│   ├── mercury_scraper.py       # Mercury scraper
│   ├── downtime_analyzer.py     # Analysis engine
│   ├── data_storage.py          # Database operations
│   └── slack_notifier.py        # Slack notifications
├── data/
│   ├── raw/                     # Raw data files
│   └── analysis/                # Analysis files
├── logs/                        # Application logs
└── induct_downtime.db          # SQLite database
```

## Production Commands

### Testing Commands
```bash
# Test individual components
python3 src/auth.py                    # Test authentication
python3 src/mercury_scraper.py --test  # Test Mercury scraping
python3 src/slack_notifier.py          # Test Slack notifications
python3 src/downtime_analyzer.py       # Test analysis engine

# Full system test
python3 main.py --test

# Mock data test
python3 test_with_mock_data.py
```

### Operational Commands
```bash
# Single scrape cycle
python3 main.py --single

# Continuous monitoring
python3 main.py --continuous

# Background operation
nohup python3 main.py --continuous > logs/monitor.log 2>&1 &
```

## Troubleshooting

### Common Issues

**1. Module Import Errors**
```bash
# Fix: Install missing dependencies
pip install -r requirements.txt
```

**2. Authentication Failures**
```bash
# Fix: Refresh Midway authentication
mwinit -o
```

**3. Mercury Access Issues**
```bash
# Check: Network connectivity and authentication
curl -I "https://mercury.amazon.com"
```

**4. Slack Notification Failures**
```bash
# Test: Webhook connectivity
python3 src/slack_notifier.py
```

**5. Database Permission Issues**
```bash
# Fix: Ensure write permissions
chmod 755 /home/mackhun/PycharmProjects/Induct-Downtime
```

### Log Files
- **Application Logs**: `logs/induct_downtime_YYYYMMDD.log`
- **System Output**: Check terminal output for real-time status
- **Database**: SQLite database at `induct_downtime.db`

## Validation Checklist

Before going live, verify:

- [ ] ✅ All dependencies installed
- [ ] ✅ Midway authentication working (`mwinit -o`)
- [ ] ✅ Mercury dashboard accessible
- [ ] ✅ Slack webhook responding
- [ ] ✅ Database permissions correct
- [ ] ✅ System test passing (`python3 main.py --test`)
- [ ] ✅ Mock data test successful
- [ ] ✅ Single cycle test working
- [ ] ✅ Logs directory writable

## Operational Schedule

**Shift Hours**: 1:20 AM - 8:30 AM
**Break Time**: 4:55 AM - 5:30 AM (no notifications)
**Scraping**: Every 2 minutes during shift
**Reports**: Every 30 minutes during shift
**Alerts**: Immediate for downtimes ≥120s, shift-end for locations >2100s

## Success Metrics

**System Health:**
- Zero missed downtime events
- 30-minute reports sent consistently
- All locations tracked (GA1-GA10)
- Proper categorization (20-60s, 60-120s, 120-780s)

**Business Impact:**
- Identification of operational bottlenecks
- Real-time alerting for issues
- Historical data for trend analysis
- Reduced downtime through pattern recognition

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Run diagnostic: `python3 main.py --test`
3. Verify authentication: `mwinit -o`
4. Test components individually using test scripts