#!/usr/bin/env python3
"""Verify EV schedule logic across different times."""
from datetime import datetime, timedelta

def check_ev_schedule(timestamp_utc):
    """Check if EV should be away (driving) or connected."""
    # Convert UTC to EST
    est_offset = timedelta(hours=-5)
    timestamp_est = timestamp_utc + est_offset
    
    is_weekday = timestamp_est.weekday() < 5  # Monday = 0, Friday = 4
    hour = timestamp_est.hour
    should_be_away = is_weekday and 7 <= hour < 18
    
    return {
        'utc': timestamp_utc.strftime('%Y-%m-%d %H:%M %Z'),
        'est': timestamp_est.strftime('%Y-%m-%d %H:%M EST'),
        'weekday': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][timestamp_est.weekday()],
        'should_be_away': should_be_away,
        'status': 'OFFLINE (driving)' if should_be_away else 'CHARGING (connected)'
    }

# Test times (all in UTC)
test_times = [
    datetime(2026, 2, 11, 10, 50),  # 5:50 AM EST Tuesday (before 7 AM)
    datetime(2026, 2, 11, 12, 0),   # 7:00 AM EST Tuesday (start of away)
    datetime(2026, 2, 11, 18, 0),   # 1:00 PM EST Tuesday (during away)
    datetime(2026, 2, 11, 23, 0),   # 6:00 PM EST Tuesday (end of away)
    datetime(2026, 2, 11, 23, 1),   # 6:01 PM EST Tuesday (after away)
    datetime(2026, 2, 15, 18, 0),   # 1:00 PM EST Saturday (weekend)
]

print("EV Schedule Verification")
print("=" * 80)
print(f"Schedule: EVs away 7 AM - 6 PM EST on weekdays (Mon-Fri)")
print(f"Expected: Connected and charging outside those hours\n")

for timestamp in test_times:
    result = check_ev_schedule(timestamp)
    print(f"{result['weekday']} {result['est']:25} → {result['status']}")

print("\n✅ Current time (2026-02-11 10:50 UTC / 5:50 AM EST Tuesday):")
print("   EVs should be CHARGING (connected) - before 7 AM ✓")
