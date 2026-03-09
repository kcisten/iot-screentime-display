import os
import requests
from dotenv import load_dotenv 
from datetime import datetime, timedelta, timezone

# config
AW_URL = "http://localhost:5600"
WINDOW_BUCKET = "aw-watcher-window_tofu"
AFK_BUCKET = "aw-watcher-afk_tofu"
DAYS = 7

BLYNK_TOKEN = os.getenv("BLYNK_TOKEN")
BLYNK_API = "https://blynk.cloud/external/api/update"
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SCREEN_TIME_LIMIT = 180

def get_stats():
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=DAYS)).isoformat()
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
    
    # Pad if fewer than 3 apps
    while len(payloads) < 4:
        payloads[f"V{11+len(payloads)-1}"] = "---"

    for pin, val in payloads.items():
        requests.get(BLYNK_API, params={"token": BLYNK_TOKEN, pin: val}, timeout=5)
        print(f"Pushed to {pin}: {val}")

def send_discord_alert(minutes):
    gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYmx3eDBzOXJpZW5pYm9tamdhM2Z2cDJwYmxsMXM5MHFvMXJoNHNybyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/q5jnZ0d18LEtOgAICr/giphy.gif"
    
    payload = {
        "content": f"⚠️ **Screen Time Alert!** You've hit {minutes} minutes today.",
        "embeds": [{
            "title": "time for a break!",
            "description": "pls go outside and touch Grass",
            "image": {"url": gif_url}
        }]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()
        print("Discord alert with GIF sent successfully.")
    except Exception as e:
        print(f"Failed to send Discord alert: {e}")

def main():
    data = get_stats()
    
    apps = {}
    total = 0
    for entry in data:
        app = entry.get("data", {}).get("app", "unknown")
        dur = float(entry.get("duration", 0))
        apps[app] = apps.get(app, 0) + dur
        total += dur

    avg_min = int(round((total / 60) / DAYS))

    if avg_min >= SCREEN_TIME_LIMIT:
        send_discord_alert(avg_min)
    
    sorted_apps = sorted(apps.items(), key=lambda x: x[1], reverse=True)
    top_apps = [name for name, _ in sorted_apps]

    print(f"Avg: {avg_min} min/day | Top Used Apps: {top_apps[:3]}")
    update_blynk(avg_min, top_apps)

if __name__ == "__main__":
    main()