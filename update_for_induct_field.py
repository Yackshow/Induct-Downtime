#!/usr/bin/env python3
"""Update the monitoring system to use the Last Induct Scan field"""

def update_config_documentation():
    """Add documentation about the induct field discovery"""
    
    print("🔧 Updating Configuration Documentation")
    print("=" * 50)
    
    # Read current config
    with open('config.yaml', 'r') as f:
        config_content = f.read()
    
    # Add note about induct field discovery
    induct_note = '''
# ✅ FIELD MAPPING DISCOVERY:
# Web Interface "Last Induct Scan" = compAtStationData.compCurrentNodeAtStationData.firstEventTimestamp (HTML)
# This field shows ACTUAL induct arrival time, not latest scan anywhere
# Perfect for downtime monitoring between consecutive induct arrivals!

'''
    
    # Add the note at the top
    if "FIELD MAPPING DISCOVERY" not in config_content:
        config_content = induct_note + config_content
        
        with open('config.yaml', 'w') as f:
            f.write(config_content)
        
        print("✅ Added induct field documentation to config.yaml")
    else:
        print("⚠️  Config already has induct field documentation")

def create_induct_test_script():
    """Create test script to verify induct timestamp extraction"""
    
    print("\n🧪 Creating Induct Timestamp Test Script")
    print("=" * 40)
    
    test_script = '''#!/usr/bin/env python3
"""Test induct timestamp field extraction"""

import sys
sys.path.insert(0, '.')

def test_induct_field():
    """Test extraction of compAtStationData.compCurrentNodeAtStationData.firstEventTimestamp"""
    
    print("🧪 Testing Induct Timestamp Field")
    print("=" * 50)
    
    try:
        from src.mercury_scraper import MercuryScraper
        
        # Test with current scraper to see if we get the field
        scraper = MercuryScraper(
            mercury_url="https://mercury.amazon.com/getQueryResponse?ID=127de24b92c1f65c47f001541fbc6974&region=na",
            valid_locations=['GA1', 'GA2', 'GA3', 'GA4', 'GA5', 'GA6', 'GA7', 'GA8', 'GA9', 'GA10'],
            valid_statuses=['READY_FOR_DEPARTURE', 'DELIVERED', 'AT_STATION', 'ON_ROAD_WITH_DELIVERY_ASSOCIATE']
        )
        
        # Get session and raw response
        print("📥 Fetching raw Mercury data...")
        session = scraper._get_session()
        if not session:
            print("❌ Failed to get session")
            return False
        
        response = session.get(scraper.mercury_url, timeout=30)
        print(f"✅ Got response: {len(response.text)} characters")
        
        # Check if induct field is in the response
        induct_field = "compAtStationData.compCurrentNodeAtStationData.firstEventTimestamp"
        
        if induct_field in response.text:
            print(f"✅ FOUND: {induct_field} is in the response!")
            
            # Count occurrences
            count = response.text.count(induct_field)
            print(f"📊 Field appears {count} times in response")
        else:
            print(f"❌ Field {induct_field} NOT found in response")
            print("⚠️  Need to ensure enhanced Mercury config is uploaded")
        
        # Also check alternative field
        alt_field = "compAtStationData.compFirstNodeAtStationData.firstEventTimestamp"
        if alt_field in response.text:
            print(f"✅ FOUND: {alt_field} is also in the response!")
        
        # Test parsing with current scraper
        print(f"\\n🔄 Testing current scraper parsing...")
        records = scraper.scrape_data()
        
        if records:
            print(f"✅ Scraped {len(records)} records")
            
            # Show sample
            sample = records[0] if records else {}
            print(f"\\n📊 Sample record structure:")
            for key, value in sample.items():
                print(f"  {key}: {str(value)[:50]}...")
        else:
            print(f"❌ No records scraped")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    success = test_induct_field()
    
    if success:
        print(f"\\n✅ Test completed!")
        print(f"\\nNEXT STEPS:")
        print(f"1. Ensure Modified_Mercury_Enhanced_Induct_Fields.json is uploaded")
        print(f"2. If induct field found, we can modify scraper to use it")
        print(f"3. This will give us TRUE induct downtime monitoring!")
    else:
        print(f"\\n❌ Test failed")
'''
    
    with open('test_induct_field.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Created test_induct_field.py")

def main():
    """Update system for induct field support"""
    
    print("🚀 Updating System for Last Induct Scan Field")
    print("=" * 50)
    
    # Update config documentation
    update_config_documentation()
    
    # Create test script
    create_induct_test_script()
    
    print(f"\n✅ SYSTEM PREPARED FOR INDUCT FIELD!")
    print(f"\n📁 Files Created:")
    print(f"  - config.yaml (updated with field documentation)")
    print(f"  - test_induct_field.py (test if field is available)")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"  1. Ensure Modified_Mercury_Enhanced_Induct_Fields.json is uploaded to Mercury")
    print(f"  2. Run: python3 test_induct_field.py")
    print(f"  3. If induct field is found, we can update the scraper")
    print(f"  4. TRUE induct downtime monitoring will be ready!")
    
    print(f"\n🎉 DISCOVERY SUMMARY:")
    print(f"  Web Interface 'Last Induct Scan' = compAtStationData.compCurrentNodeAtStationData.firstEventTimestamp")
    print(f"  This gives us ACTUAL induct arrival times for perfect downtime calculation!")

if __name__ == "__main__":
    main()