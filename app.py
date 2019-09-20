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
			print("... bot invoked ...")
			return('ok',200)

		# Get competition detials
		elif re.search('details', text, re.I):
			print("USER requested details")

			if re.search('playoff', text, re.I):
				message = "History of Playoff Champions:\nwww.kylelogic.com/playoffs\n\n'18 - Doug\n'17 - Doug\n'16 - RTRO\n'15 - RTRO\n'14 - ZJs\n'13 - Garner & Doyle\n'12 - Matt & Ross\n'11 - Mitch\n'10 - ZJs\n'09 - ZJs\n'08 - Matt & Ross\n'07 - Matt & Ross"
				send_message(message)
				return('ok',200)
			elif re.search('mwm', text, re.I) or re.search('maze', text, re.I) or re.search('marathon', text, re.I) or re.search('width', text, re.I) or re.search('stage', text, re.I):
				message = "Maze's Width Marathon\nwww.kylelogic.com/marathon\n\nPrize: $300 to $2,400\n-Win the Marathon by winning 2 Stages\n-A Sacko deletes a Stage win\n-Must qualify for Stage\n-Stage winner qualifies for next Community Shield\n\nHistory of Stage Winners:\n'20 - "
				send_message(message)
				return('ok',200)
			elif re.search('fhlc', text, re.I) or re.search('cup', text, re.I):
				message = "Finch Howe League Cup\nwww.kylelogic.com/leaguecup\n\nEach week the top 4 scorers get 3 League Cup Points, the middle 4 scorers get 1 League Cup Point, and the bottom 4 scorers get 0 Cup Points. The franchise with the most League Cup Points at the end of the 13 week regular season will hoist the Finch Howe League Cup and qualify for the next Community Shield.\n\nHistory of League Cups:\n'19 - "
				send_message(message)
				return('ok',200)
			elif re.search('shield', text, re.I) or re.search('commun', text, re.I):
				message = "Community Shield:\nwww.kylelogic.com/communityshield\n\nThe Community Shield is a head-to-head game during week 3 each season that pits the MWM Stage winner against the League Cup holder. The first Community Shield will take place between this year's Playoff Champion and Finch Howe League Cup holder\n\nHistory of Community Shields:\n'21 - "
				send_message(message)
				return('ok',200)
			else:
				return('ok',200)
		
		# Get my score and my MWM
		elif re.search('my', text, re.I):
			if re.search('score', text, re.I):
				print("USER requested 'my score'")
				
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

		# Get scoreboard
		elif re.search('board', text, re.I) or re.search('matchup', text, re.I):
			print("USER requested 'scoreboard'")
			
			scrape_scores()
			target = "none"
			message = pull_scores(target)
			send_message(message)
			return('ok',200)

		# Get ordered scores
		elif re.search('score', text, re.I) or re.search('order', text, re.I) or re.search('points', text, re.I) or re.search('live', text, re.I):
			print("USER requested scores")

			scrape_scores()
			requested_score = text_id_franchise(text)
			# if a specific franchise's score is being asked for
			if requested_score != "none":
				print("USER requested a specific franchise score")
				message = pull_scores(requested_score)
				send_message(message)
				return('ok',200)
			else:
				print("USER requested ordered scores")
				
				message = ordered_scores()
				send_message(message)
				return('ok',200)

		# Get Finch Howe League Cup table
		elif re.search('cup', text, re.I) or re.search('fhlc', text, re.I) or re.search('finch', text, re.I) or re.search('howe', text, re.I):
			print("USER requested FHLC")
			
			message = pull_league_cup_standings() 
			send_message(message)
			return('ok',200)

		# Get Playoff Standings
		elif re.search('standing', text, re.I) or re.search('rank', text, re.I) or re.search('playoff', text, re.I):
			print("USER requested standings")

			scrape_scores()
			message = pull_live_standings()
			send_message(message)
			return('ok',200)

		# Get Maze's Width Marathon
		elif re.search('mwm', text, re.I) or re.search('maze', text, re.I) or re.search('width', text, re.I) or re.search('marathon', text, re.I) or re.search('stage', text, re.I):
			print("USER requested mwm")
			
			message = "To qualify for the 2020 MWM Stage:\n1) Win a Semifinal game in week 15\n2) Win the 3rd Place Game in week 16\n3) Win the 5th Place Game in week 16\n4) Win the Consolation Ladder\n\n'@bot mwm details' for more"
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

		elif re.search('shield', text, re.I) or re.search('community', text, re.I):
			message = "Community Shield:\nwww.kylelogic.com/communityshield\n\nThe Community Shield is a head-to-head game during week 3 each season that pits the MWM Stage winner against the League Cup holder. The first Community Shield will take place between this year's Playoff Champion and Finch Howe League Cup holder"
			send_message(message)
			return('ok',200)

		elif re.search('help', text, re.I) or re.search('commands', text, re.I) or re.search('menu', text, re.I) or re.search('summary', text, re.I):
			message = "Commands:\n'@bot my score'\n'@bot -franchise- score'\n'@bot scoreboard'\n'@bot matchups'\n'@bot scores'\n\n== Four Major Competitions ==\nwww.kylelogic.com/competitions\n\n1. Playoff Championship\nwww.kylelogic.com/playoffs\n'@bot standings'\n'@bot playoff details'\n\n2. Maze's Width Marathon\nwww.kylelogic.com/marathon\n'@bot mwm'\n'@bot my mwm'\n'@bot mwm details'\n\n3. Finch Howe League Cup\nwww.kylelogic.com/leaguecup\n'@bot fhlc'\n'@bot live fhlc'\n'@bot fhlc details'\n\n4. Community Shield\nwww.kylelogic.com/communityshield\n'@bot community shield details'"
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
		'bot_id': os.environ['SANDBOx_TOKEN'] 
		}
	request = Request(url, urlencode(message).encode())
	json = urlopen(request).read().decode()
	
	# sys.stdout.write('made it to send_message function. This was passed {} << '.format(msg))
	return('ok',200)