import os
import json

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, request

# Worked before adding these 2
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium.webdriver.chrome.service as service


app = Flask(__name__)



@app.route('/', methods=['POST'])
def webhook():
	data = request.get_json()

	# We don't want to reply to ourselves
	# if data['name'] != 'bot':
	# 	msg = 'hello world: user: {} data: {}'.format(data['name'], data['text'])
	# 	send_message(msg)

	if data['text'] == 'my':		
		week = 5
		season = 2018
		scoreboard_url = 'http://games.espn.com/ffl/scoreboard?leagueId=133377&matchupPeriodId=%s&seasonId=%s' % (week, season)
		
		service = service.Service('/app/.apt/usr/bin/chromedriver') #path to driver
		service.start()
		capabilities = {'chrome.binary': '/app/.apt/usr/bin/google-chrome'} #path to chrome
		driver = webdriver.Remote(service.service_url, capabilities)
		driver.get(scoreboard_url)
		html = driver.page_source
		soup = BeautifulSoup(html, "lxml")
		driver.quit()

		points = soup.select_one('#tmTotalPts_1')


		msg = 'here is your games score'
		
		send_message(points)


	return "ok", 200


def send_message(points):
	url = 'https://api.groupme.com/v3/bots/'
	data = {'text': points, 'bot_id': "eca4646a2e4f736ab96eefa29e"}
	request = Request(url, urlencode(data).encode())
	json = urlopen(request).read().decode()