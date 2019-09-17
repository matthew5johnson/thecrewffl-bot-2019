import os
import json
import sys
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from flask import Flask, request
import re
import pymysql

from supporting_fxns import change_week, text_id_franchise, get_franchise_number, remove_bob, get_franchise_name
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
		elif re.search('my', text, re.I):
			if re.search('score', text, re.I):
				scrape_scores()
				requested_score = get_franchise_number(sender)
				message = pull_scores(requested_score)
				send_message(message)
				return('ok',200)
			elif re.search('mwm', text, re.I) or re.search('maze', text, re.I) or re.search('stage', text, re.I) or re.search('marathon', text, re.I):
				requested_franchise = get_franchise_number(sender)
				insert_franchise = get_franchise_name(requested_franchise)
				message = "The {} franchise has won 0 MWM Stages, and needs 2 to win the Marathon.\n=====\nTo qualify for the 2020 Stage of Maze's Width Marathon:\n1) Win a Semifinal (week 15)\n2) Win the 3rd Place Game (wk 16)\n3) Win the 5th Place Game (wk 16)\n4) Win the Consolation Ladder".format(insert_franchise)
				send_message(message)
				return('ok',200)
			else:
				return('ok',200)

		# Get ordered scores
		elif re.search('score', text, re.I) or re.search('order', text, re.I) or re.search('points', text, re.I) or re.search('live', text, re.I):
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
		elif re.search('board', text, re.I) or re.search('matchup', text, re.I):
			scrape_scores()
			target = "none"
			message = pull_scores(target)
			send_message(message)
			return('ok',200)

		# Get Finch Howe League Cup table
		elif re.search('cup', text, re.I) or re.search('fhlc', text, re.I) or re.search('finch', text, re.I) or re.search('howe', text, re.I):
			message = pull_league_cup_standings() 
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

		elif re.search('details', text, re.I):
			if re.search('playoff', text, re.I):
				message = "Past Playoff Champions:\n'18 - Doug\n'17 - Doug\n'16 - RTRO\n'15 - RTRO\n'14 - ZJs\n'13 - Garner & Doyle\n'12 - Matt & Ross\n'11 - Mitch\n'10 - ZJs\n'09 - ZJs\n'08 - Matt & Ross\n'07 - Matt & Ross"
				send_message(message)
				return('ok',200)
			elif re.search('mwm', text, re.I) or re.search('maze', text, re.I) or re.search('marathon', text, re.I) or re.search('width', text, re.I) or re.search('stage', text, re.I):
				message = "Maze's Width Marathon\n\nwww.kylelogic.com/marathon\nPrize: $300 to $2,400\n-Win the Marathon by winning 2 Stages\n-A Sacko deletes a Stage win\n-Qualification required each Stage"
				send_message(message)
				return('ok',200)
			elif re.search('fhlc', text, re.I) or re.search('cup', text, re.I):
				message = "Finch Howe League Cup\n\nwww.kylelogic.com/leaguecup\nEach week, the top 4 scorers get 3 League Cup Points, the middle 4 scorers get 1 League Cup Point, and the bottom 4 scorers get 0 Cup Points. The franchise with the most League Cup Points at the end of the 13 week regular season will hoist the Finch Howe League Cup."
				send_message(message)
				return('ok',200)
			elif re.search('shield', text, re.I) or re.search('commun', text, re.I):
				message = "Community Shield:\n\nwww.kylelogic.com/communityshield\nThe Community Shield is a one-week head-to-head game during week 3 each season that pits the MWM Stage winner against the League Cup holder. The first Community Shield will take place in 2021"
				send_message(message)
				return('ok',200)
			else:
				return('ok',200)

		elif re.search('shield', text, re.I) or re.search('community', text, re.I):
			message = "Community Shield:\n\nwww.kylelogic.com/communityshield\nThe Community Shield is a one-week head-to-head game during week 3 each season that pits the MWM Stage winner against the League Cup holder. The first Community Shield will take place in 2021"
			send_message(message)
			return('ok',200)

		elif re.search('help', text, re.I) or re.search('command', text, re.I) or re.search('menu', text, re.I) or re.search('summary', text, re.I):
			message = "Commands:\n'@bot my score'\n'@bot -franchise- score'\n'@bot scoreboard'\n'@bot matchups'\n\n== Four Major Competitions ==\n************\n1. Playoff Championship\n************\n'@bot standings'\n'@bot playoff details'\n\n************\n2. Maze's Width Marathon\n************\n'@bot mwm'\n'@bot my mwm'\n'@bot mwm details'\n\n************\n3. Finch Howe League Cup\n************\n'@bot fhlc'\n'@bot league cup'\n'@bot live fhlc'\n'@bot fhlc details'\n\n************\n4. Community Shield\n************\n'@bot community shield'"
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