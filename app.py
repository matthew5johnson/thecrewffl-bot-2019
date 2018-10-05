import os
import json

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, request


app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
	data = request.get_json()

	# We don't want to reply to ourselves
	# if data['name'] != 'bot':
	# 	msg = 'hello world: user: {} data: {}'.format(data['name'], data['text'])
	# 	send_message(msg)

	if data['text'] == 'my':
		msg = 'here is your games score'
		send_message(msg)


	return "ok", 200


def send_message(msg):
	url = 'https://api.groupme.com/v3/bots/post'
	data = {'text': msg, 'bot_id': "eca4646a2e4f736ab96eefa29e"}
	request = Request(url, urlencode(data).encode())
	json = urlopen(request).read().decode()