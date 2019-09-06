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

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
	data = request.get_json()
	if '@bot' in data['text']:
		sender = data['user_id']
		text = data['text']
		if "score" in text:
			target = text_id_franchise(text)
			if "my" in text:
				scrape_scores(1, sender, text)
			elif target != "none":
				scrape_scores(2, target, text)
			else:
				scrape_scores(3, sender, text)
		return('ok',200)

	else: return('ok',200)

def scrape_scores(arg, sender, text):
	website = "https://fantasy.espn.com/football/league/scoreboard?leagueId=133377&weekID=1"
	chrome_options = Options()
	chrome_options.add_argument('--disable-gpu')
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--headless')
	driver = webdriver.Chrome(executable_path=os.environ['CHROMEDRIVER_PATH'], chrome_options=chrome_options)
	driver.get(website)
	sleep(3)
	html = driver.page_source
	soup = BeautifulSoup(html, "lxml")
	driver.close()

	final = str(soup)

	all_franchises = ','.join(re.findall(r'(?<=teamId=)[0-9]*', final))
	franchises = all_franchises.split(",")
	all_projected = ','.join(re.findall(r'(?<=Proj Total:<span class="statusValue fw-bold">)[^<]*', final))
	projected = all_projected.split(",")
	all_scores = ','.join(re.findall(r'(?<=Score h4 clr-gray-01 fw-heavy tar ScoreCell_Score--scoreboard pl2">)[^<]*', final))
	scores = all_scores.split(",")

	matchups = franchises[12::3]

	if arg == 1:
		target = get_franchise_number(sender)
		target_index = matchups.index(str(target))
		my_scoreboard = ""
		if target_index % 2 == 0:
			my_scoreboard = my_scoreboard + '{} - {} | proj: {}\n{} - {} | proj: {}\n'.format(scores[target_index], get_franchise_name(target), projected[target_index], scores[target_index+1], get_franchise_name(int(matchups[target_index+1])), projected[target_index+1])
			send_message(my_scoreboard)
			return('ok',200)
		else:
			my_scoreboard = my_scoreboard + '{} - {} | proj: {}\n{} - {} | proj: {}\n'.format(scores[target_index], get_franchise_name(target), projected[target_index], scores[target_index-1], get_franchise_name(int(matchups[target_index-1])), projected[target_index-1])
			send_message(my_scoreboard)
			return('ok',200)

	elif arg == 2:
		target_index = matchups.index(str(sender))
		their_scoreboard = ""
		if target_index % 2 == 0:
			their_scoreboard = their_scoreboard + '{} - {} | proj: {}\n'.format(scores[target_index], get_franchise_name(sender), projected[target_index], scores[target_index+1], get_franchise_name(int(scores[target_index+1])), projected[target_index+1])
			send_message(their_scoreboard)
			return('ok',200)
		else:
			their_scoreboard = their_scoreboard + '{} - {} | proj: {}\n'.format(scores[target_index], get_franchise_name(target), projected[target_index], scores[target_index-1], get_franchise_name(int(scores[target_index-1])), projected[target_index-1])
			send_message(their_scoreboard)
			return('ok',200)

	elif arg == 3:
		live_scoreboard = '*** Week 1 Live Scoreboard ***\n'
		for i in range(0,12):
				franchise = int(matchups[i])
				live_scoreboard = live_scoreboard + '{} - {} | proj: {}\n'.format(scores[i], get_franchise_name(franchise), projected[i])
				if i == 1 or i == 3 or i == 5 or i == 7 or i == 9:
					live_scoreboard = live_scoreboard + "===== ===== =====\n"
		
		live_scoreboard = live_scoreboard +"-- -- --\nESPN is trash, thus the numerous projected points of 0"

		send_message(live_scoreboard)
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
		return(9)
	elif re.search('matt', text, re.I) or re.search('ross', text, re.I) or re.search('butler', text, re.I):
		return(1)
	elif re.search('scott', text, re.I) or re.search('james', text, re.I) or re.search('choice', text, re.I) or re.search('tpc', text, re.I):
		return(2)
	elif re.search('doug', text, re.I) or re.search('coach o', text, re.I) or re.search('face', text, re.I):
		return(3)
	elif re.search('crocket', text, re.I) or re.search('taylor', text, re.I):
		return(4)
	elif re.search('blake', text, re.I) or re.search('marmalade', text, re.I):
		return(5)
	elif re.search('kfish', text, re.I) or re.search('kmish', text, re.I) or re.search('kevin', text, re.I) or re.search('fischer', text, re.I):
		return(6)
	elif re.search('kyle', text, re.I) or re.search('dttw', text, re.I) or re.search('douille', text, re.I):
		return(7)
	elif re.search('gaudet', text, re.I) or re.search('cameron', text, re.I) or re.search('john', text, re.I) or re.search('zj', text, re.I):
		return(8)
	elif re.search('mitch', text, re.I):
		return(10)
	elif re.search('nick', text, re.I) or re.search('mickey', text, re.I):
		return(11)
	elif re.search('joseph', text, re.I) or re.search('craig', text, re.I) or re.search('mike', text, re.I) or re.search('black', text, re.I) or re.search('trading', text, re.I) or re.search('tbh', text, re.I):
		return(12)
	else: 
		return('none')


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