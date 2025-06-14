#!/usr/bin/env python3
"""Create detailed logging for Mercury data analysis"""

import sys
import json
import logging
import os
from datetime import datetime
from collections import Counter, defaultdict
sys.path.insert(0, '.')

from src.auth import MidwayAuth
from src.mercury_scraper import MercuryScraper

def setup_detailed_logging():
    """Setup comprehensive logging system"""
    
    # Create logs directory
    os.makedirs('logs_analysis', exist_ok=True)
    
    # Create timestamp for this session
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Setup logger
    logger = logging.getLogger('mercury_analysis')
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # File handler for detailed logs
    log_file = f'logs_analysis/mercury_analysis_{timestamp}.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler for important info
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Detailed formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger, timestamp, log_file

def comprehensive_mercury_analysis():
    """Complete Mercury data analysis with detailed logging"""
    
    logger, timestamp, log_file = setup_detailed_logging()
    
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE MERCURY DATA ANALYSIS")
    logger.info("=" * 80)
    logger.info(f"Analysis timestamp: {timestamp}")
    logger.info(f"Log file: {log_file}")
    
    try:
        # Initialize components
        logger.info("Initializing Mercury scraper...")
        
        scraper = MercuryScraper(
            mercury_url="https://mercury.amazon.com/getQueryResponse?ID=127de24b92c1f65c47f001541fbc6974&region=na",
            valid_locations=['GA1', 'GA2', 'GA3', 'GA4', 'GA5', 'GA6', 'GA7', 'GA8', 'GA9', 'GA10'],
            valid_statuses=['INDUCTED', 'INDUCT', 'STOW_BUFFER', 'AT_STATION']  # Original filter
        )
        
        # Get session
        logger.info("Getting authenticated session...")
        session = scraper._get_session()
        if not session:
            logger.error("Failed to get authenticated session")
            return None
            
        # Fetch raw data
        logger.info("Fetching raw Mercury response...")
        response = session.get(scraper.mercury_url, timeout=30)
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response size: {len(response.text):,} characters")
        
        # Save raw response
        raw_file = f'logs_analysis/raw_mercury_{timestamp}.html'
        with open(raw_file, 'w') as f:
            f.write(response.text)
        logger.info(f"Saved raw response to: {raw_file}")
        
        # Parse all data (no filters)
        logger.info("Parsing ALL data without filters...")
        all_records = parse_all_records(response.text, logger)
        logger.info(f"Total records found: {len(all_records):,}")
        
        # Parse with original filters
        logger.info("Parsing with ORIGINAL filters...")
        filtered_records = scraper._extract_records(response.text)
        logger.info(f"Filtered records (original): {len(filtered_records):,}")
        
        # Parse with expanded filters
        logger.info("Testing EXPANDED status filters...")
        expanded_scraper = MercuryScraper(
            mercury_url=scraper.mercury_url,
            valid_locations=scraper.valid_locations,
            valid_statuses=['INDUCTED', 'INDUCT', 'STOW_BUFFER', 'AT_STATION', 
                          'READY_FOR_DEPARTURE', 'DELIVERED', 'ON_ROAD_WITH_DELIVERY_ASSOCIATE']
        )
        expanded_records = expanded_scraper._extract_records(response.text)
        logger.info(f"Filtered records (expanded): {len(expanded_records):,}")
        
        # Detailed analysis
        analysis_results = perform_detailed_analysis(all_records, filtered_records, expanded_records, logger)
        
        # Save comprehensive results
        results_file = f'logs_analysis/analysis_results_{timestamp}.json'
        with open(results_file, 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        logger.info(f"Saved analysis results to: {results_file}")
        
        # Summary report
        generate_summary_report(analysis_results, logger, timestamp)
        
        logger.info("=" * 80)
        logger.info("ANALYSIS COMPLETE")
        logger.info("=" * 80)
        
        return analysis_results
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return None

def parse_all_records(html_content, logger):
    """Parse all records without any filtering"""
    from bs4 import BeautifulSoup
    
    records = []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        rows = soup.find_all('tr')
        logger.debug(f"Found {len(rows)} total table rows")
        
        if not rows:
            logger.warning("No table rows found in HTML")
            return records
        
        # Find headers
        header_row = rows[0]
        headers = [th.text.strip() for th in header_row.find_all('th')]
        logger.debug(f"Found {len(headers)} headers")
        logger.debug(f"First 10 headers: {headers[:10]}")
        
        # Map columns
        column_map = {}
        for idx, header in enumerate(headers):
            if 'compLastScanInOrder.internalStatusCode' in header:
                column_map['status'] = idx
                logger.debug(f"Status column at index {idx}")
            elif header == 'trackingId':
                column_map['tracking_id'] = idx
                logger.debug(f"TrackingId column at index {idx}")
            elif 'Induct.destination.id' in header:
                column_map['location'] = idx
                logger.debug(f"Location column at index {idx}")
            elif 'lastScanInOrder.timestamp' in header:
                column_map['timestamp'] = idx
                logger.debug(f"Timestamp column at index {idx}")
        
        logger.info(f"Column mapping: {column_map}")
        
        # Use fallback if needed
        if not column_map:
            column_map = {
                'status': 26, 'tracking_id': 3, 'location': 12, 'timestamp': 4
            }
            logger.warning(f"Using fallback column mapping: {column_map}")
        
        # Parse data rows
        valid_rows = 0
        skipped_rows = 0
        
        for i, row in enumerate(rows[1:], 1):
            cells = row.find_all('td')
            if not cells or len(cells) <= max(column_map.values()):
                skipped_rows += 1
                continue
                
            try:
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
                valid_rows += 1
                
            except Exception as e:
                logger.debug(f"Error parsing row {i}: {e}")
                skipped_rows += 1
                continue
        
        logger.info(f"Parsed {valid_rows} valid rows, skipped {skipped_rows} rows")
        
    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
        
    return records

def perform_detailed_analysis(all_records, filtered_records, expanded_records, logger):
    """Perform comprehensive analysis"""
    
    logger.info("Performing detailed analysis...")
    
    # Count by status
    status_counts = Counter(record['status'] for record in all_records)
    logger.info("Status breakdown:")
    for status, count in status_counts.most_common():
        logger.info(f"  {status}: {count:,}")
    
    # Count by location
    location_counts = Counter(record['location'] for record in all_records)
    logger.info("Location breakdown:")
    
    # GA locations first
    ga_locations = sorted([loc for loc in location_counts.keys() if loc.startswith('GA')])
    logger.info("GA Locations:")
    for location in ga_locations:
        count = location_counts[location]
        logger.info(f"  {location}: {count:,}")
    
    # Other locations
    other_locations = [loc for loc in location_counts.keys() if not loc.startswith('GA')]
    if other_locations:
        logger.info(f"Other locations ({len(other_locations)} total):")
        for location in sorted(other_locations)[:10]:  # Show first 10
            count = location_counts[location]
            logger.info(f"  {location}: {count:,}")
        if len(other_locations) > 10:
            logger.info(f"  ... and {len(other_locations) - 10} more")
    
    # Analysis by location and status
    location_status = defaultdict(lambda: defaultdict(int))
    for record in all_records:
        location_status[record['location']][record['status']] += 1
    
    logger.info("GA Location Status Breakdown:")
    for location in sorted(ga_locations):
        logger.info(f"  {location}:")
        for status, count in sorted(location_status[location].items()):
            logger.info(f"    {status}: {count:,}")
    
    # Create analysis results
    analysis = {
        'timestamp': datetime.now().isoformat(),
        'totals': {
            'all_records': len(all_records),
            'filtered_original': len(filtered_records),
            'filtered_expanded': len(expanded_records),
            'filtered_out_original': len(all_records) - len(filtered_records),
            'filtered_out_expanded': len(all_records) - len(expanded_records)
        },
        'status_breakdown': dict(status_counts),
        'location_breakdown': dict(location_counts),
        'ga_locations': ga_locations,
        'other_locations': other_locations,
        'location_status_breakdown': {
            loc: dict(statuses) for loc, statuses in location_status.items()
        },
        'sample_records': {
            'all': all_records[:3] if all_records else [],
            'filtered_original': filtered_records[:3] if filtered_records else [],
            'filtered_expanded': expanded_records[:3] if expanded_records else []
        }
    }
    
    return analysis

def generate_summary_report(analysis, logger, timestamp):
    """Generate a summary report"""
    
    logger.info("=" * 60)
    logger.info("SUMMARY REPORT")
    logger.info("=" * 60)
    
    totals = analysis['totals']
    logger.info(f"Total packages found: {totals['all_records']:,}")
    logger.info(f"Original filter (INDUCTED/INDUCT/STOW_BUFFER/AT_STATION): {totals['filtered_original']:,}")
    logger.info(f"Expanded filter (+READY_FOR_DEPARTURE/DELIVERED/ON_ROAD): {totals['filtered_expanded']:,}")
    
    logger.info(f"\nGA Locations active: {len(analysis['ga_locations'])}")
    logger.info(f"GA Locations: {', '.join(analysis['ga_locations'])}")
    
    # Status summary
    logger.info(f"\nTop statuses:")
    for status, count in sorted(analysis['status_breakdown'].items(), key=lambda x: x[1], reverse=True)[:5]:
        logger.info(f"  {status}: {count:,}")
    
    # Recommendations
    logger.info(f"\nRECOMMENDATIONS:")
    
    if totals['all_records'] < 8000:
        logger.info(f"• Total packages ({totals['all_records']:,}) is less than expected (~9000)")
        logger.info(f"  - Data might be paginated or filtered by time window")
        logger.info(f"  - Consider creating Mercury sheet with different query parameters")
    
    if totals['filtered_original'] < 100:
        logger.info(f"• Very few packages ({totals['filtered_original']}) match original filter")
        logger.info(f"  - Most packages have moved past induct stations")
        logger.info(f"  - Consider using expanded filter or AT_STATION-only Mercury sheet")
    
    at_station_count = analysis['status_breakdown'].get('AT_STATION', 0)
    if at_station_count < 50:
        logger.info(f"• Only {at_station_count} packages currently AT_STATION")
        logger.info(f"  - Creating Mercury sheet filtered to AT_STATION only would be ideal")
        logger.info(f"  - This would give real-time monitoring of active packages")
    
    # Save summary to separate file
    summary_file = f'logs_analysis/summary_report_{timestamp}.txt'
    with open(summary_file, 'w') as f:
        f.write(f"Mercury Data Analysis Summary - {timestamp}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total packages: {totals['all_records']:,}\n")
        f.write(f"Original filter: {totals['filtered_original']:,}\n")
        f.write(f"Expanded filter: {totals['filtered_expanded']:,}\n")
        f.write(f"GA locations: {', '.join(analysis['ga_locations'])}\n")
        f.write(f"AT_STATION packages: {at_station_count}\n\n")
        
        f.write("Status Breakdown:\n")
        for status, count in sorted(analysis['status_breakdown'].items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {status}: {count:,}\n")
    
    logger.info(f"\nSummary saved to: {summary_file}")

if __name__ == "__main__":
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Run comprehensive analysis
    results = comprehensive_mercury_analysis()
    
    if results:
        print(f"\n✅ Analysis complete! Check logs_analysis/ directory for detailed results.")
        print(f"Key files created:")
        print(f"  - Detailed log file")
        print(f"  - Raw Mercury HTML response")
        print(f"  - Analysis results JSON")
        print(f"  - Summary report")
    else:
        print(f"\n❌ Analysis failed. Check logs for details.")