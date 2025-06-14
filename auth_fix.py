# Add this to auth.py to replace the current cookie loading logic
def load_cookies(self) -> bool:
    """Load cookies from Midway cookie file"""
    try:
        if not os.path.exists(self.cookie_path):
            self.logger.error(f"Cookie file not found: {self.cookie_path}")
            return False
            
        # Parse Netscape format cookie file
        with open(self.cookie_path, 'r') as f:
            for line in f:
                # Skip comments and empty lines
                if line.startswith('#') or not line.strip():
                    continue
                
                # Parse Netscape cookie line (7 tab-separated fields)
                parts = line.strip().split('\t')
                if len(parts) >= 7:
                    domain = parts[0]
                    path = parts[2]
                    secure = parts[3]
                    expires = parts[4]
                    name = parts[5]
                    value = parts[6]
                    
                    # Add cookie to session
                    self.session.cookies.set(
                        name, 
                        value,
                        domain=domain,
                        path=path
                    )
        
        self.logger.info("Cookies loaded successfully")
        return True
        
    except Exception as e:
        self.logger.error(f"Failed to load cookies: {e}")
        return False
