"""
Midway Authentication Module
Handles Amazon Midway authentication for Mercury dashboard access
"""

import os
import csv
import logging
from typing import Optional
import requests
from requests.cookies import RequestsCookieJar

# Try to import SSPI auth (Windows) or fallback to basic auth
try:
    from requests_negotiate_sspi import HttpNegotiateAuth
    SSPI_AVAILABLE = True
except ImportError:
    SSPI_AVAILABLE = False

class MidwayAuth:
    """Handles Midway authentication using existing cookies"""
    
    def __init__(self, cookie_path: str = "~/.midway/cookie"):
        self.cookie_path = os.path.expanduser(cookie_path)
        self.session = None
        self.logger = logging.getLogger(__name__)
        
    def load_cookies(self) -> bool:
        """Load cookies from Midway cookie file - matching working script format"""
        try:
            if not os.path.exists(self.cookie_path):
                self.logger.error(f"Cookie file not found: {self.cookie_path}")
                return False
            
            # Parse cookies exactly like the working scripts
            with open(self.cookie_path) as cf:
                reader = list(csv.reader(cf, delimiter='\t'))
                for row in reader:
                    if len(row) > 2:
                        # Handle domain
                        if '#HttpOnly_' in row[0]:
                            dom = row[0].split('_')[1]
                        else:
                            dom = row[0]
                        
                        # Skip comment lines
                        if dom.startswith('#'):
                            continue
                        
                        # Handle secure flag
                        sec = False
                        if len(row) > 3 and 'TRUE' in row[3]:
                            sec = True
                        
                        # Create cookie with all fields
                        if len(row) >= 7:
                            required_args = {
                                'name': row[5],
                                'value': row[6]
                            }
                            
                            optional_args = {
                                'domain': dom,
                                'path': row[2],
                                'secure': sec,
                                'expires': row[4] if len(row) > 4 else None,
                                'discard': False,
                            }
                            
                            new_cookie = requests.cookies.create_cookie(**required_args, **optional_args)
                            self.session.cookies.set_cookie(new_cookie)
            
            self.logger.info("Cookies loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load cookies: {e}")
            return False
    
    def get_authenticated_session(self) -> Optional[requests.Session]:
        """Get authenticated session for Mercury requests"""
        if not self.session:
            # Create session with retry adapter
            adapter = requests.adapters.HTTPAdapter(max_retries=5)
            self.session = requests.Session()
            self.session.mount('https://', adapter)
            
            # Load cookies
            if not self.load_cookies():
                return None
            
            # Set headers that Mercury expects (from working scripts)
            self.session.headers = {
                "Accept": "application/json",
                "User-Agent": "AmzBot/1.0"
            }
            
            # Disable SSL verification for internal Mercury
            self.session.verify = False
            self.session.allow_redirects = False
            
            # Add SSPI auth if available (Windows)
            if SSPI_AVAILABLE:
                self.session.auth = HttpNegotiateAuth()
                self.logger.info("Using SSPI/Kerberos authentication")
            
            # Disable SSL warnings
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        return self.session
    
    def test_authentication(self, test_url: str) -> bool:
        """Test if authentication is working"""
        session = self.get_authenticated_session()
        if not session:
            return False
            
        try:
            response = session.get(test_url, timeout=30, verify=False)
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