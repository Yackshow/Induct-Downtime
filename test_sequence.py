#!/usr/bin/env python3
"""
Testing Sequence Script - Follow the recommended testing order
Implements the complete fix instructions testing protocol
"""

import sys
import subprocess
import os
from pathlib import Path

def run_test(test_name: str, command: str, description: str) -> bool:
    """Run a test and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST {test_name}: {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print()
    
    try:
        # Run the command
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=60
        )
        
        # Print output
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        # Check result
        if result.returncode == 0:
            print(f"\n✅ TEST {test_name} PASSED")
            return True
        else:
            print(f"\n❌ TEST {test_name} FAILED (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n⏰ TEST {test_name} TIMED OUT")
        return False
    except Exception as e:
        print(f"\n❌ TEST {test_name} ERROR: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking Dependencies")
    print("="*40)
    
    dependencies = [
        ("requests", "import requests"),
        ("beautifulsoup4", "from bs4 import BeautifulSoup"),
        ("pandas", "import pandas"),
        ("schedule", "import schedule"),
        ("yaml", "import yaml"),
        ("sqlalchemy", "import sqlalchemy")
    ]
    
    missing = []
    available = []
    
    for dep_name, import_cmd in dependencies:
        try:
            subprocess.run([sys.executable, "-c", import_cmd], 
                         check=True, capture_output=True)
            available.append(dep_name)
            print(f"✅ {dep_name}")
        except subprocess.CalledProcessError:
            missing.append(dep_name)
            print(f"❌ {dep_name}")
    
    print(f"\nDependency Status: {len(available)}/{len(dependencies)} available")
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    return True

def main():
    """Main testing sequence"""
    print("🚀 Induct Downtime System - Complete Testing Sequence")
    print("Following Critical Fix Instructions")
    print("="*70)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"📁 Current Directory: {current_dir}")
    
    # Check for required files
    required_files = [
        "src/auth.py",
        "src/slack_notifier.py", 
        "src/mercury_scraper.py",
        "test_mock_offline.py",
        "main.py"
    ]
    
    print("\n📋 Checking Required Files:")
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        print("Please ensure all system files are present.")
        return False
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependencies missing. Please install requirements first.")
        return False
    
    # Test sequence from fix instructions
    tests = [
        ("1", "python3 src/auth.py", "Test Midway Authentication"),
        ("2", "python3 src/slack_notifier.py", "Test Slack Notifications"),
        ("3", "python3 test_mock_offline.py", "Test with Mock Data (No Mercury needed)"),
        ("4", "python3 src/mercury_scraper.py --test", "Test Mercury Scraping"),
        ("5", "python3 main.py --test", "Full System Test"),
        ("6", "python3 main.py --single", "Single Cycle Test")
    ]
    
    results = []
    
    for test_num, command, description in tests:
        success = run_test(test_num, command, description)
        results.append((test_num, description, success))
        
        # If critical early tests fail, note it but continue
        if test_num in ["1", "2"] and not success:
            print(f"⚠️  Critical test {test_num} failed - may affect later tests")
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 TESTING SEQUENCE SUMMARY")
    print(f"{'='*70}")
    
    passed = sum(1 for _, _, success in results if success)
    total = len(results)
    
    for test_num, description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"Test {test_num}: {status} - {description}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("System is ready for production deployment.")
    elif passed >= total - 2:
        print(f"\n🟡 MOSTLY READY - {total - passed} tests failed")
        print("System core logic working, may need environment setup.")
    else:
        print(f"\n🔴 SIGNIFICANT ISSUES - {total - passed} tests failed")
        print("System needs troubleshooting before deployment.")
    
    # Next steps
    print(f"\n📋 Next Steps:")
    
    if passed == total:
        print("   1. Deploy to production environment")
        print("   2. Run: mwinit -o (if authentication test failed)")
        print("   3. Start monitoring: python3 main.py --continuous")
    else:
        print("   1. Address failed tests above")
        print("   2. Verify authentication: mwinit -o")
        print("   3. Check Slack webhook in workflow builder")
        print("   4. Rerun tests: python3 test_sequence.py")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)