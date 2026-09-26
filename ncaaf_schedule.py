#!/usr/bin/env python3
"""
NCAAF Schedule & TV Lookup
---------------------------
Prints college football games for a given day with kickoff time and TV
channel, pulled from ESPN's public scoreboard feed.

No API key, no sign-up, and no third-party packages required - just the
Python standard library.

Usage:
    python3 ncaaf_schedule.py              # today's games
    python3 ncaaf_schedule.py 20261003     # games on Oct 3, 2026
    python3 ncaaf_schedule.py 2026-10-03   # dashes are fine too
"""

import sys
import json
import urllib.request
import urllib.error
from datetime import datetime

SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard"


def fetch_schedule(date_str):
    """Fetch the raw scoreboard JSON from ESPN for a given YYYYMMDD date."""
    url = f"{SCOREBOARD_URL}?dates={date_str}&limit=300"
    with urllib.request.urlopen(url, timeout=15) as response:
        return json.loads(response.read().decode())


def get_channel(competition):
    """Pull the TV/streaming channel(s) out of a competition entry."""
    if competition.get("broadcast"):
        return competition["broadcast"]

    names = []
    for b in competition.get("broadcasts", []):
        names.extend(b.get("names", []))
    if names:
        return "/".join(names)

    return "TBD"


def get_matchup(event):
    """Return a readable 'Away at Home' string for the game."""
    competition = event.get("competitions", [{}])[0]
    competitors = competition.get("competitors", [])
    away = next((c for c in competitors if c.get("homeAway") == "away"), None)
    home = next((c for c in competitors if c.get("homeAway") == "home"), None)
    if away and home:
        return f"{away['team']['displayName']} at {home['team']['displayName']}"
    return event.get("name", "Unknown matchup")


def main():
    date_str = sys.argv[1].replace("-", "") if len(sys.argv) > 1 else datetime.now().strftime("%Y%m%d")

    print(f"Fetching NCAAF games for {date_str}...\n")

    try:
        data = fetch_schedule(date_str)
    except urllib.error.URLError as e:
        print(f"Couldn't reach ESPN: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Got an unexpected response from ESPN. Try again in a bit.")
        sys.exit(1)

    events = data.get("events", [])
    if not events:
        print("No NCAAF games found for that date.")
        return

    week = data.get("week", {}).get("number")
    header = f"NCAAF Schedule - {date_str}" + (f" (Week {week})" if week else "")
    print(header)
    print("=" * len(header))

    events.sort(key=lambda e: e.get("date", ""))

    for event in events:
        competition = event.get("competitions", [{}])[0]
        matchup = get_matchup(event)
        kickoff = competition.get("status", {}).get("type", {}).get("detail", "Time TBD")
        channel = get_channel(competition)

        print(f"\n{matchup}")
        print(f"  Kickoff: {kickoff}")
        print(f"  TV:      {channel}")


if __name__ == "__main__":
    main()
