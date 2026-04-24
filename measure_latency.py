"""
Measure the latency gap between NBA scoring events and Polymarket price moves.

The key question: when a basket is made, can we detect the score change on the
NBA side BEFORE the Polymarket price moves?

Two tasks run in parallel:
  1. NBA poller — polls the scoreboard every 1 second, logs when score changes
  2. Polymarket listener — streams WebSocket, logs when price moves

Both write to the same log file with wall-clock timestamps for comparison side by side after the game.
"""

import asyncio
import json
import httpx
import websockets
from datetime import datetime
from nba_api.live.nba.endpoints import scoreboard


# HARDCODE these before running 
NBA_GAME_ID = "0042500123"                          # Knicks @ Hawks
POLYMARKET_TOKEN_ID = "92430469735954963360049025962310229515467044409334320200786108488083599918032"  # Knicks YES
POLL_INTERVAL = 1.0                                 # seconds between NBA polls
LOG_FILE = "latency_log.jsonl"                      # one JSON object per line

WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"


def log_event(event_type, data):
    # Append a single event to the log file with a wall-clock timestamp.
    entry = {
        "timestamp": datetime.now().isoformat(),
        "source": event_type,
        "data": data,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    # Prints to console for live view (it also shows up automatically in the .json of course but i like the console view more :P)
    print(f"[{entry['timestamp']}] {event_type}: {data}")


async def poll_nba():
    """Poll the NBA scoreboard every second. Log when score changes."""
    last_home_score = None
    last_away_score = None

    print(f"[NBA] Starting poller for game {NBA_GAME_ID}...")

    while True:
        try:
            board = scoreboard.ScoreBoard()
            games = board.get_dict()["scoreboard"]["games"]

            game = next((g for g in games if g["gameId"] == NBA_GAME_ID), None)
            if game is None:
                log_event("nba_error", {"msg": f"game {NBA_GAME_ID} not found"})
                await asyncio.sleep(POLL_INTERVAL)
                continue
            
            # Per poll snapshots, shortened names for fields pulled out of api responses
            home_score = int(game["homeTeam"]["score"])
            away_score = int(game["awayTeam"]["score"])
            status = game["gameStatusText"]

            # First poll, "None" because nothing has been seen yet.
            if last_home_score is None:
                log_event("nba_start", {
                    "home_score": home_score,
                    "away_score": away_score,
                    "status": status,
                })
                last_home_score = home_score
                last_away_score = away_score
            # Score changed on home side
            elif home_score != last_home_score:
                log_event("nba_score_change", {
                    "team": "home",
                    "tricode": game["homeTeam"]["teamTricode"],
                    "prev": last_home_score,
                    "new": home_score,
                    "diff": home_score - last_home_score,
                    "status": status,
                })
                last_home_score = home_score
            # Score changed on away side
            elif away_score != last_away_score:
                log_event("nba_score_change", {
                    "team": "away",
                    "tricode": game["awayTeam"]["teamTricode"],
                    "prev": last_away_score,
                    "new": away_score,
                    "diff": away_score - last_away_score,
                    "status": status,
                })
                last_away_score = away_score

        except Exception as e:
            log_event("nba_error", {"msg": str(e)})

        await asyncio.sleep(POLL_INTERVAL)


async def listen_polymarket():
    #Subscribe to the Polymarket WebSocket and log every price change.
    # Wrapped in a reconnect loop so a dropped connection doesn't kill the script.
    # the WS closes for any reason, we log it, wait 2 seconds, and reconnect.

    while True:  # outer reconnect loop — keeps us alive through the whole game
        try:
            print(f"[POLY] Connecting to {WS_URL}...")
            async with websockets.connect(WS_URL) as ws:
                await ws.send(json.dumps({
                    "type": "Market",
                    "assets_ids": [POLYMARKET_TOKEN_ID],
                }))
                log_event("poly_connected", {"msg": "subscribed to feed"})

                while True:
                    raw = await ws.recv()
                    try:
                        msg = json.loads(raw)
                    except json.JSONDecodeError:
                        log_event("poly_raw", {"raw": raw[:300]})
                        continue

                    # Normalize to list so we can loop
                    events = msg if isinstance(msg, list) else [msg]

                    for e in events:
                        if not isinstance(e, dict):
                            continue
                        event_type = e.get("event_type", "unknown")

                        # Only log meaningful stuff and skip the initial book snapshot noise
                        if event_type == "price_change":
                            log_event("poly_price_change", {
                                "changes": e.get("price_changes", []),
                            })
                        elif event_type == "last_trade_price":
                            log_event("poly_trade", {
                                "price": e.get("price"),
                                "size": e.get("size"),
                                "side": e.get("side"),
                            })
                        elif event_type == "book":
                            # Just log that we got the initial snapshot, no details
                            log_event("poly_book_snapshot", {"msg": "initial orderbook received"})

        except Exception as e:
            # covers lots of exceptions here, just log and reconnect.
            log_event("poly_disconnect", {"msg": str(e), "type": type(e).__name__})
            await asyncio.sleep(2)


async def main():
    print(f"Logging to: {LOG_FILE}")
    print(f"NBA game ID: {NBA_GAME_ID}")
    print(f"Polymarket token: {POLYMARKET_TOKEN_ID[:30]}...")
    print("=" * 60)
    print("Running both tasks in parallel. Ctrl+C to stop.")
    print("=" * 60)

    # Clear the log file at start. Efficient for testing, just rename the file and it'll save the json, only latency_log refreshes when ran.
    open(LOG_FILE, "w").close()

    # Run both tasks concurrently. super important, it's like the whole point of this.
    await asyncio.gather(
        poll_nba(),
        listen_polymarket(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user.")
