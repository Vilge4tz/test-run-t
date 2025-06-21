#!/usr/bin/env python3
"""
Collect top Twitch game categories once every 10 s for ~5 min and
append them to CSV under data/twitch_top_categories.csv
"""
import csv, datetime as dt, json, requests, time, pathlib

URL = "https://gql.twitch.tv/gql"
CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"
HEADERS = {"Client-Id": CLIENT_ID,
           "Content-Type": "text/plain;charset=UTF-8"}

def top_categories(limit=30):
    payload = {
        "operationName": "BrowsePage_AllDirectories",
        "variables": {
            "limit": limit,
            "directoryFilters": ["GAMES"],
            "sortTypeIsRecency": False,
            "tags": []
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "2f67f71ba89f3c0ed26a141ec00da1defecb2303595f5cda4298169549783d9e"
            }
        }
    }
    r = requests.post(URL, headers=HEADERS, data=json.dumps(payload))
    r.raise_for_status()
    edges = r.json()["data"]["directoriesWithTags"]["edges"]
    return [(e["node"]["displayName"], e["node"]["viewersCount"]) for e in edges]

DATA_DIR = pathlib.Path("data")
DATA_DIR.mkdir(exist_ok=True)
CSV_FILE = DATA_DIR / "twitch_top_categories.csv"

def append_rows(rows):
    new = not CSV_FILE.exists()
    with CSV_FILE.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["utc_ts", "game", "viewers"])
        w.writerows(rows)

def main():
    end = time.time() + 300          # ≈5 min – keeps job inside one schedule slot
    while time.time() < end:
        now = dt.datetime.utcnow().isoformat(timespec="seconds")
        rows = [[now, name, viewers] for name, viewers in top_categories(100)]
        append_rows(rows)
        time.sleep(10)

if __name__ == "__main__":
    main()
