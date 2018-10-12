import os
import json
import sys

# from urllib.parse import urlencode
# from urllib.request import Request, urlopen

import requests


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
		team = 6
		season = 2018
		week = 6
		url = 'http://games.espn.com/ffl/scoreboard?leagueId=133377&matchupPeriodId=%s&seasonId=%s' % (week, season)
		CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
		GOOGLE_CHROME_BIN = '/app/.apt/usr/bin/google-chrome'
		chrome_options = Options()
		chrome_options.binary_location = GOOGLE_CHROME_BIN
		chrome_options.add_argument('--disable-gpu')
		chrome_options.add_argument('--no-sandbox')
		chrome_options.add_argument('--headless')
		driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
		driver.get(url)
		html = driver.page_source

		soup = BeautifulSoup(html, "lxml")

		franchise = 'Kfish'
		ytp = '#team_ytp_%s' % (team)
		pts = '#tmTotalPts_%s' % team
		proj = '#team_liveproj_%s' % (team)
		
		players_remaining = soup.select_one(ytp).text
		points = soup.select_one(pts).text
		projected = soup.select_one(proj).text

		# Puts this message into heroku logs (live updates with heroku logs --tail)
		sys.stdout.write('{} - {} | (proj: {})'.format(franchise, points, projected))
		
		msg = '{} - {} | (proj: {})'.format(franchise, points, projected) 
		send_message(msg)

	return "ok", 200


def send_message(msg):
	url = 'https://api.groupme.com/v3/bots/post'
	message = {
		'text': msg,
		'bot_id': "eca4646a2e4f736ab96eefa29e",
		'avatar_url': 'http://thecrewffl.weebly.com/uploads/5/1/9/0/51900477/the-dunk_orig.png'
		}
	json = requests.post(url, message)

	sys.stdout.write('made it to send_message function. This was passed {} << '.format(msg))



if __name__ == '__main__':
	app.run()


