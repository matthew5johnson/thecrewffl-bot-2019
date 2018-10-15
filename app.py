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
		#parse(data)
		# sys.stdout.write(data['nickname']) # Nickname doesn't work. text and user_id do work
		# sys.stdout.write(data['text'])
		# sys.stdout.write(data['user_id'])
		sender = data['user_id']
		text = data['text']
		sys.stdout.write('sender: {} | text: {}'.format(sender,text))
		parse(sender, text)
		return('ok',200)
	else: return('not related',200)

def parse(sender, text):
	# First if statement: avoid infinite bot loops
	if re.search('-----   Commands   -----', text, re.I) or re.search('my attention by @ing me. Start', text) or re.search("1. '@bot my score' = your ", text) or re.search("2. '@bot all scores' = full live scorebo", text) or re.search("3. '@bot help' for this library of comm", text) or re.search("_commands are case and space insensit", text) or re.search('ot avatar: Yes, that is Mitch attempting a monster d', text) or re.search("ese scores are pulled in real-time. Let's avoi", text) or re.search("We can add pretty much any other features you think of. Next up will be league record book integration. ", text): 
		# AVOID responding to the BOT itself (in the help message)
		return('ok',200)
	elif re.search('my', text, re.I) and re.search('score', text, re.I):
		franchise = franchise_identifier(sender)
		sys.stdout.write('franchise: {} <<'.format(franchise))
		get_data(franchise, 1)
		return('ok',200)
	elif re.search('all', text, re.I) and re.search('score', text, re.I):
		franchise = 'none'
		get_data(franchise, 2)
		return('ok',200)

	# Stock responses. Remember to add or statements to the first if test above to exclude bot responses from generating an infinite loop of responses
	elif re.search('help', text, re.I):
		help_message = "-----   Commands   -----\nGet my attention by @ing me. Start your messages with '@bot'\n1. '@bot my score' = your game's live score\n2. '@bot all scores' = full live scoreboard\n3. '@bot help' for this library of commands\n _commands are case and space insensitive_\n=====\n Bot avatar: Yes, that is Mitch attempting a monster dunk in slamball.\n=====\n   ** These scores are pulled in real-time. Let's avoid spamming the bot since we've got this thing on a free server **\n \nWe can add pretty much any other features you think of. Next up will be league record book integration. Post any other cool ideas that you think of, and we'll add them to the wish list."
		send_message(help_message)


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

	# franchise = 'Kfish'
	# ytp = '#team_ytp_%s' % (team)
	# pts = '#tmTotalPts_%s' % team
	# proj = '#team_liveproj_%s' % (team)
	
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

		my_final_message = '{} . {} | proj: {}\n{} . {} | proj: {}'.format(franchise_score, name_identifier(franchise), franchise_proj, opponent_score, name_identifier(opponent_franchise), opponent_proj)

		# sys.stdout.write(final_message) # this works perfectly

		send_message(my_final_message)
		return('ok',200)

	elif message_type == 2:
		for i in franchise_number_list[0::2]:
			matchup_message = '{} . {} | proj: {}\n{} . {} | proj: {}'.format(points_list[i], name_identifier(franchise_number_list[i]), projected_list[i], points_list[i+1], name_identifier(franchise_number_list[i+1]), projected_list[i+1])
			send_message(matchup_message)
			sys.stdout.write(matchup_message)
			return('ok',200)
		# scoreboard = {}
		# for team in franchise_number_list:
		# 	index = franchise_number_list.index(str(team))
		# 	scoreboard[index] = []
		# 	scoreboard[index].append(points_list[index])
		# 	scoreboard[index].append(name_identifier(int(team)))
		# 	scoreboard[index].append(projected_list[index])

		# # all_final_message = '{} . {} | proj: {}\n{} . {} | proj: {}\n=================\n{} . {} | proj: {}\n{} . {} | proj: {}\n=================\n{} . {} | proj: {}\n{} . {} | proj: {}\n=================\n{} . {} | proj: {}\n{} . {} | proj: {}\n=================\n{} . {} | proj: {}\n{} . {} | proj: {}\n=================\n{} . {} | proj: {}\n{} . {} | proj: {}'.format(scoreboard[0][0], scoreboard[0][1], scoreboard[0][2], scoreboard[1][0], scoreboard[1][1], scoreboard[1][2], scoreboard[2][0], scoreboard[2][1], scoreboard[2][2], scoreboard[3][0], scoreboard[3][1], scoreboard[3][2], scoreboard[4][0], scoreboard[4][1], scoreboard[4][2], scoreboard[5][0], scoreboard[5][1], scoreboard[5][2]) 	
		# sys.stdout.write(scoreboard[0][0])
		
		# # send_message(all_final_message)
		 

		return('ok',200)

	# if franchise == matchup_A[0] or franchise == matchup_A[1]:
	# 	points_A1 = soup.select_one('tmTotalPts_%s' % matchup_A[0]).text
	# 	proj_A1 = soup.select_one('team_liveproj_%s' % matchup_A[0]).text
	# 	points_A2 = soup.select_one('tmTotalPts_%s' % matchup_A[1]).text
	# 	proj_A2 = soup.select_one('team_liveproj_%s' % matchup_A[1]).text
	# 	message = 

	### This is the spot where urllib3 is throwin a connection error
	# # Separating the franchise numbers into their own matchups
	# matchup_A = [plug[0], plug[1]]
	# matchup_B = [plug[2], plug[3]]  # <<< The error was thrown with unit testing here
	# matchup_C = [plug[4], plug[5]]
	# matchup_D = [plug[6], plug[7]]
	# matchup_E = [plug[8], plug[9]]
	# matchup_F = [plug[10], plug[11]] # Comment this matchup out for week 14
	# sys.stdout.write('team 1 in matchup B; {} -- team 2 in matchup b; {}'.format(matchup_B[0], matchup_B[1]))
	# score_A_tm_1 = soup.select_one('tmTotalPts_%s' % plug[0]).text
	# score_A_tm_2 = soup.select_one('tmTotalPts_%s' % plug[1]).text
	# score_B_tm_1 = soup.select_one('tmTotalPts_%s' % plug[2]).text
	# score_B_tm_2 = soup.select_one('tmTotalPts_%s' % plug[3]).text
	# score_C_tm_1 = soup.select_one('tmTotalPts_%s' % plug[4]).text
	# score_C_tm_2 = soup.select_one('tmTotalPts_%s' % plug[5]).text
	# score_D_tm_1 = soup.select_one('tmTotalPts_%s' % plug[6]).text
	# score_D_tm_2 = soup.select_one('tmTotalPts_%s' % plug[7]).text
	# score_E_tm_1= soup.select_one('tmTotalPts_%s' % plug[8]).text
	# score_E_tm_2 = soup.select_one('tmTotalPts_%s' % plug[9]).text
	# score_F_tm_1 = soup.select_one('tmTotalPts_%s' % plug[10]).text # Comment this matchup out for wk 14
	# score_F_tm_2 = soup.select_one('tmTotalPts_%s' % plug[11]).text # COmment this matchup out for wk 14

	# proj_A_tm_1 = soup.select_one('team_liveproj_%s' % plug[0]).text
	# proj_A_tm_2 = soup.select_one('team_liveproj_%s' % plug[1]).text
	# proj_B_tm_1 = soup.select_one('team_liveproj_%s' % plug[2]).text
	# proj_B_tm_2 = soup.select_one('team_liveproj_%s' % plug[3]).text
	# proj_C_tm_1 = soup.select_one('team_liveproj_%s' % plug[4]).text
	# proj_C_tm_2 = soup.select_one('team_liveproj_%s' % plug[5]).text
	# proj_D_tm_1 = soup.select_one('team_liveproj_%s' % plug[6]).text
	# proj_D_tm_2 = soup.select_one('team_liveproj_%s' % plug[7]).text
	# proj_E_tm_1 = soup.select_one('team_liveproj_%s' % plug[8]).text
	# proj_E_tm_2 = soup.select_one('team_liveproj_%s' % plug[9]).text
	# proj_F_tm_1 = soup.select_one('team_liveproj_%s' % plug[10]).text # Comment this matchup out for wk 14
	# proj_F_tm_2 = soup.select_one('team_liveproj_%s' % plug[11]).text # COmment this matchup out for wk 14

	# if franchise == matchup_A[0] or franchise == matchup_A[1]:
	# 	message = '{:<18}- {:6} | proj: {}\n{:<18}- {:6} | proj: {}'.format(name_identifier(matchup_A[0]), score_A_tm_1, proj_A_tm_1, name_identifier(matchup_A[1]), score_A_tm_2, proj_A_tm_2)
	# 	sys.stdout.write(message)
	# 	return('ok',200)	
	# elif franchise == matchup_B[0] or franchise == matchup_B[1]:
	# 	message = '{:<18}- {:6} | proj: {}\n{:<18}- {:6} | proj: {}'.format(name_identifier(matchup_B[0]), score_B_tm_1, proj_B_tm_1, name_identifier(matchup_B[1]), score_B_tm_2, proj_B_tm_2)
	# 	return('ok',200)
	# elif franchise == matchup_C[0] or franchise == matchup_C[1]:
	# 	message = '{:<18}- {:6} | proj: {}\n{:<18}- {:6} | proj: {}'.format(name_identifier(matchup_C[0]), score_C_tm_1, proj_C_tm_1, name_identifier(matchup_C[1]), score_C_tm_2, proj_C_tm_2)
	# 	return('ok',200)	
	# elif franchise == matchup_D[0] or franchise == matchup_D[1]:
	# 	message = '{:<18}- {:6} | proj: {}\n{:<18}- {:6} | proj: {}'.format(name_identifier(matchup_D[0]), score_D_tm_1, proj_D_tm_1, name_identifier(matchup_D[1]), score_D_tm_2, proj_D_tm_2)
	# 	return('ok',200)
	# elif franchise == matchup_E[0] or franchise == matchup_E[1]:
	# 	message = '{:<18}- {:6} | proj: {}\n{:<18}- {:6} | proj: {}'.format(name_identifier(matchup_E[0]), score_E_tm_1, proj_E_tm_1, name_identifier(matchup_E[1]), score_E_tm_2, proj_E_tm_2)
	# 	return('ok',200)
	# elif franchise == matchup_F[0] or franchise == matchup_F[1]:
	# 	message = '{:<18}- {:6} | proj: {}\n{:<18}- {:6} | proj: {}'.format(name_identifier(matchup_F[0]), score_F_tm_1, proj_F_tm_1, name_identifier(matchup_F[1]), score_F_tm_2, proj_F_tm_2)
	# 	return('ok',200)
	# else: return('none')



	# sys.stdout.write('matchup A: {} <<<'.format(matchup_A))
	# sys.stdout.write('matchupA[0]: {} <<<'.format(matchup_A[0]))
	# string_form = 'nothing'
	# for x in points:
	# 	string_form = '{}, {}'.format(string_form, stringpoints[x])

	# players_remaining = soup.select_one(ytp).text
	# points = soup.select_one(pts).text
	# projected = soup.select_one(proj).text

	# Puts this message into heroku logs (live updates with heroku logs --tail)
	# sys.stdout.write('{} - {} | (proj: {})'.format(franchise, points, projected))
	# All of these are getting IndexError: list index out of range
	# sys.stdout.write('plug[0]: {} <<<'.format(plug[0]))
	
	# msg = '{} - {} | (proj: {})'.format(franchise, points, projected) 
	# message = 'simple test'
	# send_message(message)

	return('ok',200)


def send_message(msg):
	url = 'https://api.groupme.com/v3/bots/post'
	message = {
		'text': msg,  ##### The error is here prob because it can't encode a list data type in the middle of a string. work with the types. .type print to console if you can't print the list itself
		'bot_id': 'eca4646a2e4f736ab96eefa29e'
		}
	json = requests.post(url, message)

	# sys.stdout.write('made it to send_message function. This was passed {} << '.format(msg))

def name_identifier(franchise):
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


def franchise_identifier(input):
	# These inputs correspond to groupme nicknames as of 10/12/18
	if input == 'Matt Lewis' or input == 'Ross Wafer' or input == 1:
		return(1)
	elif input == 'Scott Becker' or input == 'James Roeling' or input == 2:
		return(2)
	elif input == 'Doug Ramey, League Champion' or input == 3:
		return(3)
	elif input == 'Taylor Crockett' or input == 4:
		return(4)
	elif input == 'Blake Tellarico' or input == 5:
		return(5)
	elif input == 'Kevin Fischer' or input == 6:
		return(6)
	elif input == 'Kyle Evers' or input == 7:
		return(7)
	elif input == 'John Gaudet' or input == 8:
		return(8)
	elif input == 'Bob' or input == 'Jordan Redmon' or input == 'Kevin Pohlig' or input == '7435972' or input == 9:
		return(9)
	elif input == 'Mitch Tellarico' or input == 10:
		return(10)
	elif input == 'Nicholas Hart' or input == 'Monster' or input == 11:
		return(11)
	elif input == 'Mike Evers' or input == 'Joseph Howe 2' or input == 12:
		return(12)


def franchise_namer(number):
	if number == 1:
		return('Matt & Ross')
	elif number == 2: 
		return('Scott & James')
	elif number == 3:
		return('Doug')
	elif number == 4:
		return('Crockett')
	elif number == 5:
		return('Blake')
	elif number == 6:
		return('Kfish')
	elif number == 7:
		return('Kyle')
	elif number == 8:
		return('Gaudet & Cameron')
	elif number == 9:
		return('RTRO')
	elif number == 10:
		return('Mitch')
	elif number == 11:
		return('Nick & Mickey')
	elif number == 12:
		return('Joseph & Mike')



if __name__ == '__main__':
	app.run()