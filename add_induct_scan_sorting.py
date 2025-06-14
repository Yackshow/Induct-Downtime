#!/usr/bin/env python3
"""Modify Mercury config to sort by newest induct scan timestamp first"""

import json

def add_induct_scan_sorting():
    """Update both tables to sort by induct scan timestamp (newest first)"""
    
    print("🔄 Adding Induct Scan Sorting (Newest First)")
    print("=" * 50)
    
    # Read the enhanced configuration
    try:
        with open('Modified_Mercury_Enhanced_Induct_Fields.json', 'r') as f:
            config = json.load(f)
        print("✅ Loaded Enhanced Mercury configuration")
    except FileNotFoundError:
        print("❌ Modified_Mercury_Enhanced_Induct_Fields.json not found")
        return False
    
    # Find the Data Pull section
    data_pull_section = None
    for row in config['rows']:
        if row.get('title') == 'Data Pull':
            data_pull_section = row
            break
    
    if not data_pull_section:
        print("❌ Could not find Data Pull section")
        return False
    
    print(f"✅ Found Data Pull section with {len(data_pull_section['panels'])} panels")
    
    # Update both tables
    tables_updated = 0
    
    for panel in data_pull_section['panels']:
        table_title = panel.get('title', '')
        
        if table_title in ['TBC Deep Dive Data', 'AT_STATION Real-Time Data']:
            print(f"\n🔄 Updating {table_title}...")
            
            # Current sort
            current_sort = panel.get('sort', ['_score', 'desc'])
            print(f"  Current sort: {current_sort}")
            
            # New sort: by induct timestamp, newest first
            new_sort = ["compAtStationData.compCurrentNodeAtStationData.firstEventTimestamp", "desc"]
            panel['sort'] = new_sort
            
            print(f"  New sort: {new_sort}")
            print(f"  ✅ Updated to sort by induct timestamp (newest first)")
            
            # Ensure sorting is enabled
            panel['sortable'] = True
            
            # Optimize display settings for induct monitoring
            if table_title == 'AT_STATION Real-Time Data':
                panel['size'] = 500  # Show more AT_STATION packages
                panel['batch_size'] = 1000
                print(f"  ✅ AT_STATION table: Display 500, batch 1000")
            elif table_title == 'TBC Deep Dive Data':
                panel['size'] = 300  # Moderate size for testing
                panel['batch_size'] = 1000  
                print(f"  ✅ TBC table: Display 300, batch 1000")
            
            tables_updated += 1
    
    # Save the updated configuration
    output_file = 'Modified_Mercury_Induct_Sorted.json'
    print(f"\n💾 Saving configuration to {output_file}...")
    
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Successfully created {output_file}")
    
    # Create summary
    summary = {
        'sorting_configuration': {
            'sort_field': 'compAtStationData.compCurrentNodeAtStationData.firstEventTimestamp',
            'sort_order': 'descending (newest induct scans first)',
            'purpose': 'Show most recent induct arrivals at the top'
        },
        'tables_updated': tables_updated,
        'display_settings': {
            'AT_STATION Real-Time Data': {'size': 500, 'batch_size': 1000},
            'TBC Deep Dive Data': {'size': 300, 'batch_size': 1000}
        },
        'benefits': [
            'Newest induct arrivals appear first',
            'Catch recent packages immediately',
            'Monitor most current induct activity',
            'Perfect for real-time downtime detection',
            'Avoid missing new arrivals due to pagination'
        ],
        'what_youll_see': [
            'Top rows: Packages that just arrived at induct stations',
            'Recent induct timestamps like 2025-06-14 12:xx:xx at top',
            'Older induct timestamps towards bottom',
            'Clear view of induct activity timeline'
        ]
    }
    
    with open('induct_sorting_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📊 INDUCT SCAN SORTING SUMMARY:")
    print(f"  🔄 Sort field: compAtStationData.compCurrentNodeAtStationData.firstEventTimestamp")
    print(f"  📅 Sort order: Newest induct scans first (descending)")
    print(f"  📋 Tables updated: {tables_updated}")
    print(f"  ✅ Sortable: Enabled on both tables")
    
    print(f"\n🎯 BENEFITS:")
    for benefit in summary['benefits']:
        print(f"  ✅ {benefit}")
    
    print(f"\n👀 WHAT YOU'LL SEE:")
    for item in summary['what_youll_see']:
        print(f"  📊 {item}")
    
    print(f"\n📤 NEXT STEPS:")
    print(f"  1. Upload {output_file} to Mercury")
    print(f"  2. Check both tables show newest induct scans at top")
    print(f"  3. Verify induct timestamps are sorted correctly") 
    print(f"  4. Run python3 test_induct_field.py to test extraction")
    print(f"  5. Update monitoring script to use induct timestamps")
    
    print(f"\n🎉 PERFECT FOR INDUCT DOWNTIME MONITORING!")
    print(f"   Newest induct arrivals first = catch issues immediately!")
    
    return True

if __name__ == "__main__":
    try:
        success = add_induct_scan_sorting()
        if success:
            print(f"\n✅ Induct scan sorting configured successfully!")
            print(f"📁 Upload: Modified_Mercury_Induct_Sorted.json")
            print(f"📁 Summary: induct_sorting_summary.json")
        else:
            print(f"\n❌ Failed to configure induct scan sorting")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()