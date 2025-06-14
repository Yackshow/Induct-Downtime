#!/usr/bin/env python3
"""Create modified Mercury configuration with AT_STATION table and remove redundant table"""

import json
import sys

def modify_mercury_config():
    """Modify Mercury configuration to add AT_STATION table and remove redundant table"""
    
    print("🔄 Modifying Mercury Configuration")
    print("=" * 50)
    
    # Read original configuration
    print("📥 Reading original Mercury configuration...")
    with open('Current Mercury', 'r') as f:
        config = json.load(f)
    
    print(f"✅ Loaded configuration: {config['title']}")
    
    # Find the panels containing the tables we want to modify
    data_pull_section = None
    data_pull_index = None
    
    for i, row in enumerate(config['rows']):
        if row.get('title') == 'Data Pull':
            data_pull_section = row
            data_pull_index = i
            break
    
    if not data_pull_section:
        print("❌ Could not find 'Data Pull' section")
        return False
    
    print(f"✅ Found 'Data Pull' section with {len(data_pull_section['panels'])} panels")
    
    # Find the specific tables
    tbc_table = None
    tbc_index = None
    induct_flow_table = None
    induct_flow_index = None
    
    for i, panel in enumerate(data_pull_section['panels']):
        title = panel.get('title', '')
        if title == 'TBC Deep Dive Data':
            tbc_table = panel
            tbc_index = i
            print(f"✅ Found TBC Deep Dive Data table at index {i}")
        elif title == 'Induct Flow By Location - Raw Data':
            induct_flow_table = panel
            induct_flow_index = i
            print(f"✅ Found Induct Flow By Location table at index {i}")
    
    if not tbc_table:
        print("❌ Could not find 'TBC Deep Dive Data' table")
        return False
    
    # Create new AT_STATION table by duplicating TBC table
    print("🔄 Creating AT_STATION Real-Time Data table...")
    at_station_table = json.loads(json.dumps(tbc_table))  # Deep copy
    
    # Modify the new table for AT_STATION only
    at_station_table['title'] = 'AT_STATION Real-Time Data'
    at_station_table['queries'] = {
        "mode": "selected",
        "ids": [14]  # Query ID 14 is the AT_STATION query
    }
    
    # Add custom filter to ensure we get AT_STATION packages
    at_station_table['customfilter'] = 'compLastScanInOrder.internalStatusCode:AT_STATION'
    
    # Reduce batch size for faster loading of real-time data
    at_station_table['default_batch_size_v2'] = 10000
    at_station_table['batch_size'] = 1000
    
    print("✅ Created AT_STATION Real-Time Data table")
    
    # Remove the redundant Induct Flow table if it exists
    if induct_flow_table and induct_flow_index is not None:
        print(f"🗑️ Removing 'Induct Flow By Location - Raw Data' table...")
        data_pull_section['panels'].pop(induct_flow_index)
        print("✅ Removed redundant table")
        
        # Adjust TBC index if needed
        if tbc_index > induct_flow_index:
            tbc_index -= 1
    
    # Insert the new AT_STATION table after the original TBC table
    data_pull_section['panels'].insert(tbc_index + 1, at_station_table)
    print("✅ Added AT_STATION Real-Time Data table")
    
    # Update the configuration
    config['rows'][data_pull_index] = data_pull_section
    
    # Save the modified configuration
    output_file = 'Modified_Mercury_AT_STATION.json'
    print(f"💾 Saving modified configuration to {output_file}...")
    
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Successfully created {output_file}")
    
    # Create summary of changes
    summary = {
        'original_title': config['title'],
        'changes_made': [
            'Duplicated "TBC Deep Dive Data" table',
            'Created "AT_STATION Real-Time Data" table with Query ID 14',
            'Added AT_STATION filter: compLastScanInOrder.internalStatusCode:AT_STATION',
            'Reduced batch size for faster real-time loading',
        ],
        'tables_in_data_pull_section': [panel.get('title', 'Untitled') for panel in data_pull_section['panels']],
        'at_station_query_id': 14,
        'at_station_filter': 'compLastScanInOrder.internalStatusCode:AT_STATION'
    }
    
    if induct_flow_table:
        summary['changes_made'].append('Removed "Induct Flow By Location - Raw Data" table')
    
    # Save summary
    with open('mercury_modification_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n📊 SUMMARY OF CHANGES:")
    for change in summary['changes_made']:
        print(f"  ✅ {change}")
    
    print(f"\n📋 Tables now in Data Pull section:")
    for i, title in enumerate(summary['tables_in_data_pull_section'], 1):
        print(f"  {i}. {title}")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"  1. Upload {output_file} to Mercury")
    print(f"  2. Test the new 'AT_STATION Real-Time Data' table")
    print(f"  3. Update your Python script to use the new Mercury URL/ID")
    print(f"  4. Verify you get more AT_STATION packages than before")
    
    return True

if __name__ == "__main__":
    try:
        success = modify_mercury_config()
        if success:
            print(f"\n✅ Mercury configuration modified successfully!")
            print(f"📁 Files created:")
            print(f"  - Modified_Mercury_AT_STATION.json (upload this to Mercury)")
            print(f"  - mercury_modification_summary.json (summary of changes)")
        else:
            print(f"\n❌ Failed to modify Mercury configuration")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)