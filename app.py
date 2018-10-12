import os
import json

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, request

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
import selenium.webdriver.chrome.service as service

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
	data = request.get_json()
	if data['text'] == 'test':
		team = 1
		season = 2018
		week = 6
		url = 'http://games.espn.com/ffl/scoreboard?leagueId=133377&matchupPeriodId=%s&seasonId=%s' % (week, season)
		CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
		GOOGLE_CHROME_BIN = '/app/.apt/usr/bin/google-chrome'
		chrome_options = Options()
		chrome_options.binary_location = GOOGLE_CHROME_BIN
		chrome_options.add_argument('--disable-gpu')
		chrome_options.add_argument('--no-sandbox')
		driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
		driver.get(url)
		html = driver.page_source

		soup = BeautifulSoup(html, "lxml")

		points = soup.select_one('#tmTotalPts_1').text
		# points = 'this is how we do it'


		send_message(points)

	else:
		msg = 'insert message here'
		second_message(msg)


		# ytp = '#team_ytp_%s' % (team)
		# pts = '#tmTotalPts_%s' % (team)
		# proj = '#team_liveproj_%s' % (team)
		
		
		# send_message(points)


	return "ok", 200

def send_message(points):
	url = 'https://api.groupme.com/v3/bots/'
	data = {'text': 'remaining: {}'.format(points), 'bot_id': "eca4646a2e4f736ab96eefa29e"}
	request = Request(url, urlencode(data).encode())
	json = urlopen(request).read().decode()
def second_message(msg):
	url = 'https://api.groupme.com/v3/bots/'
	data = {'text': 'hey now {}'.format(msg), 'bot_id': "eca4646a2e4f736ab96eefa29e"}
	request = Request(url, urlencode(data).encode())
	json = urlopen(request).read().decode()

if __name__ == '__main__':
	app.run(debug=True)


