import os
import json
import sys
# import requests
# requests==2.19.1
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from flask import Flask, request
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options 
# import selenium.webdriver.chrome.service as service
import re
import pymysql


app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
	data = request.get_json()
	#####     Sniffing for @bot     #####
	if '@bot' in data['text']:
		sender = data['user_id']
		text = data['text']
		# sys.stdout.write('sender: {} | text: {}'.format(sender,text))
		parse(sender, text)
		return('ok',200)

	#####     Sniffing for @testing     #####
	elif '@testing' in data['text']:
		# Sends us into a play function (sandbox_testing) that feeds into a send message function aimed at File Sharing group
		text = data['text']
		# sys.stdout.write('sent into testing environment')
		sandbox_testing(text)
		return('ok',200)
	else: return('ok',200)

def database_access(table, command):
	con = pymysql.connect(host='us-cdbr-iron-east-01.cleardb.net', user='bc01d34543e31a', password='02cdeb05', database='heroku_29a4da67c47b565')
	cur = con.cursor()


	##########  SETTINGS
	if table == 'settings':
		cur.execute("SELECT settings_rbvotes, settings_week FROM settings WHERE description='main';")
		settings_tuple = cur.fetchall()
		con.commit()
		con.close()
		if command == 'week':
			week = int(settings_tuple[0][1])
			return(week)
		elif command == 'rb':
			rb_votes = int(settings_tuple[0][0])
			return(rb_votes)
	
	#########   RECORDS		
	elif table == 'records':
		if command == 'all':
			# Highest single game score
			cur.execute("SELECT weekly_points, franchise, season, week, opponent FROM weekly_records WHERE type=1 ORDER BY weekly_points desc LIMIT 1;")
			weekly_highscore_tuple = cur.fetchall()
			con.commit()
			# Lowest single game score
			cur.execute("SELECT weekly_points, franchise, season, week, opponent FROM weekly_records WHERE type=2 ORDER BY weekly_points asc LIMIT 1;")
			weekly_lowcore_tuple = cur.fetchall()
			con.commit()
			# Biggest blowout
			cur.execute("SELECT weekly_margin, franchise, season, week, opponent FROM weekly_records WHERE type=3 ORDER BY weekly_margin desc LIMIT 1;")
			weekly_blowout_tuple = cur.fetchall()
			con.commit()
			# Closest game
			cur.execute("SELECT weekly_margin, franchise, season, week, opponent FROM weekly_records WHERE type=4 ORDER BY weekly_margin asc LIMIT 1;")
			weekly_closest_tuple = cur.fetchall()
			con.commit()
			# Most PPG Season
			cur.execute("SELECT season_ppg, franchise, season FROM season_records WHERE type=5 ORDER BY season_ppg desc LIMIT 1;")
			season_highppg_tuple = cur.fetchall()
			con.commit()
			# Fewest PPG Season
			cur.execute("SELECT season_ppg, franchise, season FROM season_records WHERE type=6 ORDER BY season_ppg asc LIMIT 1;")
			season_lowppg_tuple = cur.fetchall()
			con.commit()
			# Most WINS
			cur.execute("SELECT season_wins, franchise, season FROM season_records WHERE type=7 ORDER BY season_wins desc LIMIT 1;")
			season_highwins_tuple = cur.fetchall()
			con.commit()
			# Fewest WINS
			cur.execute("SELECT season_wins, franchise, season FROM season_records WHERE type=8 ORDER BY season_wins asc LIMIT 1;")
			season_lowwins_tuple = cur.fetchall()
			con.commit()
			# Highest avg margin of victory
			cur.execute("SELECT season_margin, franchise, season FROM season_records WHERE type=9 ORDER BY season_margin desc LIMIT 1;")
			season_highmargin_tuple = cur.fetchall()
			con.commit()

			con.close()
			# weekly_points = weekly_highscore_tuple[0][0]
			# franchise = weekly_highscore_tuple[0][1]
			# season = weekly_highscore_tuple[0][2]
			# week = weekly_highscore_tuple[0][3]
			# opponent = weekly_highscore_tuple[0][4]
			return(weekly_highscore_tuple, weekly_lowcore_tuple, weekly_blowout_tuple, weekly_closest_tuple, season_highppg_tuple, season_lowppg_tuple, season_highwins_tuple, season_lowwins_tuple, season_highmargin_tuple)
			# return(weekly_points, franchise, season, week, opponent)
		else: 
			return('none',200)
	else:
		con.close()
		sys.stdout.write('entered db access but no relevant command')
		return('ok',200)

def database_change_week(direction):
	week = database_access('settings', 'week')
	if direction == 'plus':
		week += 1
	elif direction == 'minus':
		week -= 1

	con = pymysql.connect(host='us-cdbr-iron-east-01.cleardb.net', user='bc01d34543e31a', password='02cdeb05', database='heroku_29a4da67c47b565')
	cur = con.cursor()
	cur.execute("UPDATE settings SET settings_week=%s WHERE description='main';", (week))
	con.commit()
	con.close()
	return('Week updated to %s') % (week)

def database_remove_bob():
	rb_votes = database_access('settings', 'rb')
	rb_votes += 1

	con = pymysql.connect(host='us-cdbr-iron-east-01.cleardb.net', user='bc01d34543e31a', password='02cdeb05', database='heroku_29a4da67c47b565')
	cur = con.cursor()
	cur.execute("UPDATE settings SET settings_rbvotes=%s WHERE description='main';", (rb_votes))
	con.commit()
	con.close()
	return('Total #RB votes: %s') % (rb_votes)




def parse(sender, text):
	#### Ignore every line that the bot prints out itself
	if re.search("'@bot", text) or re.search("All scores are scraped in real-time", text) or re.search("-----   Commands   -----", text) or re.search("1. '@bot help' = this help message", text) or re.search("2. '@bot scores' = live scores", text) or re.search("3. '@bot my score' = your live score", text) or re.search("4. '@bot (franchise) score' = enter any franchise name", text) or re.search("5. '@bot records' = record book", text) or re.search("_commands are case and space insensitive_", text) or re.search("We can add pretty much any other features you think of. Post any other cool ideas that you've got, and we'll add them to the wish list.", text) or re.search('Total #RB votes', text) or re.search('Week has been set to', text): 
		# AVOID responding to the BOT itself (in the help message)
		return('ok',200)
	# 1   ...   @bot my score 
	elif re.search('my', text, re.I) and re.search('score', text, re.I):
		franchise = get_franchise_number(sender)
		# sys.stdout.write('franchise: {} <<'.format(franchise))
		get_data(franchise, 1)
		return('ok',200)
	
	# 2   ...   @bot all scores
	elif re.search('score', text, re.I): #re.search('all', text, re.I) and
		franchise, message_type = text_id_franchise(text)
		get_data(franchise, message_type)
		return('ok',200)

	# 3   ...   @bot my mwm score
	# elif re.search('my', text, re.I) and re.search('mwm', text, re.I) and re.search('score', text, re.I):
	# 	franchise = get_franchise_number(sender)
	# 	# sys.stdout.write('franchise: {} <<'.format(franchise))
	# 	get_data(franchise, 1)
	# 	return('ok',200)
	
	# 4   ...   @bot mwm scores
	# elif re.search('my', text, re.I) and re.search('score', text, re.I):
	# 	franchise = get_franchise_number(sender)
	# 	# sys.stdout.write('franchise: {} <<'.format(franchise))
	# 	get_data(franchise, 1)
	# 	return('ok',200)

	# 5   ...   @bot mwm standings
	# elif re.search('my', text, re.I) and re.search('score', text, re.I):
	# 	franchise = get_franchise_number(sender)
	# 	# sys.stdout.write('franchise: {} <<'.format(franchise))
	# 	get_data(franchise, 1)
	# 	return('ok',200)
	
	# 6   ...   @bot mwm schedule
	# elif re.search('my', text, re.I) and re.search('score', text, re.I):
	# 	franchise = get_franchise_number(sender)
	# 	# sys.stdout.write('franchise: {} <<'.format(franchise))
	# 	get_data(franchise, 1)
	# 	return('ok',200)
	
	
	# 7   ...   @bot records
	elif re.search('record', text, re.I):
		weekly_highscore_tuple, weekly_lowcore_tuple, weekly_blowout_tuple, weekly_closest_tuple, season_highppg_tuple, season_lowppg_tuple, season_highwins_tuple, season_lowwins_tuple, season_highmargin_tuple = database_access('records', 'all')
		# message = '1. %s : %s - %s/%s vs %s' % (weekly_points, franchise, season, week, opponent)
		### Weekly
		best_game = 'Most points scored in a game:\n%s - %s (%s/%s)' % (weekly_highscore_tuple[0][0], weekly_highscore_tuple[0][1], weekly_highscore_tuple[0][2], weekly_highscore_tuple[0][3])
		worst_game = 'Fewest points in a game:\n%s - %s (%s/%s)' % (weekly_lowcore_tuple[0][0], weekly_lowcore_tuple[0][1], weekly_lowcore_tuple[0][2], weekly_lowcore_tuple[0][3])
		blowout = 'Biggest blowout:\n%s - %s (%s/%s)' % (weekly_blowout_tuple[0][0], weekly_blowout_tuple[0][1], weekly_blowout_tuple[0][2], weekly_blowout_tuple[0][3])
		closest_game = 'Closest game:\n%s - %s (%s/%s)' % (weekly_closest_tuple[0][0], weekly_closest_tuple[0][1], weekly_closest_tuple[0][2], weekly_closest_tuple[0][3])
		### Seasonal
		best_ppg = 'Most points-per-game in a season:\n%s - %s (%s)' % (season_highppg_tuple[0][0], season_highppg_tuple[0][1], season_highppg_tuple[0][2])
		fewest_ppg = 'Fewest ppg in a season:\n%s - %s (%s)' % (season_lowppg_tuple[0][0], season_lowppg_tuple[0][1], season_lowppg_tuple[0][2])
		most_wins = 'Most wins:\n%s - %s (%s)' % (season_highwins_tuple[0][0], season_highwins_tuple[0][1], season_highwins_tuple[0][2])
		high_margin = 'Largest average margin of victory:\n%s - %s (%s)' % (season_highmargin_tuple[0][0], season_highmargin_tuple[0][1], season_highmargin_tuple[0][2])
		message = "=== Modern Era Record Book ===\n-----  Week  -----\n%s\n%s\n%s\n%s\n-----  Season  -----\n%s\n%s\n%s\n%s" % (best_game, worst_game, blowout, closest_game, best_ppg, fewest_ppg, most_wins, high_margin)
		send_message(message)
		return('ok',200) 

	#### Stock responses. ** Remember to add or statements to the first if test above to exclude bot responses from generating an infinite loop of responses
	
	# Get list of NFL bets
	elif re.search('bets', text, re.I):
		get_bets()
		return('ok',200)

	# help   ...   and posts response
	elif re.search('help', text, re.I):
		help_message = "All scores are scraped in real-time\n-----   Commands   -----\n1. '@bot help' = this help message\n2. '@bot scores' = live scores\n3. '@bot my score' = your live score\n4. '@bot (franchise) score' = enter any franchise name\n5. '@bot records' = record book\n=====\nWe can add pretty much any other features you think of. Post any other cool ideas that you've got, and we'll add them to the wish list. Wishlist: Ross - live standings, Kmish - FAAB, Gilhop - franchise summary"
		send_message(help_message)
		return('ok',200)
	#    ...   @bot remove bob   ...   and posts vote tally
	elif re.search('remove', text, re.I) and re.search('bob', text, re.I):
		rb_message = database_remove_bob()
		send_message(rb_message)
		return('ok',200)

	# elif re.search('vegas', text, re.I):
	# 	# vegas_message = get_vegas_lines(text)
	# 	# send_message(vegas_message)
	# 	get_vegas_lines(text)
	# 	return('ok',200)
	
	##### Settings from within the groupme
	# Set the week. Can only be done when '@bot advance week' is sent by me
	elif re.search('next week', text, re.I) and sender == '7435972':
		settings_message = database_change_week('plus')
		send_message(settings_message)
		return('ok',200)
	elif re.search('last week', text, re.I) and sender == '7435972':
		settings_message = database_change_week('minus')
		send_message(settings_message)
		return('ok',200)
	elif re.search('next week', text, re.I) or re.search('last week', text, re.I):
		message = '#KyleLogic'
		send_message(message)
	else: return('off topic',200)

def get_data(franchise, message_type):
	try:
		from bs4 import BeautifulSoup
		from selenium import webdriver
		from selenium.webdriver.chrome.options import Options 
		import selenium.webdriver.chrome.service as service
		season = 2018
		week = database_access('settings', 'week')
		url = 'http://games.espn.com/ffl/scoreboard?leagueId=133377&matchupPeriodId=%s&seasonId=%s' % (week, season)
		chrome_options = Options()
		chrome_options.binary_location = os.environ['GOOGLE_CHROME_BIN']
		chrome_options.add_argument('--disable-gpu')
		chrome_options.add_argument('--no-sandbox')
		chrome_options.add_argument('--headless')
		driver = webdriver.Chrome(executable_path=os.environ['CHROMEDRIVER_PATH'], chrome_options=chrome_options)
		driver.get(url)
		html = driver.page_source
		driver.close()
		soup = BeautifulSoup(html, "lxml")

		# This gives a list of franchise numbers in the order that they're matched up
		franchise_number_list = re.findall(r'(?<=id="teamscrg_)[0-9]*', str(soup)) # confirmed: this creates a list
		points_list = []
		projected_list = []

		# The if statement tests to see if the matchup is ongoing (returns true if so) or already completed (returns false if so)
		if re.search('tmTotalPts_', str(soup)):
			for i in franchise_number_list:
				points_list.append(soup.select_one('#tmTotalPts_%s' % (i)).text)
				projected_list.append(soup.select_one('#team_liveproj_%s' % (i)).text)
		else:
			points_list = re.findall(r'(?<=width="18%">)[0-9]*[.]?[0-9]', str(soup))
			projected_list = 'GAME COMPLETED'
			sys.stdout.write('nestled into a completed game. no projs')

		generate_message(franchise, message_type, franchise_number_list, points_list, projected_list)
		return('ok',200) 
		# return(franchise_number_list, points_list, projected_list)  # Return franchishe, message_type, franchise_number_list, points_list, and projected_list, then these things can be used in a mwm function. If projected_list == 'GAME COMPLETED': enter the scores into the mwm db
		# Adding Try/Except mitigated the connection error issue on run #1

	except:
		send_message('Error. Our combination of free cloud hosting + webdriver is lagging like a noob. Try a different command, or retry the same command in a few mintues.')
		return('get_data failed')


def generate_message(franchise, message_type, franchise_number_list, points_list, projected_list):
	
	#####     @bot my score     #####

	if message_type == 1:
		position = franchise_number_list.index(str(franchise))
		franchise_score = points_list[position]
		# sys.stdout.write(franchise_score)
		
		# Tests to see if the game is already over. 'N/A' projected list means it's over and there are no longer projections available
		if projected_list != 'GAME COMPLETED':
			franchise_proj = projected_list[position]
			sys.stdout.write(franchise_proj)
		if position % 2 == 0:
			opponent_position = position + 1
			# sys.stdout.write('even index')
		else: 
			opponent_position = position - 1
			# sys.stdout.write('odd index')

		opponent_franchise = int(franchise_number_list[opponent_position])
		opponent_score = points_list[opponent_position]
		# sys.stdout.write('opponent score')
		
		# Tests to see if the game is already over. 'N/A' projected list means it's over and there are no longer projections available
		if projected_list != 'GAME COMPLETED':
			opponent_proj = projected_list[opponent_position]
			# sys.stdout.write(opponent_proj)

		# Test to see if the game is already over. 'N/A' projected list means it's over and there are no longer projections available
		if projected_list != 'GAME COMPLETED':
			my_ongoing_matchup = '{} - {} | proj: {}\n{} - {} | proj: {}'.format(franchise_score, get_franchise_name(franchise), franchise_proj, opponent_score, get_franchise_name(opponent_franchise), opponent_proj)
			send_message(my_ongoing_matchup)
			return('ok',200)
			# WORKED B
		else: 
			my_completed_matchup = '{} - {}\n{} - {}'.format(franchise_score, get_franchise_name(franchise), opponent_score, get_franchise_name(opponent_franchise))
			sys.stdout.write('It should send my score from last week')
			send_message(my_completed_matchup)
			return('ok',200)
			# WORKED C
	
	#####     @bot all scores     #####

	elif message_type == 2:
		week = database_access('settings', 'week')
		if projected_list != 'GAME COMPLETED':
			live_scoreboard = '*** Week %i Live Scoreboard ***\n' % week
			for i in range(len(franchise_number_list))[0::2]:
				live_scoreboard = live_scoreboard + '{} - {} | proj: {}\n{} - {} | proj: {}\n===== ===== =====\n'.format(points_list[i], get_franchise_name(int(franchise_number_list[i])), projected_list[i], points_list[i+1], get_franchise_name(int(franchise_number_list[i+1])), projected_list[i+1])
			send_message(live_scoreboard)
			return('ok',200)
			# WORKED A
		else:
			final_scoreboard = '*** Week %i Final Scoreboard ***\n' % week
			for i in range(len(franchise_number_list))[0::2]:
				final_scoreboard = final_scoreboard + '{} - {}\n{} - {}\n===== ===== =====\n'.format(points_list[i], get_franchise_name(int(franchise_number_list[i])), points_list[i+1], get_franchise_name(int(franchise_number_list[i+1])))
			send_message(final_scoreboard)
			return('ok',200)
			# WORKED C after pinging a different message and trying again


# def mwm(message_request, sender):
# 	# message_request will be: 3. mine, 4. Scores, 5. Standings, 6. Schedule
# 	if message_request == 'mine':
# 		franchise_number_list, points_list, projected_list = get_data()
# 		position = franchise_number_list.index(str(sender))
# 		franchise_score = points_list[position]
# 		# sys.stdout.write(franchise_score)
		
# 		# Tests to see if the game is already over. 'GAME COMPLETED' projected list means it's over and there are no longer projections available
# 		if projected_list != 'GAME COMPLETED':
# 			franchise_proj = projected_list[position]
# 			# sys.stdout.write(franchise_proj)
# 		opponent_franchise = #### LEAVING OFF HERE --- write a function that takes week & sender, and spits out the opponent. Easier to store each teams schedule as a list, and find week's opponent via index slicing the list. Then apply that to :: int(franchise_number_list[opponent_position])
# 		## Need to find opponent_position in the franchise_number_list. Same way we did for franchise above
# 		opponent_score = points_list[opponent_position]
# 		# sys.stdout.write('opponent score')
		
# 		# Tests to see if the game is already over. 'N/A' projected list means it's over and there are no longer projections available
# 		if projected_list != 'GAME COMPLETED':
# 			opponent_proj = projected_list[opponent_position]
# 			# sys.stdout.write(opponent_proj)

# 		# Test to see if the game is already over. 'N/A' projected list means it's over and there are no longer projections available
# 		if projected_list != 'GAME COMPLETED':
# 			my_ongoing_matchup = '{} - {} | proj: {}\n{} - {} | proj: {}'.format(franchise_score, get_franchise_name(franchise), franchise_proj, opponent_score, get_franchise_name(opponent_franchise), opponent_proj)
# 			send_message(my_ongoing_matchup)
# 			return('ok',200)
# 			# WORKED B
# 		else: 
# 			my_completed_matchup = '{} - {}\n{} - {}'.format(franchise_score, get_franchise_name(franchise), opponent_score, get_franchise_name(opponent_franchise))
# 			sys.stdout.write('It should send my score from last week')
# 			send_message(my_completed_matchup)
# 			return('ok',200)
# 			# WORKED C
	
# def get_vegas_lines(text):
# 	try:
# 		from bs4 import BeautifulSoup
# 		# from urllib.request import urlopen
# 		from selenium import webdriver
# 		from selenium.webdriver.chrome.options import Options 
# 		import selenium.webdriver.chrome.service as service
# 		url = 'http://www.espn.com/nfl/lines'
# 		chrome_options = Options()
# 		chrome_options.binary_location = os.environ['GOOGLE_CHROME_BIN']
# 		chrome_options.add_argument('--disable-gpu')
# 		chrome_options.add_argument('--no-sandbox')
# 		chrome_options.add_argument('--headless')
# 		driver = webdriver.Chrome(executable_path=os.environ['CHROMEDRIVER_PATH'], chrome_options=chrome_options)
# 		driver.get(url)
# 		html = driver.page_source
# 		driver.close()
# 		# page = urlopen(url)
# 		# page_content = page.read()

# 		soup = BeautifulSoup(html, "lxml")


# 		first_team = re.findall(r'(?<=<td width="50%">)[+-.0-9]*(?=<br/>)', str(soup)) # Makes a list of spreads of the first teams
# 		second_team = re.findall(r'(?<=<br/>)[+-.0-9]*(?=</td>)', str(soup)) # Makes a list of spreads of the second teams
# 		# overunder = re.findall(r'(?<=<td width="50%">)[0-9.]*(?=\sO/U)', str(soup)) ### LENGTH = 3  # Makes a list of over unders
# 		# games = re.findall(r'(?<=<td colspan="4">)[\sa-zA-Z]*(?=\s-)', str(soup)) ### LENGTH = 1  # Makes a list of all matchups
# 		games = re.findall(r'(?<=<td colspan="4">)[^-]*', str(soup))
# 		home = first_team[::5]
# 		away = second_team[::5]
# 		ou = overunder[::5]
		
# 		length = len(games)

# 		send_message(length)
# 		# for i in range(0, length):
# 		# 	send_message('%s %s %s || %s O/U' % (home[i], games[i], away[i], ou[i]))
		
# 		# slate = []
# 		# for i in range(len(games)):
# 		# 	slate.append('%s %s %s || %s O/U' % (home[i], games[i], away[i], ou[i]))
		    
# 		# modified = ''.join(re.findall(r'(?<=gas\s)[\sa-zA-Z]*', str(text)))
# 		# send = slate[0]
# 		# send = 'blank'


# 		# send_message(home[2])
# 		# return(slate[7])

# 		##### All 32 NFL Teams
# 		# if re.search('denver', text, re.I) or re.search('broncos', text, re.I):
# 		# 	for i in range(len(games)):
# 		# 		if 'Denver' in games[i]:
# 		# 			# message = slate[i]
# 		# 			return(slate[i])
# 		# 			# return(message)        
# 		# elif re.search('new orleans', text, re.I) or re.search('saints', text, re.I):
# 		# 	for i in range(len(slate)):
# 		# 		if 'New Orleans' in slate[i]:
# 		# 			message = slate[i]
# 		# 			return(message)
# 		# elif re.search('tampa', text, re.I) or re.search('bucs', text, re.I):
# 		# 	for i in range(len(slate)):
# 		# 		if 'Tampa Bay' in slate[i]:
# 		# 			return(slate[i])
# 		# elif re.search('carolina', text, re.I) or re.search('panthers', text, re.I):
# 		# 	for i in range(len(slate)):
# 		# 		if 'Carolina' in slate[i]:
# 		# 			return(slate[i])
# 		# else:
# 		# 	return("'@bot vegas City' is the command. Example: '@bot vegas New Orleans' ... LA Rams, LA Chargers, NY Giants, NY Jets for those 4 teams.")
			
# 	except:
# 		send_message('Error. Our combination of free cloud hosting + webdriver is lagging like a noob. Try a different command, or retry the same command in a few mintues.')

def get_bets():
	con = pymysql.connect(host='us-cdbr-iron-east-01.cleardb.net', user='bc01d34543e31a', password='02cdeb05', database='heroku_29a4da67c47b565')
	cur = con.cursor()
	cur.execute("SELECT * FROM betting_table;")
	bets = cur.fetchall()
	con.commit()
	cur.close()
	con.close()

	message = "This week's NFL slate:\n"
	bet_length = len(bets)
	for i in range(0,bet_length):
		message = message + "{}\n".format(bets[i][0])
	send_message(message)
	return('ok',200)





def send_message(msg):
	url = 'https://api.groupme.com/v3/bots/post'
	##### Formatting wishlist: {:>8} . {:18} proj: {}   ... The error is here prob because it can't encode a list data type in the middle of a string. work with the types. .type print to console if you can't print the list itself.
	# os.environ['GROUPME_TOKEN']   ...   os.environ['SANDBOX_TOKEN']
	message = {
		'text': msg,  
		'bot_id': os.environ['GROUPME_TOKEN'] 
		}
	request = Request(url, urlencode(message).encode())
	json = urlopen(request).read().decode()
	

	# json = requests.post(url, message) # This was tossing epic urllib3.exceptions.ProtocolError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
	# sys.stdout.write('made it to send_message function. This was passed {} << '.format(msg))
	return('ok',200)

def get_franchise_name(franchise):
	if franchise == 1:
		return('Matt & Ross')
	elif franchise == 2:
		return('Scott & James')
	elif franchise == 3:
		return('Doug')
	elif franchise == 4:
		return('Crockett')
	elif franchise == 5:
		return('Blake')
	elif franchise == 6:
		return('Kfish')
	elif franchise == 7:
		return('Kyle')
	elif franchise == 8:
		return('Gaudet & Cameron')
	elif franchise == 9:
		return('RTRO')
	elif franchise == 10:
		return('Mitch')
	elif franchise == 11:
		return('Nick & Mickey')
	elif franchise == 12:
		return('Joseph & Mike')

def get_franchise_number(input):
	# These inputs correspond to groupme ids as of 10/12/18
	if input == '3491271' or input == '7435976':
		return(1)
	elif input == '7435971' or input == '3931770' or input == 2:
		return(2)
	elif input == '7435973' or input == 3:
		return(3)
	elif input == '7435977' or input == 4:
		return(4)
	elif input == '12610331' or input == 5:
		return(5)
	elif input == '7435975' or input == 6:
		return(6)
	elif input == '7435974' or input == 7:
		return(7)
	elif input == '22905' or input == 8:
		return(8)
	elif input == '4747679' or input == '29542085' or input == '3054470' or input == '7435972' or input == 9:
		return(9)
	elif input == '7435969' or input == 10:
		return(10)
	elif input == '3165727' or input == '3159027' or input == 11:
		return(11)
	elif input == '6602218' or input == '55209013' or input == 12:
		return(12)

def text_id_franchise(text):
	if re.search('mattjohn', text, re.I) or re.search('matt john', text, re.I) or re.search('gilhop', text, re.I) or re.search('jordan', text, re.I) or re.search('bob', text, re.I) or re.search('rtro', text, re.I) or re.search('retro', text, re.I):
		return(9, 1)
	elif re.search('matt', text, re.I) or re.search('ross', text, re.I) or re.search('butler', text, re.I):
		return(1, 1)
	elif re.search('scott', text, re.I) or re.search('james', text, re.I) or re.search('choice', text, re.I) or re.search('tpc', text, re.I):
		return(2, 1)
	elif re.search('doug', text, re.I) or re.search('rollin', text, re.I):
		return(3, 1)
	elif re.search('crocket', text, re.I) or re.search('taylor', text, re.I):
		return(4, 1)
	elif re.search('blake', text, re.I):
		return(5, 1)
	elif re.search('kfish', text, re.I) or re.search('kmish', text, re.I) or re.search('kevin', text, re.I) or re.search('fischer', text, re.I):
		return(6, 1)
	elif re.search('kyle', text, re.I) or re.search('dttw', text, re.I) or re.search('douille', text, re.I):
		return(7, 1)
	elif re.search('gaudet', text, re.I) or re.search('cameron', text, re.I) or re.search('john', text, re.I) or re.search('zj', text, re.I):
		return(8, 1)
	elif re.search('mitch', text, re.I):
		return(10, 1)
	elif re.search('nick', text, re.I) or re.search('mickey', text, re.I):
		return(11, 1)
	elif re.search('joseph', text, re.I) or re.search('craig', text, re.I) or re.search('mike', text, re.I):
		return(12, 1)
	else: 
		return('none', 2)







def sandbox_testing(text):
	# Just don't output 'testing' or 'bot' into the sandbox and you're good
	week = database_access('settings', 'week')
	message_to_sandbox(week)
	return('ok',200)

def message_to_sandbox(message):
	# Sent to File Sharing group for testing purposes
	url = 'https://api.groupme.com/v3/bots/post'
	message = {
		'text': message,  
		'bot_id': os.environ['SANDBOX_TOKEN'] 
		}
	request = Request(url, urlencode(message).encode())
	json = urlopen(request).read().decode()

	
	# json = requests.post(url, message)
	return('ok',200)

if __name__ == '__main__':
	app.run()