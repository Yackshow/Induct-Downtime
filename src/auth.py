"""
Midway Authentication Module
Handles Amazon Midway authentication for Mercury dashboard access
"""

import os
import logging
from typing import Optional, Dict
import requests
from requests.cookies import RequestsCookieJar


class MidwayAuth:
    """Handles Midway authentication using existing cookies"""
    
    def __init__(self, cookie_path: str = "~/.midway/cookie"):
        self.cookie_path = os.path.expanduser(cookie_path)
        self.session = requests.Session()
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
        if not self.load_cookies():
            return None
            
        # Set common headers for Amazon internal requests
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
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