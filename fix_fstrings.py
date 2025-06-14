#!/usr/bin/env python3
"""
Replace f-strings with .format() for Python 3.7 compatibility
"""

import re
import os

def fix_fstring_in_file(file_path):
    """Replace f-strings with .format() in a file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Simple f-string patterns to fix
        # Pattern: f"text {variable}" -> "text {}".format(variable)
        # Pattern: f"text {variable1} more {variable2}" -> "text {} more {}".format(variable1, variable2)
        
        # Find all f-strings
        fstring_pattern = r'f"([^"]*?)"'
        
        def replace_fstring(match):
            fstring_content = match.group(1)
            
            # Find all {} expressions
            var_pattern = r'\{([^}]+)\}'
            variables = re.findall(var_pattern, fstring_content)
            
            # Replace {} expressions with simple {}
            new_string = re.sub(var_pattern, '{}', fstring_content)
            
            # Build .format() call
            if variables:
                format_vars = ', '.join(variables)
                return f'"{new_string}".format({format_vars})'
            else:
                return f'"{new_string}"'
        
        # Replace f-strings
        new_content = re.sub(fstring_pattern, replace_fstring, content)
        
        # Also handle f' strings
        fstring_pattern_single = r"f'([^']*?)'"
        
        def replace_fstring_single(match):
            fstring_content = match.group(1)
            
            # Find all {} expressions
            var_pattern = r'\{([^}]+)\}'
            variables = re.findall(var_pattern, fstring_content)
            
            # Replace {} expressions with simple {}
            new_string = re.sub(var_pattern, '{}', fstring_content)
            
            # Build .format() call
            if variables:
                format_vars = ', '.join(variables)
                return f"'{new_string}'.format({format_vars})"
            else:
                return f"'{new_string}'"
        
        new_content = re.sub(fstring_pattern_single, replace_fstring_single, new_content)
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Fixed f-strings in {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix f-strings in all Python files"""
    files_to_fix = [
        'main.py',
        'src/mercury_scraper.py', 
        'src/downtime_analyzer.py',
        'src/data_storage.py',
        'src/slack_notifier.py',
        'src/auth.py'
    ]
    
    print("🔧 Fixing f-strings for Python 3.7 compatibility...")
    
    success_count = 0
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_fstring_in_file(file_path):
                success_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n✅ Fixed {success_count}/{len(files_to_fix)} files")
    print("🎯 System should now be compatible with Python 3.7")

if __name__ == "__main__":
    main()