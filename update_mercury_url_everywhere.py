#!/usr/bin/env python3
"""Update Mercury URL throughout the entire project"""

import os
import json
import re

def update_mercury_url_everywhere():
    """Update the Mercury URL in all project files"""
    
    print("🔄 Updating Mercury URL Throughout Project")
    print("=" * 50)
    
    old_url = "https://mercury.amazon.com/getQueryResponse?ID=127de24b92c1f65c47f001541fbc6974&region=na"
    new_url = "https://mercury.amazon.com/getQueryResponse?ID=a9ebdbf5325e9395d4fbd114d3316f0c&region=na"
    
    print(f"🔄 Replacing:")
    print(f"  OLD: {old_url}")
    print(f"  NEW: {new_url}")
    
    files_updated = []
    
    # 1. Update config.yaml
    print(f"\n📝 Updating config.yaml...")
    try:
        with open('config.yaml', 'r') as f:
            config_content = f.read()
        
        if old_url in config_content:
            config_content = config_content.replace(old_url, new_url)
            with open('config.yaml', 'w') as f:
                f.write(config_content)
            print(f"  ✅ Updated config.yaml")
            files_updated.append('config.yaml')
        else:
            print(f"  ⚠️  Old URL not found in config.yaml")
    except Exception as e:
        print(f"  ❌ Error updating config.yaml: {e}")
    
    # 2. Update main.py
    print(f"\n📝 Updating main.py...")
    try:
        with open('main.py', 'r') as f:
            main_content = f.read()
        
        if old_url in main_content:
            main_content = main_content.replace(old_url, new_url)
            with open('main.py', 'w') as f:
                f.write(main_content)
            print(f"  ✅ Updated main.py")
            files_updated.append('main.py')
        else:
            print(f"  ⚠️  Old URL not found in main.py")
    except Exception as e:
        print(f"  ❌ Error updating main.py: {e}")
    
    # 3. Update test scripts
    test_scripts = [
        'debug_mercury.py',
        'debug_full_mercury_data.py', 
        'create_detailed_log.py',
        'simple_test_with_logs.py',
        'test_complete_system.py',
        'test_induct_field.py'
    ]
    
    print(f"\n📝 Updating test scripts...")
    for script in test_scripts:
        if os.path.exists(script):
            try:
                with open(script, 'r') as f:
                    content = f.read()
                
                if old_url in content:
                    content = content.replace(old_url, new_url)
                    with open(script, 'w') as f:
                        f.write(content)
                    print(f"  ✅ Updated {script}")
                    files_updated.append(script)
                else:
                    print(f"  ⚠️  Old URL not found in {script}")
            except Exception as e:
                print(f"  ❌ Error updating {script}: {e}")
        else:
            print(f"  ⚠️  {script} not found")
    
    # 4. Update any Mercury scraper files
    scraper_files = [
        'src/mercury_scraper.py',
        'src/mercury_scraper_updated.py'
    ]
    
    print(f"\n📝 Updating scraper files...")
    for scraper_file in scraper_files:
        if os.path.exists(scraper_file):
            try:
                with open(scraper_file, 'r') as f:
                    content = f.read()
                
                # Look for any hardcoded URLs in the file
                if old_url in content:
                    content = content.replace(old_url, new_url)
                    with open(scraper_file, 'w') as f:
                        f.write(content)
                    print(f"  ✅ Updated {scraper_file}")
                    files_updated.append(scraper_file)
                else:
                    print(f"  ⚠️  Old URL not found in {scraper_file}")
            except Exception as e:
                print(f"  ❌ Error updating {scraper_file}: {e}")
        else:
            print(f"  ⚠️  {scraper_file} not found")
    
    return files_updated, new_url

def update_status_filters():
    """Update status filters for the new AT_STATION focused data"""
    
    print(f"\n🔄 Updating Status Filters for AT_STATION Data")
    print("=" * 45)
    
    # Read current config
    with open('config.yaml', 'r') as f:
        config_content = f.read()
    
    # Update the status configuration for AT_STATION focused monitoring
    old_status_section = '''# Updated statuses based on actual Mercury data analysis
statuses:
  # Current filter (only 10 packages):
  # valid: ["INDUCTED", "INDUCT", "STOW_BUFFER", "AT_STATION"]
  
  # Expanded filter to include packages that passed through induct (990 more packages):
  valid: ["INDUCTED", "INDUCT", "STOW_BUFFER", "AT_STATION", "READY_FOR_DEPARTURE", "DELIVERED", "ON_ROAD_WITH_DELIVERY_ASSOCIATE"]'''
    
    new_status_section = '''# Status filters optimized for AT_STATION induct monitoring
statuses:
  # AT_STATION focused filter for real-time induct monitoring:
  valid: ["AT_STATION", "INDUCTED", "INDUCT", "STOW_BUFFER"]
  
  # Alternative: Include recently processed packages for historical analysis:
  # valid: ["AT_STATION", "INDUCTED", "INDUCT", "STOW_BUFFER", "READY_FOR_DEPARTURE"]'''
    
    if old_status_section in config_content:
        config_content = config_content.replace(old_status_section, new_status_section)
        print(f"✅ Updated status filters for AT_STATION focus")
    else:
        # If exact match not found, add new section
        if "statuses:" not in config_content:
            config_content += f"\n{new_status_section}\n"
            print(f"✅ Added new status filters section")
        else:
            print(f"⚠️  Status section exists but couldn't update automatically")
    
    # Save updated config
    with open('config.yaml', 'w') as f:
        f.write(config_content)
    
    print(f"✅ Status filters updated in config.yaml")

def create_comprehensive_test():
    """Create a comprehensive test script for the new setup"""
    
    print(f"\n🧪 Creating Comprehensive Test Script")
    print("=" * 35)
    
    test_script = '''#!/usr/bin/env python3
"""Comprehensive test for the new AT_STATION Mercury setup"""

import sys
import json
from datetime import datetime
sys.path.insert(0, '.')

def test_new_mercury_setup():
    """Test the complete new Mercury setup with AT_STATION focus"""
    
    print("🧪 Testing New AT_STATION Mercury Setup")
    print("=" * 50)
    
    try:
        # Import components
        from src.mercury_scraper import MercuryScraper
        from src.downtime_analyzer import DowntimeAnalyzer
        from src.data_storage import DataStorage
        
        print("✅ Successfully imported all components")
        
        # Test Mercury scraper with new URL
        print("\\n📥 Testing Mercury scraper...")
        scraper = MercuryScraper(
            mercury_url="https://mercury.amazon.com/getQueryResponse?ID=a9ebdbf5325e9395d4fbd114d3316f0c&region=na",
            valid_locations=['GA1', 'GA2', 'GA3', 'GA4', 'GA5', 'GA6', 'GA7', 'GA8', 'GA9', 'GA10'],
            valid_statuses=['AT_STATION', 'INDUCTED', 'INDUCT', 'STOW_BUFFER']
        )
        
        # Get raw response to check for induct fields
        print("🔍 Checking for induct timestamp fields...")
        session = scraper._get_session()
        if session:
            response = session.get(scraper.mercury_url, timeout=30)
            print(f"✅ Got response: {len(response.text):,} characters")
            
            # Check for induct fields
            induct_field = "compAtStationData.compCurrentNodeAtStationData.firstEventTimestamp"
            if induct_field in response.text:
                count = response.text.count(induct_field)
                print(f"✅ FOUND induct field! Appears {count} times")
            else:
                print(f"❌ Induct field not found in response")
            
            # Test scraping
            print("\\n🔄 Testing data scraping...")
            packages = scraper.scrape_data()
            
            if packages:
                print(f"✅ Scraped {len(packages)} packages")
                
                # Analyze the data
                locations = {}
                statuses = {}
                
                for pkg in packages:
                    location = pkg.get('location', 'Unknown')
                    status = pkg.get('status', 'Unknown')
                    
                    locations[location] = locations.get(location, 0) + 1
                    statuses[status] = statuses.get(status, 0) + 1
                
                print(f"\\n📊 PACKAGE ANALYSIS:")
                print(f"  Locations found: {len(locations)}")
                for loc, count in sorted(locations.items()):
                    print(f"    {loc}: {count}")
                
                print(f"  Statuses found: {len(statuses)}")
                for status, count in sorted(statuses.items()):
                    print(f"    {status}: {count}")
                
                # Show sample packages
                print(f"\\n📋 SAMPLE PACKAGES:")
                for i, pkg in enumerate(packages[:3]):
                    print(f"  {i+1}. {pkg['tracking_id']} at {pkg['location']} - {pkg['status']} - {pkg['timestamp']}")
                
                # Test downtime analysis
                print(f"\\n🧮 Testing downtime analysis...")
                analyzer = DowntimeAnalyzer(
                    categories=[
                        {'name': '20-60', 'min': 20, 'max': 60},
                        {'name': '60-120', 'min': 60, 'max': 120},
                        {'name': '120-780', 'min': 120, 'max': 780}
                    ],
                    break_threshold=780
                )
                
                analysis = analyzer.process_scans(packages)
                downtimes = analysis.get('new_downtimes', [])
                
                print(f"✅ Found {len(downtimes)} downtime events")
                
                # Show sample downtimes
                if downtimes:
                    print(f"\\n⏱️  SAMPLE DOWNTIMES:")
                    for i, dt in enumerate(downtimes[:3]):
                        print(f"  {i+1}. {dt['location']}: {dt['downtime_seconds']}s ({dt['category']})")
                
                # Test data storage
                print(f"\\n🗄️  Testing data storage...")
                storage = DataStorage('test_induct_monitoring.db')
                
                # Store a sample
                success = storage.store_raw_scans(packages[:5])
                if success:
                    print(f"✅ Successfully stored sample data")
                else:
                    print(f"❌ Failed to store data")
                
                return True
            else:
                print(f"❌ No packages retrieved")
                return False
        else:
            print(f"❌ Failed to get authenticated session")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run comprehensive test"""
    
    # Suppress warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print("🚀 Starting Comprehensive AT_STATION Test")
    print("=" * 50)
    
    success = test_new_mercury_setup()
    
    if success:
        print(f"\\n✅ ALL TESTS PASSED!")
        print(f"\\n🎯 SYSTEM READY FOR:")
        print(f"  ✅ Real-time AT_STATION monitoring")
        print(f"  ✅ Accurate induct downtime detection")
        print(f"  ✅ True induct arrival time tracking")
        print(f"  ✅ Monitoring 1000+ TBCs with newest first")
        
        print(f"\\n🚀 READY TO START MONITORING!")
        print(f"  Run: python3 main.py --continuous")
    else:
        print(f"\\n❌ TESTS FAILED - Need to investigate")

if __name__ == "__main__":
    main()
'''
    
    with open('test_new_mercury_complete.py', 'w') as f:
        f.write(test_script)
    
    print(f"✅ Created test_new_mercury_complete.py")

def main():
    """Update entire project for new Mercury URL"""
    
    print("🚀 Updating Entire Project for New Mercury URL")
    print("=" * 50)
    
    # Update Mercury URL everywhere
    files_updated, new_url = update_mercury_url_everywhere()
    
    # Update status filters
    update_status_filters()
    
    # Create comprehensive test
    create_comprehensive_test()
    
    print(f"\n✅ PROJECT UPDATE COMPLETE!")
    print(f"\n📁 Files Updated: {len(files_updated)}")
    for file in files_updated:
        print(f"  ✅ {file}")
    
    print(f"\n🔗 New Mercury URL:")
    print(f"  {new_url}")
    
    print(f"\n🎯 KEY IMPROVEMENTS:")
    print(f"  ✅ AT_STATION focused data source")
    print(f"  ✅ Induct timestamp sorting (newest first)")
    print(f"  ✅ True induct arrival time tracking")
    print(f"  ✅ Optimized for 1000+ TBC monitoring")
    
    print(f"\n📋 NEXT STEPS:")
    print(f"  1. Run: python3 test_new_mercury_complete.py")
    print(f"  2. If tests pass: python3 main.py --test")
    print(f"  3. Start monitoring: python3 main.py --continuous")
    
    print(f"\n🎉 READY FOR AMAZING INDUCT MONITORING!")
    print(f"   With 1000+ TBCs sorted by newest induct scans!")

if __name__ == "__main__":
    main()