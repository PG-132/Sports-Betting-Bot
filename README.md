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
  
