# -*- coding: utf-8 -*-
"""
Slack Notification Module
Sends formatted notifications to Slack webhook for downtime monitoring
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Handle requests import with urllib3 compatibility issue
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Requests not available ({e})")
    REQUESTS_AVAILABLE = False


class SlackNotifier:
    """Handles Slack notifications for induct downtime monitoring"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.logger = logging.getLogger(__name__)
    
    def send_notification(self, message: str, content2: str = None) -> bool:
        """Send notification to Slack workflow"""
        if not REQUESTS_AVAILABLE:
            self.logger.warning("Requests library not available - cannot send Slack notification")
            print(f"[MOCK SLACK] {message}")
            if content2:
                print(f"[MOCK SLACK DETAILS] {content2}")
            return False
            
        try:
            # Slack workflow builder expects 'Content' and 'Content2' fields
            payload = {
                "Content": message,
                "Content2": content2 if content2 else ""
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            response.raise_for_status()
            self.logger.info("Slack notification sent successfully")
            return True
            
        except requests.RequestException as e:
            self.logger.error("Failed to send Slack notification: {}".format(e))
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error("Response content: {}".format(e.response.text))
            return False
        except Exception as e:
            self.logger.error("Unexpected error sending notification: {}".format(e))
            return False
    
    def send_30_minute_report(self, location_summaries, timestamp=None):
        """Send 30-minute downtime report"""
        if not timestamp:
            timestamp = datetime.now().strftime("%I:%M %p")
        
        title = "📊 Induct Downtime Report - {}".format(timestamp)
        
        # Build report content
        report_lines = []
        total_events = 0
        total_downtime = 0
        
        for location, summary in sorted(location_summaries.items()):
            if summary['event_count'] == 0:
                continue
                
            event_count = summary['event_count']
            total_time = summary['total_downtime']
            category_counts = summary.get('category_counts', {})
            
            # Format category breakdown
            categories = []
            if category_counts.get('20-60', 0) > 0:
                categories.append("20-60: {}".format(category_counts['20-60']))
            if category_counts.get('60-120', 0) > 0:
                categories.append("60-120: {}".format(category_counts['60-120']))
            if category_counts.get('120-780', 0) > 0:
                categories.append("120-780: {}".format(category_counts['120-780']))
            
            category_str = "({})".format(', '.join(categories)) if categories else ""
            
            report_lines.append(
                "{}: {} events {} Total: {}s".format(location, event_count, category_str, total_time)
            )
            
            total_events += event_count
            total_downtime += total_time
        
        if not report_lines:
            content2 = "✅ No significant downtime events in the last 30 minutes"
        else:
            content2 = "\n".join(report_lines)
            content2 += "\n\n📈 Summary: {} total events, {}s total downtime".format(total_events, total_downtime)
        
        return self.send_notification(title, content2)
    
    def send_shift_end_alert(self, alerts):
        """Send shift-end excessive downtime alerts"""
        if not alerts:
            return True
        
        for alert in alerts:
            title = "🚨 Shift End Alert - {} Excessive Downtime".format(alert['location'])
            content2 = (
                "{} has exceeded {} seconds of downtime\n".format(alert['location'], alert['threshold']) +
                "Current: {:,}s ({} events)".format(alert['total_downtime'], alert['event_count'])
            )
            
            success = self.send_notification(title, content2)
            if not success:
                return False
        
        return True
    
    def send_system_alert(self, alert_type, message, details=None):
        """Send system-level alerts (errors, warnings, etc.)"""
        icons = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'success': '✅'
        }
        
        icon = icons.get(alert_type.lower(), '🔔')
        title = "{} System Alert - {}".format(icon, message)
        
        return self.send_notification(title, details)
    
    def send_downtime_alert(self, event):
        """Send immediate alert for significant downtime events"""
        # Only alert for longer downtimes (>120s)
        if event['downtime_seconds'] < 120:
            return True
        
        title = "⏰ Significant Downtime - {}".format(event['location'])
        content2 = (
            "Location: {}\n".format(event['location']) +
            "Duration: {}s ({})\n".format(event['downtime_seconds'], event['category']) +
            "From: {} → {}\n".format(event['start_status'], event['end_status']) +
            "Time: {} - ".format(event['start_timestamp'].strftime('%H:%M:%S')) +
            "{}".format(event['end_timestamp'].strftime('%H:%M:%S'))
        )
        
        return self.send_notification(title, content2)
    
    def send_shift_summary(self, location_summaries, shift_start, shift_end):
        """Send end-of-shift summary report"""
        title = "📋 Shift Summary Report ({} - {})".format(shift_start, shift_end)
        
        # Calculate totals
        total_events = sum(s['event_count'] for s in location_summaries.values())
        total_downtime = sum(s['total_downtime'] for s in location_summaries.values())
        active_locations = len([l for l, s in location_summaries.items() if s['event_count'] > 0])
        
        # Build detailed report
        report_lines = [
            "🎯 Shift Overview:",
            "  • Total downtime events: {}".format(total_events),
            "  • Total downtime: {:,}s ({:.1f} minutes)".format(total_downtime, total_downtime/60),
            "  • Active locations: {}/10".format(active_locations),
            "  • Average per location: {:.0f}s".format(total_downtime/10),
            "",
            "📊 Location Breakdown:"
        ]
        
        # Sort locations by total downtime (worst first)
        sorted_locations = sorted(
            location_summaries.items(),
            key=lambda x: x[1]['total_downtime'],
            reverse=True
        )
        
        for location, summary in sorted_locations:
            if summary['event_count'] == 0:
                continue
                
            avg_downtime = summary['average_downtime']
            category_counts = summary.get('category_counts', {})
            
            report_lines.append(
                "  • {}: {:,}s ".format(location, summary['total_downtime']) +
                "({} events, avg: {}s)".format(summary['event_count'], avg_downtime)
            )
            
            # Add category breakdown for locations with many events
            if summary['event_count'] >= 3:
                categories = []
                for cat, count in category_counts.items():
                    if count > 0:
                        categories.append("{}: {}".format(cat, count))
                if categories:
                    report_lines.append("    └ {}".format(', '.join(categories)))
        
        content2 = "\n".join(report_lines)
        return self.send_notification(title, content2)
    
    def test_connection(self):
        """Test Slack webhook connection"""
        test_message = "🧪 Test notification from Induct Downtime Monitor"
        test_details = "Connection test at {}\n\nThis tests both Content and Content2 fields for the workflow builder.".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        return self.send_notification(test_message, test_details)


def main():
    """Test Slack notifier functionality"""
    import yaml
    from datetime import datetime, timedelta
    
    logging.basicConfig(level=logging.INFO)
    
    # Load configuration
    try:
        with open('/workspace/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ config.yaml not found")
        return
    
    # Initialize notifier
    notifier = SlackNotifier(config['slack']['webhook'])
    
    print("📱 Testing Slack notifications...")
    
    # Test basic connection
    if notifier.test_connection():
        print("✅ Connection test successful")
    else:
        print("❌ Connection test failed")
        return
    
    # Test 30-minute report
    test_summaries = {
        'GA1': {
            'total_downtime': 245,
            'event_count': 3,
            'category_counts': {'20-60': 2, '60-120': 1},
            'average_downtime': 82
        },
        'GA2': {
            'total_downtime': 85,
            'event_count': 2,
            'category_counts': {'20-60': 2},
            'average_downtime': 43
        },
        'GA3': {
            'total_downtime': 0,
            'event_count': 0,
            'category_counts': {},
            'average_downtime': 0
        }
    }
    
    print("📊 Sending test 30-minute report...")
    if notifier.send_30_minute_report(test_summaries):
        print("✅ 30-minute report sent")
    else:
        print("❌ 30-minute report failed")
    
    # Test shift-end alert
    test_alerts = [{
        'location': 'GA5',
        'total_downtime': 2245,
        'threshold': 2100,
        'event_count': 15
    }]
    
    print("🚨 Sending test shift-end alert...")
    if notifier.send_shift_end_alert(test_alerts):
        print("✅ Shift-end alert sent")
    else:
        print("❌ Shift-end alert failed")
    
    print("📱 Slack notification tests completed")


if __name__ == "__main__":
    main()