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

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
	data = request.get_json()
	if '@bot' in data['text']:
		sender = data['user_id']
		text = data['text']
		send_message(sender)
		return('ok',200)

	else: return('ok',200)

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