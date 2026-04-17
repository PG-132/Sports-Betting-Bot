"""Data models — clean structures for data flowing through the bot.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class GameEvent:
    """A single play by play event from the NBA API."""
    game_id: str
    period: int                # quarter (1-4, 5+ for OT)
    clock: str                 # time remaining, "PT04M32.00S"
    team: str                  # team abbreviation,"NYK"
    action_type: str           # i.e. "2pt", "3pt", "freethrow", "rebound"
    description: str           # i.e. "Jayyyllllleeennnnnnnn. Bruuuuunnnnnseeeeeeeen 27' 3PT"
    score_home: int
    score_away: int
    timestamp: datetime        # (updating in real-world time)


@dataclass
class MarketSnapshot:
    """A snapshot of a polymarket game market at a point in time."""
    slug: str                  # i.e. "nba-cha-nyk-2026-04-12"
    market_id: str             # polymarket's market ID, "1891036"
    question: str              # i.e. "Hornets vs. Knicks"
    price_yes: float           # ie. 0.725 (72.5% chance)
    price_no: float            # i.e 0.275 (27.5% chance)
    volume: float              # total dollars traded on this market
    timestamp: datetime        # when we grabbed this snapshot
