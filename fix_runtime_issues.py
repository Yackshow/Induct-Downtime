#!/usr/bin/env python3
"""Fix runtime issues for the Induct Downtime monitoring system"""

import os
import shutil
import logging

def fix_database_permissions():
    """Fix database file permissions"""
    db_path = "induct_downtime.db"
    
    if os.path.exists(db_path):
        # Check if we can write to it
        try:
            with open(db_path, 'a'):
                pass
            print(f"✅ Database {db_path} is writable")
            return True
        except PermissionError:
            print(f"❌ Database {db_path} is not writable")
            # Try to make a backup and create new one
            backup_path = f"{db_path}.backup"
            try:
                shutil.copy2(db_path, backup_path)
                print(f"📁 Created backup at {backup_path}")
                
                # Remove the old database
                try:
                    os.remove(db_path)
                    print(f"🗑️  Removed readonly database")
                    print("✅ New database will be created on next run")
                    return True
                except:
                    print("❌ Cannot remove readonly database")
                    print("Try: rm induct_downtime.db")
                    return False
            except:
                print("❌ Cannot backup database")
                return False
    else:
        print("✅ No existing database - will be created on first run")
        return True

def create_logging_config():
    """Create a logging configuration to suppress Kerberos warnings"""
    config_content = """# Logging configuration to suppress noisy warnings
import logging

# Suppress Kerberos authentication warnings
logging.getLogger('requests_kerberos').setLevel(logging.ERROR)
logging.getLogger('spnego').setLevel(logging.ERROR)
logging.getLogger('gssapi').setLevel(logging.ERROR)

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
"""
    
    with open('suppress_warnings.py', 'w') as f:
        f.write(config_content)
    
    print("✅ Created suppress_warnings.py to reduce log noise")
    print("   Add 'import suppress_warnings' to main.py to use it")

def main():
    print("🔧 Fixing Runtime Issues")
    print("=" * 50)
    
    # Fix database permissions
    print("\n1. Fixing database permissions...")
    fix_database_permissions()
    
    # Create warning suppression config
    print("\n2. Creating warning suppression config...")
    create_logging_config()
    
    print("\n✅ Fixes applied!")
    print("\nNext steps:")
    print("1. Run: rm induct_downtime.db (if still getting permission errors)")
    print("2. Run: python3 main.py --test")
    print("3. Run: python3 main.py --continuous")

if __name__ == "__main__":
    main()