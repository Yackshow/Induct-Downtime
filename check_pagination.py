#!/usr/bin/env python3
"""Check if Mercury data is paginated and we need to fetch more pages"""

import sys
import json
sys.path.insert(0, '.')

from src.auth import MidwayAuth

def check_mercury_pagination():
    """Check if Mercury query supports pagination or different parameters"""
    
    print("🔍 Checking Mercury Pagination Options")
    print("=" * 50)
    
    auth = MidwayAuth()
    session = auth.get_authenticated_session()
    
    if not session:
        print("❌ Failed to get authenticated session")
        return
    
    base_url = "https://mercury.amazon.com/getQueryResponse"
    
    # Test different query parameters
    test_queries = [
        # Original query
        {
            "name": "Original",
            "params": {"ID": "127de24b92c1f65c47f001541fbc6974", "region": "na"}
        },
        # Try with limit parameter
        {
            "name": "With Limit 5000", 
            "params": {"ID": "127de24b92c1f65c47f001541fbc6974", "region": "na", "limit": "5000"}
        },
        # Try with offset
        {
            "name": "With Offset 1000",
            "params": {"ID": "127de24b92c1f65c47f001541fbc6974", "region": "na", "offset": "1000"}
        },
        # Try different page size
        {
            "name": "Page Size 10000",
            "params": {"ID": "127de24b92c1f65c47f001541fbc6974", "region": "na", "pageSize": "10000"}
        }
    ]
    
    results = {}
    
    for query in test_queries:
        print(f"\n🧪 Testing: {query['name']}")
        try:
            response = session.get(base_url, params=query['params'], timeout=30)
            print(f"Status: {response.status_code}")
            print(f"Content length: {len(response.text)}")
            
            # Quick count of table rows
            row_count = response.text.count('<tr')
            print(f"Estimated rows: {row_count}")
            
            results[query['name']] = {
                "status": response.status_code,
                "content_length": len(response.text),
                "estimated_rows": row_count,
                "params": query['params']
            }
            
            # Save response if significantly different
            if query['name'] != "Original":
                filename = f"mercury_response_{query['name'].lower().replace(' ', '_')}.html"
                with open(filename, 'w') as f:
                    f.write(response.text)
                print(f"Saved to: {filename}")
                
        except Exception as e:
            print(f"Error: {e}")
            results[query['name']] = {"error": str(e)}
    
    # Save results
    with open('pagination_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 SUMMARY:")
    for name, result in results.items():
        if 'error' in result:
            print(f"{name}: ERROR - {result['error']}")
        else:
            print(f"{name}: {result['estimated_rows']} rows, {result['content_length']} chars")
    
    print(f"\n💡 If any test shows significantly more rows, we can use those parameters!")
    print(f"Check pagination_test_results.json for detailed results")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    check_mercury_pagination()