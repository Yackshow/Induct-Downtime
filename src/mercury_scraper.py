"""
Mercury Dashboard Scraper
Scrapes Amazon Mercury dashboard for induct station data
"""

import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional
import requests
from requests.exceptions import RequestException

from .auth import MidwayAuth


class MercuryScraper:
    """Scrapes Mercury dashboard for induct station scan data"""
    
    def __init__(self, mercury_url: str, valid_locations: List[str], valid_statuses: List[str]):
        self.mercury_url = mercury_url
        self.valid_locations = set(valid_locations)
        self.valid_statuses = set(valid_statuses)
        self.auth = MidwayAuth()
        self.session = None
        self.logger = logging.getLogger(__name__)
        
    def _get_session(self) -> Optional[requests.Session]:
        """Get authenticated session"""
        if not self.session:
            self.session = self.auth.get_authenticated_session()
        return self.session
    
    def scrape_data(self) -> Optional[List[Dict]]:
        """Scrape Mercury dashboard data"""
        session = self._get_session()
        if not session:
            self.logger.error("Failed to get authenticated session")
            return None
            
        try:
            self.logger.info(f"Scraping Mercury data from {self.mercury_url}")
            response = session.get(self.mercury_url, timeout=30)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Extract relevant records
            records = self._extract_records(data)
            self.logger.info(f"Extracted {len(records)} valid records")
            
            return records
            
        except RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Scraping error: {e}")
            return None
    
    def _extract_records(self, data: Dict) -> List[Dict]:
        """Extract and filter relevant records from Mercury response"""
        records = []
        
        try:
            # Handle different possible response structures
            if 'data' in data:
                raw_data = data['data']
            elif 'results' in data:
                raw_data = data['results']
            elif isinstance(data, list):
                raw_data = data
            else:
                raw_data = [data]
            
            for item in raw_data:
                record = self._parse_record(item)
                if record:
                    records.append(record)
                    
        except Exception as e:
            self.logger.error(f"Error extracting records: {e}")
            
        return records
    
    def _parse_record(self, item: Dict) -> Optional[Dict]:
        """Parse individual record and extract required fields"""
        try:
            # Extract key fields based on roadmap specifications
            status = self._get_nested_value(item, ['compLastScanInOrder', 'internalStatusCode'])
            tracking_id = self._get_nested_value(item, ['trackingId'])
            location = self._get_nested_value(item, ['Induct', 'destination', 'id'])
            timestamp = self._get_nested_value(item, ['lastScanInOrder', 'timestamp'])
            
            # Validate required fields
            if not all([status, tracking_id, location, timestamp]):
                return None
                
            # Filter by valid status and location
            if status not in self.valid_statuses or location not in self.valid_locations:
                return None
            
            # Parse timestamp
            parsed_timestamp = self._parse_timestamp(timestamp)
            if not parsed_timestamp:
                return None
            
            return {
                'status': status,
                'tracking_id': tracking_id,
                'location': location,
                'timestamp': parsed_timestamp,
                'raw_timestamp': timestamp,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.debug(f"Error parsing record: {e}")
            return None
    
    def _get_nested_value(self, data: Dict, keys: List[str]) -> Optional[str]:
        """Safely get nested dictionary value"""
        try:
            current = data
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            return str(current) if current is not None else None
        except:
            return None
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp from various formats"""
        if not timestamp_str:
            return None
            
        # Common timestamp formats to try
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # Try parsing as epoch timestamp
        try:
            if timestamp_str.isdigit():
                epoch = int(timestamp_str)
                if epoch > 1000000000:  # Reasonable epoch range
                    return datetime.fromtimestamp(epoch)
        except:
            pass
            
        self.logger.warning(f"Could not parse timestamp: {timestamp_str}")
        return None
    
    def scrape_with_retry(self, max_retries: int = 3, delay: int = 5) -> Optional[List[Dict]]:
        """Scrape data with retry logic"""
        for attempt in range(max_retries):
            try:
                data = self.scrape_data()
                if data is not None:
                    return data
                    
            except Exception as e:
                self.logger.warning(f"Scrape attempt {attempt + 1} failed: {e}")
                
            if attempt < max_retries - 1:
                self.logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
                
        self.logger.error("All scrape attempts failed")
        return None


def main():
    """Test Mercury scraper functionality"""
    import sys
    import yaml
    
    logging.basicConfig(level=logging.INFO)
    
    # Load configuration
    try:
        with open('/workspace/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ config.yaml not found")
        sys.exit(1)
    
    # Initialize scraper
    scraper = MercuryScraper(
        mercury_url=config['mercury']['url'],
        valid_locations=config['locations']['valid'],
        valid_statuses=['INDUCTED', 'INDUCT', 'STOW_BUFFER', 'AT_STATION']
    )
    
    # Test scraping
    if '--test' in sys.argv:
        print("🔍 Testing Mercury scraper...")
        data = scraper.scrape_with_retry()
        
        if data:
            print(f"✅ Successfully scraped {len(data)} records")
            if data:
                print("📊 Sample record:")
                print(json.dumps(data[0], indent=2))
        else:
            print("❌ Scraping failed")
    else:
        print("Use --test flag to test scraper")


if __name__ == "__main__":
    main()