#!/usr/bin/env python3
"""Simple test with clear logging output"""

import sys
import json
import os
from datetime import datetime
sys.path.insert(0, '.')

def simple_test():
    """Run a simple test and capture the output"""
    
    print("🔍 Simple Mercury Test with Logging")
    print("=" * 50)
    
    # Create timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        # Import after adding path
        from src.mercury_scraper import MercuryScraper
        
        print("✅ Successfully imported MercuryScraper")
        
        # Test original configuration
        print("\n🧪 Testing ORIGINAL configuration...")
        scraper_original = MercuryScraper(
            mercury_url="https://mercury.amazon.com/getQueryResponse?ID=127de24b92c1f65c47f001541fbc6974&region=na",
            valid_locations=['GA1', 'GA2', 'GA3', 'GA4', 'GA5', 'GA6', 'GA7', 'GA8', 'GA9', 'GA10'],
            valid_statuses=['INDUCTED', 'INDUCT', 'STOW_BUFFER', 'AT_STATION']
        )
        
        data_original = scraper_original.scrape_data()
        print(f"Original filter result: {len(data_original) if data_original else 0} packages")
        
        # Test expanded configuration  
        print("\n🧪 Testing EXPANDED configuration...")
        scraper_expanded = MercuryScraper(
            mercury_url="https://mercury.amazon.com/getQueryResponse?ID=127de24b92c1f65c47f001541fbc6974&region=na",
            valid_locations=['GA1', 'GA2', 'GA3', 'GA4', 'GA5', 'GA6', 'GA7', 'GA8', 'GA9', 'GA10'],
            valid_statuses=['INDUCTED', 'INDUCT', 'STOW_BUFFER', 'AT_STATION', 'READY_FOR_DEPARTURE', 'DELIVERED', 'ON_ROAD_WITH_DELIVERY_ASSOCIATE']
        )
        
        data_expanded = scraper_expanded.scrape_data()
        print(f"Expanded filter result: {len(data_expanded) if data_expanded else 0} packages")
        
        # Create summary
        summary = {
            'timestamp': timestamp,
            'original_filter_count': len(data_original) if data_original else 0,
            'expanded_filter_count': len(data_expanded) if data_expanded else 0,
            'difference': (len(data_expanded) if data_expanded else 0) - (len(data_original) if data_original else 0),
            'original_sample': data_original[:3] if data_original else [],
            'expanded_sample': data_expanded[:3] if data_expanded else []
        }
        
        # Save results
        os.makedirs('test_logs', exist_ok=True)
        results_file = f'test_logs/simple_test_{timestamp}.json'
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n📊 RESULTS:")
        print(f"Original filter (INDUCTED/INDUCT/STOW_BUFFER/AT_STATION): {summary['original_filter_count']:,}")
        print(f"Expanded filter (+READY_FOR_DEPARTURE/DELIVERED/ON_ROAD): {summary['expanded_filter_count']:,}")
        print(f"Additional packages with expanded filter: {summary['difference']:,}")
        
        print(f"\n💾 Results saved to: {results_file}")
        
        # Recommendations
        print(f"\n🎯 RECOMMENDATIONS:")
        if summary['original_filter_count'] < 100:
            print("• Very few packages in original filter - most have moved past induct")
            print("• Consider creating Mercury sheet with AT_STATION filter only")
        
        if summary['expanded_filter_count'] > 500:
            print("• Expanded filter captures much more data")
            print("• This includes historical package flows through induct")
        
        if summary['original_filter_count'] < 50:
            print("• Strong recommendation: Create new Mercury sheet filtered to AT_STATION only")
            print("• This will give real-time monitoring of packages currently at induct")
        
        return summary
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Set logging to reduce noise
    import logging
    logging.getLogger('requests_kerberos').setLevel(logging.ERROR)
    logging.getLogger('spnego').setLevel(logging.ERROR)
    logging.getLogger('gssapi').setLevel(logging.ERROR)
    
    result = simple_test()
    
    if result:
        print(f"\n✅ Test completed successfully!")
        print(f"Check test_logs/ directory for detailed results")
    else:
        print(f"\n❌ Test failed")