
from datetime import datetime, timedelta

def parse_time(s):
    return datetime.strptime(s, "%H:%M")

def format_time(dt):
    return dt.strftime("%H:%M")

def apply_rules(df, report_type):
    log = []
    new_rows = []
    for i, row in df.iterrows():
        start = parse_time(row["start"])
        end = parse_time(row["end"])
        minutes_offset = (i % 5) * 3
        start += timedelta(minutes=minutes_offset)
        end += timedelta(minutes=minutes_offset)
        hours = (end - start).total_seconds() / 3600
        new_rows.append({"date": row["date"], "start": format_time(start), "end": format_time(end), "hours": round(hours, 2)})
    return (df.__class__(new_rows), log)
