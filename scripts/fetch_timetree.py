import json
import urllib.parse
import urllib.request
from pathlib import Path

CALENDARS = {
    "永遠のセツナ": "setsuna",
    "&youth!": "andyouthchannel",
    "Serenade": "s1220",
    "MellBell": "mellbell_0719",
}
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


def fetch_calendar(group, calendar_id):
    base = f"https://timetreeapp.com/api/v2/public_calendars/{calendar_id}/public_events"
    all_events = []
    cursor = None
    guard = 0
    while guard < 50:
        params = {"from": 0}
        if cursor:
            params["cursor"] = cursor
        data = get_json(base + "?" + urllib.parse.urlencode(params))
        for event in data.get("public_events", []):
            event["_group"] = group
            event["_calendar_id"] = calendar_id
            all_events.append(event)
        paging = data.get("paging") or {}
        if not paging.get("next"):
            break
        cursor = paging.get("next_cursor")
        if not cursor:
            break
        guard += 1
    print(f"{group}: {len(all_events)} events")
    return all_events


def main():
    all_events = []
    errors = []
    for group, calendar_id in CALENDARS.items():
        try:
            all_events.extend(fetch_calendar(group, calendar_id))
        except Exception as exc:
            errors.append({"group": group, "calendar_id": calendar_id, "error": str(exc)})
            print(f"ERROR {group}: {exc}")

    out = Path("data/timetree-events.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {"calendars": CALENDARS, "events": all_events, "errors": errors},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"saved {len(all_events)} events from {len(CALENDARS) - len(errors)} calendars")
    if len(errors) == len(CALENDARS):
        raise RuntimeError("All TimeTree calendar fetches failed")


if __name__ == "__main__":
    main()
