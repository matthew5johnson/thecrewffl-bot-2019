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

	send_message(projected[0])
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