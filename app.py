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
		scrape_scores()
		return('ok',200)

	else: return('ok',200)

def scrape_scores():
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

	live_scoreboard = '*** Week 1 Live Scoreboard ***\n'
	for i in range(0,12):
			franchise = int(matchups[i])
			# live_scoreboard = live_scoreboard + '{} - {} | proj: {}\n{} - {} | proj: {}\n===== ===== =====\n'.format(scores[i], get_franchise_name(matchups[i]), projected[i])
			# franchise = get_franchise_name(int(matchups[i]))
			# live_scoreboard = live_scoreboard + franchise
			live_scoreboard = live_scoreboard + '{} - {} | proj: {}\n'.format(scores[i], get_franchise_name(franchise), projected[i])
	# message = "franchises: {}, proj: {}, scores: {}".format(len(matchups), len(projected), len(scores))

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