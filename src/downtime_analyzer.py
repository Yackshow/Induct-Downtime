# -*- coding: utf-8 -*-
"""
Downtime Analysis Engine
Calculates downtime between consecutive package scans at induct stations
"""

import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Optional, Any


class DowntimeAnalyzer:
    """Analyzes downtime between consecutive scans at the same location"""
    
    def __init__(self, categories: List[Dict], break_threshold: int = 780):
        self.categories = categories
        self.break_threshold = break_threshold
        self.location_trackers = defaultdict(lambda: {
            'last_scan': None,
            'downtimes': [],
            'total_downtime': 0,
            'category_counts': defaultdict(int)
        })
        self.logger = logging.getLogger(__name__)
    
    def process_scans(self, scans: List[Dict]) -> Dict[str, Any]:
        """Process new scans and calculate downtimes"""
        new_downtimes = []
        
        # Sort scans by timestamp to ensure proper ordering
        sorted_scans = sorted(scans, key=lambda x: x['timestamp'])
        
        for scan in sorted_scans:
            downtime_event = self._process_single_scan(scan)
            if downtime_event:
                new_downtimes.append(downtime_event)
        
        return {
            'new_downtimes': new_downtimes,
            'location_summaries': self._get_location_summaries()
        }
    
    def _process_single_scan(self, scan: Dict) -> Optional[Dict]:
        """Process a single scan and calculate downtime if applicable"""
        location = scan['location']
        timestamp = scan['timestamp']
        
        tracker = self.location_trackers[location]
        
        # If this is the first scan for this location, just record it
        if tracker['last_scan'] is None:
            tracker['last_scan'] = {
                'timestamp': timestamp,
                'tracking_id': scan['tracking_id'],
                'status': scan['status']
            }
            self.logger.debug(f"First scan recorded for {location}")
            return None
        
        # Calculate downtime
        downtime_seconds = (timestamp - tracker['last_scan']['timestamp']).total_seconds()
        
        # Ignore gaps longer than break threshold (likely breaks or shift changes)
        if downtime_seconds > self.break_threshold:
            self.logger.debug(f"Ignoring {downtime_seconds}s gap at {location} (exceeds break threshold)")
            tracker['last_scan'] = {
                'timestamp': timestamp,
                'tracking_id': scan['tracking_id'],
                'status': scan['status']
            }
            return None
        
        # Only track meaningful downtimes (>= 20 seconds based on roadmap)
        if downtime_seconds < 20:
            tracker['last_scan'] = {
                'timestamp': timestamp,
                'tracking_id': scan['tracking_id'],
                'status': scan['status']
            }
            return None
        
        # Categorize downtime
        category = self._categorize_downtime(downtime_seconds)
        
        # Create downtime event
        downtime_event = {
            'location': location,
            'downtime_seconds': int(downtime_seconds),
            'category': category,
            'start_timestamp': tracker['last_scan']['timestamp'],
            'end_timestamp': timestamp,
            'start_tracking_id': tracker['last_scan']['tracking_id'],
            'end_tracking_id': scan['tracking_id'],
            'start_status': tracker['last_scan']['status'],
            'end_status': scan['status'],
            'detected_at': datetime.now()
        }
        
        # Update tracker
        tracker['downtimes'].append(downtime_event)
        tracker['total_downtime'] += downtime_seconds
        tracker['category_counts'][category] += 1
        tracker['last_scan'] = {
            'timestamp': timestamp,
            'tracking_id': scan['tracking_id'],
            'status': scan['status']
        }
        
        self.logger.info(f"Downtime detected at {location}: {downtime_seconds}s ({category})")
        return downtime_event
    
    def _categorize_downtime(self, seconds: float) -> str:
        """Categorize downtime based on duration"""
        for category in self.categories:
            if category['min'] <= seconds <= category['max']:
                return category['name']
        
        # Handle edge cases
        if seconds < self.categories[0]['min']:
            return f"<{self.categories[0]['min']}"
        else:
            return f">{self.categories[-1]['max']}"
    
    def _get_location_summaries(self) -> Dict[str, Dict]:
        """Get summary statistics for all locations"""
        summaries = {}
        
        for location, tracker in self.location_trackers.items():
            summaries[location] = {
                'total_downtime': int(tracker['total_downtime']),
                'event_count': len(tracker['downtimes']),
                'category_counts': dict(tracker['category_counts']),
                'last_scan_time': tracker['last_scan']['timestamp'] if tracker['last_scan'] else None,
                'average_downtime': int(tracker['total_downtime'] / max(1, len(tracker['downtimes'])))
            }
        
        return summaries
    
    def get_recent_downtimes(self, minutes: int = 30) -> List[Dict]:
        """Get downtimes from the last N minutes"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent_downtimes = []
        
        for location, tracker in self.location_trackers.items():
            for downtime in tracker['downtimes']:
                if downtime['detected_at'] >= cutoff:
                    recent_downtimes.append(downtime)
        
        return sorted(recent_downtimes, key=lambda x: x['detected_at'], reverse=True)
    
    def check_shift_end_alerts(self, threshold: int = 2100) -> List[Dict]:
        """Check for locations exceeding shift-end downtime threshold"""
        alerts = []
        
        for location, tracker in self.location_trackers.items():
            if tracker['total_downtime'] > threshold:
                alerts.append({
                    'location': location,
                    'total_downtime': int(tracker['total_downtime']),
                    'threshold': threshold,
                    'event_count': len(tracker['downtimes']),
                    'last_scan': tracker['last_scan']['timestamp'] if tracker['last_scan'] else None
                })
        
        return alerts
    
    def reset_shift_data(self) -> None:
        """Reset tracking data for new shift"""
        self.logger.info("Resetting shift data")
        for location in self.location_trackers:
            self.location_trackers[location] = {
                'last_scan': None,
                'downtimes': [],
                'total_downtime': 0,
                'category_counts': defaultdict(int)
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        total_events = sum(len(tracker['downtimes']) for tracker in self.location_trackers.values())
        total_downtime = sum(tracker['total_downtime'] for tracker in self.location_trackers.values())
        
        # Category distribution
        category_totals = defaultdict(int)
        for tracker in self.location_trackers.values():
            for category, count in tracker['category_counts'].items():
                category_totals[category] += count
        
        return {
            'total_events': total_events,
            'total_downtime_seconds': int(total_downtime),
            'average_downtime': int(total_downtime / max(1, total_events)),
            'category_distribution': dict(category_totals),
            'active_locations': len([l for l, t in self.location_trackers.items() if t['last_scan']]),
            'location_summaries': self._get_location_summaries()
        }


def main():
    """Test downtime analyzer functionality"""
    import yaml
    from datetime import datetime, timedelta
    
    logging.basicConfig(level=logging.INFO)
    
    # Load configuration
    with open('/workspace/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize analyzer
    analyzer = DowntimeAnalyzer(
        categories=config['downtime']['categories'],
        break_threshold=config['downtime']['break_threshold']
    )
    
    # Test with sample data
    base_time = datetime.now()
    test_scans = [
        {'location': 'GA1', 'timestamp': base_time, 'tracking_id': 'T001', 'status': 'INDUCTED'},
        {'location': 'GA1', 'timestamp': base_time + timedelta(seconds=45), 'tracking_id': 'T002', 'status': 'INDUCTED'},
        {'location': 'GA2', 'timestamp': base_time + timedelta(seconds=30), 'tracking_id': 'T003', 'status': 'INDUCT'},
        {'location': 'GA1', 'timestamp': base_time + timedelta(seconds=150), 'tracking_id': 'T004', 'status': 'STOW_BUFFER'},
        {'location': 'GA2', 'timestamp': base_time + timedelta(seconds=95), 'tracking_id': 'T005', 'status': 'AT_STATION'},
    ]
    
    print("🧮 Testing downtime analyzer...")
    result = analyzer.process_scans(test_scans)
    
    print(f"✅ Processed {len(test_scans)} scans")
    print(f"📊 Found {len(result['new_downtimes'])} downtime events")
    
    if result['new_downtimes']:
        print("\n🔍 Downtime events:")
        for event in result['new_downtimes']:
            print(f"  {event['location']}: {event['downtime_seconds']}s ({event['category']})")
    
    print("\n📈 Statistics:")
    stats = analyzer.get_statistics()
    for key, value in stats.items():
        if key != 'location_summaries':
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()