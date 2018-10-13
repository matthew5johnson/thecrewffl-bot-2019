import os
import json
import sys
import requests
from flask import Flask, request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
import selenium.webdriver.chrome.service as service

import re

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
	data = request.get_json()
	if '@bot' in data['text']:
		#parse(data)
		# sys.stdout.write(data['nickname']) # Nickname doesn't work. text and user_id do work
		# sys.stdout.write(data['text'])
		# sys.stdout.write(data['user_id'])
		sender = data['user_id']
		text = data['text']
		sys.stdout.write('sender: {} | text: {}'.format(sender,text))
		parse(sender, text)
		return('ok',200)
	else: return('not related',200)

def parse(sender, text):
	if re.search('my', text, re.I) and re.search('score', text, re.I):
		franchise = franchise_identifier(sender)
		sys.stdout.write('franchise: {}'.format(franchise))
		get_data(franchise)
		return('ok',200)


def get_data(franchise):
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
	chrome_options.add_argument('--headless')
	driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
	driver.get(url)
	html = driver.page_source
	driver.close()
	soup = BeautifulSoup(html, "lxml")

	# franchise = 'Kfish'
	# ytp = '#team_ytp_%s' % (team)
	# pts = '#tmTotalPts_%s' % team
	# proj = '#team_liveproj_%s' % (team)
	
	plug = re.findall(r'#tmTotalPts_[0-9]*', str(soup))
	points = []
	for i in plug:
		points = points.append(soup.select_one(i).text)

	# string_form = 'nothing'
	# for x in points:
	# 	string_form = '{}, {}'.format(string_form, stringpoints[x])

	# players_remaining = soup.select_one(ytp).text
	# points = soup.select_one(pts).text
	# projected = soup.select_one(proj).text

	# Puts this message into heroku logs (live updates with heroku logs --tail)
	# sys.stdout.write('{} - {} | (proj: {})'.format(franchise, points, projected))
	# All of these are getting IndexError: list index out of range
	# sys.stdout.write('points: {} <<<'.format(points[1]))
	# sys.stdout.write('points: {} <<<'.format(points[2]))
	# sys.stdout.write('points: {} <<<'.format(points[3]))
	# sys.stdout.write('points: {} <<<'.format(points[4]))
	# sys.stdout.write('points: {} <<<'.format(points[5]))
	# sys.stdout.write('points: {} <<<'.format(points[6]))
	# sys.stdout.write('points: {} <<<'.format(points[7]))
	# sys.stdout.write('points: {} <<<'.format(points[8]))
	# sys.stdout.write('points: {} <<<'.format(points[9]))
	# sys.stdout.write('points: {} <<<'.format(points[10]))
	# sys.stdout.write('points: {} <<<'.format(points[11]))

	# msg = '{} - {} | (proj: {})'.format(franchise, points, projected) 
	send_message(points)

	return('ok',200)


def send_message(msg):
	url = 'https://api.groupme.com/v3/bots/post'
	message = {
		'text': 'this is it: {} <<'.format(msg),
		'bot_id': "eca4646a2e4f736ab96eefa29e"
		}
	json = requests.post(url, message)

	sys.stdout.write('made it to send_message function. This was passed {} << '.format(msg))


def franchise_identifier(input):
	# These inputs correspond to groupme nicknames as of 10/12/18
	if input == 'Matt Lewis' or input == 'Ross Wafer' or input == 1:
		return(1)
	elif input == 'Scott Becker' or input == 'James Roeling' or input == 2:
		return(2)
	elif input == 'Doug Ramey, League Champion' or input == 3:
		return(3)
	elif input == 'Taylor Crockett' or input == 4:
		return(4)
	elif input == 'Blake Tellarico' or input == 5:
		return(5)
	elif input == 'Kevin Fischer' or input == 6:
		return(6)
	elif input == 'Kyle Evers' or input == 7:
		return(7)
	elif input == 'John Gaudet' or input == 8:
		return(8)
	elif input == 'Bob' or input == 'Jordan Redmon' or input == 'Kevin Pohlig' or input == '7435972' or input == 9:
		return(9)
	elif input == 'Mitch Tellarico' or input == 10:
		return(10)
	elif input == 'Nicholas Hart' or input == 'Monster' or input == 11:
		return(11)
	elif input == 'Mike Evers' or input == 'Joseph Howe 2' or input == 12:
		return(12)


def franchise_namer(number):
	if number == 1:
		return('Matt & Ross')
	elif number == 2: 
		return('Scott & James')
	elif number == 3:
		return('Doug')
	elif number == 4:
		return('Crockett')
	elif number == 5:
		return('Blake')
	elif number == 6:
		return('Kfish')
	elif number == 7:
		return('Kyle')
	elif number == 8:
		return('Gaudet & Cameron')
	elif number == 9:
		return('RTRO')
	elif number == 10:
		return('Mitch')
	elif number == 11:
		return('Nick & Mickey')
	elif number == 12:
		return('Joseph & Mike')



if __name__ == '__main__':
	app.run()