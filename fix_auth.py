# Add this function to auth.py to parse Netscape cookies
def parse_netscape_cookies(cookie_path):
    """Parse Netscape format cookie file"""
    cookies = {}
    with open(cookie_path, 'r') as f:
        for line in f:
            # Skip comments and empty lines
            if line.startswith('#') or not line.strip():
                continue
            
            # Parse cookie line (7 fields)
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                domain = parts[0]
                name = parts[5]
                value = parts[6]
                
                # Store cookies we care about
                if 'amazon_enterprise_access' in name:
                    cookies[name] = value
                    
    return cookies

# Test it
import os
cookie_path = os.path.expanduser("~/.midway/cookie")
cookies = parse_netscape_cookies(cookie_path)
print(f"Found {len(cookies)} cookies")
for name, value in cookies.items():
    print(f"{name}: {value[:50]}...")
