import os
import json
import sys
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from flask import Flask, request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
import selenium.webdriver.chrome.service as service
import re
import pymysql
from time import sleep

from supporting_fxns import change_week, text_id_franchise, get_franchise_number
from scraper import scrape_scores
from database_interaction import pull_scores

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
	data = request.get_json()
	if '@bot' in data['text']:
		sender = data['user_id']
		text = data['text']
		
		if re.search('score', text, re.I):
			scrape_scores()
			# each of these returns the number of the franchise being requested
			if re.search('my', text, re.I):
				requested_score = get_franchise_number(sender)
			else:
				requested_score = text_id_franchise(text)
			
			message = pull_scores(requested_score)
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
			message = "Get up on outta heeerrrreeee with my eyeholes. I'm the eyehole man"
			send_message(message)
			return('ok',200)

		elif re.search('echo', text, re.I) and sender == '7435972':
			message = text[9:]
			send_message(message)
			return('ok',200)

	else: 
		return('ok',200)





def send_message(msg):
	url = 'https://api.groupme.com/v3/bots/post'
	# os.environ['GROUPME_TOKEN']   ...   os.environ['SANDBOX_TOKEN']
	message = {
		'text': msg,  
		'bot_id': os.environ['GROUPME_TOKEN'] 
		}
	request = Request(url, urlencode(message).encode())
	json = urlopen(request).read().decode()
	
	# sys.stdout.write('made it to send_message function. This was passed {} << '.format(msg))
	return('ok',200)