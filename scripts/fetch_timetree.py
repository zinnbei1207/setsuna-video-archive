import json
import urllib.parse
import urllib.request
from pathlib import Path

CALENDAR_ID = "setsuna"
BASE = f"https://timetreeapp.com/api/v2/public_calendars/{CALENDAR_ID}/public_events"
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-Timetreea": "web/2.1.0/en",
    "User-Agent": "Mozilla/5.0 SetsunaVideoArchive/1.0",
}


def get_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode("utf-8"))


def main():
    all_events = []
    cursor = None
    guard = 0
    while guard < 50:
        params = {"from": 0}
        if cursor:
            params["cursor"] = cursor
        data = get_json(BASE + "?" + urllib.parse.urlencode(params))
        all_events.extend(data.get("public_events", []))
        paging = data.get("paging") or {}
        if not paging.get("next"):
            break
        cursor = paging.get("next_cursor")
        if not cursor:
            break
        guard += 1

    out = Path("data/timetree-events.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps({"calendar_id": CALENDAR_ID, "events": all_events}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"saved {len(all_events)} events")


if __name__ == "__main__":
    main()
