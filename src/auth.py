# -*- coding: utf-8 -*-
"""
Midway Authentication Module
Handles Amazon Midway authentication for Mercury dashboard access
"""

import os
import logging
from typing import Optional
from requests.cookies import RequestsCookieJar

# Handle requests import with urllib3 compatibility issue
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Requests not available ({e})")
    REQUESTS_AVAILABLE = False
    # Define dummy classes for type safety
    class requests:
        class Session:
            def __init__(self):
                pass


class MidwayAuth:
    """Handles Midway authentication using existing cookies"""
    
    def __init__(self, cookie_path: str = "~/.midway/cookie"):
        self.cookie_path = os.path.expanduser(cookie_path)
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
        else:
            self.session = None
        self.logger = logging.getLogger(__name__)
        
    def load_cookies(self) -> bool:
        """Load cookies from Midway cookie file"""
        try:
            if not os.path.exists(self.cookie_path):
                self.logger.error(f"Cookie file not found: {self.cookie_path}")
                return False
                
            with open(self.cookie_path, 'r') as f:
                cookie_content = f.read().strip()
                
            # Parse cookie content (format varies)
            if '=' in cookie_content:
                # Simple key=value format
                parts = cookie_content.split('=', 1)
                if len(parts) == 2:
                    self.session.cookies.set(parts[0], parts[1])
            else:
                # Treat as raw cookie value
                self.session.cookies.set('midway_cookie', cookie_content)
                
            self.logger.info("Cookies loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load cookies: {e}")
            return False
    
    def get_authenticated_session(self) -> Optional[requests.Session]:
        """Get authenticated session for Mercury requests"""
        if not REQUESTS_AVAILABLE:
            self.logger.error("Requests library not available due to urllib3/OpenSSL compatibility issue")
            return None
            
        if not self.load_cookies():
            return None
            
        # Set headers that Mercury expects
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
        return self.session
    
    def test_authentication(self, test_url: str) -> bool:
        """Test if authentication is working"""
        session = self.get_authenticated_session()
        if not session:
            return False
            
        try:
            response = session.get(test_url, timeout=30)
            if response.status_code == 200:
                self.logger.info("Authentication test successful")
                return True
            else:
                self.logger.error(f"Authentication test failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Authentication test error: {e}")
            return False


def main():
    """Test authentication functionality"""
    logging.basicConfig(level=logging.INFO)
    
    auth = MidwayAuth()
    test_url = "https://mercury.amazon.com/getQueryResponse?ID=127de24b92c1f65c47f001541fbc6974&region=na"
    
    if auth.test_authentication(test_url):
        print("✅ Authentication successful")
    else:
        print("❌ Authentication failed")
        print("Try running: mwinit -o")


if __name__ == "__main__":
    main()