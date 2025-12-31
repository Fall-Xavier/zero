from datetime import datetime, timezone, timedelta
from collections import Counter

def time_now():
    now_utc = datetime.now(timezone.utc)
    formatted_time = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    return formatted_time
    
def convert_time(time_string):
    value, unit = time_string.split()[:2]
    value, unit = int(value), unit.lower()
    mapping = {
        "detik": timedelta(seconds=value),
        "menit": timedelta(minutes=value),
        "jam": timedelta(hours=value),
        "hari": timedelta(days=value)
    }
    return (datetime.utcnow() - mapping.get(unit, timedelta())).isoformat(timespec="seconds") + "Z"
    
def detect_update_day(chapter_times):
    days = []
    for t in chapter_times:
        dt = datetime.fromisoformat(t.replace("Z", "+00:00"))
        days.append(dt.weekday())
    counter = Counter(days)
    most_common_day = counter.most_common(1)[0][0]
    
    DAY_NAME = ["senin", "selasa", "rabu", "kamis", "jumat", "sabtu", "minggu"]
    return DAY_NAME[most_common_day]
    
    