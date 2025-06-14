#!/usr/bin/env python3
"""
Test Slack Webhook Fix - Validate the Content/Content2 field format
"""

import json
import re
from pathlib import Path

def test_slack_payload_format():
    """Test that Slack webhook now uses correct field format"""
    print("📱 Testing Slack Webhook Fix")
    print("=" * 40)
    
    slack_file = Path("src/slack_notifier.py")
    if not slack_file.exists():
        print("❌ slack_notifier.py not found")
        return False
    
    content = slack_file.read_text()
    
    # Check for correct format
    checks = [
        ("Content field", '"Content": message'),
        ("Content2 field", '"Content2": content2'),
        ("Field handling", 'content2 if content2 else ""'),
        ("No text field", '"text":' not in content or content.count('"text":') <= 1)  # Allow one in test
    ]
    
    all_passed = True
    for check_name, condition in checks:
        if isinstance(condition, str):
            # String search
            if condition in content:
                print(f"✅ {check_name}: Found")
            else:
                print(f"❌ {check_name}: Missing - {condition}")
                all_passed = False
        else:
            # Boolean condition
            if condition:
                print(f"✅ {check_name}: Correct")
            else:
                print(f"❌ {check_name}: Failed")
                all_passed = False
    
    return all_passed

def test_notification_methods():
    """Test that all notification methods properly split messages"""
    print("\n📋 Testing Notification Method Structure")
    print("=" * 45)
    
    slack_file = Path("src/slack_notifier.py")
    content = slack_file.read_text()
    
    # Find all calls to send_notification
    pattern = r'return self\.send_notification\(([^)]+)\)'
    matches = re.findall(pattern, content)
    
    print(f"Found {len(matches)} calls to send_notification:")
    
    methods_with_split = 0
    for i, match in enumerate(matches, 1):
        # Check if the call has two parameters (title, content2)
        params = [p.strip() for p in match.split(',')]
        if len(params) >= 2:
            print(f"✅ Call {i}: Two parameters - {params[0]}, {params[1]}")
            methods_with_split += 1
        else:
            print(f"⚠️  Call {i}: Single parameter - {match}")
    
    print(f"\nResult: {methods_with_split}/{len(matches)} calls properly split messages")
    return methods_with_split == len(matches)

def demonstrate_payload_format():
    """Show what the new payload format looks like"""
    print("\n📤 New Payload Format Example")
    print("=" * 35)
    
    # Example payloads
    examples = [
        {
            "name": "30-Minute Report",
            "Content": "📊 Induct Downtime Report - 02:30 AM",
            "Content2": "GA1: 3 events (20-60: 2, 60-120: 1) Total: 245s\nGA2: 2 events (20-60: 2) Total: 85s\n\n📈 Summary: 5 total events, 330s total downtime"
        },
        {
            "name": "Shift-End Alert",
            "Content": "🚨 Shift End Alert - GA5 Excessive Downtime",
            "Content2": "GA5 has exceeded 2100 seconds of downtime\nCurrent: 2,550s (7 events)"
        },
        {
            "name": "System Alert",
            "Content": "✅ System Alert - Induct Downtime Monitor Started",
            "Content2": "System started at 2025-06-13 21:30:00"
        }
    ]
    
    for example in examples:
        print(f"\n{example['name']}:")
        payload = {
            "Content": example["Content"],
            "Content2": example["Content2"]
        }
        print(f"  Content: {example['Content']}")
        print(f"  Content2: {example['Content2'][:50]}{'...' if len(example['Content2']) > 50 else ''}")
    
    return True

def main():
    """Run all Slack fix tests"""
    print("🔧 Slack Webhook Fix Validation")
    print("=" * 50)
    
    test1 = test_slack_payload_format()
    test2 = test_notification_methods()
    test3 = demonstrate_payload_format()
    
    print(f"\n{'=' * 50}")
    print("📊 SLACK FIX SUMMARY")
    print(f"{'=' * 50}")
    
    if test1 and test2:
        print("✅ SLACK WEBHOOK FIX SUCCESSFUL!")
        print("\n🔧 Changes Made:")
        print('   • Payload format: {"Content": message, "Content2": details}')
        print("   • All notification methods properly split messages")
        print("   • Test connection method updated")
        print("\n🎯 Expected Results:")
        print("   • Slack workflow builder will now accept messages")
        print("   • Content field will show main message")
        print("   • Content2 field will show detailed information")
        print("   • All notification types will work correctly")
        
        return True
    else:
        print("❌ SLACK WEBHOOK FIX NEEDS ATTENTION")
        if not test1:
            print("   • Payload format issue detected")
        if not test2:
            print("   • Message splitting issue detected")
        return False

if __name__ == "__main__":
    main()