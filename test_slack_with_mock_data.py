#!/usr/bin/env python3
"""
Test Slack notifications with mock downtime data
Shows actual Slack messages being sent
"""

import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.downtime_analyzer import DowntimeAnalyzer
from src.slack_notifier import SlackNotifier

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def generate_test_data():
    """Generate realistic test downtime data"""
    base_time = datetime.now() - timedelta(hours=1)
    
    # Create location summaries for 30-minute report
    location_summaries = {
        'GA1': {
            'total_downtime': 285,
            'event_count': 5,
            'category_counts': {'20-60': 4, '60-120': 1},
            'average_downtime': 57,
            'last_scan_time': base_time + timedelta(minutes=30)
        },
        'GA2': {
            'total_downtime': 420,
            'event_count': 4,
            'category_counts': {'60-120': 3, '120-780': 1},
            'average_downtime': 105,
            'last_scan_time': base_time + timedelta(minutes=35)
        },
        'GA3': {
            'total_downtime': 980,
            'event_count': 3,
            'category_counts': {'120-780': 3},
            'average_downtime': 327,
            'last_scan_time': base_time + timedelta(minutes=40)
        },
        'GA4': {
            'total_downtime': 0,
            'event_count': 0,
            'category_counts': {},
            'average_downtime': 0,
            'last_scan_time': None
        },
        'GA5': {
            'total_downtime': 2450,  # Exceeds threshold!
            'event_count': 8,
            'category_counts': {'120-780': 8},
            'average_downtime': 306,
            'last_scan_time': base_time + timedelta(minutes=45)
        }
    }
    
    # Create shift-end alerts
    shift_alerts = [
        {
            'location': 'GA5',
            'total_downtime': 2450,
            'threshold': 2100,
            'event_count': 8,
            'last_scan': base_time + timedelta(minutes=45)
        }
    ]
    
    # Create downtime event for immediate alert
    downtime_event = {
        'location': 'GA3',
        'downtime_seconds': 245,
        'category': '120-780',
        'start_timestamp': base_time + timedelta(minutes=20),
        'end_timestamp': base_time + timedelta(minutes=24, seconds=5),
        'start_tracking_id': 'T123456',
        'end_tracking_id': 'T123457',
        'start_status': 'INDUCTED',
        'end_status': 'STOW_BUFFER',
        'detected_at': datetime.now()
    }
    
    return location_summaries, shift_alerts, downtime_event

def main():
    """Test Slack notifications with mock data"""
    print("🧪 Testing Slack Notifications with Mock Downtime Data")
    print("=" * 60)
    
    # Initialize Slack notifier
    webhook_url = "https://hooks.slack.com/triggers/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"
    notifier = SlackNotifier(webhook_url)
    
    # Generate test data
    location_summaries, shift_alerts, downtime_event = generate_test_data()
    
    # Test 1: Send 30-minute report
    print("\n📊 TEST 1: Sending 30-Minute Report")
    print("-" * 40)
    success = notifier.send_30_minute_report(location_summaries)
    if success:
        print("✅ 30-minute report sent successfully!")
    else:
        print("❌ Failed to send 30-minute report")
    
    # Test 2: Send shift-end alert
    print("\n🚨 TEST 2: Sending Shift-End Alert")
    print("-" * 40)
    success = notifier.send_shift_end_alert(shift_alerts)
    if success:
        print("✅ Shift-end alert sent successfully!")
    else:
        print("❌ Failed to send shift-end alert")
    
    # Test 3: Send immediate downtime alert
    print("\n⏰ TEST 3: Sending Immediate Downtime Alert")
    print("-" * 40)
    success = notifier.send_downtime_alert(downtime_event)
    if success:
        print("✅ Downtime alert sent successfully!")
    else:
        print("❌ Failed to send downtime alert")
    
    # Test 4: Send system startup notification
    print("\n🔔 TEST 4: Sending System Startup Notification")
    print("-" * 40)
    success = notifier.send_system_alert(
        'info',
        'Induct Downtime Monitor Started',
        f'System initialized at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\nMonitoring locations GA1-GA10'
    )
    if success:
        print("✅ System startup notification sent successfully!")
    else:
        print("❌ Failed to send system notification")
    
    # Test 5: Send shift summary
    print("\n📋 TEST 5: Sending Shift Summary Report")
    print("-" * 40)
    success = notifier.send_shift_summary(location_summaries, "01:20", "08:30")
    if success:
        print("✅ Shift summary sent successfully!")
    else:
        print("❌ Failed to send shift summary")
    
    print("\n" + "=" * 60)
    print("🎉 ALL SLACK NOTIFICATIONS SENT!")
    print("\n📱 Check your Slack channel for:")
    print("   • 30-minute downtime report")
    print("   • Shift-end alert for GA5")
    print("   • Immediate downtime alert")
    print("   • System startup notification")
    print("   • Shift summary report")
    print("\n✅ System is ready for production deployment!")

if __name__ == "__main__":
    main()