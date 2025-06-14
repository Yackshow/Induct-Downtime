
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
