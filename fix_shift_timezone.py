#!/usr/bin/env python3
"""Fix shift timezone issue - add timezone support or override shift check"""

import subprocess
import sys

print("🕐 Fixing Shift Timezone Issue")
print("=" * 50)

# Check current time
result = subprocess.run(['date'], capture_output=True, text=True)
print(f"Current system time (UTC): {result.stdout.strip()}")

print("\nThe issue: Your shift runs 1:20 AM - 8:30 AM PST, but the system uses UTC")
print("UTC is 7-8 hours ahead of PST/PDT")

print("\nOptions to fix this:")
print("\n1. Quick fix - Comment out shift check (for testing)")
print("2. Add timezone to config.yaml")
print("3. Convert times to UTC in config")

# Create a patched version that ignores shift check for testing
patch_content = '''
# Quick patch to disable shift checking for testing
import sys
sys.path.insert(0, '.')

print("Patching main.py to disable shift check...")

with open('main.py', 'r') as f:
    content = f.read()

# Replace the shift check with always True
old_line = "            if not self.is_shift_active():"
new_line = "            if False:  # TEMP: Disabled shift check for testing"

if old_line in content:
    content = content.replace(old_line, new_line)
    with open('main.py', 'w') as f:
        f.write(content)
    print("✅ Patched main.py - shift check disabled")
else:
    print("❌ Could not find shift check line to patch")
'''

with open('disable_shift_check.py', 'w') as f:
    f.write(patch_content)

print("\n✅ Created disable_shift_check.py")
print("\nTo disable shift checking for testing:")
print("  python3 disable_shift_check.py")
print("\nThen run:")
print("  python3 main.py --continuous")
print("\nFor a permanent fix, update config.yaml with UTC times:")
print("  shift:")
print("    start: '09:20'   # 1:20 AM PST = 9:20 AM UTC")
print("    end: '16:30'     # 8:30 AM PST = 4:30 PM UTC")
print("    break_start: '12:55'  # 4:55 AM PST")
print("    break_end: '13:30'    # 5:30 AM PST")