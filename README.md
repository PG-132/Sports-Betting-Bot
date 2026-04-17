4/6 ---
  explored json files from nba api (https://github.com/swar/nba_api)
  cleaned up raw data to get specifics (scoreboard, play be plays, boxscore), understanding what structure I'll be working with moving forward.




4/6 - 4/11
  had to tweak web search to look for nba games rather than "nba" tagged slop. Constructed custom url search using data retrieved from nba api so gamma api accurately looks up the games I want.

  -slug is built then parsed into gamma api web link.
	  :error codes to test any issues with scraping data

  -games and date are hard coded for easy testing. just wanted to verify proper data retrieval.

  -last for loop simply goes through each game in list of games that are played on specified date (again, hard coded for test purposes) away team is not always presented first. intentional building only to follow rules of current slug build.


*Important notes*
if __name__ == "__main__": following code only runs if file is executed directly. functions like build_slug can be imported
to other files without all test code at bottom running on and on. no need to have this data update to terminal when bot updates. redundant and consumes resources.



4/11 - 4/17
School got in the way of work, bit slower to work on. managed to assemble new working script that confirms if program can talk to polymarkets websocket feed. we had already verified nba api polymarket gamma api return data and can communicate. needed to verify if websocket would feed me live data and it does!

-Went with crypto markets for active trading, always on markets. 
  -Main starting issues:
  First iteration just sent a snapshot right as I subscribed to market feed, came back as a list which crashed program. had to account for list, dict, and json 
  had to account for multiple potential submarkets within an umbrella market (Example: MegaETH market cap one day after launch: bunch of submarkets: > 1.5 bil, > 2bil, > 4 bil, etc )
  nested loop solution. loop through crypto markets, find one with good liquidity, find the sub market with highest liquidity (if exists multiple)

-Not gonna bother talking about all the other atrocities that come with debugging code. above were main logic issues, everything else is clicking run and crashing * 2000 times, fixing line by line till it works you know how it is.

*Important notes*
Aggregated data might look a little weird, it's important to note that **price** in output does not necessarily represent x shares were bought at x price. so:
If price change #1 says 1531 shares were bought at 0.18 and price change #2 says 3491 shares were "bought" at 0.3 does NOT necessarily mean there was a 15% drop in price. websocket accounts for **ANY CHANGESSS** in the orderbook at any point in time. could be a lowball bid sitting on the OB hoping to get sold (limit order) careful here as cancelled limit orders may appear as 0 price change. may have to revisit this later but for now i just needed to know websocket will pull live data. 

NEXT TIME: We're gonna be testing for latency. i think. unless something pops up
  
