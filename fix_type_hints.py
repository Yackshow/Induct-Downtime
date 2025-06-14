#!/usr/bin/env python3
"""
Remove type hints for Python 2.7 compatibility
"""

import re
import os

def remove_type_hints_from_file(file_path):
    """Remove type hints from a Python file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Remove type hints from function parameters
        # Pattern: parameter: type = value -> parameter=value
        # Pattern: parameter: type -> parameter
        content = re.sub(r'(\w+):\s*[A-Za-z_][A-Za-z0-9_\[\],\s]*(\s*=)', r'\1\2', content)
        content = re.sub(r'(\w+):\s*[A-Za-z_][A-Za-z0-9_\[\],\s]*(?=\s*[,)])', r'\1', content)
        
        # Remove return type annotations
        # Pattern: ) -> Type: -> ):
        content = re.sub(r'\)\s*->\s*[A-Za-z_][A-Za-z0-9_\[\],\s]*:', r'):', content)
        
        # Remove Optional and typing imports if they exist
        content = re.sub(r'from typing import.*\n', '', content)
        content = re.sub(r'import typing.*\n', '', content)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed type hints in {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix type hints in main files"""
    files_to_fix = [
        'main.py',
        'src/mercury_scraper.py', 
        'src/downtime_analyzer.py',
        'src/data_storage.py'
    ]
    
    print("🔧 Removing type hints for Python 2.7 compatibility...")
    
    success_count = 0
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if remove_type_hints_from_file(file_path):
                success_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n✅ Fixed {success_count}/{len(files_to_fix)} files")
    print("🎯 System should now be compatible with older Python versions")

if __name__ == "__main__":
    main()