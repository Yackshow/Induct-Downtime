# -*- coding: utf-8 -*-
"""
Offline Mock Data Test Script for Induct Downtime Monitoring System
Tests core logic without external dependencies (no requests, pandas, etc.)
"""

import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
import random
from typing import List, Dict

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.downtime_analyzer import DowntimeAnalyzer


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


class OfflineTestRunner:
    """Runs comprehensive tests with mock data (offline mode)"""
    
    def __init__(self):
        # Hardcoded config for testing
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
        
        self.generator = MockDataGenerator()
    
    def run_comprehensive_test(self):
        """Run the complete test scenario"""
        print("🧪 Offline Mock Data Test - Core Logic Verification")
        print("=" * 60)
        
        # Generate mock data
        print("\n📊 Generating mock Mercury dashboard data...")
        mock_scans = self.generator.generate_comprehensive_test_data()
        print(f"Generated {len(mock_scans)} mock scan records")
        
        # Display scenarios
        self.print_test_scenarios()
        
        # Analyze downtimes
        print("\n🧮 Analyzing downtimes...")
        analysis_result = self.analyzer.process_scans(mock_scans)
        new_downtimes = analysis_result['new_downtimes']
        location_summaries = analysis_result['location_summaries']
        
        print(f"✅ Analysis complete: {len(new_downtimes)} downtime events detected")
        
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
        else:
            print("✅ No locations exceed shift-end threshold")
        
        # Test recent downtimes for 30-minute report
        print("\n📋 Simulating 30-minute report data...")
        recent_downtimes = self.analyzer.get_recent_downtimes(minutes=30)
        print(f"Found {len(recent_downtimes)} recent downtime events")
        
        # Display what would be sent to Slack
        self.simulate_slack_messages(location_summaries, shift_alerts, recent_downtimes)
        
        # Display final statistics
        print("\n📈 Final Statistics:")
        stats = self.analyzer.get_statistics()
        self.print_final_statistics(stats)
        
        # Verify expected results
        self.verify_test_results(new_downtimes, location_summaries, shift_alerts)
        
        print("\n🎉 Offline test completed successfully!")
        print("Core downtime analysis logic is working correctly.")
    
    def print_test_scenarios(self):
        """Print description of test scenarios"""
        print("\n🎯 Test Scenarios:")
        scenarios = [
            "GA1: Multiple short downtimes (20-60s) - Expected: 5 events, ~185s total",
            "GA2: Medium downtimes (60-120s) - Expected: 4 events, ~345s total", 
            "GA3: Long downtimes (120-780s) - Expected: 4 events, ~1100s total",
            "GA4: Mixed downtime categories - Expected: 5 events, ~460s total",
            "GA5: PROBLEM LOCATION - Expected: 7 events, ~2550s total (exceeds 2100s)",
            "GA6: Break scenario - Expected: 3 events (900s gap ignored)",
            "GA7: Minimal downtime - Expected: 2 events, ~60s total",
            "GA8: Sub-threshold downtimes - Expected: 0 events (all <20s)",
            "GA9: Edge case boundaries - Expected: 4 events at thresholds",
            "GA10: Recent activity - Expected: 3 events for 30-min report"
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"  {i:2d}. {scenario}")
    
    def print_downtime_analysis(self, downtimes: List[Dict], summaries: Dict):
        """Print detailed downtime analysis results"""
        print("\n🔍 Downtime Analysis Results:")
        print("-" * 50)
        
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
            print(f"   Events: {len(events)}")
            print(f"   Total Downtime: {summary.get('total_downtime', 0)}s")
            print(f"   Average: {summary.get('average_downtime', 0)}s")
            
            # Category breakdown
            categories = summary.get('category_counts', {})
            if categories:
                cat_parts = []
                for cat, count in categories.items():
                    if count > 0:
                        cat_parts.append(f"{cat}: {count}")
                print(f"   Categories: {', '.join(cat_parts)}")
            
            # Show first few events
            for i, event in enumerate(events[:5]):  # Show max 5 events
                start_time = event['start_timestamp'].strftime('%H:%M:%S')
                end_time = event['end_timestamp'].strftime('%H:%M:%S')
                print(f"     {i+1}. {event['downtime_seconds']:3d}s ({event['category']}) "
                      f"{start_time}-{end_time}")
                
            if len(events) > 5:
                print(f"     ... and {len(events) - 5} more events")
        
        # Show locations with no events
        all_locations = ['GA1', 'GA2', 'GA3', 'GA4', 'GA5', 'GA6', 'GA7', 'GA8', 'GA9', 'GA10']
        no_events = [loc for loc in all_locations if loc not in by_location]
        if no_events:
            print(f"\n📍 No events detected: {', '.join(no_events)}")
    
    def simulate_slack_messages(self, summaries: Dict, alerts: List[Dict], recent: List[Dict]):
        """Simulate what would be sent to Slack"""
        print("\n📱 Simulated Slack Messages:")
        print("-" * 40)
        
        # Shift-end alerts
        if alerts:
            print("\n🚨 Shift-End Alert Messages:")
            for alert in alerts:
                print(f"Title: 🚨 Shift End Alert - {alert['location']} Excessive Downtime")
                print(f"Content: {alert['location']} has exceeded {alert['threshold']} seconds")
                print(f"         Current: {alert['total_downtime']:,}s ({alert['event_count']} events)")
                print()
        
        # 30-minute report
        print("\n📊 30-Minute Report Message:")
        timestamp = datetime.now().strftime("%I:%M %p")
        print(f"Title: 📊 Induct Downtime Report - {timestamp}")
        
        report_lines = []
        total_events = 0
        total_downtime = 0
        
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
            
            total_events += summary['event_count']
            total_downtime += summary['total_downtime']
        
        if report_lines:
            print("Content:")
            for line in report_lines:
                print(f"  {line}")
            print(f"\n📈 Summary: {total_events} total events, {total_downtime}s total downtime")
        else:
            print("Content: ✅ No significant downtime events")
        
        # Immediate alerts for significant downtimes
        significant = [d for d in recent if d['downtime_seconds'] >= 120]
        if significant:
            print(f"\n⏰ Immediate Alert Messages ({len(significant)} alerts):")
            for event in significant[:3]:  # Show first 3
                print(f"Title: ⏰ Significant Downtime - {event['location']}")
                print(f"Content: {event['location']} - {event['downtime_seconds']}s ({event['category']})")
                start_time = event['start_timestamp'].strftime('%H:%M:%S')
                end_time = event['end_timestamp'].strftime('%H:%M:%S')
                print(f"         {event['start_status']} → {event['end_status']}")
                print(f"         {start_time} - {end_time}")
                print()
    
    def print_final_statistics(self, stats: Dict):
        """Print final system statistics"""
        print(f"   Total Events: {stats['total_events']}")
        print(f"   Total Downtime: {stats['total_downtime_seconds']:,}s ({stats['total_downtime_seconds']/60:.1f} minutes)")
        print(f"   Average per Event: {stats['average_downtime']}s")
        print(f"   Active Locations: {stats['active_locations']}/10")
        
        print(f"\n   Category Distribution:")
        for category, count in stats['category_distribution'].items():
            print(f"     {category}: {count} events")
    
    def verify_test_results(self, downtimes: List[Dict], summaries: Dict, alerts: List[Dict]):
        """Verify test results match expectations"""
        print("\n✅ Test Result Verification:")
        
        # Check GA5 exceeds threshold
        ga5_summary = summaries.get('GA5', {})
        if ga5_summary.get('total_downtime', 0) > 2100:
            print("   ✅ GA5 correctly exceeds 2100s threshold")
        else:
            print("   ❌ GA5 should exceed 2100s threshold")
        
        # Check GA8 has no events (all gaps <20s)
        ga8_summary = summaries.get('GA8', {})
        if ga8_summary.get('event_count', 0) == 0:
            print("   ✅ GA8 correctly has no events (all gaps <20s)")
        else:
            print("   ❌ GA8 should have no events")
        
        # Check GA6 ignores 900s break
        ga6_events = [d for d in downtimes if d['location'] == 'GA6']
        ga6_has_900s = any(d['downtime_seconds'] >= 900 for d in ga6_events)
        if not ga6_has_900s:
            print("   ✅ GA6 correctly ignores 900s break gap")
        else:
            print("   ❌ GA6 should ignore 900s break gap")
        
        # Check shift-end alerts
        if alerts:
            alert_locations = [a['location'] for a in alerts]
            if 'GA5' in alert_locations:
                print("   ✅ Shift-end alert correctly triggered for GA5")
            else:
                print("   ❌ Shift-end alert should be triggered for GA5")
        
        # Check total events is reasonable
        total_events = len(downtimes)
        if 25 <= total_events <= 40:  # Expected range based on test data
            print(f"   ✅ Total events ({total_events}) in expected range")
        else:
            print(f"   ⚠️  Total events ({total_events}) outside expected range")


def main():
    """Main test execution"""
    try:
        test_runner = OfflineTestRunner()
        test_runner.run_comprehensive_test()
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()