#!/usr/bin/env python3
"""Debug script to analyze full Mercury response and check data completeness"""

import sys
import json
import logging
from collections import Counter, defaultdict
sys.path.insert(0, '.')

from src.auth import MidwayAuth
from src.mercury_scraper import MercuryScraper

def analyze_mercury_data():
    """Comprehensive analysis of Mercury data"""
    
    print("🔍 Mercury Data Analysis")
    print("=" * 60)
    
    # Initialize scraper
    scraper = MercuryScraper(
        mercury_url="https://mercury.amazon.com/getQueryResponse?ID=127de24b92c1f65c47f001541fbc6974&region=na",
        valid_locations=['GA1', 'GA2', 'GA3', 'GA4', 'GA5', 'GA6', 'GA7', 'GA8', 'GA9', 'GA10'],
        valid_statuses=['INDUCTED', 'INDUCT', 'STOW_BUFFER', 'AT_STATION']
    )
    
    # Get raw HTML response
    session = scraper._get_session()
    if not session:
        print("❌ Failed to get authenticated session")
        return
    
    print("📥 Fetching raw Mercury response...")
    response = session.get(scraper.mercury_url, timeout=30)
    print(f"Response status: {response.status_code}")
    print(f"Response size: {len(response.text)} characters")
    
    # Save raw response for inspection
    with open('raw_mercury_response.html', 'w') as f:
        f.write(response.text)
    print("💾 Saved raw response to raw_mercury_response.html")
    
    # Parse with original scraper (filtered)
    print("\n🔄 Analyzing filtered data...")
    filtered_records = scraper._extract_records(response.text)
    print(f"Filtered records: {len(filtered_records)}")
    
    # Now let's analyze without filters to see ALL data
    print("\n🔄 Analyzing ALL data (no filters)...")
    
    # Create a version without filters
    unfiltered_scraper = MercuryScraper(
        mercury_url=scraper.mercury_url,
        valid_locations=[],  # Empty = accept all
        valid_statuses=[]    # Empty = accept all
    )
    
    # Temporarily override the filter logic
    all_records = analyze_without_filters(response.text)
    
    print(f"\n📊 COMPARISON:")
    print(f"Total records found: {len(all_records)}")
    print(f"Filtered records: {len(filtered_records)}")
    print(f"Filtered out: {len(all_records) - len(filtered_records)}")
    
    # Analyze by status
    print(f"\n📈 STATUS BREAKDOWN:")
    status_counts = Counter(record.get('status', 'UNKNOWN') for record in all_records)
    for status, count in status_counts.most_common():
        in_filter = status in scraper.valid_statuses
        print(f"  {status}: {count} {'✅' if in_filter else '❌'}")
    
    # Analyze by location
    print(f"\n🏪 LOCATION BREAKDOWN:")
    location_counts = Counter(record.get('location', 'UNKNOWN') for record in all_records)
    
    # Show GA locations first
    ga_locations = sorted([loc for loc in location_counts.keys() if loc.startswith('GA')])
    for location in ga_locations:
        count = location_counts[location]
        in_filter = location in scraper.valid_locations
        print(f"  {location}: {count} {'✅' if in_filter else '❌'}")
    
    # Show other locations
    other_locations = sorted([loc for loc in location_counts.keys() if not loc.startswith('GA')])
    if other_locations:
        print(f"\n  Other locations:")
        for location in other_locations[:20]:  # Show first 20
            count = location_counts[location]
            print(f"    {location}: {count}")
        if len(other_locations) > 20:
            print(f"    ... and {len(other_locations) - 20} more")
    
    # Check if we're close to 9000
    total_packages = len(all_records)
    print(f"\n🎯 EXPECTATION CHECK:")
    print(f"Expected ~9000 packages")
    print(f"Found {total_packages} packages")
    
    if total_packages < 8000:
        print("⚠️  Significantly fewer packages than expected!")
        print("   This could indicate:")
        print("   1. Query filters are too restrictive")
        print("   2. Different query ID needed")
        print("   3. Data might be paginated")
        print("   4. Time window restrictions")
    elif total_packages > 8000:
        print("✅ Package count looks reasonable")
    
    # Save analysis results
    analysis = {
        'total_records': len(all_records),
        'filtered_records': len(filtered_records),
        'status_breakdown': dict(status_counts),
        'location_breakdown': dict(location_counts),
        'ga_locations_found': [loc for loc in location_counts.keys() if loc.startswith('GA')],
        'sample_records': all_records[:5] if all_records else []
    }
    
    with open('mercury_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    print(f"\n💾 Saved analysis to mercury_analysis.json")
    
    return analysis

def analyze_without_filters(html_content):
    """Extract all records without any filtering"""
    from bs4 import BeautifulSoup
    from datetime import datetime
    
    records = []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        rows = soup.find_all('tr')
        
        if not rows:
            print("⚠️  No table rows found in HTML")
            return records
        
        print(f"Found {len(rows)} table rows")
        
        # Find header row to map column indices
        header_row = rows[0]
        headers = [th.text.strip() for th in header_row.find_all('th')]
        print(f"Headers found: {len(headers)}")
        
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
        
        print(f"Column mapping: {column_map}")
        
        # Use fallback mapping if headers not found
        if not column_map:
            column_map = {
                'status': 26,      # compLastScanInOrder.internalStatusCode
                'tracking_id': 3,  # trackingId
                'location': 12,    # Induct.destination.id
                'timestamp': 4     # lastScanInOrder.timestamp
            }
            print(f"Using fallback column mapping: {column_map}")
        
        # Process all data rows
        for i, row in enumerate(rows[1:], 1):  # Skip header row
            cells = row.find_all('td')
            if not cells:
                continue
                
            if len(cells) <= max(column_map.values()):
                continue
                
            try:
                # Extract values (no filtering!)
                status = cells[column_map['status']].text.strip() if 'status' in column_map else 'UNKNOWN'
                tracking_id = cells[column_map['tracking_id']].text.strip() if 'tracking_id' in column_map else f'UNKNOWN_{i}'
                location = cells[column_map['location']].text.strip() if 'location' in column_map else 'UNKNOWN'
                timestamp_str = cells[column_map['timestamp']].text.strip() if 'timestamp' in column_map else ''
                
                records.append({
                    'status': status,
                    'tracking_id': tracking_id,
                    'location': location,
                    'timestamp_str': timestamp_str,
                    'row_number': i
                })
                
            except (IndexError, AttributeError) as e:
                # Skip problematic rows but don't stop
                continue
        
        print(f"Successfully parsed {len(records)} records")
        
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        
    return records

if __name__ == "__main__":
    # Suppress warnings for cleaner output
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    logging.basicConfig(level=logging.WARNING)  # Reduce log noise
    
    analysis = analyze_mercury_data()
    
    print(f"\n🎯 SUMMARY:")
    if analysis:
        print(f"Total packages found: {analysis['total_records']}")
        print(f"GA locations: {len([loc for loc in analysis['ga_locations_found']])}")
        print(f"Different statuses: {len(analysis['status_breakdown'])}")
        
        if analysis['total_records'] < 8000:
            print(f"\n🔍 RECOMMENDATIONS:")
            print(f"1. Check if Mercury query needs different parameters")
            print(f"2. Verify time window (might be filtering by time)")
            print(f"3. Check if data is paginated")
    else:
        print("Failed to analyze data")