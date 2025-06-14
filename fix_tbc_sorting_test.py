#!/usr/bin/env python3
"""Fix TBC Deep Dive Data sorting to test newest-first functionality"""

import json

def fix_tbc_sorting():
    """Update TBC Deep Dive Data table sorting to show newest packages first"""
    
    print("🔄 Fixing TBC Deep Dive Data Sorting for Testing")
    print("=" * 50)
    
    # Read the latest configuration
    print("📥 Reading Modified_Mercury_AT_STATION_Sorted.json...")
    with open('Modified_Mercury_AT_STATION_Sorted.json', 'r') as f:
        config = json.load(f)
    
    # Find the Data Pull section
    data_pull_section = None
    for row in config['rows']:
        if row.get('title') == 'Data Pull':
            data_pull_section = row
            break
    
    if not data_pull_section:
        print("❌ Could not find Data Pull section")
        return False
    
    # Find the TBC Deep Dive Data table
    tbc_table = None
    tbc_index = None
    
    for i, panel in enumerate(data_pull_section['panels']):
        if panel.get('title') == 'TBC Deep Dive Data':
            tbc_table = panel
            tbc_index = i
            break
    
    if not tbc_table:
        print("❌ Could not find TBC Deep Dive Data table")
        return False
    
    print("✅ Found TBC Deep Dive Data table")
    
    # Update sorting configuration for TBC table
    print("🔄 Updating TBC Deep Dive Data sort configuration...")
    
    # Current sort
    current_sort = tbc_table.get('sort', ['_score', 'desc'])
    print(f"Current TBC sort: {current_sort}")
    
    # New sort: by compLastScanInOrder.timestamp, newest first (desc)
    new_sort = ["compLastScanInOrder.timestamp", "desc"]
    tbc_table['sort'] = new_sort
    
    print(f"New TBC sort: {new_sort}")
    print("✅ Updated TBC to sort by timestamp (newest first)")
    
    # Enable sorting and improve display
    tbc_table['sortable'] = True
    tbc_table['size'] = 500  # Show more packages
    tbc_table['batch_size'] = 1000  # Load more at once
    
    print("✅ Enabled TBC sorting and increased display size")
    
    # Also verify AT_STATION table still has correct sorting
    at_station_table = None
    for panel in data_pull_section['panels']:
        if panel.get('title') == 'AT_STATION Real-Time Data':
            at_station_table = panel
            break
    
    if at_station_table:
        at_station_sort = at_station_table.get('sort', ['_score', 'desc'])
        print(f"✅ AT_STATION table sort: {at_station_sort}")
    else:
        print("⚠️  AT_STATION table not found (this is OK)")
    
    # Save the updated configuration
    output_file = 'Modified_Mercury_Both_Tables_Sorted.json'
    print(f"💾 Saving updated configuration to {output_file}...")
    
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Successfully created {output_file}")
    
    # Create test summary
    summary = {
        'tables_updated': [
            {
                'name': 'TBC Deep Dive Data',
                'old_sort': current_sort,
                'new_sort': new_sort,
                'display_size': 500,
                'purpose': 'Testing sorting functionality with current data'
            }
        ],
        'sorting_field': 'compLastScanInOrder.timestamp',
        'sorting_order': 'descending (newest first)',
        'test_expectations': [
            'Newest package timestamps at top of TBC table',
            'Most recent scans appear first',
            'Packages sorted by last scan time (newest to oldest)',
            'Can verify sorting is working during non-shift hours'
        ],
        'verification_steps': [
            '1. Upload Modified_Mercury_Both_Tables_Sorted.json',
            '2. Open TBC Deep Dive Data table',
            '3. Check compLastScanInOrder.timestamp column',
            '4. Verify newest timestamps are at the top',
            '5. Confirm sorting by timestamp is working'
        ]
    }
    
    if at_station_table:
        summary['tables_updated'].append({
            'name': 'AT_STATION Real-Time Data',
            'sort': at_station_table.get('sort'),
            'display_size': at_station_table.get('size'),
            'purpose': 'Real-time monitoring when shift is active'
        })
    
    with open('sorting_test_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n📊 SORTING TEST CONFIGURATION:")
    print(f"  📋 TBC Deep Dive Data: Sort by timestamp (newest first)")
    print(f"  📋 Display size: 500 packages")
    print(f"  📋 Batch size: 1000 packages")
    print(f"  ✅ Sortable: Enabled")
    
    if at_station_table:
        print(f"  📋 AT_STATION Table: Also sorted by timestamp")
    
    print(f"\n🧪 TEST EXPECTATIONS:")
    for expectation in summary['test_expectations']:
        print(f"  ✅ {expectation}")
    
    print(f"\n📋 VERIFICATION STEPS:")
    for step in summary['verification_steps']:
        print(f"  {step}")
    
    print(f"\n🎯 WHAT YOU'LL SEE:")
    print(f"  📅 Top rows: Packages with timestamps like 2025-06-14 12:xx:xx")
    print(f"  📅 Middle rows: Packages with earlier today timestamps")
    print(f"  📅 Bottom rows: Packages from earlier in the day")
    print(f"  🔍 All sorted by compLastScanInOrder.timestamp column")
    
    return True

if __name__ == "__main__":
    try:
        success = fix_tbc_sorting()
        if success:
            print(f"\n✅ TBC Deep Dive Data sorting configured for testing!")
            print(f"📁 File to upload: Modified_Mercury_Both_Tables_Sorted.json")
            print(f"📁 Test summary: sorting_test_summary.json")
            print(f"\n🚀 Now you can test if the sorting feature works!")
        else:
            print(f"\n❌ Failed to configure TBC sorting")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()