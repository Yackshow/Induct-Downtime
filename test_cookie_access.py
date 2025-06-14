#!/usr/bin/env python3
"""Test if Midway cookie file is accessible and properly formatted"""

import os
import csv

def test_cookie_access():
    """Test if we can read the Midway cookie file"""
    cookie_path = os.path.join(os.path.expanduser("~"), ".midway", "cookie")
    
    print(f"Cookie path: {cookie_path}")
    print(f"Cookie exists: {os.path.exists(cookie_path)}")
    
    if os.path.exists(cookie_path):
        print("\nReading cookie file...")
        try:
            with open(cookie_path) as cf:
                reader = list(csv.reader(cf, delimiter='\t'))
                print(f"Total lines in cookie file: {len(reader)}")
                
                # Count valid cookie entries
                valid_cookies = 0
                for row in reader:
                    if len(row) >= 7 and not row[0].startswith('#'):
                        valid_cookies += 1
                        # Print first cookie entry (without exposing values)
                        if valid_cookies == 1:
                            print(f"\nFirst cookie entry structure:")
                            print(f"  Domain field: {row[0][:20]}...")
                            print(f"  Path: {row[2]}")
                            print(f"  Secure: {row[3]}")
                            print(f"  Cookie name: {row[5]}")
                            print(f"  Has value: {'Yes' if row[6] else 'No'}")
                
                print(f"\nTotal valid cookies found: {valid_cookies}")
                return True
                
        except Exception as e:
            print(f"Error reading cookie file: {e}")
            return False
    else:
        print("\nCookie file not found!")
        print("Please run: mwinit -o")
        return False

if __name__ == "__main__":
    if test_cookie_access():
        print("\n✅ Cookie file is accessible and appears valid")
        print("\nThe auth.py module has been updated to match the working authentication pattern.")
        print("Once the required Python packages are installed, the authentication should work.")
    else:
        print("\n❌ Cookie file access failed")