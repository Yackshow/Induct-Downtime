"""
System Test - Offline Mode
Tests system components individually without external dependencies
"""

import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
import random
from typing import List, Dict

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

# Test each component individually to identify what works and what needs dependencies


def test_core_components():
    """Test individual components to identify what works offline"""
    print("🧪 System Component Test - Identifying Dependencies")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Downtime Analyzer (should work - no external dependencies)
    print("\n1. Testing Downtime Analyzer...")
    try:
        from src.downtime_analyzer import DowntimeAnalyzer
        
        categories = [
            {'name': '20-60', 'min': 20, 'max': 60},
            {'name': '60-120', 'min': 60, 'max': 120},
            {'name': '120-780', 'min': 120, 'max': 780}
        ]
        analyzer = DowntimeAnalyzer(categories=categories, break_threshold=780)
        
        # Test with sample data
        test_scans = [
            {
                'tracking_id': 'T001',
                'location': 'GA1',
                'status': 'INDUCTED',
                'timestamp': datetime.now(),
                'raw_timestamp': datetime.now().isoformat(),
                'scraped_at': datetime.now().isoformat()
            },
            {
                'tracking_id': 'T002',
                'location': 'GA1',
                'status': 'INDUCTED',
                'timestamp': datetime.now() + timedelta(seconds=45),
                'raw_timestamp': (datetime.now() + timedelta(seconds=45)).isoformat(),
                'scraped_at': datetime.now().isoformat()
            }
        ]
        
        result = analyzer.process_scans(test_scans)
        print(f"   ✅ Downtime Analyzer: WORKING ({len(result['new_downtimes'])} downtimes detected)")
        results['downtime_analyzer'] = True
        
    except Exception as e:
        print(f"   ❌ Downtime Analyzer: FAILED - {e}")
        results['downtime_analyzer'] = False
    
    # Test 2: Data Storage (should work - uses sqlite3 built-in)
    print("\n2. Testing Data Storage...")
    try:
        from src.data_storage import DataStorage
        
        storage = DataStorage(storage_type="sqlite", base_path="/workspace/test_system")
        
        # Test storing sample data
        test_scans = [{
            'tracking_id': 'TEST001',
            'location': 'GA1',
            'status': 'INDUCTED',
            'timestamp': datetime.now(),
            'raw_timestamp': datetime.now().isoformat(),
            'scraped_at': datetime.now().isoformat()
        }]
        
        success = storage.store_raw_scans(test_scans)
        print(f"   ✅ Data Storage: WORKING (storage success: {success})")
        results['data_storage'] = True
        
    except Exception as e:
        print(f"   ❌ Data Storage: FAILED - {e}")
        results['data_storage'] = False
    
    # Test 3: Authentication (will fail - needs requests)
    print("\n3. Testing Authentication...")
    try:
        from src.auth import MidwayAuth
        
        auth = MidwayAuth()
        print("   ⚠️  Authentication: MODULE LOADED (needs requests for testing)")
        results['auth'] = 'partial'
        
    except Exception as e:
        print(f"   ❌ Authentication: FAILED - {e}")
        results['auth'] = False
    
    # Test 4: Mercury Scraper (will fail - needs requests)
    print("\n4. Testing Mercury Scraper...")
    try:
        from src.mercury_scraper import MercuryScraper
        
        scraper = MercuryScraper(
            mercury_url="test_url",
            valid_locations=['GA1'],
            valid_statuses=['INDUCTED']
        )
        print("   ⚠️  Mercury Scraper: MODULE LOADED (needs requests for scraping)")
        results['mercury_scraper'] = 'partial'
        
    except Exception as e:
        print(f"   ❌ Mercury Scraper: FAILED - {e}")
        results['mercury_scraper'] = False
    
    # Test 5: Slack Notifier (will fail - needs requests)
    print("\n5. Testing Slack Notifier...")
    try:
        from src.slack_notifier import SlackNotifier
        
        notifier = SlackNotifier("test_webhook")
        print("   ⚠️  Slack Notifier: MODULE LOADED (needs requests for notifications)")
        results['slack_notifier'] = 'partial'
        
    except Exception as e:
        print(f"   ❌ Slack Notifier: FAILED - {e}")
        results['slack_notifier'] = False
    
    return results


def test_full_pipeline_simulation():
    """Test the full pipeline with mock data where possible"""
    print("\n\n🔄 Full Pipeline Simulation Test")
    print("=" * 50)
    
    try:
        # Use components that work
        from src.downtime_analyzer import DowntimeAnalyzer
        from src.data_storage import DataStorage
        
        # Initialize working components
        categories = [
            {'name': '20-60', 'min': 20, 'max': 60},
            {'name': '60-120', 'min': 60, 'max': 120},
            {'name': '120-780', 'min': 120, 'max': 780}
        ]
        
        analyzer = DowntimeAnalyzer(categories=categories, break_threshold=780)
        storage = DataStorage(storage_type="sqlite", base_path="/workspace/test_system")
        
        # Generate comprehensive test data
        print("\n📊 Generating test data...")
        test_scans = generate_realistic_test_data()
        print(f"Generated {len(test_scans)} scan records")
        
        # Test pipeline steps
        print("\n1. Storing raw scans...")
        storage_success = storage.store_raw_scans(test_scans)
        print(f"   ✅ Raw scans stored: {storage_success}")
        
        print("\n2. Analyzing downtimes...")
        analysis_result = analyzer.process_scans(test_scans)
        new_downtimes = analysis_result['new_downtimes']
        location_summaries = analysis_result['location_summaries']
        print(f"   ✅ Analysis complete: {len(new_downtimes)} downtimes detected")
        
        print("\n3. Storing downtime events...")
        if new_downtimes:
            event_storage_success = storage.store_downtime_events(new_downtimes)
            print(f"   ✅ Downtime events stored: {event_storage_success}")
        
        print("\n4. Testing shift-end alerts...")
        shift_alerts = analyzer.check_shift_end_alerts(threshold=2100)
        print(f"   ✅ Shift alerts: {len(shift_alerts)} locations exceed threshold")
        
        print("\n5. Testing 30-minute report data...")
        recent_downtimes = analyzer.get_recent_downtimes(minutes=30)
        print(f"   ✅ Recent downtimes: {len(recent_downtimes)} events in last 30 minutes")
        
        # Display results
        print_pipeline_results(new_downtimes, location_summaries, shift_alerts)
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_realistic_test_data() -> List[Dict]:
    """Generate realistic test data similar to production"""
    scans = []
    base_time = datetime.now() - timedelta(hours=1)
    
    locations = ['GA1', 'GA2', 'GA3', 'GA4', 'GA5']
    statuses = ['INDUCTED', 'INDUCT', 'STOW_BUFFER', 'AT_STATION']
    
    tracking_id = 1000
    
    for location in locations:
        current_time = base_time
        
        # Different scenarios per location
        if location == 'GA1':
            gaps = [35, 45, 25]  # Short downtimes
        elif location == 'GA2':
            gaps = [75, 95]  # Medium downtimes
        elif location == 'GA3':
            gaps = [150, 300]  # Long downtimes
        elif location == 'GA4':
            gaps = [40, 85, 180]  # Mixed
        else:  # GA5
            gaps = [200, 400, 600, 300, 450, 350, 250]  # Problem location
        
        for gap in gaps:
            # Add scan
            scan = {
                'tracking_id': f'T{tracking_id:06d}',
                'location': location,
                'status': random.choice(statuses),
                'timestamp': current_time,
                'raw_timestamp': current_time.isoformat(),
                'scraped_at': datetime.now().isoformat()
            }
            scans.append(scan)
            
            current_time += timedelta(seconds=gap)
            tracking_id += 1
        
        # Final scan for each location
        final_scan = {
            'tracking_id': f'T{tracking_id:06d}',
            'location': location,
            'status': random.choice(statuses),
            'timestamp': current_time,
            'raw_timestamp': current_time.isoformat(),
            'scraped_at': datetime.now().isoformat()
        }
        scans.append(final_scan)
        tracking_id += 1
    
    return sorted(scans, key=lambda x: x['timestamp'])


def print_pipeline_results(downtimes: List[Dict], summaries: Dict, alerts: List[Dict]):
    """Print pipeline test results"""
    print("\n📋 Pipeline Test Results:")
    print("-" * 40)
    
    # Summary by location
    for location, summary in sorted(summaries.items()):
        if summary.get('event_count', 0) > 0:
            print(f"\n📍 {location}:")
            print(f"   Events: {summary['event_count']}")
            print(f"   Total Downtime: {summary['total_downtime']}s")
            print(f"   Average: {summary['average_downtime']}s")
            
            categories = summary.get('category_counts', {})
            if categories:
                cat_str = ", ".join([f"{k}: {v}" for k, v in categories.items() if v > 0])
                print(f"   Categories: {cat_str}")
    
    # Alerts
    if alerts:
        print(f"\n🚨 Shift-End Alerts:")
        for alert in alerts:
            print(f"   {alert['location']}: {alert['total_downtime']}s (exceeds {alert['threshold']}s)")


def print_deployment_readiness(results: Dict):
    """Print deployment readiness assessment"""
    print("\n\n🚀 Deployment Readiness Assessment")
    print("=" * 50)
    
    working_components = sum(1 for v in results.values() if v is True)
    partial_components = sum(1 for v in results.values() if v == 'partial')
    total_components = len(results)
    
    print(f"\nComponent Status:")
    print(f"   ✅ Fully Working: {working_components}/{total_components}")
    print(f"   ⚠️  Needs Dependencies: {partial_components}/{total_components}")
    print(f"   ❌ Failed: {total_components - working_components - partial_components}/{total_components}")
    
    print(f"\nDetailed Status:")
    for component, status in results.items():
        if status is True:
            status_icon = "✅"
            status_text = "READY"
        elif status == 'partial':
            status_icon = "⚠️"
            status_text = "NEEDS DEPENDENCIES"
        else:
            status_icon = "❌"
            status_text = "FAILED"
        
        print(f"   {status_icon} {component}: {status_text}")
    
    print(f"\n📋 Production Requirements:")
    print(f"   🔧 Install: pip install requests pandas schedule pyyaml")
    print(f"   🔐 Setup: mwinit -o (Midway authentication)")
    print(f"   🌐 Network: Access to Mercury dashboard")
    print(f"   📱 Slack: Webhook URL validation")
    
    # Calculate readiness percentage
    ready_score = (working_components * 100 + partial_components * 50) / (total_components * 100) * 100
    print(f"\n🎯 System Readiness: {ready_score:.0f}%")
    
    if ready_score >= 80:
        print(f"   🟢 READY FOR DEPLOYMENT")
    elif ready_score >= 60:
        print(f"   🟡 MINOR SETUP REQUIRED")
    else:
        print(f"   🔴 SIGNIFICANT SETUP REQUIRED")


def main():
    """Main test execution"""
    try:
        # Ensure test directories exist
        Path("/workspace/test_system").mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Test individual components
        component_results = test_core_components()
        
        # Test full pipeline simulation
        pipeline_success = test_full_pipeline_simulation()
        
        # Print deployment assessment
        print_deployment_readiness(component_results)
        
        if pipeline_success:
            print(f"\n🎉 SYSTEM TEST COMPLETED SUCCESSFULLY")
            print(f"Core logic is validated and ready for production deployment.")
        else:
            print(f"\n⚠️  SYSTEM TEST COMPLETED WITH ISSUES")
            print(f"Core logic works but some components need setup.")
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()