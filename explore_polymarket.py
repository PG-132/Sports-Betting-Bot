"""
Explore the Polymarket sports API.
Given a list of NBA game slugs, pull market data for each one.
"""

import httpx
import json


def build_slug(away_code, home_code, date):
    """Build a Polymarket slug from team codes and date.

    Example: build_slug("CHA", "NYK", "2026-04-12")
             returns "nba-cha-nyk-2026-04-12"
    """
    return f"nba-{away_code.lower()}-{home_code.lower()}-{date}"


def get_game_markets(slug):
    """Given a Polymarket slug, pull all markets for that game."""
    resp = httpx.get("https://gamma-api.polymarket.com/events", params={
        "slug": slug,
        "active": "true"
    })

    if resp.status_code != 200:
        print(f"  Error: status {resp.status_code}")
        return None

    data = resp.json()
    if not data:
        print(f"  No markets found for slug: {slug}")
        return None

    return data[0]


if __name__ == "__main__":
    #Tomorrow's known games (April 12, 2026)
    #temp Format: (away_code, home_code) 
    tomorrows_games = [
        ("CHA", "NYK"),
        ("BKN", "TOR"),
        ("ATL", "MIA"),
        ("ORL", "BOS"),
        ("MIL", "PHI"),
        ("WAS", "CLE"),
    ]
    date = "2026-04-12"

    print("=" * 60)
    print(f"POLYMARKET NBA GAMES — {date}")
    print("=" * 60)

    for away, home in tomorrows_games:
        slug = build_slug(away, home, date)
        print(f"\n{away} @ {home}  (slug: {slug})")

        event = get_game_markets(slug)
        if event:
            for m in event.get("markets", []):
                question = m.get("question", "")
                prices = m.get("outcomePrices", "N/A")
                volume = float(m.get("volume", 0))
                print(f"  -> {question}")
                print(f"     Prices: {prices}  |  Volume: ${volume:,.2f}")
