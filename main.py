# -*- coding: utf-8 -*-
"""
Induct Downtime Monitoring System - Main Orchestrator
Coordinates Mercury scraping, downtime analysis, and Slack notifications
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime, time as dt_time
from pathlib import Path
from typing import Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.mercury_scraper import MercuryScraper
from src.downtime_analyzer import DowntimeAnalyzer
from src.data_storage import DataStorage
from src.slack_notifier import SlackNotifier


class InductDowntimeMonitor:
    """Main orchestrator for induct downtime monitoring system"""
    
    def __init__(self, config_path: str = "config.yaml"):
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.scraper = MercuryScraper(
            mercury_url=self.config['mercury']['url'],
            valid_locations=self.config['locations']['valid'],
            valid_statuses=['INDUCTED', 'INDUCT', 'STOW_BUFFER', 'AT_STATION']
        )
        
        self.analyzer = DowntimeAnalyzer(
            categories=self.config['downtime']['categories'],
            break_threshold=self.config['downtime']['break_threshold']
        )
        
        self.storage = DataStorage(storage_type="sqlite")
        
        self.notifier = SlackNotifier(self.config['slack']['webhook'])
        
        # State tracking
        self.last_scrape_time = None
        self.last_report_time = None
        self.shift_start_time = None
        self.system_errors = 0
        self.max_errors = 5
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file or use fallback"""
        if YAML_AVAILABLE and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load YAML config: {e}, using fallback")
        
        # Fallback configuration
        return {
            'mercury': {
                'url': 'https://mercury.amazon.com/getQueryResponse?ID=127de24b92c1f65c47f001541fbc6974&region=na',
                'scrape_interval': 120
            },
            'locations': {
                'valid': ['GA1', 'GA2', 'GA3', 'GA4', 'GA5', 'GA6', 'GA7', 'GA8', 'GA9', 'GA10']
            },
            'downtime': {
                'categories': [
                    {'name': '20-60', 'min': 20, 'max': 60},
                    {'name': '60-120', 'min': 60, 'max': 120},
                    {'name': '120-780', 'min': 120, 'max': 780}
                ],
                'break_threshold': 780
            },
            'slack': {
                'webhook': 'https://hooks.slack.com/triggers/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',
                'report_interval': 1800,
                'shift_end_threshold': 2100
            },
            'shift': {
                'start': '01:20',
                'end': '08:30',
                'break_start': '04:55',
                'break_end': '05:30'
            },
            'auth': {
                'cookie_path': '~/.midway/cookie'
            }
        }
    
    def _setup_logging(self):
        """Configure logging for the application"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"induct_downtime_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def is_shift_active(self):
        """Check if shift is currently active"""
        current_time = datetime.now().time()
        shift_start = dt_time.fromisoformat(self.config['shift']['start'])
        shift_end = dt_time.fromisoformat(self.config['shift']['end'])
        
        # Handle overnight shifts
        if shift_start > shift_end:
            return current_time >= shift_start or current_time <= shift_end
        else:
            return shift_start <= current_time <= shift_end
    
    def is_break_time(self):
        """Check if it's currently break time"""
        current_time = datetime.now().time()
        break_start = dt_time.fromisoformat(self.config['shift']['break_start'])
        break_end = dt_time.fromisoformat(self.config['shift']['break_end'])
        
        return break_start <= current_time <= break_end
    
    def scrape_and_analyze(self):
        """Main scraping and analysis cycle"""
        try:
            self.logger.info("Starting scrape and analysis cycle")
            
            # Check if shift is active
            if not self.is_shift_active():
                self.logger.info("Shift not active, skipping scrape")
                return
            
            # Scrape new data
            scan_data = self.scraper.scrape_with_retry()
            if not scan_data:
                self.system_errors += 1
                self.logger.error(f"Scraping failed (error count: {self.system_errors})")
                
                if self.system_errors >= self.max_errors:
                    self.notifier.send_system_alert(
                        'error',
                        'Scraping System Failure',
                        f'Failed to scrape data {self.system_errors} times in a row'
                    )
                return
            
            # Reset error counter on success
            self.system_errors = 0
            self.logger.info(f"Successfully scraped {len(scan_data)} records")
            
            # Store raw data
            self.storage.store_raw_scans(scan_data)
            
            # Analyze for downtimes
            analysis_result = self.analyzer.process_scans(scan_data)
            new_downtimes = analysis_result['new_downtimes']
            
            if new_downtimes:
                self.logger.info(f"Detected {len(new_downtimes)} new downtime events")
                
                # Store downtime events
                self.storage.store_downtime_events(new_downtimes)
                
                # Send immediate alerts for significant downtimes
                for event in new_downtimes:
                    if event['downtime_seconds'] >= 120:  # Alert for downtimes >= 2 minutes
                        self.notifier.send_downtime_alert(event)
            
            # Check for shift-end alerts
            shift_alerts = self.analyzer.check_shift_end_alerts(
                threshold=self.config['slack']['shift_end_threshold']
            )
            
            if shift_alerts:
                self.notifier.send_shift_end_alert(shift_alerts)
            
            self.last_scrape_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Scrape and analysis cycle failed: {e}")
            self.system_errors += 1
    
    def send_30_minute_report(self):
        """Send 30-minute downtime report"""
        try:
            if not self.is_shift_active() or self.is_break_time():
                self.logger.info("Skipping 30-minute report (shift inactive or break time)")
                return
            
            self.logger.info("Sending 30-minute report")
            
            # Get recent downtimes (last 30 minutes)
            recent_downtimes = self.analyzer.get_recent_downtimes(minutes=30)
            
            # Build location summaries for report
            location_summaries = self.analyzer._get_location_summaries()
            
            # Filter to only recent activity
            recent_summaries = {}
            for location, summary in location_summaries.items():
                # Check if location had activity in last 30 minutes
                location_recent = [d for d in recent_downtimes if d['location'] == location]
                if location_recent or summary['event_count'] > 0:
                    recent_summaries[location] = summary
            
            success = self.notifier.send_30_minute_report(recent_summaries)
            if success:
                self.last_report_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"30-minute report failed: {e}")
    
    def send_shift_summary(self):
        """Send end-of-shift summary report"""
        try:
            self.logger.info("Sending shift summary report")
            
            location_summaries = self.analyzer._get_location_summaries()
            shift_start = self.config['shift']['start']
            shift_end = self.config['shift']['end']
            
            success = self.notifier.send_shift_summary(location_summaries, shift_start, shift_end)
            
            if success:
                # Store daily summary
                today = datetime.now().strftime('%Y-%m-%d')
                self.storage.store_daily_summary(today, location_summaries)
                
                # Reset analyzer for new shift
                self.analyzer.reset_shift_data()
                
        except Exception as e:
            self.logger.error(f"Shift summary failed: {e}")
    
    def setup_scheduler(self):
        """Setup scheduled tasks"""
        if not SCHEDULE_AVAILABLE:
            self.logger.warning("Schedule module not available, skipping scheduler setup")
            return
            
        # Scraping every 2 minutes during shift
        schedule.every(self.config['mercury']['scrape_interval']).seconds.do(self.scrape_and_analyze)
        
        # 30-minute reports
        report_interval = self.config['slack']['report_interval'] // 60  # Convert to minutes
        schedule.every(report_interval).minutes.do(self.send_30_minute_report)
        
        # Shift summary at end of shift
        shift_end = self.config['shift']['end']
        schedule.every().day.at(shift_end).do(self.send_shift_summary)
        
        self.logger.info("Scheduler configured")
    
    def run_continuous(self):
        """Run monitoring system continuously"""
        self.logger.info("Starting continuous monitoring")
        
        # Send startup notification
        self.notifier.send_system_alert(
            'info',
            'Induct Downtime Monitor Started',
            f'System started at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        )
        
        self.setup_scheduler()
        
        try:
            if not SCHEDULE_AVAILABLE:
                self.logger.error("Schedule module not available for continuous mode")
                return
                
            while True:
                schedule.run_pending()
                time.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
            self.notifier.send_system_alert(
                'info',
                'Induct Downtime Monitor Stopped',
                'System stopped by user'
            )
        except Exception as e:
            self.logger.error(f"Monitoring system crashed: {e}")
            self.notifier.send_system_alert(
                'error',
                'System Crash',
                f'Monitoring system crashed with error: {str(e)}'
            )
    
    def run_single_cycle(self):
        """Run a single scrape and analysis cycle"""
        self.logger.info("Running single cycle")
        self.scrape_and_analyze()
    
    def test_system(self):
        """Test all system components"""
        self.logger.info("Running system tests")
        
        print("🧪 Testing Induct Downtime Monitoring System")
        print("=" * 50)
        
        # Test Slack connection
        print("📱 Testing Slack notifications...")
        if self.notifier.test_connection():
            print("✅ Slack connection successful")
        else:
            print("❌ Slack connection failed")
            return False
        
        # Test Mercury scraping
        print("🔍 Testing Mercury scraping...")
        test_data = self.scraper.scrape_with_retry(max_retries=1)
        if test_data:
            print(f"✅ Mercury scraping successful ({len(test_data)} records)")
        else:
            print("❌ Mercury scraping failed")
            return False
        
        # Test data storage
        print("🗄️  Testing data storage...")
        if test_data:
            success = self.storage.store_raw_scans(test_data[:1])  # Store one record
            if success:
                print("✅ Data storage successful")
            else:
                print("❌ Data storage failed")
                return False
        
        # Test analysis
        print("🧮 Testing downtime analysis...")
        if test_data:
            result = self.analyzer.process_scans(test_data)
            print(f"✅ Analysis successful ({len(result['new_downtimes'])} downtimes detected)")
        
        print("\n✅ All system tests passed!")
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Induct Downtime Monitoring System')
    parser.add_argument('--test', action='store_true', help='Run system tests')
    parser.add_argument('--continuous', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--single', action='store_true', help='Run single scrape cycle')
    parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    
    args = parser.parse_args()
    
    try:
        monitor = InductDowntimeMonitor(config_path=args.config)
        
        if args.test:
            monitor.test_system()
        elif args.continuous:
            monitor.run_continuous()
        elif args.single:
            monitor.run_single_cycle()
        else:
            print("Use --test, --continuous, or --single")
            print("For help: python main.py --help")
            
    except IOError:
        print(f"❌ Configuration file not found: {args.config}")
    except Exception as e:
        print(f"❌ System startup failed: {e}")


if __name__ == "__main__":
    main()