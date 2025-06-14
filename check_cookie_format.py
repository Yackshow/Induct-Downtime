#!/usr/bin/env python3
"""Check Midway cookie format without requiring external packages"""

import os
import sys

# Allow specifying cookie path as argument
cookie_path = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.midway/cookie")

print(f"Checking cookie at: {cookie_path}")

if not os.path.exists(cookie_path):
    print(f"❌ Cookie file not found!")
    print("\nTry one of these:")
    print("1. python3 check_cookie_format.py /home/mackhun/.midway/cookie")
    print("2. cp /home/mackhun/.midway/cookie ~/.midway/cookie")
    sys.exit(1)

print("✅ Cookie file found!")
print("\nAnalyzing cookie format...")

try:
    with open(cookie_path, 'r') as f:
        lines = f.readlines()
        
    print(f"Total lines: {len(lines)}")
    
    # Count different types of lines
    comment_lines = 0
    cookie_lines = 0
    valid_cookies = 0
    
    for line in lines:
        if line.startswith('#'):
            comment_lines += 1
        elif line.strip():
            cookie_lines += 1
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                valid_cookies += 1
                # Show structure of first valid cookie (without sensitive data)
                if valid_cookies == 1:
                    print("\nFirst cookie structure:")
                    print(f"  Domain: {parts[0][:30]}...")
                    print(f"  Path: {parts[2]}")
                    print(f"  Secure: {parts[3]}")
                    print(f"  Name: {parts[5]}")
                    print(f"  Has value: {'Yes' if parts[6] else 'No'}")
                    print(f"  Total fields: {len(parts)}")
    
    print(f"\nSummary:")
    print(f"  Comment lines: {comment_lines}")
    print(f"  Cookie lines: {cookie_lines}")
    print(f"  Valid cookies (7+ fields): {valid_cookies}")
    
    if valid_cookies > 0:
        print("\n✅ Cookie file appears to be valid Netscape format")
        print("\nThe auth.py module has been updated to handle this format.")
        print("However, you need to install Python packages to use it:")
        print("  - requests")
        print("  - beautifulsoup4")
        print("  - schedule")
        print("  - PyYAML")
    else:
        print("\n❌ No valid cookies found in file")
        
except Exception as e:
    print(f"\n❌ Error reading cookie file: {e}")