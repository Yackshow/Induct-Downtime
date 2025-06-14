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

# Suppress authentication warnings
logging.getLogger('requests_kerberos').setLevel(logging.ERROR)
logging.getLogger('spnego').setLevel(logging.ERROR)
logging.getLogger('gssapi').setLevel(logging.ERROR)

# Try to import SSPI auth (Windows) or Kerberos auth (Linux)
try:
    from requests_negotiate_sspi import HttpNegotiateAuth
    SSPI_AVAILABLE = True
except ImportError:
    SSPI_AVAILABLE = False
    # Try Kerberos auth for Linux
    try:
        from requests_kerberos import HTTPKerberosAuth, OPTIONAL
        KERBEROS_AVAILABLE = True
    except ImportError:
        KERBEROS_AVAILABLE = False

class MidwayAuth:
    """Handles Midway authentication using existing cookies"""
    
    def __init__(self, cookie_path: str = "~/.midway/cookie"):
        self.cookie_path = os.path.expanduser(cookie_path)
        self.session = None
        self.logger = logging.getLogger(__name__)
        
    def load_cookies(self) -> bool:
        """Load cookies from Midway cookie file - matching working script format"""
        try:
            cookiefile = os.path.join(os.path.expanduser("~"), ".midway", "cookie")
            
            if not os.path.exists(cookiefile):
                self.logger.error(f"Cookie file not found: {cookiefile}")
                return False
            
            with open(cookiefile) as cf:
                reader = list(csv.reader(cf, delimiter='\t'))
                for row in reader:
                    if len(row) > 2:
                        # Handle domain
                        if '#HttpOnly_' in row[0]:
                            dom = row[0].split('_')[1]
                        else:
                            dom = row[0]
                        
                        # Handle secure flag
                        sec = False
                        if 'TRUE' in row[3]:
                            sec = True
                        
                        required_args = {
                            'name': row[5],
                            'value': row[6]
                        }
                        
                        optional_args = {
                            'domain': dom,
                            'path': row[2],
                            'secure': sec,
                            'expires': row[4],
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
        if self.session is not None:
            self.session.close()
        
        # Create session with retry adapter
        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        self.session = requests.Session()
        self.session.mount('https://', adapter)
        
        # Set headers BEFORE loading cookies (critical order)
        self.session.headers = {
            "Accept": "application/json",
            "User-Agent": "AmzBot/1.0"
        }
        
        # Disable SSL verification for internal Mercury
        self.session.verify = False
        self.session.allow_redirects = False
        
        # Load cookies
        if not self.load_cookies():
            return None
        
        # Add SSPI auth if available (Windows)
        if SSPI_AVAILABLE:
            self.session.auth = HttpNegotiateAuth()
            self.logger.info("Using SSPI/Kerberos authentication")
        elif 'KERBEROS_AVAILABLE' in globals() and KERBEROS_AVAILABLE:
            # Suppress Kerberos warnings when using Midway cookies
            import logging
            logging.getLogger('requests_kerberos').setLevel(logging.WARNING)
            self.session.auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)
            self.logger.info("Using Kerberos authentication")
        
        # Make initial request to establish session
        try:
            response = self.session.get('https://logistics.amazon.com/station/dashboard/ageing')
            # Check if we got redirected to login page
            if response.status_code == 302 or 'login' in response.url.lower():
                self.logger.error("Authentication failed - redirected to login page")
                return None
        except Exception as e:
            self.logger.error(f"Failed to establish session: {e}")
            return None
        
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