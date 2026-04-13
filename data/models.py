"""
Data models — clean structures for the data flowing through the bot.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class GameEvent:
    """A single play-by-play event from the NBA API."""
    game_id: str
    period: int                # quarter (1-4, 5+ for OT)
    clock: str                 # time remaining, e.g. "PT04M32.00S"
    team: str                  # team abbreviation, e.g. "NYK"
    action_type: str           # e.g. "2pt", "3pt", "freethrow", "rebound"
    description: str           # e.g. "J. Brunson 27' 3PT"
    score_home: int
    score_away: int
    timestamp: datetime        # when it actually happened (real-world time)


@dataclass
class MarketSnapshot:
    """A snapshot of a Polymarket game market at a point in time."""
    slug: str                  # e.g. "nba-cha-nyk-2026-04-12"
    market_id: str             # Polymarket's market ID, e.g. "1891036"
    question: str              # e.g. "Hornets vs. Knicks"
    price_yes: float           # e.g. 0.725 (72.5% chance)
    price_no: float            # e.g. 0.275 (27.5% chance)
    volume: float              # total dollars traded on this market
    timestamp: datetime        # when we grabbed this snapshot
