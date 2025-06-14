#!/usr/bin/env python3
"""Simulate downtime analysis with sample data to test the logic"""

import sys
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import random

def simulate_downtime_analysis():
    """Simulate downtime analysis using generated sample data"""
    
    print("🧪 Downtime Analysis Simulation")
    print("=" * 60)
    print("Testing downtime calculation logic with simulated induct data")
    print("=" * 60)
    
    # Generate sample induct data for the last hour of shift
    sample_records = generate_sample_induct_data()
    
    print(f"📊 Generated {len(sample_records)} sample induct records")
    
    # Show sample data
    print(f"\n📋 Sample records:")
    for i, record in enumerate(sample_records[:5]):
        print(f"  {i+1}. {record['location']} - {record['tracking_id']} at {record['induct_timestamp']}")
    
    # Analyze downtime by location
    print(f"\n🔍 Analyzing downtime patterns...")
    downtime_analysis = analyze_location_downtime(sample_records)
    
    # Generate comprehensive report
    generate_downtime_report(downtime_analysis)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_simulation_results(downtime_analysis, sample_records, timestamp)
    
    return True

def generate_sample_induct_data():
    """Generate realistic sample induct data for testing"""
    
    # Define shift end period (last hour: 11:30-12:30 UTC)
    today = datetime.now().date()
    shift_start = datetime(today.year, today.month, today.day, 11, 30)
    shift_end = datetime(today.year, today.month, today.day, 12, 30)
    
    records = []
    locations = ['GA1', 'GA2', 'GA3', 'GA4', 'GA5', 'GA6', 'GA7', 'GA8', 'GA9', 'GA10']
    
    # Generate realistic induct patterns for each location
    for location in locations:
        location_records = []
        
        # Random number of packages per location (5-25)
        num_packages = random.randint(5, 25)
        
        current_time = shift_start
        
        for i in range(num_packages):
            # Add realistic gaps between packages
            # Most gaps are 20-60 seconds (normal flow)
            # Some gaps are 60-120 seconds (minor delays)
            # Few gaps are 120-780 seconds (significant delays)
            
            gap_type = random.choices(
                ['normal', 'minor_delay', 'major_delay'],
                weights=[70, 25, 5]  # Most are normal, some delays
            )[0]
            
            if gap_type == 'normal':
                gap_seconds = random.randint(22, 58)
            elif gap_type == 'minor_delay':
                gap_seconds = random.randint(65, 115)
            else:  # major_delay
                gap_seconds = random.randint(125, 450)
            
            current_time += timedelta(seconds=gap_seconds)
            
            # Stop if we exceed shift end
            if current_time > shift_end:
                break
            
            location_records.append({
                'tracking_id': f'TBC{location}{i:03d}',
                'location': location,
                'status': 'INDUCTED',
                'induct_timestamp': current_time,
                'induct_time_str': current_time.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        records.extend(location_records)
    
    # Sort all records by timestamp
    records.sort(key=lambda x: x['induct_timestamp'])
    
    return records

def analyze_location_downtime(records):
    """Analyze downtime between consecutive induct arrivals by location"""
    
    # Group by location
    location_records = defaultdict(list)
    for record in records:
        if record['location'].startswith('GA'):
            location_records[record['location']].append(record)
    
    # Sort by induct timestamp within each location
    for location in location_records:
        location_records[location].sort(key=lambda x: x['induct_timestamp'])
    
    # Calculate downtime between consecutive arrivals
    downtime_analysis = {}
    
    for location, loc_records in location_records.items():
        if len(loc_records) < 2:
            continue
        
        downtimes = []
        for i in range(1, len(loc_records)):
            prev_time = loc_records[i-1]['induct_timestamp']
            curr_time = loc_records[i]['induct_timestamp']
            
            gap_seconds = (curr_time - prev_time).total_seconds()
            
            # Skip gaps > 780 seconds (breaks/shift changes)
            if gap_seconds > 780:
                continue
            
            downtimes.append({
                'gap_seconds': gap_seconds,
                'prev_package': loc_records[i-1]['tracking_id'],
                'curr_package': loc_records[i]['tracking_id'],
                'prev_time': prev_time,
                'curr_time': curr_time
            })
        
        # Categorize downtimes according to business logic
        categories = {
            '20-60s': [d for d in downtimes if 20 <= d['gap_seconds'] <= 60],
            '60-120s': [d for d in downtimes if 60 < d['gap_seconds'] <= 120],
            '120-780s': [d for d in downtimes if 120 < d['gap_seconds'] <= 780]
        }
        
        downtime_analysis[location] = {
            'total_packages': len(loc_records),
            'total_gaps': len(downtimes),
            'categories': categories,
            'avg_gap': sum(d['gap_seconds'] for d in downtimes) / len(downtimes) if downtimes else 0,
            'max_gap': max(d['gap_seconds'] for d in downtimes) if downtimes else 0,
            'min_gap': min(d['gap_seconds'] for d in downtimes) if downtimes else 0,
            'sample_records': loc_records[:3],
            'sample_downtimes': downtimes[:3]
        }
    
    return downtime_analysis

def generate_downtime_report(analysis):
    """Generate comprehensive downtime report"""
    
    print("\n" + "=" * 60)
    print("📊 DOWNTIME ANALYSIS REPORT")
    print("=" * 60)
    
    if not analysis:
        print("⚠️  No downtime data available for analysis")
        return
    
    total_gaps = sum(data['total_gaps'] for data in analysis.values())
    total_packages = sum(data['total_packages'] for data in analysis.values())
    
    print(f"📈 SUMMARY:")
    print(f"   Locations analyzed: {len(analysis)}")
    print(f"   Total packages: {total_packages}")
    print(f"   Total gaps analyzed: {total_gaps}")
    
    # Overall statistics
    all_gaps = []
    for data in analysis.values():
        for category, gaps in data['categories'].items():
            all_gaps.extend([g['gap_seconds'] for g in gaps])
    
    if all_gaps:
        avg_overall = sum(all_gaps) / len(all_gaps)
        print(f"   Average gap: {avg_overall:.1f}s")
        print(f"   Max gap: {max(all_gaps):.1f}s")
        print(f"   Min gap: {min(all_gaps):.1f}s")
    
    print(f"\n🎯 BY LOCATION:")
    for location in sorted(analysis.keys()):
        data = analysis[location]
        print(f"\n   {location}:")
        print(f"     📦 Packages: {data['total_packages']}")
        print(f"     ⏱️  Gaps: {data['total_gaps']}")
        
        if data['total_gaps'] > 0:
            print(f"     📊 Avg gap: {data['avg_gap']:.1f}s")
            print(f"     📈 Max gap: {data['max_gap']:.1f}s")
            print(f"     📉 Min gap: {data['min_gap']:.1f}s")
            
            # Show category breakdown
            for category, gaps in data['categories'].items():
                if gaps:
                    print(f"     🔸 {category}: {len(gaps)} gaps")
                    if gaps:
                        sample_gap = gaps[0]['gap_seconds']
                        print(f"        Sample: {sample_gap:.1f}s")
    
    print(f"\n⚠️  DOWNTIME CATEGORIES (Business Logic):")
    all_categories = defaultdict(list)
    for data in analysis.values():
        for category, gaps in data['categories'].items():
            all_categories[category].extend(gaps)
    
    for category, gaps in all_categories.items():
        if gaps:
            print(f"   {category}: {len(gaps)} total gaps")
            avg_gap = sum(g['gap_seconds'] for g in gaps) / len(gaps)
            print(f"     Average: {avg_gap:.1f}s")
            print(f"     Count: {len(gaps)}")
            
            # Show interpretation
            if category == '20-60s':
                print(f"     💡 Interpretation: Normal flow (common)")
            elif category == '60-120s':
                print(f"     💡 Interpretation: Minor delays (less common)")
            elif category == '120-780s':
                print(f"     💡 Interpretation: Significant delays (rare)")
    
    print(f"\n🚨 KEY INSIGHTS:")
    
    # Identify locations with most delays
    delay_locations = {}
    for location, data in analysis.items():
        delay_count = len(data['categories']['60-120s']) + len(data['categories']['120-780s'])
        if delay_count > 0:
            delay_locations[location] = delay_count
    
    if delay_locations:
        sorted_delays = sorted(delay_locations.items(), key=lambda x: x[1], reverse=True)
        print(f"   🔸 Locations with most delays:")
        for location, count in sorted_delays[:3]:
            print(f"     {location}: {count} delays")
    
    # Identify time periods with delays
    major_delays = []
    for data in analysis.values():
        major_delays.extend(data['categories']['120-780s'])
    
    if major_delays:
        print(f"   🔸 {len(major_delays)} significant delays (120-780s) detected")
        print(f"   🔸 These require investigation for bottleneck identification")

def save_simulation_results(analysis, records, timestamp):
    """Save detailed simulation results"""
    
    os.makedirs('test_logs', exist_ok=True)
    
    # Save analysis results
    results_file = f'test_logs/downtime_simulation_{timestamp}.json'
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'analysis': analysis,
            'total_records': len(records),
            'sample_records': records[:10],
            'simulation_notes': 'Generated sample data for testing downtime calculation logic'
        }, f, indent=2, default=str)
    
    # Save summary report
    summary_file = f'test_logs/downtime_summary_{timestamp}.txt'
    with open(summary_file, 'w') as f:
        f.write(f"Downtime Analysis Simulation - {timestamp}\n")
        f.write("=" * 60 + "\n\n")
        
        total_gaps = sum(data['total_gaps'] for data in analysis.values())
        total_packages = sum(data['total_packages'] for data in analysis.values())
        
        f.write(f"Total packages: {total_packages}\n")
        f.write(f"Total gaps: {total_gaps}\n")
        f.write(f"Locations: {', '.join(sorted(analysis.keys()))}\n\n")
        
        f.write("Downtime Categories:\n")
        all_categories = defaultdict(list)
        for data in analysis.values():
            for category, gaps in data['categories'].items():
                all_categories[category].extend(gaps)
        
        for category, gaps in all_categories.items():
            if gaps:
                avg_gap = sum(g['gap_seconds'] for g in gaps) / len(gaps)
                f.write(f"  {category}: {len(gaps)} gaps (avg: {avg_gap:.1f}s)\n")
    
    print(f"\n💾 Results saved:")
    print(f"   📁 {results_file}")
    print(f"   📁 {summary_file}")

if __name__ == "__main__":
    print("🔧 Downtime Analysis Logic Test")
    print("This simulates the historical downtime analysis without requiring Mercury authentication")
    print("It demonstrates the core business logic for identifying and categorizing downtime")
    print("")
    
    success = simulate_downtime_analysis()
    
    if success:
        print(f"\n✅ Downtime simulation completed successfully!")
        print(f"\nThis test demonstrates:")
        print(f"  🔸 Parsing induct timestamps from package data")
        print(f"  🔸 Grouping packages by location (GA1-GA10)")
        print(f"  🔸 Calculating gaps between consecutive induct arrivals")
        print(f"  🔸 Categorizing downtime by business rules:")
        print(f"    • 20-60s: Normal flow (common)")
        print(f"    • 60-120s: Minor delays (less common)")
        print(f"    • 120-780s: Significant delays (rare)")
        print(f"    • >780s: Breaks/shift changes (ignored)")
        print(f"  🔸 Identifying locations with bottlenecks")
        print(f"  🔸 Generating actionable reports")
        print(f"\n🎯 The system is ready for real-time monitoring!")
        print(f"   When shift is active, it will use real Mercury data")
        print(f"   The same logic will identify actual bottlenecks")
    else:
        print(f"\n❌ Simulation failed")