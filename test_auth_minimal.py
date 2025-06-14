#!/usr/bin/env python3
"""Minimal authentication test using only standard library"""

import os
import http.cookiejar
import urllib.request
import urllib.parse
import ssl
import csv

def test_mercury_auth():
    """Test Mercury authentication using urllib (standard library only)"""
    
    # Cookie file path
    cookie_file = os.path.expanduser("~/.midway/cookie")
    
    if not os.path.exists(cookie_file):
        print(f"❌ Cookie file not found at: {cookie_file}")
        print("Please run: mwinit -o")
        return False
    
    print(f"✅ Found cookie file at: {cookie_file}")
    
    # Create cookie jar
    cj = http.cookiejar.MozillaCookieJar()
    
    # Parse Midway cookie file manually (Netscape format)
    print("\nParsing cookies...")
    cookie_count = 0
    
    try:
        with open(cookie_file, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                
                parts = line.strip().split('\t')
                if len(parts) >= 7:
                    domain = parts[0].replace('#HttpOnly_', '')
                    flag = parts[1]
                    path = parts[2]
                    secure = parts[3] == 'TRUE'
                    expires = parts[4]
                    name = parts[5]
                    value = parts[6]
                    
                    # Create cookie
                    cookie = http.cookiejar.Cookie(
                        version=0,
                        name=name,
                        value=value,
                        port=None,
                        port_specified=False,
                        domain=domain,
                        domain_specified=True,
                        domain_initial_dot=domain.startswith('.'),
                        path=path,
                        path_specified=True,
                        secure=secure,
                        expires=None,
                        discard=False,
                        comment=None,
                        comment_url=None,
                        rest={'HttpOnly': None},
                        rfc2109=False
                    )
                    cj.set_cookie(cookie)
                    cookie_count += 1
        
        print(f"✅ Loaded {cookie_count} cookies")
        
        # Create opener with cookie support
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ssl_context),
            urllib.request.HTTPCookieProcessor(cj)
        )
        
        # Test URLs
        test_urls = [
            "https://logistics.amazon.com/station/dashboard/ageing",
            "https://mercury.amazon.com/getQueryResponse?ID=127de24b92c1f65c47f001541fbc6974&region=na"
        ]
        
        for url in test_urls:
            print(f"\nTesting: {url}")
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'AmzBot/1.0')
            req.add_header('Accept', 'application/json')
            
            try:
                response = opener.open(req, timeout=10)
                final_url = response.geturl()
                status = response.getcode()
                
                print(f"Status: {status}")
                print(f"Final URL: {final_url}")
                
                if 'login' in final_url.lower() or 'midway-auth' in final_url.lower():
                    print("❌ Redirected to login - authentication failed")
                else:
                    print("✅ No login redirect - authentication may be working")
                    
                # Read a bit of content
                content = response.read(500).decode('utf-8', errors='ignore')
                print(f"First 100 chars: {content[:100]}...")
                
            except urllib.error.HTTPError as e:
                print(f"HTTP Error: {e.code} - {e.reason}")
                if e.code == 302:
                    print(f"Redirect to: {e.headers.get('Location', 'Unknown')}")
            except Exception as e:
                print(f"Error: {type(e).__name__}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing cookies: {e}")
        return False

if __name__ == "__main__":
    print("Mercury Authentication Test (Standard Library Only)")
    print("=" * 50)
    
    if test_mercury_auth():
        print("\n✅ Test completed")
    else:
        print("\n❌ Test failed")
    
    print("\nNOTE: This uses only Python standard library.")
    print("The actual implementation requires the 'requests' package for full functionality.")
    print("To install required packages, you need pip or system package manager access.")