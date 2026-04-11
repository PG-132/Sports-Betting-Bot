"""
Quick exploration script - see what the NBA API actually gives us.
This is throwaway code, just for learning the data shapes.
"""

from nba_api.live.nba.endpoints import scoreboard, boxscore, playbyplay
import json


def explore_scoreboard():
    """What games are on today?"""
    print("==================================================================")
    print("TODAY'S SCOREBOARD")
    print("==================================================================")

    board = scoreboard.ScoreBoard()
    games = board.get_dict()["scoreboard"]["games"]

    print(f"Found {len(games)} games today\n")

    for game in games:
        game_id = game["gameId"]
        home = game["homeTeam"]
        away = game["awayTeam"]
        status = game["gameStatusText"]
        period = game["period"]

        print(f"Game ID: {game_id}")
        print(f"  {away['teamTricode']} ({away['score']}) @ {home['teamTricode']} ({home['score']})")
        print(f"  Status: {status}")
        print(f"  Period: {period}")
        print()

    return games


def explore_play_by_play(game_id):
    """What does play-by-play data look like for a game?"""
    print("==================================================================")
    print(f"PLAY-BY-PLAY for game {game_id}")
    print("==================================================================")

    pbp = playbyplay.PlayByPlay(game_id)
    actions = pbp.get_dict()["game"]["actions"]

    print(f"Total actions: {len(actions)}\n")

    # Show the last 10 actions so we see recent plays
    print("--- Last 10 actions ---")
    for action in actions[-10:]:
        clock = action.get("clock", "")
        period = action.get("period", "")
        team = action.get("teamTricode", "")
        action_type = action.get("actionType", "")
        description = action.get("description", "")
        score_home = action.get("scoreHome", "")
        score_away = action.get("scoreAway", "")

        print(f"  Q{period} {clock} | {team} | {action_type}: {description} | Score: {score_away}-{score_home}")

    # Print full structure of one action so we see ALL available fields
    print("\n--- Full structure of one action ---")
    print(json.dumps(actions[-1], indent=2))


def explore_boxscore(game_id):
    """What does the boxscore look like?"""
    print("==================================================================")
    print(f"BOXSCORE for game {game_id}")
    print("==================================================================")

    bs = boxscore.BoxScore(game_id)
    game_data = bs.get_dict()["game"]

    home = game_data["homeTeam"]
    away = game_data["awayTeam"]

    print(f"{away['teamTricode']} ({away['score']}) @ {home['teamTricode']} ({home['score']})")
    print(f"Status: {game_data['gameStatusText']}")
    print(f"Period: {game_data['period']}")

    # Show team stats keys so we know what's available
    if home.get("statistics"):
        print(f"\nAvailable team stats: {list(home['statistics'].keys())[:10]}...")


if __name__ == "__main__":
    games = explore_scoreboard()

    if games:
        # Pick the first game that has data (finished or in-progress)
        target = None
        for g in games:
            if int(g["homeTeam"]["score"]) > 0:
                target = g["gameId"]
                break

        if target:
            # Game is live or finished — we can pull play-by-play
            print()
            explore_play_by_play(target)
            print()
            explore_boxscore(target)
        else:
            # Games haven't started yet — use a recent completed game
            print("\nNo live/completed games yet today. Using a recent game instead...\n")
            fallback_id = "0022501138"
            try:
                explore_play_by_play(fallback_id)
            except Exception:
                print("Fallback game not available either. Try again during a live game!")
    else:
        print("No games today - try again on a game day!")
