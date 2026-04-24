4/6/2026 ---
  explored json files from nba api (https://github.com/swar/nba_api)
  cleaned up raw data to get specifics (scoreboard, play be plays, boxscore), understanding what structure I'll be working with moving forward.




4/6 - 4/11/2026
  had to tweak web search to look for nba games rather than "nba" tagged slop. Constructed custom url search using data retrieved from nba api so gamma api accurately looks up the games I want.

  -slug is built then parsed into gamma api web link.
	  :error codes to test any issues with scraping data

  -games and date are hard coded for easy testing. just wanted to verify proper data retrieval.

  -last for loop simply goes through each game in list of games that are played on specified date (again, hard coded for test purposes) away team is not always presented first. intentional building only to follow rules of current slug build.


*Important notes*
if __name__ == "__main__": following code only runs if file is executed directly. functions like build_slug can be imported
to other files without all test code at bottom running on and on. no need to have this data update to terminal when bot updates. redundant and consumes resources.



4/12/2026
	started the process of building the model itself. right now empty framework exists but will be used for storing real time data -> then fed into portion of model that will make the decisions and trade.
	have to think about how data for these games update before forming the strategy. probably going to do live testing with data, see what those results are, and form a model based off those results.



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
  


 
 
 
  4/17-4/24
*SUPER IMPORTANT DAY*

  this text script was actually a pain to bring together so i'm gonna detail this one. Before I can even build the model for this program I have to test to see if i have enough of a latency gap 
  that allows me to exploit. if I can get feed from nba api even a second, second and a half ahead of polymarket I have something to work with, if that gap does not exist, it makes no sense to
  continue this project. So that's what I did, concurrently running our api polls with the data streamed from polymarket's websocket. Both not only run concurrently but they also share the
  same clock, so if poll_nba logs at a particular time and listen_polymarket logs **hopefully** 1 second, 1.4, 1.5 seconds later whatever it is, that gap is real and what im really looking for.
  Building the model in production only increases latency where buying overhead shows up and selling at a good price. ill get into our main functions here for this 1 aspect latency test:

  poll_nba():
    right now this function polls scoreboard every 1 second which is actually really slow. But, one second ensures I get a good stream of data without anything breaking due to network jitter's 
    and don't get any network errors when im requesting. When i compile all this data that i've logged (which i can't upload to git here, the text file is 390mb, a crazy size for some text in a
    .json) I'll at least have a start, then can go deeper, i just want to see the results of this first test. polling our api just gives us a snapshot of current score, so to keep track of score
    we use our own variables for last home and last away scores. if it's different, log it as a CHANGe in score with the difference. 

  listen_polymarket()
    subscribes to poly's websocket for a particular token (im focused on the main moneyline, i dont care for spreads that gets into a whole different thing. for this first test it was
    the knicks vs hawks, whether the knicks will win or hawks, simple). The websocket is nice cause it's push based and poly can reliably send that in pretty much instantly so the real
    bottleneck is how quickly i can get game data. I filtered for 3 main events here: 
        the price change (orderbook updates bids/asks moving)
        last trading price (executed fills)
        general orderbook snapshots

  main
  wipes the latency_log json at the start so each run is fresh (yea restarting mid progress is a main but im just banking on that not happening, this whole script is just a test anyone it's
  fine). this makes handling logs easy for me, i can simply rename the json to whatever i want after it's done and that'll be saved, when i run the script next it'll refresh the latency_log.
  async here is used to run concurrently on same event loo. since both spend most of time awaiting network input output, python makes progress on one while other is waiting. Both tasks log
  to the same file with the same clock timestamp source (both use datetime.now) which is what i'll be looking at whem compiling all this data later. important to note that shared clock isn't
  actually from async it's from running both in one python process so when datetime.now is called against the same os system clock for comparable timestamps.



Next time I'll be compiling the data to see if there is a gap or not. If no visible gap appears it's not necessarily lost yet i just need to tighten up tests to find out of a real sub second
edge is possible. Easiest way to do this is obviously shorten polling times for the api, reduce from 1s to 700-500ms (careful about going too low and hitting rate limits or bad data)
ill get into it more in detail next time.
