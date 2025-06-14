#!/usr/bin/env python3
"""Test the complete authentication and Mercury scraping system"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.auth import MidwayAuth
from src.mercury_scraper import MercuryScraper

def test_auth():
    """Test authentication"""
    print("=" * 50)
    print("Testing Authentication")
    print("=" * 50)
    
    auth = MidwayAuth()
    session = auth.get_authenticated_session()
    
    if session:
        print("✅ Authentication successful - session created")
        return True
    else:
        print("❌ Authentication failed")
        return False

def test_mercury():
    """Test Mercury scraping"""
    print("\n" + "=" * 50)
    print("Testing Mercury Scraper")
    print("=" * 50)
    
    scraper = MercuryScraper(
        mercury_url="https://mercury.amazon.com/getQueryResponse?ID=127de24b92c1f65c47f001541fbc6974&region=na",
        valid_locations=['GA1', 'GA2', 'GA3', 'GA4', 'GA5', 'GA6', 'GA7', 'GA8', 'GA9', 'GA10'],
        valid_statuses=['INDUCTED', 'INDUCT', 'STOW_BUFFER', 'AT_STATION']
    )
    
    print("Fetching data from Mercury...")
    packages = scraper.scrape_data()
    
    if packages:
        print(f"✅ Successfully retrieved {len(packages)} packages")
        
        # Show sample data
        print("\nSample packages:")
        for i, pkg in enumerate(packages[:3]):
            print(f"  {i+1}. Location: {pkg['location']}, Status: {pkg['status']}, Time: {pkg['timestamp']}")
        
        return True
    else:
        print("❌ No packages retrieved")
        return False

def main():
    """Run all tests"""
    print("Induct Downtime Monitoring - System Test")
    print("=" * 50)
    
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Test authentication
    if not test_auth():
        print("\n⚠️  Authentication failed. Please check:")
        print("  1. Cookie exists: mwinit -o")
        print("  2. Cookie path is correct")
        return
    
    # Test Mercury scraping
    if not test_mercury():
        print("\n⚠️  Mercury scraping failed. Please check:")
        print("  1. Mercury URL is correct")
        print("  2. Network connectivity")
        return
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! System is ready.")
    print("\nNext steps:")
    print("  1. Run main.py to start monitoring")
    print("  2. Check logs in logs/ directory")
    print("  3. Monitor Slack for notifications")

if __name__ == "__main__":
    main()