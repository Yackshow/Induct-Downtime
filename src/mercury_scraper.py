# -*- coding: utf-8 -*-
"""
Mercury Dashboard Scraper
Scrapes Amazon Mercury dashboard for induct station data
"""

import json
import logging
import time
import re
from datetime import datetime

# Handle requests import with urllib3 compatibility issue
try:
    import requests
    from requests.exceptions import RequestException
    REQUESTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Requests not available ({e})")
    REQUESTS_AVAILABLE = False
    # Define dummy classes for type safety
    class RequestException(Exception):
        pass

# Try to import BeautifulSoup, fall back to simple parsing if not available
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("Warning: BeautifulSoup4 not available, using simple HTML parsing fallback")

from .auth import MidwayAuth


class MercuryScraper:
    """Scrapes Mercury dashboard for induct station scan data"""
    
    def __init__(self, mercury_url, valid_locations, valid_statuses, cookie_path="~/.midway/cookie"):
        self.mercury_url = mercury_url
        self.valid_locations = set(valid_locations)
        self.valid_statuses = set(valid_statuses)
        self.auth = MidwayAuth(cookie_path=cookie_path)
        self.session = None
        self.logger = logging.getLogger(__name__)
        
    def _get_session(self):
        """Get authenticated session"""
        if not REQUESTS_AVAILABLE:
            self.logger.error("Requests library not available due to urllib3/OpenSSL compatibility issue")
            return None
            
        if not self.session:
            self.session = self.auth.get_authenticated_session()
        return self.session
    
    def scrape_data(self):
        """Scrape Mercury dashboard data"""
        session = self._get_session()
        if not session:
            self.logger.error("Failed to get authenticated session")
            return None
            
        try:
            self.logger.info("Scraping Mercury data from {}".format(self.mercury_url))
            response = session.get(self.mercury_url, timeout=30)
            response.raise_for_status()
            
            # Extract from HTML
            records = self._extract_records(response.text)
            self.logger.info("Extracted {} valid records".format(len(records)))
            
            return records
            
        except RequestException as e:
            self.logger.error("Request failed: {}".format(e))
            return None
        except Exception as e:
            self.logger.error("Scraping error: {}".format(e))
            return None
    
    def _extract_records(self, html_content):
        """Extract records from HTML table"""
        records = []
        
        if BS4_AVAILABLE:
            return self._extract_records_bs4(html_content)
        else:
            return self._extract_records_fallback(html_content)
    
    def _extract_records_bs4(self, html_content):
        """Extract records using BeautifulSoup"""
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
            self.logger.error("Missing required columns: {}".format(missing_columns))
            # Fallback to hardcoded indices based on sample
            column_map = {
                'status': 26,      # compLastScanInOrder.internalStatusCode
                'tracking_id': 3,  # trackingId
                'location': 12,    # Induct.destination.id
                'timestamp': 4     # lastScanInOrder.timestamp
            }
            self.logger.info("Using fallback column mapping: {}".format(column_map))
        
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
                self.logger.debug("Error parsing row: {}".format(e))
                continue
        
        return records
    
    def _extract_records_fallback(self, html_content):
        """Extract records using simple regex parsing (fallback when BeautifulSoup not available)"""
        records = []
        
        try:
            # Simple regex approach - look for table rows
            # This is a basic fallback that may not work perfectly with complex HTML
            self.logger.info("Using fallback HTML parsing (BeautifulSoup not available)")
            
            # Use hardcoded column positions based on known Mercury table structure
            column_map = {
                'status': 26,      # compLastScanInOrder.internalStatusCode
                'tracking_id': 3,  # trackingId
                'location': 12,    # Induct.destination.id
                'timestamp': 4     # lastScanInOrder.timestamp
            }
            
            # Find table rows using simple regex
            tr_pattern = r'<tr[^>]*>(.*?)</tr>'
            rows = re.findall(tr_pattern, html_content, re.DOTALL | re.IGNORECASE)
            
            self.logger.info("Found {} table rows with fallback parsing".format(len(rows)))
            
            for row_html in rows[1:]:  # Skip header row
                # Extract cell contents
                td_pattern = r'<td[^>]*>(.*?)</td>'
                cells = re.findall(td_pattern, row_html, re.DOTALL | re.IGNORECASE)
                
                if len(cells) <= max(column_map.values()):
                    continue
                
                try:
                    # Extract data using column mapping
                    status = self._clean_html_text(cells[column_map['status']])
                    tracking_id = self._clean_html_text(cells[column_map['tracking_id']])
                    location = self._clean_html_text(cells[column_map['location']])
                    timestamp_str = self._clean_html_text(cells[column_map['timestamp']])
                    
                    # Validate the data
                    if not all([status, tracking_id, location, timestamp_str]):
                        continue
                    
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
                    
                except (IndexError, ValueError) as e:
                    self.logger.debug("Error parsing row with fallback: {}".format(e))
                    continue
            
            self.logger.info("Extracted {} valid records using fallback parsing".format(len(records)))
            return records
            
        except Exception as e:
            self.logger.error("Fallback parsing failed: {}".format(e))
            return []
    
    def _clean_html_text(self, html_text):
        """Remove HTML tags and clean up text"""
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', html_text)
        # Clean up whitespace
        clean_text = ' '.join(clean_text.split())
        return clean_text.strip()
    
    def _parse_timestamp(self, timestamp_str):
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
                
        self.logger.warning("Could not parse timestamp: {}".format(timestamp_str))
        return None
    
    def scrape_with_retry(self, max_retries= 3, delay= 5):
        """Scrape data with retry logic"""
        for attempt in range(max_retries):
            try:
                data = self.scrape_data()
                if data is not None:
                    return data
                    
            except Exception as e:
                self.logger.warning("Scrape attempt {} failed: {}".format(attempt + 1, e))
                
            if attempt < max_retries - 1:
                self.logger.info("Retrying in {} seconds...".format(delay))
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
        valid_statuses=['INDUCTED', 'INDUCT', 'STOW_BUFFER', 'AT_STATION'],
        cookie_path=config['auth']['cookie_path']
    )
    
    # Test scraping
    if '--test' in sys.argv:
        print("🔍 Testing Mercury scraper...")
        data = scraper.scrape_with_retry()
        
        if data:
            print("✅ Successfully scraped {} records".format(len(data)))
            if data:
                print("📊 Sample record:")
                print(json.dumps(data[0], indent=2))
        else:
            print("❌ Scraping failed")
    else:
        print("Use --test flag to test scraper")


if __name__ == "__main__":
    main()