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
from bs4 import BeautifulSoup

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
            
            # Extract from HTML
            records = self._extract_records(response.text)
            self.logger.info(f"Extracted {len(records)} valid records")
            
            return records
            
        except RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Scraping error: {e}")
            return None
    
    def _extract_records(self, html_content: str) -> List[Dict]:
        """Extract records from HTML table"""
        records = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all table rows
        rows = soup.find_all('tr')
        
        if not rows:
            self.logger.warning("No table rows found in HTML")
            return records
        
        # Find header row to map column indices
        header_row = rows[0]
        headers = [th.text.strip() for th in header_row.find_all('th')]
        
        # Map column names to indices
        column_map = {}
        for idx, header in enumerate(headers):
            if 'compLastScanInOrder.internalStatusCode' in header:
                column_map['status'] = idx
            elif header == 'trackingId':
                column_map['tracking_id'] = idx
            elif 'Induct.destination.id' in header:
                column_map['location'] = idx
            elif 'lastScanInOrder.timestamp' in header:
                column_map['timestamp'] = idx
        
        # Verify we have all required columns
        required_columns = ['status', 'tracking_id', 'location', 'timestamp']
        missing_columns = [col for col in required_columns if col not in column_map]
        
        if missing_columns:
            self.logger.error(f"Missing required columns: {missing_columns}")
            # Fallback to hardcoded indices based on sample
            column_map = {
                'status': 26,      # compLastScanInOrder.internalStatusCode
                'tracking_id': 3,  # trackingId
                'location': 12,    # Induct.destination.id
                'timestamp': 4     # lastScanInOrder.timestamp
            }
            self.logger.info(f"Using fallback column mapping: {column_map}")
        
        # Process data rows
        for row in rows[1:]:  # Skip header row
            cells = row.find_all('td')
            if not cells or len(cells) <= max(column_map.values()):
                continue
                
            try:
                # Extract values
                status = cells[column_map['status']].text.strip()
                tracking_id = cells[column_map['tracking_id']].text.strip()
                location = cells[column_map['location']].text.strip()
                timestamp_str = cells[column_map['timestamp']].text.strip()
                
                # Validate required fields
                if not all([status, tracking_id, location, timestamp_str]):
                    continue
                    
                # Filter by valid status and location
                if status not in self.valid_statuses or location not in self.valid_locations:
                    continue
                
                # Parse timestamp
                parsed_timestamp = self._parse_timestamp(timestamp_str)
                if not parsed_timestamp:
                    continue
                
                records.append({
                    'status': status,
                    'tracking_id': tracking_id,
                    'location': location,
                    'timestamp': parsed_timestamp,
                    'raw_timestamp': timestamp_str,
                    'scraped_at': datetime.now().isoformat()
                })
                
            except (IndexError, AttributeError) as e:
                self.logger.debug(f"Error parsing row: {e}")
                continue
        
        return records
    
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp from various formats"""
        if not timestamp_str:
            return None
            
        # Common timestamp formats to try
        formats = [
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
                
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