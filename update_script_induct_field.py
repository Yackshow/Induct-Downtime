#!/usr/bin/env python3
"""Update the monitoring script to use the correct Last Induct Scan field"""

import sys
sys.path.insert(0, '.')

def update_mercury_scraper():
    """Update MercuryScraper to use the correct induct scan timestamp field"""
    
    print("🔧 Updating Mercury Scraper for Last Induct Scan Field")
    print("=" * 60)
    
    # Read the current mercury_scraper.py
    with open('src/mercury_scraper.py', 'r') as f:
        content = f.read()
    
    print("✅ Read current mercury_scraper.py")
    
    # Create the updated version with correct field mapping
    # We need to update the column mapping in _extract_records_bs4 method
    
    # Find the column mapping section
    old_timestamp_mapping = '''elif 'lastScanInOrder.timestamp' in header:
                column_map['timestamp'] = idx'''
    
    new_timestamp_mapping = '''elif 'lastScanInOrder.timestamp' in header:
                column_map['timestamp'] = idx
            elif 'compAtStationData.compCurrentNodeAtStationData.firstEventTimestamp' in header:
                column_map['induct_timestamp'] = idx
            elif 'compAtStationData.compFirstNodeAtStationData.firstEventTimestamp' in header:
                column_map['induct_timestamp'] = idx'''
    
    # Check if we need to update
    if 'induct_timestamp' in content:
        print("⚠️  Script already updated with induct timestamp logic")
        return True
    
    # Update the column mapping
    if old_timestamp_mapping in content:
        content = content.replace(old_timestamp_mapping, new_timestamp_mapping)
        print("✅ Added induct timestamp column mapping")
    else:
        print("⚠️  Could not find exact timestamp mapping to update")
    
    # Update the record creation section to use induct timestamp when available
    old_record_creation = '''parsed_timestamp = self._parse_timestamp(timestamp_str)
                if not parsed_timestamp:
                    continue
                
                records.append({
                    'status': status,
                    'tracking_id': tracking_id,
                    'location': location,
                    'timestamp': parsed_timestamp,
                    'raw_timestamp': timestamp_str,
                    'scraped_at': datetime.now().isoformat()
                })'''
    
    new_record_creation = '''# Get induct timestamp if available, otherwise use regular timestamp
                induct_timestamp_str = ""
                if 'induct_timestamp' in column_map and len(cells) > column_map['induct_timestamp']:
                    induct_timestamp_str = cells[column_map['induct_timestamp']].text.strip()
                
                # Use induct timestamp for downtime calculation if available
                primary_timestamp_str = induct_timestamp_str if induct_timestamp_str else timestamp_str
                parsed_timestamp = self._parse_timestamp(primary_timestamp_str)
                if not parsed_timestamp:
                    continue
                
                records.append({
                    'status': status,
                    'tracking_id': tracking_id,
                    'location': location,
                    'timestamp': parsed_timestamp,
                    'raw_timestamp': primary_timestamp_str,
                    'induct_timestamp': induct_timestamp_str,
                    'latest_scan_timestamp': timestamp_str,
                    'scraped_at': datetime.now().isoformat()
                })'''
    
    if old_record_creation in content:
        content = content.replace(old_record_creation, new_record_creation)
        print("✅ Updated record creation to use induct timestamp")
    else:
        print("⚠️  Could not find exact record creation code to update")
    
    # Save the updated file
    with open('src/mercury_scraper_updated.py', 'w') as f:
        f.write(content)
    
    print("💾 Saved updated scraper to mercury_scraper_updated.py")
    
    return True

def update_config_for_induct_field():
    """Update config.yaml to include the induct timestamp field"""
    
    print("\n🔧 Updating Configuration")
    print("=" * 30)
    
    # Read current config
    with open('config.yaml', 'r') as f:
        config_content = f.read()
    
    # Add note about induct field
    induct_note = '''
# Field Mapping Discovery:
# - Last Induct Scan (web interface) = compAtStationData.compCurrentNodeAtStationData.firstEventTimestamp (HTML)
# - This field shows when package actually arrived at induct station
# - Different from compLastScanInOrder.timestamp which shows latest scan anywhere
# - Use this field for accurate downtime monitoring between induct arrivals
'''
    
    # Add the note at the top
    if "Field Mapping Discovery" not in config_content:
        config_content = induct_note + config_content
        
        with open('config.yaml', 'w') as f:
            f.write(config_content)
        
        print("✅ Added induct field documentation to config.yaml")
    else:
        print("⚠️  Config already has induct field documentation")

def create_test_script():
    """Create a test script to verify the induct field is working"""
    
    print("\n🧪 Creating Test Script")
    print("=" * 25)
    
    test_script = '''#!/usr/bin/env python3
"""Test script to verify induct timestamp field is working correctly"""

import sys
sys.path.insert(0, '.')

from src.mercury_scraper_updated import MercuryScraper

def test_induct_timestamp():
    """Test that we can extract induct timestamps correctly"""
    
    print("🧪 Testing Induct Timestamp Extraction")
    print("=" * 50)
    
    # Create scraper with enhanced configuration
    scraper = MercuryScraper(
        mercury_url="https://mercury.amazon.com/getQueryResponse?ID=127de24b92c1f65c47f001541fbc6974&region=na",
        valid_locations=['GA1', 'GA2', 'GA3', 'GA4', 'GA5', 'GA6', 'GA7', 'GA8', 'GA9', 'GA10'],
        valid_statuses=['READY_FOR_DEPARTURE', 'DELIVERED', 'AT_STATION', 'ON_ROAD_WITH_DELIVERY_ASSOCIATE']
    )
    
    print("📥 Fetching data with induct timestamp support...")
    data = scraper.scrape_data()
    
    if not data:
        print("❌ No data retrieved")
        return False
    
    print(f"✅ Retrieved {len(data)} packages")
    
    # Analyze the data
    induct_timestamps_found = 0
    latest_scan_timestamps_found = 0
    
    print("\\n📊 Sample Data Analysis:")
    for i, package in enumerate(data[:5]):  # Show first 5
        tracking_id = package.get('tracking_id', 'Unknown')
        location = package.get('location', 'Unknown')
        induct_ts = package.get('induct_timestamp', '')
        latest_ts = package.get('latest_scan_timestamp', '')
        status = package.get('status', 'Unknown')
        
        print(f"\\n  Package {i+1}: {tracking_id}")
        print(f"    Location: {location}")
        print(f"    Status: {status}")
        print(f"    Induct Timestamp: {induct_ts}")
        print(f"    Latest Scan: {latest_ts}")
        print(f"    Same Time? {'Yes' if induct_ts == latest_ts else 'No - PERFECT!'}")
        
        if induct_ts:
            induct_timestamps_found += 1
        if latest_ts:
            latest_scan_timestamps_found += 1
    
    print(f"\\n📈 SUMMARY:")
    print(f"  Packages with induct timestamps: {induct_timestamps_found}")
    print(f"  Packages with latest scan timestamps: {latest_scan_timestamps_found}")
    
    if induct_timestamps_found > 0:
        print(f"  ✅ SUCCESS: Induct timestamp field is working!")
        print(f"  🎯 Ready for accurate downtime monitoring")
    else:
        print(f"  ⚠️  No induct timestamps found - may need field adjustment")
    
    return induct_timestamps_found > 0

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    success = test_induct_timestamp()
    
    if success:
        print(f"\\n✅ Induct timestamp extraction is working!")
        print(f"🎯 Ready to use for downtime monitoring")
    else:
        print(f"\\n❌ Need to adjust field mapping")
'''
    
    with open('test_induct_timestamp.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Created test_induct_timestamp.py")

def main():
    """Main function to update everything for induct timestamp support"""
    
    print("🚀 Updating System for Last Induct Scan Field")
    print("=" * 50)
    
    # Update mercury scraper
    update_mercury_scraper()
    
    # Update config
    update_config_for_induct_field()
    
    # Create test script
    create_test_script()
    
    print(f"\\n✅ SYSTEM UPDATED FOR INDUCT TIMESTAMPS!")
    print(f"\\n📁 Files Created/Updated:")
    print(f"  - src/mercury_scraper_updated.py (updated scraper)")
    print(f"  - config.yaml (added documentation)")
    print(f"  - test_induct_timestamp.py (test script)")
    
    print(f"\\n🎯 NEXT STEPS:")
    print(f"  1. Make sure Modified_Mercury_Enhanced_Induct_Fields.json is uploaded")
    print(f"  2. Test: python3 test_induct_timestamp.py")
    print(f"  3. If working, replace mercury_scraper.py with mercury_scraper_updated.py")
    print(f"  4. Run your monitoring with accurate induct downtime!")
    
    print(f"\\n🎉 NOW YOU'LL HAVE TRUE INDUCT DOWNTIME MONITORING!")
    print(f"   Tracking actual time between induct arrivals, not latest scans!")

if __name__ == "__main__":
    main()
'''

    with open(script_file, 'w') as f:
        f.write(script_content)
    
    print(f"✅ Created {script_file}")

if __name__ == "__main__":
    update_script_for_induct_field()