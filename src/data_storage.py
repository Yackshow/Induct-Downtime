"""
Data Storage Module
Handles both SQLite database and CSV file storage for induct downtime data
"""

import os
import csv
import sqlite3
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from pathlib import Path


class DataStorage:
    """Handles data storage operations for induct downtime monitoring"""
    
    def __init__(self, storage_type: str = "sqlite", base_path: str = "/workspace"):
        self.storage_type = storage_type.lower()
        self.base_path = Path(base_path)
        self.logger = logging.getLogger(__name__)
        
        # Ensure directories exist
        (self.base_path / "data" / "raw").mkdir(parents=True, exist_ok=True)
        (self.base_path / "data" / "analysis").mkdir(parents=True, exist_ok=True)
        
        if self.storage_type == "sqlite":
            self.db_path = self.base_path / "induct_downtime.db"
            self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Raw scans table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS raw_scans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tracking_id TEXT NOT NULL,
                        location TEXT NOT NULL,
                        status TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        raw_timestamp TEXT,
                        scraped_at DATETIME NOT NULL,
                        UNIQUE(tracking_id, timestamp)
                    )
                ''')
                
                # Downtime events table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS downtime_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        location TEXT NOT NULL,
                        downtime_seconds INTEGER NOT NULL,
                        category TEXT NOT NULL,
                        start_timestamp DATETIME NOT NULL,
                        end_timestamp DATETIME NOT NULL,
                        start_tracking_id TEXT NOT NULL,
                        end_tracking_id TEXT NOT NULL,
                        start_status TEXT NOT NULL,
                        end_status TEXT NOT NULL,
                        detected_at DATETIME NOT NULL
                    )
                ''')
                
                # Daily summaries table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_summaries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE NOT NULL,
                        location TEXT NOT NULL,
                        total_downtime INTEGER NOT NULL,
                        event_count INTEGER NOT NULL,
                        category_20_60 INTEGER DEFAULT 0,
                        category_60_120 INTEGER DEFAULT 0,
                        category_120_780 INTEGER DEFAULT 0,
                        average_downtime INTEGER NOT NULL,
                        created_at DATETIME NOT NULL,
                        UNIQUE(date, location)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_raw_scans_location_timestamp ON raw_scans(location, timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_downtime_events_location ON downtime_events(location)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_downtime_events_detected_at ON downtime_events(detected_at)')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def store_raw_scans(self, scans: List[Dict]) -> bool:
        """Store raw scan data"""
        if not scans:
            return True
            
        try:
            if self.storage_type == "sqlite":
                return self._store_scans_sqlite(scans)
            else:
                return self._store_scans_csv(scans)
        except Exception as e:
            self.logger.error(f"Failed to store raw scans: {e}")
            return False
    
    def _store_scans_sqlite(self, scans: List[Dict]) -> bool:
        """Store scans in SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for scan in scans:
                    cursor.execute('''
                        INSERT OR IGNORE INTO raw_scans 
                        (tracking_id, location, status, timestamp, raw_timestamp, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        scan['tracking_id'],
                        scan['location'],
                        scan['status'],
                        scan['timestamp'],
                        scan['raw_timestamp'],
                        scan['scraped_at']
                    ))
                
                conn.commit()
                self.logger.info(f"Stored {len(scans)} raw scans in database")
                return True
                
        except Exception as e:
            self.logger.error(f"SQLite storage error: {e}")
            return False
    
    def _store_scans_csv(self, scans: List[Dict]) -> bool:
        """Store scans in CSV files"""
        try:
            today = date.today().strftime('%Y-%m-%d')
            csv_path = self.base_path / "data" / "raw" / f"induct_raw_{today}.csv"
            
            # Check if file exists to determine if we need headers
            file_exists = csv_path.exists()
            
            with open(csv_path, 'a', newline='') as csvfile:
                fieldnames = ['tracking_id', 'location', 'status', 'timestamp', 'raw_timestamp', 'scraped_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerows(scans)
            
            self.logger.info(f"Stored {len(scans)} raw scans in CSV")
            return True
            
        except Exception as e:
            self.logger.error(f"CSV storage error: {e}")
            return False
    
    def store_downtime_events(self, events: List[Dict]) -> bool:
        """Store downtime events"""
        if not events:
            return True
            
        try:
            if self.storage_type == "sqlite":
                return self._store_events_sqlite(events)
            else:
                return self._store_events_csv(events)
        except Exception as e:
            self.logger.error(f"Failed to store downtime events: {e}")
            return False
    
    def _store_events_sqlite(self, events: List[Dict]) -> bool:
        """Store downtime events in SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for event in events:
                    cursor.execute('''
                        INSERT INTO downtime_events 
                        (location, downtime_seconds, category, start_timestamp, end_timestamp,
                         start_tracking_id, end_tracking_id, start_status, end_status, detected_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        event['location'],
                        event['downtime_seconds'],
                        event['category'],
                        event['start_timestamp'],
                        event['end_timestamp'],
                        event['start_tracking_id'],
                        event['end_tracking_id'],
                        event['start_status'],
                        event['end_status'],
                        event['detected_at']
                    ))
                
                conn.commit()
                self.logger.info(f"Stored {len(events)} downtime events in database")
                return True
                
        except Exception as e:
            self.logger.error(f"SQLite event storage error: {e}")
            return False
    
    def _store_events_csv(self, events: List[Dict]) -> bool:
        """Store downtime events in CSV"""
        try:
            today = date.today().strftime('%Y-%m-%d')
            csv_path = self.base_path / "data" / "analysis" / f"downtime_analysis_{today}.csv"
            
            file_exists = csv_path.exists()
            
            with open(csv_path, 'a', newline='') as csvfile:
                fieldnames = ['location', 'downtime_seconds', 'category', 'start_timestamp', 
                             'end_timestamp', 'start_tracking_id', 'end_tracking_id', 
                             'start_status', 'end_status', 'detected_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerows(events)
            
            self.logger.info(f"Stored {len(events)} downtime events in CSV")
            return True
            
        except Exception as e:
            self.logger.error(f"CSV event storage error: {e}")
            return False
    
    def get_recent_scans(self, location: str = None, hours: int = 1) -> List[Dict]:
        """Get recent scans from storage"""
        try:
            if self.storage_type == "sqlite":
                return self._get_recent_scans_sqlite(location, hours)
            else:
                return self._get_recent_scans_csv(location, hours)
        except Exception as e:
            self.logger.error(f"Failed to get recent scans: {e}")
            return []
    
    def _get_recent_scans_sqlite(self, location: str = None, hours: int = 1) -> List[Dict]:
        """Get recent scans from SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = '''
                    SELECT * FROM raw_scans 
                    WHERE timestamp > datetime('now', '-{} hours')
                '''.format(hours)
                
                if location:
                    query += ' AND location = ?'
                    cursor.execute(query + ' ORDER BY timestamp DESC', (location,))
                else:
                    cursor.execute(query + ' ORDER BY timestamp DESC')
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"SQLite query error: {e}")
            return []
    
    def _get_recent_scans_csv(self, location: str = None, hours: int = 1) -> List[Dict]:
        """Get recent scans from CSV files"""
        # For CSV, we'll read today's file
        today = date.today().strftime('%Y-%m-%d')
        csv_path = self.base_path / "data" / "raw" / f"induct_raw_{today}.csv"
        
        if not csv_path.exists():
            return []
        
        try:
            records = []
            cutoff = datetime.now() - timedelta(hours=hours)
            
            with open(csv_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Parse timestamp
                    try:
                        timestamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                    except:
                        continue
                    
                    # Filter by time
                    if timestamp <= cutoff:
                        continue
                    
                    # Filter by location if specified
                    if location and row['location'] != location:
                        continue
                    
                    row['timestamp'] = timestamp
                    records.append(row)
            
            return records
            
        except Exception as e:
            self.logger.error(f"CSV query error: {e}")
            return []
    
    def store_daily_summary(self, date_str: str, location_summaries: Dict) -> bool:
        """Store daily summary statistics"""
        try:
            if self.storage_type == "sqlite":
                return self._store_summary_sqlite(date_str, location_summaries)
            else:
                return self._store_summary_csv(date_str, location_summaries)
        except Exception as e:
            self.logger.error(f"Failed to store daily summary: {e}")
            return False
    
    def _store_summary_sqlite(self, date_str: str, location_summaries: Dict) -> bool:
        """Store daily summary in SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for location, summary in location_summaries.items():
                    category_counts = summary.get('category_counts', {})
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO daily_summaries 
                        (date, location, total_downtime, event_count, category_20_60, 
                         category_60_120, category_120_780, average_downtime, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        date_str,
                        location,
                        summary['total_downtime'],
                        summary['event_count'],
                        category_counts.get('20-60', 0),
                        category_counts.get('60-120', 0),
                        category_counts.get('120-780', 0),
                        summary['average_downtime'],
                        datetime.now()
                    ))
                
                conn.commit()
                self.logger.info(f"Stored daily summary for {date_str}")
                return True
                
        except Exception as e:
            self.logger.error(f"SQLite summary storage error: {e}")
            return False
    
    def _store_summary_csv(self, date_str: str, location_summaries: Dict) -> bool:
        """Store daily summary in CSV"""
        try:
            csv_path = self.base_path / "data" / "analysis" / f"daily_summary_{date_str}.csv"
            
            with open(csv_path, 'w', newline='') as csvfile:
                fieldnames = ['location', 'total_downtime', 'event_count', 'category_20_60',
                             'category_60_120', 'category_120_780', 'average_downtime']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for location, summary in location_summaries.items():
                    category_counts = summary.get('category_counts', {})
                    
                    writer.writerow({
                        'location': location,
                        'total_downtime': summary['total_downtime'],
                        'event_count': summary['event_count'],
                        'category_20_60': category_counts.get('20-60', 0),
                        'category_60_120': category_counts.get('60-120', 0),
                        'category_120_780': category_counts.get('120-780', 0),
                        'average_downtime': summary['average_downtime']
                    })
            
            self.logger.info(f"Stored daily summary CSV for {date_str}")
            return True
            
        except Exception as e:
            self.logger.error(f"CSV summary storage error: {e}")
            return False


def main():
    """Test data storage functionality"""
    import yaml
    from datetime import datetime, timedelta
    
    logging.basicConfig(level=logging.INFO)
    
    # Test with SQLite
    print("🗄️  Testing SQLite storage...")
    storage = DataStorage(storage_type="sqlite")
    
    # Test data
    test_scans = [
        {
            'tracking_id': 'TEST001',
            'location': 'GA1',
            'status': 'INDUCTED',
            'timestamp': datetime.now(),
            'raw_timestamp': '2025-06-13T10:00:00Z',
            'scraped_at': datetime.now().isoformat()
        }
    ]
    
    test_events = [
        {
            'location': 'GA1',
            'downtime_seconds': 45,
            'category': '20-60',
            'start_timestamp': datetime.now() - timedelta(seconds=45),
            'end_timestamp': datetime.now(),
            'start_tracking_id': 'TEST001',
            'end_tracking_id': 'TEST002',
            'start_status': 'INDUCTED',
            'end_status': 'INDUCTED',
            'detected_at': datetime.now()
        }
    ]
    
    # Test operations
    success1 = storage.store_raw_scans(test_scans)
    success2 = storage.store_downtime_events(test_events)
    
    print(f"✅ Raw scans stored: {success1}")
    print(f"✅ Events stored: {success2}")
    
    # Test CSV storage
    print("\n📄 Testing CSV storage...")
    csv_storage = DataStorage(storage_type="csv")
    
    success3 = csv_storage.store_raw_scans(test_scans)
    success4 = csv_storage.store_downtime_events(test_events)
    
    print(f"✅ CSV scans stored: {success3}")
    print(f"✅ CSV events stored: {success4}")


if __name__ == "__main__":
    main()