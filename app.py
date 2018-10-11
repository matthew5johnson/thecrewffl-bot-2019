import os
import json

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, request
from requests_html import HTMLSession

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
	data = request.get_json()
	if data['text'] == 'my':
		team = 1
		season = 2018
		week = 6
		url = 'http://games.espn.com/ffl/scoreboard?leagueId=133377&matchupPeriodId=%s&seasonId=%s' % (week, season)
		session = HTMLSession()
		r = session.get(url)
		r.html.render()
		ytp = '#team_ytp_%s' % (team)
		pts = '#tmTotalPts_%s' % (team)
		proj = '#team_liveproj_%s' % (team)
		for tag in r.html.find(ytp):
			players_remaining = tag.text

		msg = players_remaining
		
		send_message(msg)


	return "ok", 200

def send_message(msg):
	url = 'https://api.groupme.com/v3/bots/'
	data = {'text': 'remaining: {}'.format(msg), 'bot_id': "eca4646a2e4f736ab96eefa29e"}
	request = Request(url, urlencode(data).encode())
	json = urlopen(request).read().decode()


if __name__ == '__main__':
	app.run(debug=True)


