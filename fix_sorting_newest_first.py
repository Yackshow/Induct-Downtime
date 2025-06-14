#!/usr/bin/env python3
"""Fix Mercury table sorting to show newest AT_STATION packages first"""

import json

def fix_sorting():
    """Update sorting to show newest packages first"""
    
    print("🔄 Fixing Mercury Sorting Configuration")
    print("=" * 50)
    
    # Read the modified configuration
    print("📥 Reading Modified_Mercury_AT_STATION.json...")
    with open('Modified_Mercury_AT_STATION.json', 'r') as f:
        config = json.load(f)
    
    # Find the Data Pull section and AT_STATION table
    data_pull_section = None
    for row in config['rows']:
        if row.get('title') == 'Data Pull':
            data_pull_section = row
            break
    
    if not data_pull_section:
        print("❌ Could not find Data Pull section")
        return False
    
    # Find the AT_STATION Real-Time Data table
    at_station_table = None
    at_station_index = None
    
    for i, panel in enumerate(data_pull_section['panels']):
        if panel.get('title') == 'AT_STATION Real-Time Data':
            at_station_table = panel
            at_station_index = i
            break
    
    if not at_station_table:
        print("❌ Could not find AT_STATION Real-Time Data table")
        return False
    
    print("✅ Found AT_STATION Real-Time Data table")
    
    # Update sorting configuration
    print("🔄 Updating sort configuration...")
    
    # Current sort
    current_sort = at_station_table.get('sort', ['_score', 'desc'])
    print(f"Current sort: {current_sort}")
    
    # New sort: by compLastScanInOrder.timestamp, newest first (desc)
    new_sort = ["compLastScanInOrder.timestamp", "desc"]
    at_station_table['sort'] = new_sort
    
    print(f"New sort: {new_sort}")
    print("✅ Updated to sort by timestamp (newest first)")
    
    # Also update the sortable flag to ensure sorting is enabled
    at_station_table['sortable'] = True
    
    # Increase the default display size to show more packages
    at_station_table['size'] = 500  # Show 500 packages by default
    at_station_table['batch_size'] = 1000  # Load 1000 at a time
    
    print("✅ Enabled sorting and increased display size to 500 packages")
    
    # Save the updated configuration
    output_file = 'Modified_Mercury_AT_STATION_Sorted.json'
    print(f"💾 Saving updated configuration to {output_file}...")
    
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Successfully created {output_file}")
    
    # Create summary
    summary = {
        'sorting_changes': {
            'old_sort': current_sort,
            'new_sort': new_sort,
            'sort_field': 'compLastScanInOrder.timestamp',
            'sort_order': 'descending (newest first)'
        },
        'display_changes': {
            'default_size': 500,
            'batch_size': 1000,
            'sortable': True
        },
        'benefits': [
            'Newest AT_STATION packages appear first',
            'Catch new arrivals immediately',
            'Avoid missing packages due to pagination',
            'Prioritize recent induct activity',
            'Better real-time monitoring'
        ]
    }
    
    with open('sorting_fix_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n📊 SORTING IMPROVEMENTS:")
    print(f"  🔄 Sort field: compLastScanInOrder.timestamp")
    print(f"  📅 Sort order: Newest first (descending)")
    print(f"  📋 Display size: 500 packages")
    print(f"  📦 Batch size: 1000 packages")
    print(f"  ✅ Sortable: Enabled")
    
    print(f"\n🎯 BENEFITS:")
    for benefit in summary['benefits']:
        print(f"  ✅ {benefit}")
    
    print(f"\n📤 NEXT STEPS:")
    print(f"  1. Upload {output_file} to Mercury")
    print(f"  2. Verify newest packages appear at the top")
    print(f"  3. Test that you see 500+ AT_STATION packages")
    print(f"  4. Update monitoring script to use new URL")
    
    return True

if __name__ == "__main__":
    try:
        success = fix_sorting()
        if success:
            print(f"\n✅ Sorting configuration fixed successfully!")
            print(f"📁 Files created:")
            print(f"  - Modified_Mercury_AT_STATION_Sorted.json (upload this)")
            print(f"  - sorting_fix_summary.json (summary of changes)")
        else:
            print(f"\n❌ Failed to fix sorting configuration")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()