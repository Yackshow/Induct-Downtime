#!/usr/bin/env python3
"""Find the Last Induct Scan field mapping between web interface and HTML response"""

import json
from datetime import datetime

def analyze_induct_scan_fields():
    """Analyze the field mappings to find Last Induct Scan equivalent"""
    
    print("🔍 Finding 'Last Induct Scan' Field in HTML Response")
    print("=" * 60)
    
    # The data you provided
    web_interface_data = {
        "Tracking ID": "TBC498199730009",
        "Induct Location": "GA6", 
        "Last Induct Scan": "2025-06-14 03:54:43 AM",  # This is what we want!
        "Latest Scan": "2025-06-14 03:54:43 AM",
        "Status": "DELIVERED"
    }
    
    html_response_data = {
        "trackingId": "TBC498199730009",
        "Induct.destination.id": "GA6",
        "lastScanInOrder.timestamp": "2025-06-14T07:54:43Z",
        "compLastScanInOrder.timestamp": "2025-06-14T07:54:43Z",
        "compLastScanInOrder.internalStatusCode": "DELIVERED"
    }
    
    print("📊 WEB INTERFACE DATA:")
    for key, value in web_interface_data.items():
        print(f"  {key}: {value}")
    
    print(f"\n📊 HTML RESPONSE DATA:")
    for key, value in html_response_data.items():
        print(f"  {key}: {value}")
    
    print(f"\n🤔 ANALYSIS:")
    print(f"❌ 'Last Induct Scan' (03:54:43 AM) ≠ 'lastScanInOrder.timestamp' (07:54:43Z)")
    print(f"❌ 'Last Induct Scan' (03:54:43 AM) ≠ 'compLastScanInOrder.timestamp' (07:54:43Z)")
    print(f"✅ 'Latest Scan' (03:54:43 AM) = 'compLastScanInOrder.timestamp' (07:54:43Z) [timezone diff]")
    
    print(f"\n💡 HYPOTHESIS:")
    print(f"The 'Last Induct Scan' field is likely a separate field that tracks")
    print(f"specifically when the package was scanned at an INDUCT station,")
    print(f"while 'compLastScanInOrder.timestamp' tracks the most recent scan anywhere.")
    
    # Potential field names to look for
    potential_fields = [
        "Induct.timestamp",
        "Induct.lastScan",
        "Induct.scanTime", 
        "inductScan.timestamp",
        "compAtStationData.compCurrentNodeAtStationData.firstEventTimestamp",
        "compAtStationData.compFirstNodeAtStationData.firstEventTimestamp",
        "Induct.metaData.SCAN_TIME",
        "Induct.metaData.TIMESTAMP",
        "Induct.scanTimestamp",
        "lastInductScan",
        "lastInductScanTimestamp"
    ]
    
    print(f"\n🔍 POTENTIAL FIELD NAMES TO INVESTIGATE:")
    for i, field in enumerate(potential_fields, 1):
        print(f"  {i:2d}. {field}")
    
    print(f"\n🛠️ RECOMMENDED INVESTIGATION STEPS:")
    print(f"1. Check current Mercury table configuration for induct-related fields")
    print(f"2. Add potential induct scan fields to the Mercury table")
    print(f"3. Compare HTML response with web interface to find the mapping")
    print(f"4. Test with a few packages to confirm the field")
    
    return potential_fields

def create_enhanced_mercury_config():
    """Create Mercury config with additional induct-related fields"""
    
    print(f"\n🔧 Creating Enhanced Mercury Configuration")
    print("=" * 50)
    
    # Read the current configuration
    try:
        with open('Modified_Mercury_Both_Tables_Sorted.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Modified_Mercury_Both_Tables_Sorted.json not found")
        return False
    
    # Find the Data Pull section and tables
    data_pull_section = None
    for row in config['rows']:
        if row.get('title') == 'Data Pull':
            data_pull_section = row
            break
    
    if not data_pull_section:
        print("❌ Could not find Data Pull section")
        return False
    
    # Additional fields to add for induct scan investigation
    additional_fields = [
        "compAtStationData.compCurrentNodeAtStationData.firstEventTimestamp",
        "compAtStationData.compFirstNodeAtStationData.firstEventTimestamp", 
        "Induct.timestamp",
        "Induct.scanTimestamp",
        "Induct.metaData.SCAN_TIME",
        "Induct.metaData.TIMESTAMP",
        "lastInductScan",
        "lastInductScanTimestamp"
    ]
    
    # Update both tables to include these fields
    tables_updated = 0
    
    for panel in data_pull_section['panels']:
        table_title = panel.get('title', '')
        
        if table_title in ['TBC Deep Dive Data', 'AT_STATION Real-Time Data']:
            current_fields = panel.get('fields', [])
            
            # Add new fields if not already present
            for field in additional_fields:
                if field not in current_fields:
                    current_fields.append(field)
            
            panel['fields'] = current_fields
            tables_updated += 1
            print(f"✅ Updated {table_title} with {len(additional_fields)} additional fields")
    
    # Save enhanced configuration
    output_file = 'Modified_Mercury_Enhanced_Induct_Fields.json'
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"💾 Saved enhanced configuration to {output_file}")
    
    # Create investigation summary
    summary = {
        'objective': 'Find the Last Induct Scan field equivalent in HTML response',
        'web_interface_target': 'Last Induct Scan column',
        'added_fields': additional_fields,
        'tables_updated': tables_updated,
        'next_steps': [
            'Upload Modified_Mercury_Enhanced_Induct_Fields.json',
            'Check which new fields contain induct scan data',
            'Compare timestamps with web interface Last Induct Scan',
            'Identify the correct field for downtime monitoring',
            'Update Python script to use the correct field'
        ]
    }
    
    with open('induct_field_investigation.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📋 ENHANCED CONFIGURATION SUMMARY:")
    print(f"  📊 Tables updated: {tables_updated}")
    print(f"  🔍 Additional fields added: {len(additional_fields)}")
    print(f"  📁 Configuration file: {output_file}")
    
    print(f"\n🎯 INVESTIGATION PLAN:")
    for step in summary['next_steps']:
        print(f"  📋 {step}")
    
    return True

if __name__ == "__main__":
    # Analyze the field mappings
    potential_fields = analyze_induct_scan_fields()
    
    # Create enhanced Mercury configuration
    success = create_enhanced_mercury_config()
    
    if success:
        print(f"\n✅ Enhanced Mercury configuration created!")
        print(f"📁 Upload: Modified_Mercury_Enhanced_Induct_Fields.json")
        print(f"📁 Investigation guide: induct_field_investigation.json")
        print(f"\n🎯 This will help us find the 'Last Induct Scan' field!")
    else:
        print(f"\n❌ Failed to create enhanced configuration")