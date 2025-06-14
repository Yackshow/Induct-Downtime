#!/usr/bin/env python3
"""
Test Slack Notifier Syntax - Check for syntax errors without dependencies
"""

import ast
import sys
from pathlib import Path

def test_syntax():
    """Test Python syntax of slack_notifier.py"""
    print("🔍 Testing Slack Notifier Syntax")
    print("=" * 35)
    
    slack_file = Path("src/slack_notifier.py")
    
    if not slack_file.exists():
        print("❌ File not found: src/slack_notifier.py")
        return False
    
    try:
        # Read and parse the file
        with open(slack_file, 'r') as f:
            content = f.read()
        
        # Parse as AST to check syntax
        ast.parse(content)
        print("✅ Syntax check: PASSED")
        
        # Check for specific method
        if "def __init__(self, webhook_url: str):" in content:
            print("✅ __init__ method: Correctly defined")
        else:
            print("❌ __init__ method: Not found or malformed")
            return False
        
        # Show line 16 specifically
        lines = content.split('\n')
        if len(lines) >= 16:
            line16 = lines[15]  # 0-indexed
            print(f"✅ Line 16: {line16.strip()}")
        
        print("\n📋 Class structure check:")
        
        # Check class definition
        if "class SlackNotifier:" in content:
            print("✅ SlackNotifier class: Found")
        else:
            print("❌ SlackNotifier class: Not found")
            return False
        
        # Check key methods
        methods = [
            "def __init__",
            "def send_notification", 
            "def send_30_minute_report",
            "def send_shift_end_alert",
            "def test_connection"
        ]
        
        for method in methods:
            if method in content:
                print(f"✅ {method}: Found")
            else:
                print(f"❌ {method}: Missing")
                return False
        
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax Error: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_init_method():
    """Show the __init__ method definition"""
    print("\n📝 __init__ Method Definition:")
    print("-" * 30)
    
    try:
        with open("src/slack_notifier.py", 'r') as f:
            lines = f.readlines()
        
        # Find __init__ method
        for i, line in enumerate(lines):
            if "def __init__" in line:
                print(f"Line {i+1}: {line.rstrip()}")
                # Show next few lines too
                for j in range(1, 4):
                    if i+j < len(lines):
                        print(f"Line {i+j+1}: {lines[i+j].rstrip()}")
                break
        
    except Exception as e:
        print(f"Error reading file: {e}")

def main():
    """Run syntax tests"""
    success = test_syntax()
    show_init_method()
    
    if success:
        print("\n🎉 ALL SYNTAX CHECKS PASSED!")
        print("The slack_notifier.py file is syntactically correct.")
        print("The __init__ method is properly defined with double underscores.")
    else:
        print("\n❌ SYNTAX ISSUES DETECTED!")
        print("Please check the file for syntax errors.")
    
    return success

if __name__ == "__main__":
    main()