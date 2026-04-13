import os
from dotenv import load_dotenv

load_dotenv()


#Polymarket 
POLYMARKET_BASE_URL = os.getenv("POLYMARKET_BASE_URL", "https://clob.polymarket.com")
POLYMARKET_WS_URL = os.getenv("POLYMARKET_WS_URL", "wss://ws-subscriptions-clob.polymarket.com/ws/market")

# NBA 
NBA_REQUEST_DELAY = float(os.getenv("NBA_REQUEST_DELAY", 0.5))

# Paper Trading 
STARTING_BALANCE = float(os.getenv("STARTING_BALANCE", 10000))
DEFAULT_POSITION_SIZE = float(os.getenv("DEFAULT_POSITION_SIZE", 100))
