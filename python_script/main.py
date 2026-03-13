import os
import requests
from dotenv import load_dotenv
from datetime import datetime, time, timezone


AW_URL = os.getenv("AW_URL")
WINDOW_BUCKET = os.getenv("WINDOW_BUCKET")
AFK_BUCKET = os.getenv("AFK_BUCKET")
BLYNK_TOKEN = os.getenv("BLYNK_TOKEN")

BLYNK_UPDATE_URL = "https://blynk.cloud/external/api/update"
BLYNK_EVENT_URL = "https://blynk.cloud/external/api/logEvent"
BLYNK_EVENT_NAME = "limit_reached" 

SCREEN_TIME_LIMIT = 20 

def get_stats():

    now = datetime.now(timezone.utc)
    start = datetime.combine(now.date(), time.min, tzinfo=timezone.utc).isoformat()
    end = now.isoformat()

    query = [
        f"afk = query_bucket('{AFK_BUCKET}');",
        f"win = query_bucket('{WINDOW_BUCKET}');",
        "win = filter_period_intersect(win, filter_keyvals(afk, 'status', ['not-afk']));",
        "RETURN = merge_events_by_keys(win, ['app']);",
    ]
    
    resp = requests.post(f"{AW_URL}/api/0/query/", 
                         json={"timeperiods": [f"{start}/{end}"], "query": query}, 
                         timeout=20)
    resp.raise_for_status()
    
    return resp.json()[0]

def update_blynk(avg_min, apps):
    payloads = {"V10": avg_min}
    for i, app in enumerate(apps[:3]):
        name = app.split('.')[0].strip()
        payloads[f"V{11+i}"] = name[:14]
    

    while len(payloads) < 4:
        payloads[f"V{11+len(payloads)-1}"] = "---"

    for pin, val in payloads.items():
        try:
            requests.get(BLYNK_UPDATE_URL, params={"token": BLYNK_TOKEN, pin: val}, timeout=5)
            print(f"Pushed to {pin}: {val}")
        except Exception as e:
            print(f"Failed to push to {pin}: {e}")

def trigger_blynk_event():

    print(f"Screen time limit reached! Telling Blynk to trigger the '{BLYNK_EVENT_NAME}' event...")
    try:
        response = requests.get(BLYNK_EVENT_URL, params={
            "token": BLYNK_TOKEN, 
            "code": BLYNK_EVENT_NAME  
        }, timeout=5)
        response.raise_for_status()
        print("Blynk Event triggered successfully! Blynk should now forward the Webhook to Discord.")
    except Exception as e:
        print(f"Failed to trigger Blynk Event: {e}")

def main():
    data = get_stats()
    apps = {}
    total_seconds = 0
    
    for entry in data:
        app = entry.get("data", {}).get("app", "unknown")
        dur = float(entry.get("duration", 0))
        apps[app] = apps.get(app, 0) + dur
        total_seconds += dur

    today_minutes = int(round(total_seconds / 60))

    if today_minutes >= SCREEN_TIME_LIMIT:
        trigger_blynk_event()
    
    sorted_apps = sorted(apps.items(), key=lambda x: x[1], reverse=True)
    top_apps = [name for name, _ in sorted_apps]

    print(f"Today's Total: {today_minutes} min | Top Used Apps: {top_apps[:3]}")
    
    update_blynk(today_minutes, top_apps)

if __name__ == "__main__":
    main()