#!/usr/bin/env python3
"""Analyze Mercury HTML to find available fields and suggest fixes"""

import sys
import re
from collections import Counter

def analyze_mercury_html():
    """Analyze the raw Mercury HTML to understand available fields"""
    
    print("🔍 Mercury HTML Field Analysis")
    print("=" * 60)
    
    try:
        # Read the raw Mercury HTML
        with open('mercury_logs/raw_mercury_20250614_141857.html', 'r') as f:
            html_content = f.read()
        
        print(f"✅ Loaded Mercury HTML: {len(html_content):,} characters")
        
        # Find table headers
        print("\n📊 TABLE HEADER ANALYSIS:")
        header_pattern = r'<th[^>]*>([^<]+)</th>'
        headers = re.findall(header_pattern, html_content)
        
        print(f"Found {len(headers)} table headers:")
        for i, header in enumerate(headers):
            print(f"  {i:2d}: {header}")
        
        # Look for location-related fields
        print("\n🗺️  LOCATION FIELD ANALYSIS:")
        location_fields = [h for h in headers if 'location' in h.lower() or 'destination' in h.lower() or 'induct' in h.lower()]
        if location_fields:
            print("Found location-related headers:")
            for field in location_fields:
                print(f"  • {field}")
        else:
            print("⚠️  No obvious location fields found in headers")
        
        # Look for timestamp fields
        print("\n🕐 TIMESTAMP FIELD ANALYSIS:")
        timestamp_fields = [h for h in headers if 'time' in h.lower() or 'scan' in h.lower() or 'event' in h.lower()]
        if timestamp_fields:
            print("Found timestamp-related headers:")
            for field in timestamp_fields:
                print(f"  • {field}")
        else:
            print("⚠️  No obvious timestamp fields found in headers")
        
        # Look for the specific induct field we need
        print("\n🎯 INDUCT TIMESTAMP FIELD SEARCH:")
        induct_field = "compAtStationData.compCurrentNodeAtStationData.firstEventTimestamp"
        if induct_field in html_content:
            count = html_content.count(induct_field)
            print(f"✅ FOUND: {induct_field}")
            print(f"   Appears {count} times in HTML")
        else:
            print(f"❌ NOT FOUND: {induct_field}")
            print("   This means the enhanced Mercury config needs to be uploaded")
        
        # Look for alternative timestamp fields
        alt_patterns = [
            "firstEventTimestamp",
            "lastScanTimestamp", 
            "timestamp",
            "eventTimestamp",
            "scanTime"
        ]
        
        print(f"\n🔍 ALTERNATIVE TIMESTAMP FIELDS:")
        for pattern in alt_patterns:
            if pattern in html_content:
                count = html_content.count(pattern)
                print(f"  ✅ {pattern}: appears {count} times")
            else:
                print(f"  ❌ {pattern}: not found")
        
        # Analyze table structure
        print(f"\n📋 TABLE STRUCTURE ANALYSIS:")
        
        # Count table rows
        row_pattern = r'<tr[^>]*>'
        rows = re.findall(row_pattern, html_content)
        print(f"  Total table rows: {len(rows)}")
        
        # Look for data patterns
        cell_pattern = r'<td[^>]*>([^<]*)</td>'
        cells = re.findall(cell_pattern, html_content)
        print(f"  Total table cells: {len(cells)}")
        
        # Find GA location patterns
        ga_pattern = r'GA\d+'
        ga_matches = re.findall(ga_pattern, html_content)
        ga_counter = Counter(ga_matches)
        
        print(f"\n🏭 GA LOCATION ANALYSIS:")
        if ga_counter:
            print(f"  Found GA locations in HTML:")
            for location, count in sorted(ga_counter.items()):
                print(f"    {location}: appears {count} times")
        else:
            print(f"  ⚠️  No GA locations found in HTML content")
            print(f"     This suggests Mercury table is not configured to show locations")
        
        # Status analysis
        print(f"\n📊 STATUS ANALYSIS:")
        status_patterns = ["AT_STATION", "READY_FOR_DEPARTURE", "INDUCTED", "INDUCT", "STOW_BUFFER", "DELIVERED"]
        for status in status_patterns:
            if status in html_content:
                count = html_content.count(status)
                print(f"  {status}: {count} occurrences")
        
        # Generate recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if induct_field not in html_content:
            print(f"  🔧 CRITICAL: Upload enhanced Mercury configuration")
            print(f"     • File: Modified_Mercury_Enhanced_Induct_Sorted.json")
            print(f"     • This will add the 'Last Induct Scan' field")
        
        if not ga_counter or len(ga_counter) == 1:
            print(f"  🔧 Location field issue detected")
            print(f"     • Mercury table may not be showing proper induct locations")
            print(f"     • Verify 'Induct.destination.id' field is included")
        
        if html_content.count("READY_FOR_DEPARTURE") > html_content.count("AT_STATION") * 10:
            print(f"  🔧 Status filter optimization needed")
            print(f"     • Most packages have left induct stations")
            print(f"     • Consider AT_STATION-only Mercury table for real-time monitoring")
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"  1. Upload Modified_Mercury_Enhanced_Induct_Sorted.json to Mercury")
        print(f"  2. Verify table shows GA1-GA10 locations properly")
        print(f"  3. Re-run test to confirm induct timestamp field appears")
        print(f"  4. Test real downtime analysis with enhanced data")
        
        return True
        
    except FileNotFoundError:
        print("❌ Mercury HTML file not found")
        print("   Run test_real_mercury_downtime.py first to generate the data")
        return False
    except Exception as e:
        print(f"❌ Error analyzing HTML: {e}")
        return False

if __name__ == "__main__":
    success = analyze_mercury_html()
    
    if success:
        print(f"\n✅ Analysis complete!")
        print(f"   The findings above show exactly what needs to be fixed")
        print(f"   for full downtime monitoring capability")
    else:
        print(f"\n❌ Analysis failed")