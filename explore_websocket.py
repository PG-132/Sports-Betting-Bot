"""
Explore Polymarket's WebSocket feed.

Testing Goal: connect to the WebSocket, subscribe to one active market,
print every message we receive for 90 seconds then disconnect.

crypto markets for 24/7 activity and huge liquidity ^-^
"""

import asyncio
import json
import httpx
import websockets
from datetime import datetime


WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
GAMMA_URL = "https://gamma-api.polymarket.com"

# How long to listen before disconnecting (seconds)
LISTEN_DURATION = 90


def find_active_crypto_market():
    # Find an active crypto market with decent volume AND real uncertainty.(something not definitive like between 10-90 for trading volume)
    print("Searching for an active crypto market...")

    resp = httpx.get(f"{GAMMA_URL}/events", params={
        "active": "true",
        "closed": "false",
        "limit": 200,
    })
    events = resp.json()

    candidates = []

    # MEAT of this script. 
    #Loops through top level events, loops through markets within event if exists (markets can have sub-specific markets) otherwise use the 1 simple YES/No market listed. 
    # Parse clob tokens for the ids to sub to websocket. NOTE: token_ids[0] is YES (for some reason, dk why they didn't just use boolean) token_ids[1] is NO (???)
    for event in events:
        tags = event.get("tags", [])
        tag_labels = [t.get("label", "").lower() for t in tags if isinstance(t, dict)]

        if "crypto" not in tag_labels:
            continue

        for market in event.get("markets", []):
            token_ids_raw = market.get("clobTokenIds", "")
            if not token_ids_raw:
                continue
            try:
                token_ids = json.loads(token_ids_raw)
            except (json.JSONDecodeError, TypeError):
                continue
            if not token_ids:
                continue

            # Only keep markets with real uncertainty (price between 0.10 and 0.90)
            try:
                prices = json.loads(market.get("outcomePrices", "[]"))
                yes_price = float(prices[0]) if prices else 0
            except (json.JSONDecodeError, ValueError, IndexError):
                continue

            if not (0.10 < yes_price < 0.90):
                continue

            candidates.append({
                "question": market.get("question", ""),
                "token_id": token_ids[0],
                "volume": float(market.get("volume", 0)),
                "yes_price": yes_price,
            })

    if not candidates:
        return None

    # Pick the one with highest volume (again just for testing)
    return max(candidates, key=lambda m: m["volume"])


async def listen_to_market(token_id, question):
    # Connect to WebSocket, subscribe to the market, print messages.
    print(f"\nConnecting to {WS_URL}...")

    async with websockets.connect(WS_URL) as ws:
        print("Connected!")

        # Subscribe to the market feed for this asset
        subscribe_msg = {
            "type": "Market",
            "assets_ids": [token_id],
        }
        await ws.send(json.dumps(subscribe_msg))
        print(f"Subscribed to: {question}")
        print(f"Token ID: {token_id[:20]}...\n")
        print("========================================================================")
        print(f"Listening for {LISTEN_DURATION} seconds...")
        print("========================================================================")

        message_count = 0
        start_time = asyncio.get_event_loop().time()

        try:
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                remaining = LISTEN_DURATION - elapsed
                if remaining <= 0:
                    break

                try:
                    # Wait for a message, but end when the timer's up
                    raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
                except asyncio.TimeoutError:
                    break

                message_count += 1
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

                # Try to parse as json. Polymarket sometimes sends a dict, sometimes batched)
                msg = json.loads(raw)
                print(f"[{timestamp}] #{message_count}")
                print(json.dumps(msg, indent=2)[:400])

                print()

        finally:
            print("=" * 60)
            print(f"Done. Received {message_count} messages in {LISTEN_DURATION}s.")
            print("Closing connection cleanly...")


async def main():
    market = find_active_crypto_market()
    if not market:
        print("No active crypto market found. Try again later.")
        return

    print(f"\nFound market: {market['question']}")
    print(f"Volume: ${market['volume']:,.2f}")

    await listen_to_market(market["token_id"], market["question"])


if __name__ == "__main__":
    asyncio.run(main())
