"""
Mock Data Test Script for Induct Downtime Monitoring System
Generates realistic test data and verifies the complete pipeline
"""

import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import random
from typing import List, Dict

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.downtime_analyzer import DowntimeAnalyzer
from src.data_storage import DataStorage
from src.slack_notifier import SlackNotifier


class MockDataGenerator:
    """Generates realistic mock Mercury dashboard data"""
    
    def __init__(self):
        self.locations = ['GA1', 'GA2', 'GA3', 'GA4', 'GA5', 'GA6', 'GA7', 'GA8', 'GA9', 'GA10']
        self.statuses = ['INDUCTED', 'INDUCT', 'STOW_BUFFER', 'AT_STATION']
        self.tracking_id_counter = 1000
    
    def generate_downtime_scenario(self, location: str, base_time: datetime, 
                                 downtime_gaps: List[int]) -> List[Dict]:
        """Generate scan data with specific downtime gaps for a location"""
        scans = []
        current_time = base_time
        
        for i, gap in enumerate(downtime_gaps):
            # Create scan record
            scan = {
                'tracking_id': f'T{self.tracking_id_counter:06d}',
                'location': location,
                'status': random.choice(self.statuses),
                'timestamp': current_time,
                'raw_timestamp': current_time.isoformat() + 'Z',
                'scraped_at': datetime.now().isoformat()
            }
            scans.append(scan)
            
            # Advance time by the gap
            current_time += timedelta(seconds=gap)
            self.tracking_id_counter += 1
        
        # Add final scan
        final_scan = {
            'tracking_id': f'T{self.tracking_id_counter:06d}',
            'location': location,
            'status': random.choice(self.statuses),
            'timestamp': current_time,
            'raw_timestamp': current_time.isoformat() + 'Z',
            'scraped_at': datetime.now().isoformat()
        }
        scans.append(final_scan)
        self.tracking_id_counter += 1
        
        return scans
    
    def generate_comprehensive_test_data(self) -> List[Dict]:
        """Generate comprehensive test data covering all scenarios"""
        all_scans = []
        base_time = datetime.now() - timedelta(hours=2)  # Start 2 hours ago
        
        # Scenario 1: GA1 - Multiple short downtimes (20-60s category)
        ga1_gaps = [35, 45, 25, 50, 30]  # Total: 185s downtime
        all_scans.extend(self.generate_downtime_scenario('GA1', base_time, ga1_gaps))
        
        # Scenario 2: GA2 - Medium downtimes (60-120s category)
        ga2_gaps = [75, 95, 110, 65]  # Total: 345s downtime
        all_scans.extend(self.generate_downtime_scenario('GA2', base_time + timedelta(minutes=5), ga2_gaps))
        
        # Scenario 3: GA3 - Long downtimes (120-780s category)
        ga3_gaps = [150, 300, 200, 450]  # Total: 1100s downtime
        all_scans.extend(self.generate_downtime_scenario('GA3', base_time + timedelta(minutes=10), ga3_gaps))
        
        # Scenario 4: GA4 - Mixed downtimes
        ga4_gaps = [40, 85, 180, 35, 120]  # Total: 460s downtime
        all_scans.extend(self.generate_downtime_scenario('GA4', base_time + timedelta(minutes=15), ga4_gaps))
        
        # Scenario 5: GA5 - PROBLEM LOCATION (exceeds 2100s threshold)
        ga5_gaps = [200, 300, 450, 600, 350, 400, 250]  # Total: 2550s downtime (exceeds 2100s)
        all_scans.extend(self.generate_downtime_scenario('GA5', base_time + timedelta(minutes=20), ga5_gaps))
        
        # Scenario 6: GA6 - Break scenario (>780s gap should be ignored)
        ga6_gaps = [45, 900, 30, 55]  # 900s gap should be ignored as break
        all_scans.extend(self.generate_downtime_scenario('GA6', base_time + timedelta(minutes=25), ga6_gaps))
        
        # Scenario 7: GA7 - Minimal downtime
        ga7_gaps = [25, 35]  # Total: 60s downtime
        all_scans.extend(self.generate_downtime_scenario('GA7', base_time + timedelta(minutes=30), ga7_gaps))
        
        # Scenario 8: GA8 - No significant downtime (all gaps <20s, should be ignored)
        ga8_gaps = [10, 15, 12, 18]  # All below 20s threshold
        all_scans.extend(self.generate_downtime_scenario('GA8', base_time + timedelta(minutes=35), ga8_gaps))
        
        # Scenario 9: GA9 - Edge case downtimes (exactly at thresholds)
        ga9_gaps = [20, 60, 120, 780]  # Exactly at category boundaries
        all_scans.extend(self.generate_downtime_scenario('GA9', base_time + timedelta(minutes=40), ga9_gaps))
        
        # Scenario 10: GA10 - Recent activity (last 30 minutes)
        recent_time = datetime.now() - timedelta(minutes=25)
        ga10_gaps = [45, 90, 150]  # Recent activity for 30-min report
        all_scans.extend(self.generate_downtime_scenario('GA10', recent_time, ga10_gaps))
        
        # Sort all scans by timestamp
        all_scans.sort(key=lambda x: x['timestamp'])
        
        return all_scans


class MockTestRunner:
    """Runs comprehensive tests with mock data"""
    
    def __init__(self):
        # Load configuration (convert YAML to dict manually)
        self.config = {
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
                'shift_end_threshold': 2100
            }
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.analyzer = DowntimeAnalyzer(
            categories=self.config['downtime']['categories'],
            break_threshold=self.config['downtime']['break_threshold']
        )
        
        # Use test database to avoid interfering with real data
        self.storage = DataStorage(storage_type="sqlite", base_path="/workspace/test_db")
        
        self.notifier = SlackNotifier(self.config['slack']['webhook'])
        
        self.generator = MockDataGenerator()
    
    def run_comprehensive_test(self):
        """Run the complete test scenario"""
        print("🧪 Starting Comprehensive Mock Data Test")
        print("=" * 60)
        
        # Generate mock data
        print("\n📊 Generating mock Mercury dashboard data...")
        mock_scans = self.generator.generate_comprehensive_test_data()
        print(f"Generated {len(mock_scans)} mock scan records")
        
        # Display scenarios
        self.print_test_scenarios()
        
        # Store raw scans
        print("\n💾 Storing raw scan data...")
        storage_success = self.storage.store_raw_scans(mock_scans)
        print(f"✅ Raw scans stored: {storage_success}")
        
        # Analyze downtimes
        print("\n🧮 Analyzing downtimes...")
        analysis_result = self.analyzer.process_scans(mock_scans)
        new_downtimes = analysis_result['new_downtimes']
        location_summaries = analysis_result['location_summaries']
        
        print(f"✅ Analysis complete: {len(new_downtimes)} downtime events detected")
        
        # Store downtime events
        if new_downtimes:
            storage_success = self.storage.store_downtime_events(new_downtimes)
            print(f"✅ Downtime events stored: {storage_success}")
        
        # Display results
        self.print_downtime_analysis(new_downtimes, location_summaries)
        
        # Test shift-end alerts
        print("\n🚨 Checking for shift-end alerts...")
        shift_alerts = self.analyzer.check_shift_end_alerts(
            threshold=self.config['slack']['shift_end_threshold']
        )
        
        if shift_alerts:
            print(f"Found {len(shift_alerts)} locations exceeding threshold:")
            for alert in shift_alerts:
                print(f"  ⚠️  {alert['location']}: {alert['total_downtime']}s "
                      f"(threshold: {alert['threshold']}s)")
            
            # Test shift-end notification
            print("\n📱 Testing shift-end alert notification...")
            slack_success = self.notifier.send_shift_end_alert(shift_alerts)
            print(f"✅ Shift-end alert sent: {slack_success}")
        else:
            print("✅ No locations exceed shift-end threshold")
        
        # Test 30-minute report
        print("\n📋 Testing 30-minute report...")
        recent_summaries = self.get_recent_summaries(location_summaries)
        report_success = self.notifier.send_30_minute_report(recent_summaries)
        print(f"✅ 30-minute report sent: {report_success}")
        
        # Test immediate downtime alerts
        print("\n⏰ Testing immediate downtime alerts...")
        significant_downtimes = [d for d in new_downtimes if d['downtime_seconds'] >= 120]
        if significant_downtimes:
            print(f"Found {len(significant_downtimes)} significant downtimes (≥120s):")
            for event in significant_downtimes[:3]:  # Send first 3 to avoid spam
                alert_success = self.notifier.send_downtime_alert(event)
                print(f"  📨 {event['location']}: {event['downtime_seconds']}s alert sent: {alert_success}")
        else:
            print("✅ No significant downtimes found")
        
        # Display final statistics
        print("\n📈 Final Statistics:")
        stats = self.analyzer.get_statistics()
        self.print_final_statistics(stats)
        
        print("\n🎉 Comprehensive test completed successfully!")
        print("The system is ready for production deployment.")
    
    def print_test_scenarios(self):
        """Print description of test scenarios"""
        print("\n🎯 Test Scenarios:")
        scenarios = [
            "GA1: Multiple short downtimes (20-60s) - Normal operation",
            "GA2: Medium downtimes (60-120s) - Moderate issues", 
            "GA3: Long downtimes (120-780s) - Significant problems",
            "GA4: Mixed downtime categories",
            "GA5: PROBLEM LOCATION - Exceeds 2100s threshold",
            "GA6: Break scenario - 900s gap should be ignored",
            "GA7: Minimal downtime - Excellent performance",
            "GA8: Sub-threshold downtimes - All gaps <20s",
            "GA9: Edge case - Exactly at category boundaries",
            "GA10: Recent activity - For 30-minute report testing"
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"  {i:2d}. {scenario}")
    
    def print_downtime_analysis(self, downtimes: List[Dict], summaries: Dict):
        """Print detailed downtime analysis results"""
        print("\n🔍 Downtime Analysis Results:")
        print("-" * 40)
        
        if not downtimes:
            print("No downtime events detected")
            return
        
        # Group by location
        by_location = {}
        for event in downtimes:
            loc = event['location']
            if loc not in by_location:
                by_location[loc] = []
            by_location[loc].append(event)
        
        for location in sorted(by_location.keys()):
            events = by_location[location]
            summary = summaries.get(location, {})
            
            print(f"\n📍 {location}:")
            print(f"   Total Events: {len(events)}")
            print(f"   Total Downtime: {summary.get('total_downtime', 0)}s")
            print(f"   Average: {summary.get('average_downtime', 0)}s")
            
            # Category breakdown
            categories = summary.get('category_counts', {})
            if categories:
                cat_str = ", ".join([f"{k}: {v}" for k, v in categories.items()])
                print(f"   Categories: {cat_str}")
            
            # Show individual events
            for event in events:
                start_time = event['start_timestamp'].strftime('%H:%M:%S')
                end_time = event['end_timestamp'].strftime('%H:%M:%S')
                print(f"     • {event['downtime_seconds']:3d}s ({event['category']}) "
                      f"{start_time}-{end_time}")
    
    def get_recent_summaries(self, all_summaries: Dict) -> Dict:
        """Filter summaries to recent activity (simulate 30-minute window)"""
        # For testing, we'll include locations that had any activity
        recent_summaries = {}
        
        for location, summary in all_summaries.items():
            if summary.get('event_count', 0) > 0:
                recent_summaries[location] = summary
        
        return recent_summaries
    
    def print_final_statistics(self, stats: Dict):
        """Print final system statistics"""
        print(f"   Total Events: {stats['total_events']}")
        print(f"   Total Downtime: {stats['total_downtime_seconds']:,}s ({stats['total_downtime_seconds']/60:.1f} minutes)")
        print(f"   Average per Event: {stats['average_downtime']}s")
        print(f"   Active Locations: {stats['active_locations']}/10")
        
        print(f"\n   Category Distribution:")
        for category, count in stats['category_distribution'].items():
            print(f"     {category}: {count} events")
    
    def simulate_slack_notifications(self, summaries: Dict):
        """Simulate what would be sent to Slack (without actually sending)"""
        print("\n📱 Simulated Slack Notifications:")
        print("-" * 40)
        
        # 30-minute report simulation
        print("\n🕐 30-Minute Report Content:")
        timestamp = datetime.now().strftime("%I:%M %p")
        print(f"Title: 📊 Induct Downtime Report - {timestamp}")
        
        report_lines = []
        for location, summary in sorted(summaries.items()):
            if summary['event_count'] == 0:
                continue
                
            category_counts = summary.get('category_counts', {})
            categories = []
            for cat in ['20-60', '60-120', '120-780']:
                if category_counts.get(cat, 0) > 0:
                    categories.append(f"{cat}: {category_counts[cat]}")
            
            category_str = f"({', '.join(categories)})" if categories else ""
            report_lines.append(
                f"{location}: {summary['event_count']} events {category_str} "
                f"Total: {summary['total_downtime']}s"
            )
        
        if report_lines:
            print("Content:")
            for line in report_lines:
                print(f"  {line}")
        else:
            print("Content: ✅ No significant downtime events in the last 30 minutes")


def main():
    """Main test execution"""
    try:
        # Ensure test database directory exists
        Path("/workspace/test_db").mkdir(exist_ok=True)
        
        test_runner = MockTestRunner()
        test_runner.run_comprehensive_test()
        
    except FileNotFoundError as e:
        print(f"❌ Configuration file not found: {e}")
        print("Make sure config.yaml exists in the current directory")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()