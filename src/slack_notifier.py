"""
Slack Notification Module
Sends formatted notifications to Slack webhook for downtime monitoring
"""

import json
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional


class SlackNotifier:
    """Handles Slack notifications for induct downtime monitoring"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.logger = logging.getLogger(__name__)
    
    def send_notification(self, message: str, content2: str = None) -> bool:
        """Send notification to Slack workflow"""
        try:
            # Workflow builder expects 'text' field
            if content2:
                full_message = f"{message}\n\n{content2}"
            else:
                full_message = message
                
            payload = {
                "text": full_message  # Changed from "Content" to "text"
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            response.raise_for_status()
            self.logger.info(f"Slack notification sent successfully")
            return True
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to send Slack notification: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response content: {e.response.text}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending notification: {e}")
            return False
    
    def send_30_minute_report(self, location_summaries: Dict, timestamp: str = None) -> bool:
        """Send 30-minute downtime report"""
        if not timestamp:
            timestamp = datetime.now().strftime("%I:%M %p")
        
        title = f"📊 Induct Downtime Report - {timestamp}"
        
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
                categories.append(f"20-60: {category_counts['20-60']}")
            if category_counts.get('60-120', 0) > 0:
                categories.append(f"60-120: {category_counts['60-120']}")
            if category_counts.get('120-780', 0) > 0:
                categories.append(f"120-780: {category_counts['120-780']}")
            
            category_str = f"({', '.join(categories)})" if categories else ""
            
            report_lines.append(
                f"{location}: {event_count} events {category_str} Total: {total_time}s"
            )
            
            total_events += event_count
            total_downtime += total_time
        
        if not report_lines:
            content2 = "✅ No significant downtime events in the last 30 minutes"
        else:
            content2 = "\n".join(report_lines)
            content2 += f"\n\n📈 Summary: {total_events} total events, {total_downtime}s total downtime"
        
        return self.send_notification(title, content2)
    
    def send_shift_end_alert(self, alerts: List[Dict]) -> bool:
        """Send shift-end excessive downtime alerts"""
        if not alerts:
            return True
        
        for alert in alerts:
            title = f"🚨 Shift End Alert - {alert['location']} Excessive Downtime"
            content2 = (
                f"{alert['location']} has exceeded {alert['threshold']} seconds of downtime\n"
                f"Current: {alert['total_downtime']:,}s ({alert['event_count']} events)"
            )
            
            success = self.send_notification(title, content2)
            if not success:
                return False
        
        return True
    
    def send_system_alert(self, alert_type: str, message: str, details: str = None) -> bool:
        """Send system-level alerts (errors, warnings, etc.)"""
        icons = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'success': '✅'
        }
        
        icon = icons.get(alert_type.lower(), '🔔')
        title = f"{icon} System Alert - {message}"
        
        return self.send_notification(title, details)
    
    def send_downtime_alert(self, event: Dict) -> bool:
        """Send immediate alert for significant downtime events"""
        # Only alert for longer downtimes (>120s)
        if event['downtime_seconds'] < 120:
            return True
        
        title = f"⏰ Significant Downtime - {event['location']}"
        content2 = (
            f"Location: {event['location']}\n"
            f"Duration: {event['downtime_seconds']}s ({event['category']})\n"
            f"From: {event['start_status']} → {event['end_status']}\n"
            f"Time: {event['start_timestamp'].strftime('%H:%M:%S')} - "
            f"{event['end_timestamp'].strftime('%H:%M:%S')}"
        )
        
        return self.send_notification(title, content2)
    
    def send_shift_summary(self, location_summaries: Dict, shift_start: str, shift_end: str) -> bool:
        """Send end-of-shift summary report"""
        title = f"📋 Shift Summary Report ({shift_start} - {shift_end})"
        
        # Calculate totals
        total_events = sum(s['event_count'] for s in location_summaries.values())
        total_downtime = sum(s['total_downtime'] for s in location_summaries.values())
        active_locations = len([l for l, s in location_summaries.items() if s['event_count'] > 0])
        
        # Build detailed report
        report_lines = [
            f"🎯 Shift Overview:",
            f"  • Total downtime events: {total_events}",
            f"  • Total downtime: {total_downtime:,}s ({total_downtime/60:.1f} minutes)",
            f"  • Active locations: {active_locations}/10",
            f"  • Average per location: {total_downtime/10:.0f}s",
            "",
            f"📊 Location Breakdown:"
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
                f"  • {location}: {summary['total_downtime']:,}s "
                f"({summary['event_count']} events, avg: {avg_downtime}s)"
            )
            
            # Add category breakdown for locations with many events
            if summary['event_count'] >= 3:
                categories = []
                for cat, count in category_counts.items():
                    if count > 0:
                        categories.append(f"{cat}: {count}")
                if categories:
                    report_lines.append(f"    └ {', '.join(categories)}")
        
        content2 = "\n".join(report_lines)
        return self.send_notification(title, content2)
    
    def test_connection(self) -> bool:
        """Test Slack webhook connection"""
        test_message = "🧪 Test notification from Induct Downtime Monitor"
        test_details = f"Connection test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
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