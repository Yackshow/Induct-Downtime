#!/usr/bin/env python3
"""Calculate correct UTC times for Toronto (EST/EDT) timezone"""

print("🕐 Toronto Timezone Configuration")
print("=" * 50)

print("\nYour shift times:")
print("  Start: 1:20 AM EST/EDT")
print("  End: 8:30 AM EST/EDT")
print("  Break: 4:55 AM - 5:30 AM EST/EDT")

print("\nCurrent timezone offset:")
print("  EST (winter): UTC-5")
print("  EDT (summer): UTC-4")
print("  June = EDT (UTC-4)")

print("\nConverting to UTC for June (EDT):")
print("  1:20 AM EDT = 5:20 AM UTC")
print("  8:30 AM EDT = 12:30 PM UTC")
print("  4:55 AM EDT = 8:55 AM UTC")
print("  5:30 AM EDT = 9:30 AM UTC")

# Create updated config
updated_config = """# Update these lines in config.yaml:

shift:
  start: "05:20"      # 1:20 AM EDT = 5:20 AM UTC
  end: "12:30"        # 8:30 AM EDT = 12:30 PM UTC  
  break_start: "08:55"  # 4:55 AM EDT = 8:55 AM UTC
  break_end: "09:30"    # 5:30 AM EDT = 9:30 AM UTC
  
# Note: These times are for EDT (summer time)
# For EST (winter), add 1 hour to each time
"""

with open('toronto_shift_times.txt', 'w') as f:
    f.write(updated_config)

print("\n✅ Created toronto_shift_times.txt with correct UTC times")

# Check if shift would be active now
import datetime
current_utc = datetime.datetime.utcnow()
shift_start = datetime.time(5, 20)  # 5:20 AM UTC
shift_end = datetime.time(12, 30)   # 12:30 PM UTC
current_time = current_utc.time()

print(f"\nCurrent UTC time: {current_time}")
print(f"Shift active time: {shift_start} - {shift_end}")

if shift_start <= current_time <= shift_end:
    print("✅ Shift would be ACTIVE right now!")
else:
    print("❌ Shift would NOT be active right now")
    
print("\nTo apply these times:")
print("1. Edit config.yaml with the times above")
print("2. Run: python3 main.py --continuous")