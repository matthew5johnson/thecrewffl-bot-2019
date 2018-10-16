import os
import json
import sys
import requests
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
	if '@bot' in data['text']:
		sender = data['user_id']
		text = data['text']
		sys.stdout.write('sender: {} | text: {}'.format(sender,text))
		parse(sender, text)
	return('ok',200)


def remove_bob():
	global remove_bob_count
	remove_bob_count += 1
	return(remove_bob_count)

def parse(sender, text):
	# First if statement: avoid infinite bot loops
	if re.search('-----   Commands   -----', text, re.I) or re.search("I'm a bot", text) or re.search('my attention by @ing me. Start', text) or re.search("1. '@bot my score' = your ", text) or re.search("2. '@bot all scores' = full live scorebo", text) or re.search("3. '@bot help' for this library of comm", text) or re.search("_commands are case and space insensit", text) or re.search('ot avatar: Yes, that is Mitch attempting a monster d', text) or re.search("ese scores are pulled in real-time. Let's avoi", text) or re.search("We can add pretty much any other features you think of. Next up will be league record book integration. ", text) or re.search('Running vote count in favor of #RB', text): 
		# AVOID responding to the BOT itself (in the help message)
		return('ok',200)
	# Looks for @bot my score command
	elif re.search('my', text, re.I) and re.search('score', text, re.I):
		franchise = get_franchise_number(sender)
		sys.stdout.write('franchise: {} <<'.format(franchise))
		get_data(franchise, 1)
		return('ok',200)
	# Looks for @bot all scores command
	elif re.search('all', text, re.I) and re.search('score', text, re.I):
		franchise = 'none'
		get_data(franchise, 2)
		return('ok',200)

	# Stock responses. Remember to add or statements to the first if test above to exclude bot responses from generating an infinite loop of responses
	# Looks for help command and posts response
	elif re.search('help', text, re.I):
		help_message = "I'm a bot. Get my attention by @ing me.\n** All scores are live (scraped in real-time) **\n-----   Commands   -----\nStart your messages with '@bot'\n1. '@bot my score' = your game's live score\n2. '@bot all scores' = full live scoreboard\n3. '@bot help' for this help message\n _commands are case and space insensitive_\n=====\nMisc.\n=====\nBot avatar: attempted dunk in slamball at EHS.\n \nWe can add pretty much any other features you think of. Next up will be an attempt at league record book integration. Post any other cool ideas that you've got, and we'll add them to the wish list."
		send_message(help_message)
		return('ok',200)
	elif re.search('remove', text, re.I) and re.search('bob', text, re.I):
		remove_bob()
		vote_message = 'Total #RemoveBob votes: {}'.format(remove_bob_count)
		send_message(vote_message)
		return('ok',200)
	else: return('off topic',200)

def get_data(franchise, message_type):
	season = 2018
	week = 6  # This is the only variable that needs to be changed each week
	url = 'http://games.espn.com/ffl/scoreboard?leagueId=133377&matchupPeriodId=%s&seasonId=%s' % (week, season)
	#CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
	#GOOGLE_CHROME_BIN = '/app/.apt/usr/bin/google-chrome'
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
	franchise_number_list = re.findall(r'(?<=tmTotalPts_)[0-9]*', str(soup)) # confirmed: this creates a list
	# sys.stdout.write('first team: {}, second: {} <<< '.format(plug[2], plug[3]))  # This worked perfectly
	points_list = []
	projected_list = []
	for i in franchise_number_list:
		points_list.append(soup.select_one('#tmTotalPts_%s' % (i)).text)
		projected_list.append(soup.select_one('#team_liveproj_%s' % (i)).text)

	if message_type == 1:
		position = franchise_number_list.index(str(franchise))
		franchise_score = points_list[position]
		franchise_proj = projected_list[position]
		if position % 2 == 0:
			opponent_position = position + 1
		else: opponent_position = position - 1

		opponent_franchise = int(franchise_number_list[opponent_position])
		opponent_score = points_list[opponent_position]
		opponent_proj = projected_list[opponent_position]

		# sys.stdout.write('franchise: {} points: {} proj: {} <<<\nopponent: {} points: {} proj: {} <<< '.format(name_identifier(franchise), franchise_score, franchise_proj, name_identifier(opponent_franchise), opponent_score, opponent_proj))

		my_score_message = '{} - {} | proj: {}\n{} - {} | proj: {}'.format(franchise_score, get_franchise_name(franchise), franchise_proj, opponent_score, get_franchise_name(opponent_franchise), opponent_proj)
		# my_final_message = 'this is testing'
		# sys.stdout.write(final_message) # this works perfectly
		send_message(my_score_message)
		return('ok',200)

	elif message_type == 2:
		scoreboard = '*** Live Scoreboard ***\n'
		for i in range(len(franchise_number_list))[0::2]:
			scoreboard = scoreboard + '{} - {} | proj: {}\n{} - {} | proj: {}\n===== ===== =====\n'.format(points_list[i], get_franchise_name(int(franchise_number_list[i])), projected_list[i], points_list[i+1], get_franchise_name(int(franchise_number_list[i+1])), projected_list[i+1])
		send_message(scoreboard)
		return('ok',200)

def send_message(msg):
	url = 'https://api.groupme.com/v3/bots/post'
	message = {
		'text': msg,  ##### Formatting wishlist: {:>8} . {:18} proj: {}   ... The error is here prob because it can't encode a list data type in the middle of a string. work with the types. .type print to console if you can't print the list itself.
		'bot_id': 'ba284f3f9f43fb0ef944c59350' #'eca4646a2e4f736ab96eefa29e'
		}
	json = requests.post(url, message)
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


if __name__ == '__main__':
	app.run()