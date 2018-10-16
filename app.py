import os
import json
import sys
# import requests
# requests==2.19.1
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from flask import Flask, request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
import selenium.webdriver.chrome.service as service
import re

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

###### Global variables
## Remove Bob vote count
rb_votes = 0
## Week
week = 6


def parse(sender, text):
	#### Ignore every line that the bot prints out itself
	if re.search('-----   Commands   -----', text, re.I) or re.search("I'm a bot", text) or re.search('my attention by @ing me. Start', text) or re.search("1. '@bot my score' = your ", text) or re.search("2. '@bot all scores' = full live scorebo", text) or re.search("3. '@bot help' for this library of comm", text) or re.search("_commands are case and space insensit", text) or re.search('ot avatar: Yes, that is Mitch attempting a monster d', text) or re.search("ese scores are pulled in real-time. Let's avoi", text) or re.search("We can add pretty much any other features you think of. Next up will be league record book integration. ", text) or re.search('Total #RB votes', text) or re.search('Week has been set to', text): 
		# AVOID responding to the BOT itself (in the help message)
		return('ok',200)
	
	# 1   ...   @bot my score 
	elif re.search('my', text, re.I) and re.search('score', text, re.I):
		franchise = get_franchise_number(sender)
		# sys.stdout.write('franchise: {} <<'.format(franchise))
		get_data(franchise, 1)
		return('ok',200)
	
	# 2   ...   @bot all scores
	elif re.search('all', text, re.I) and re.search('score', text, re.I):
		franchise = 'none'
		get_data(franchise, 2)
		return('ok',200)

	#### Stock responses. ** Remember to add or statements to the first if test above to exclude bot responses from generating an infinite loop of responses
	
	# help   ...   and posts response
	elif re.search('help', text, re.I):
		help_message = "I'm a bot. Get my attention by @ing me.\n** All scores are live (scraped in real-time) **\n-----   Commands   -----\nStart your messages with '@bot'\n1. '@bot my score' = your game's live score\n2. '@bot all scores' = full live scoreboard\n3. '@bot help' for this help message\n _commands are case and space insensitive_\n=====\nWe can add pretty much any other features you think of. Next up will be an attempt at league record book integration. Post any other cool ideas that you've got, and we'll add them to the wish list."
		send_message(help_message)
		return('ok',200)
	#    ...   @bot remove bob   ...   and posts vote tally
	elif re.search('remove', text, re.I) and re.search('bob', text, re.I):
		global rb_votes
		rb_votes += 1
		vote_message = 'Total #RB votes: {}'.format(rb_votes)
		send_message(vote_message)
		return(rb_votes)
	
	##### Settings from within the groupme
	# Set the week. Can only be done when '@bot advance week' is sent by me
	# elif re.search('Advance week', text, re.I) and sender == '7435972':
	# 	global week 
	# 	week += 1
	# 	settings_message = 'Week has been set to {}'.format(week)
	# 	send_message(settings_message)
	# 	return(week)
	else: return('off topic',200)

def get_data(franchise, message_type):
	season = 2018
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


def send_message(msg):
	url = 'https://api.groupme.com/v3/bots/post'
	##### Formatting wishlist: {:>8} . {:18} proj: {}   ... The error is here prob because it can't encode a list data type in the middle of a string. work with the types. .type print to console if you can't print the list itself.
	message = {
		'text': msg,  
		'bot_id': os.environ['SANDBOX_TOKEN'] 
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
	# These inputs correspond to groupme nicknames as of 10/12/18
	if input == '3491271' or input == '7435976' or input == 1:
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







def sandbox_testing(text):
	# Just don't output 'testing' or 'bot' into the sandbox and you're good
	say = 'Votes to #RemoveBob:'
	message_to_sandbox(say)
	return('ok',200)

def message_to_sandbox(message):
	# Sent to File Sharing group for testing purposes
	url = 'https://api.groupme.com/v3/bots/post'
	message = {
		'text': message, 
		'bot_id': 'token'   
		}
	message['bot_id'] = os.environ['SANDBOX_TOKEN']
	json = requests.post(url, message)
	return('ok',200)

if __name__ == '__main__':
	app.run()