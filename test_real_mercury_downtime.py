#!/usr/bin/env python3
"""Test downtime analysis with real Mercury data"""

import sys
import json
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, '.')

def test_real_mercury_downtime():
    """Test downtime analysis using real Mercury data"""
    
    print("🔍 Real Mercury Downtime Analysis")
    print("=" * 70)
    print("Testing with actual Mercury data and induct timestamps")
    print("=" * 70)
    
    # Create detailed logging
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_dir = 'mercury_logs'
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = f'{log_dir}/mercury_downtime_test_{timestamp}.log'
    
    try:
        # Import Mercury scraper
        from src.mercury_scraper import MercuryScraper
        
        print("✅ MercuryScraper imported successfully")
        
        # Initialize scraper with current configuration
        scraper = MercuryScraper(
            mercury_url="https://mercury.amazon.com/getQueryResponse?ID=a9ebdbf5325e9395d4fbd114d3316f0c&region=na",
            valid_locations=['GA1', 'GA2', 'GA3', 'GA4', 'GA5', 'GA6', 'GA7', 'GA8', 'GA9', 'GA10'],
            valid_statuses=['AT_STATION', 'INDUCTED', 'INDUCT', 'STOW_BUFFER', 'READY_FOR_DEPARTURE', 'DELIVERED']
        )
        
        print("📡 Fetching Mercury data...")
        
        # Get authenticated session
        session = scraper._get_session()
        if not session:
            print("❌ Failed to get authenticated session")
            print("   Make sure you've run: mwinit -o")
            return False
        
        print("✅ Authentication successful")
        
        # Fetch raw Mercury response
        response = session.get(scraper.mercury_url, timeout=30)
        print(f"✅ Mercury response received: {len(response.text):,} characters")
        
        # Save raw response for analysis
        raw_file = f'{log_dir}/raw_mercury_{timestamp}.html'
        with open(raw_file, 'w') as f:
            f.write(response.text)
        print(f"💾 Raw response saved: {raw_file}")
        
        # Parse standard package data
        print("📊 Parsing standard package data...")
        packages = scraper._extract_records(response.text)
        print(f"✅ Found {len(packages)} packages with standard parsing")
        
        # Parse induct timestamp data
        print("🕐 Parsing induct timestamp data...")
        induct_records = parse_induct_timestamps_from_html(response.text)
        print(f"✅ Found {len(induct_records)} records with induct timestamps")
        
        # Analyze the data
        analysis_results = analyze_mercury_data(packages, induct_records, timestamp)
        
        # Generate comprehensive report
        generate_mercury_report(analysis_results, log_file)
        
        # Save detailed results
        results_file = f'{log_dir}/analysis_results_{timestamp}.json'
        with open(results_file, 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        print(f"💾 Analysis results saved: {results_file}")
        
        print("\n" + "="*70)
        print("✅ REAL MERCURY TEST COMPLETED")
        print("="*70)
        print(f"📁 Check {log_dir}/ directory for detailed results:")
        print(f"   • {raw_file} - Raw Mercury HTML")
        print(f"   • {results_file} - Analysis results JSON")
        print(f"   • {log_file} - Detailed test log")
        
        return True
        
    except Exception as e:
        error_msg = f"❌ Error: {e}"
        print(error_msg)
        
        # Save error to log
        with open(log_file, 'a') as f:
            f.write(f"\nERROR: {error_msg}\n")
            import traceback
            f.write(traceback.format_exc())
        
        print(f"💾 Error details saved to: {log_file}")
        return False

def parse_induct_timestamps_from_html(html_content):
    """Parse induct timestamps from Mercury HTML using multiple methods"""
    
    records = []
    
    print("🔍 Method 1: Looking for induct timestamp field...")
    
    # Method 1: Look for the specific induct timestamp field
    induct_field_pattern = r'compAtStationData\.compCurrentNodeAtStationData\.firstEventTimestamp[^>]*>([^<]+)<'
    induct_matches = re.findall(induct_field_pattern, html_content)
    
    if induct_matches:
        print(f"   ✅ Found {len(induct_matches)} induct timestamp matches")
        
        # Try to correlate with other data in the same table rows
        for i, timestamp_str in enumerate(induct_matches):
            if timestamp_str.strip() and timestamp_str.strip() != 'null':
                parsed_time = parse_timestamp_string(timestamp_str.strip())
                if parsed_time:
                    records.append({
                        'tracking_id': f'MERCURY_{i:04d}',
                        'location': f'GA{(i % 10) + 1}',  # This would need proper parsing
                        'induct_timestamp': parsed_time,
                        'induct_time_str': timestamp_str.strip(),
                        'source': 'induct_field'
                    })
    else:
        print("   ⚠️  No induct timestamp field found")
    
    print("🔍 Method 2: Looking for general timestamp patterns...")
    
    # Method 2: Look for any timestamp patterns that might be induct times
    timestamp_patterns = [
        r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
        r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})'
    ]
    
    all_timestamps = []
    for pattern in timestamp_patterns:
        matches = re.findall(pattern, html_content)
        all_timestamps.extend(matches)
    
    print(f"   ✅ Found {len(all_timestamps)} general timestamp patterns")
    
    # Parse and filter recent timestamps (last 24 hours)
    recent_cutoff = datetime.now() - timedelta(hours=24)
    
    for i, timestamp_str in enumerate(set(all_timestamps)):  # Remove duplicates
        parsed_time = parse_timestamp_string(timestamp_str)
        if parsed_time and parsed_time > recent_cutoff:
            records.append({
                'tracking_id': f'TIMESTAMP_{i:04d}',
                'location': f'GA{(i % 10) + 1}',
                'induct_timestamp': parsed_time,
                'induct_time_str': timestamp_str,
                'source': 'general_pattern'
            })
    
    # Sort by timestamp
    records.sort(key=lambda x: x['induct_timestamp'])
    
    print(f"📊 Total parsed records: {len(records)}")
    return records

def parse_timestamp_string(timestamp_str):
    """Parse various timestamp formats"""
    
    if not timestamp_str or timestamp_str.strip() == 'null':
        return None
    
    timestamp_str = timestamp_str.strip()
    
    # Common formats
    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S.%f',
        '%m/%d/%Y %H:%M:%S',
        '%d/%m/%Y %H:%M:%S'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    
    # Try removing timezone info and parsing
    try:
        # Remove common timezone suffixes
        clean_str = re.sub(r'[+-]\d{2}:?\d{2}$', '', timestamp_str)
        clean_str = clean_str.replace('Z', '')
        
        for fmt in formats:
            try:
                return datetime.strptime(clean_str, fmt)
            except ValueError:
                continue
    except:
        pass
    
    return None

def analyze_mercury_data(packages, induct_records, timestamp):
    """Analyze Mercury data for downtime patterns"""
    
    print("\n📊 ANALYZING MERCURY DATA")
    print("="*50)
    
    # Standard package analysis
    location_counts = defaultdict(int)
    status_counts = defaultdict(int)
    
    for pkg in packages:
        location_counts[pkg.get('location', 'UNKNOWN')] += 1
        status_counts[pkg.get('status', 'UNKNOWN')] += 1
    
    print(f"📈 Standard package data:")
    print(f"   Total packages: {len(packages)}")
    print(f"   Locations: {len(location_counts)}")
    print(f"   GA locations: {len([loc for loc in location_counts.keys() if loc.startswith('GA')])}")
    
    # Show top locations
    print(f"   Top locations:")
    for loc, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"     {loc}: {count}")
    
    # Show statuses
    print(f"   Statuses:")
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"     {status}: {count}")
    
    # Induct timestamp analysis
    print(f"\n🕐 Induct timestamp data:")
    print(f"   Total induct records: {len(induct_records)}")
    
    if induct_records:
        # Group by location
        induct_by_location = defaultdict(list)
        for record in induct_records:
            if record['location'].startswith('GA'):
                induct_by_location[record['location']].append(record)
        
        print(f"   GA locations with induct data: {len(induct_by_location)}")
        
        # Analyze downtime if we have enough data
        downtime_analysis = None
        if len(induct_records) >= 10:
            print(f"\n⏱️  DOWNTIME ANALYSIS")
            downtime_analysis = perform_downtime_analysis(induct_by_location)
        
        # Time range analysis
        timestamps = [r['induct_timestamp'] for r in induct_records]
        if timestamps:
            min_time = min(timestamps)
            max_time = max(timestamps)
            time_span = max_time - min_time
            
            print(f"   Time range: {min_time} to {max_time}")
            print(f"   Span: {time_span}")
    
    return {
        'timestamp': timestamp,
        'standard_packages': {
            'count': len(packages),
            'location_breakdown': dict(location_counts),
            'status_breakdown': dict(status_counts),
            'sample_packages': packages[:5]
        },
        'induct_records': {
            'count': len(induct_records),
            'sample_records': induct_records[:5],
            'time_range': {
                'min': min(r['induct_timestamp'] for r in induct_records) if induct_records else None,
                'max': max(r['induct_timestamp'] for r in induct_records) if induct_records else None
            }
        },
        'downtime_analysis': perform_downtime_analysis(defaultdict(list)) if induct_records else None
    }

def perform_downtime_analysis(induct_by_location):
    """Perform downtime analysis on induct data"""
    
    analysis = {}
    
    for location, records in induct_by_location.items():
        if len(records) < 2:
            continue
        
        # Sort by timestamp
        records.sort(key=lambda x: x['induct_timestamp'])
        
        # Calculate gaps
        gaps = []
        for i in range(1, len(records)):
            gap_seconds = (records[i]['induct_timestamp'] - records[i-1]['induct_timestamp']).total_seconds()
            
            # Only analyze reasonable gaps (20s to 780s)
            if 20 <= gap_seconds <= 780:
                gaps.append({
                    'gap_seconds': gap_seconds,
                    'from_time': records[i-1]['induct_timestamp'],
                    'to_time': records[i]['induct_timestamp']
                })
        
        if gaps:
            # Categorize gaps
            categories = {
                '20-60s': [g for g in gaps if 20 <= g['gap_seconds'] <= 60],
                '60-120s': [g for g in gaps if 60 < g['gap_seconds'] <= 120],
                '120-780s': [g for g in gaps if 120 < g['gap_seconds'] <= 780]
            }
            
            analysis[location] = {
                'total_records': len(records),
                'total_gaps': len(gaps),
                'categories': categories,
                'avg_gap': sum(g['gap_seconds'] for g in gaps) / len(gaps),
                'max_gap': max(g['gap_seconds'] for g in gaps),
                'min_gap': min(g['gap_seconds'] for g in gaps)
            }
    
    return analysis

def generate_mercury_report(analysis, log_file):
    """Generate comprehensive Mercury analysis report"""
    
    report_lines = []
    report_lines.append("="*70)
    report_lines.append("MERCURY DOWNTIME ANALYSIS REPORT")
    report_lines.append("="*70)
    report_lines.append(f"Generated: {datetime.now()}")
    report_lines.append("")
    
    # Standard package summary
    std_packages = analysis['standard_packages']
    report_lines.append("📊 STANDARD PACKAGE DATA:")
    report_lines.append(f"   Total packages: {std_packages['count']}")
    report_lines.append(f"   Locations found: {len(std_packages['location_breakdown'])}")
    
    # GA locations
    ga_locations = {loc: count for loc, count in std_packages['location_breakdown'].items() if loc.startswith('GA')}
    if ga_locations:
        report_lines.append(f"   GA locations: {len(ga_locations)}")
        for loc in sorted(ga_locations.keys()):
            report_lines.append(f"     {loc}: {ga_locations[loc]} packages")
    
    # Status breakdown
    report_lines.append(f"   Status breakdown:")
    for status, count in sorted(std_packages['status_breakdown'].items(), key=lambda x: x[1], reverse=True):
        report_lines.append(f"     {status}: {count}")
    
    # Induct timestamp data
    induct_data = analysis['induct_records']
    report_lines.append("")
    report_lines.append("🕐 INDUCT TIMESTAMP DATA:")
    report_lines.append(f"   Total induct records: {induct_data['count']}")
    
    if induct_data['time_range']['min']:
        report_lines.append(f"   Time range: {induct_data['time_range']['min']} to {induct_data['time_range']['max']}")
    
    # Downtime analysis
    if analysis.get('downtime_analysis'):
        report_lines.append("")
        report_lines.append("⏱️  DOWNTIME ANALYSIS:")
        
        downtime = analysis['downtime_analysis']
        for location, data in sorted(downtime.items()):
            report_lines.append(f"   {location}:")
            report_lines.append(f"     Records: {data['total_records']}")
            report_lines.append(f"     Gaps: {data['total_gaps']}")
            report_lines.append(f"     Avg gap: {data['avg_gap']:.1f}s")
            
            for category, gaps in data['categories'].items():
                if gaps:
                    report_lines.append(f"     {category}: {len(gaps)} gaps")
    
    # Recommendations
    report_lines.append("")
    report_lines.append("💡 RECOMMENDATIONS:")
    
    if std_packages['count'] < 100:
        report_lines.append("   • Low package count - may need different status filters")
    
    if induct_data['count'] == 0:
        report_lines.append("   • No induct timestamps found - verify Mercury configuration")
        report_lines.append("   • Ensure 'Last Induct Scan' field is included in Mercury query")
    elif induct_data['count'] < 50:
        report_lines.append("   • Limited induct timestamp data")
        report_lines.append("   • May need expanded time window or different filters")
    
    # Print and save report
    report_text = "\n".join(report_lines)
    print("\n" + report_text)
    
    with open(log_file, 'w') as f:
        f.write(report_text)
    
    print(f"\n💾 Full report saved to: {log_file}")

if __name__ == "__main__":
    print("🚀 Real Mercury Downtime Analysis Test")
    print("This will connect to Mercury with your authentication")
    print("Make sure you've run: mwinit -o")
    print("")
    
    # Suppress SSL warnings
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except ImportError:
        pass
    
    success = test_real_mercury_downtime()
    
    if success:
        print("\n✅ Test completed! Review the logs to see:")
        print("  • What data Mercury is returning")
        print("  • Whether induct timestamps are available")
        print("  • Downtime analysis results")
        print("  • Recommendations for optimization")
    else:
        print("\n❌ Test failed - check logs for details")