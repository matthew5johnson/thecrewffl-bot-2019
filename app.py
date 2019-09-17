import os
import json
import sys
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from flask import Flask, request
import re
import pymysql

from supporting_fxns import change_week, text_id_franchise, get_franchise_number, remove_bob
from scraper import scrape_scores
from database_interaction import pull_scores, pull_live_standings, pull_league_cup_standings, ordered_scores

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
	data = request.get_json()
	if '@bot' in data['text']:
		sender = data['user_id']
		text = data['text']
		
		# Ignore the '@bot' instructions in the help/command message
		if re.search("'@bot", text, re.I):
			return('ok',200)
		
		# Get my score and my MWM
		if re.search('my', text, re.I):
			if re.search('score', text, re.I):
				scrape_scores()
				requested_score = get_franchise_number(sender)
				message = pull_scores(requested_score)
				send_message(message)
				return('ok',200)
			elif re.search('mwm', text, re.I) or re.search('maze', text, re.I) or re.search('stage', text, re.I) or re.search('marathon', text, re.I):
				requested_franchise = get_franchise_number(sender)
				message = "{} has won 0 MWM Stages, and needs 2 to win the Marathon.\n=====\nTo qualify for the 2020 Stage of Maze's Width Marathon:\n1) Win a Semifinal (week 15)\n2) Win the 3rd Place Game (week 16)\n3) Win the 5th Place Game (week 16)\n4) Win the Consolation Ladder Championship (week 16)".format(requested_franchise)
				send_message(message)
				return('ok',200)
			else:
				return('ok',200)

		# Get ordered scores
		elif re.search('score', text, re.I) or re.search('order', text, re.I) or re.search('points', text, re.I) or re.search('live'):
			scrape_scores()
			requested_score = text_id_franchise(text)
			# if a specific franchise's score is being asked for
			if requested_score != "none":
				message = pull_scores(requested_score)
				return('ok',200)
			else:
				message = ordered_scores()
				send_message(message)
				return('ok',200)

		# Get scoreboard
		elif re.search('board', text, re.I) or ('matchup', text, re.I):
			scrape_scores()
			target = "none"
			message = pull_scores(target)
			send_message(message)

		# Get Finch Howe League Cup table
		elif re.search('cup', text, re.I) or re.search('fhlc', text, re.I) or re.search('finch', text, re.I) or re.search('howe', text, re.I):
			message = pull_league_cup_standings() +"\n\n'@bot scores' or '@bot fhlc live' for live ordered scores" 
			send_message(message)
			return('ok',200)

		# Get Playoff Standings
		elif re.search('standing', text, re.I) or re.search('rank', text, re.I):
			scrape_scores()
			message = pull_live_standings()
			send_message(message)
			return('ok',200)

		# Get Maze's Width Marathon
		elif re.search('mwm', text, re.I) or re.search('maze', text, re.I) or re.search('width', text, re.I) or re.search('marathon', text, re.I) or re.search('stage', text, re.I):
			message = "To qualify for the 2020 MWM Stage:\n1) Win a Semifinal game in week 15\n2) Win the 3rd Place Game in week 16\n3) Win the 5th Place Game in week 16\n4) Win the Consolation Ladder"
			send_message(message)
			return('ok',200)
			

		elif re.search('next week', text, re.I) and sender == '7435972':
			settings_message = change_week('next')
			send_message(settings_message)
			return('ok',200)
		elif re.search('last week', text, re.I) and sender == '7435972':
			settings_message = change_week('last')
			send_message(settings_message)
			return('ok',200)
		elif re.search('next week', text, re.I) or re.search('last week', text, re.I):
			message = "Get up on outta here with my eyeholes. I'm the eyehole man"
			send_message(message)
			return('ok',200)


		elif re.search('remove', text, re.I) or re.search('#rb', text, re.I):
			message = remove_bob()
			send_message(message)
			return('ok',200)


		elif re.search('echo', text, re.I) and sender == '7435972':
			message = text[10:]
			send_message(message)
			return('ok',200)

		
		elif re.search('help', text, re.I) or re.search('command', text, re.I) or re.search('menu', text, re.I) or re.search('summary', text, re.I):
			message = "Available Commands:\n(typed commands don't need to be exact)\n\n'@bot my score'\n'@bot -franchise- score'\n'@bot scoreboard' or '@bot matchups'\n\n== Competitions ==\n'@bot standings'\nfor Playoff Standings\n\n'@bot mwm' or '@bot marathon'\nfor Maze's Width Marathon\n\n@bot league cup' or '@bot fhlc' or '@bot finch'\nfor Finch Howe League Cup table\n\n'@bot shield' or '@bot community shield'\nfor Community Shield"
			send_message(message)
			return('ok',200)

		else:
			return('ok',200)


	else: 
		return('ok',200)





def send_message(msg):
	url = 'https://api.groupme.com/v3/bots/post'
	# os.environ['GROUPME_TOKEN']   ...   os.environ['SANDBOX_TOKEN']
	message = {
		'text': msg,  
		'bot_id': os.environ['SANDBOX_TOKEN'] 
		}
	request = Request(url, urlencode(message).encode())
	json = urlopen(request).read().decode()
	
	# sys.stdout.write('made it to send_message function. This was passed {} << '.format(msg))
	return('ok',200)