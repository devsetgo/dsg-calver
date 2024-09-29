__version__ = "2024-09-27-007"

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, available_timezones

# Prepare a list to store time zone information
timezones = []

for tz_name in sorted(available_timezones()):
    tz = ZoneInfo(tz_name)
    now = datetime.now(tz)
    offset = tz.utcoffset(now)
    
    if offset is None:
        offset_str = 'Unknown'
    else:
        total_seconds = offset.total_seconds()
        sign = '+' if total_seconds >= 0 else '-'
        total_seconds = abs(total_seconds)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        offset_str = f"UTC{sign}{int(hours):02d}:{int(minutes):02d}"
    
    timezones.append((tz_name, offset_str))

# Generate Markdown table
print("| Timezone | UTC Offset |")
print("| --- | --- |")
for tz_name, offset_str in timezones:
    print(f"| {tz_name} | {offset_str} |")