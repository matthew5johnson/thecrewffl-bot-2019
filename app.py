from flask import Flask 

app = Flask(__name__)

@app.route('/')
def index():
	return 'OK!'

if __name__ == '__main__':
	app.run()


# import os
# import json

# from urllib.parse import urlencode
# from urllib.request import Request, urlopen

# from flask import Flask, request

# app = Flask(__name__)

# msg = 'Whatttt is your favorite color?'

# @app.route('/', methods=['POST'])
# def send_message(msg):
# 	url = 'https://api.groupme.com/v3/bots/post'
# 	data = {'bot_id': 'eca4646a2e4f736ab96eefa29e', 'text': msg}
# 	request = Request(url, urlencode(data).endcode())




# def webhook():
# 	data = request.get_json()

# 	# We don't want to reply to ourselves
# 	if data['name'] != 'bot':
# 		msg = '{}, you sent {}.'.format(data['name'], data['text'])
# 		send_message(msg)

# 	return "ok", 200

# def send_message(msg):
# 	url = 'https://api.groupme.com/v3/bots/post'

# 	data = {
# 			'bot_id' : 'eca4646a2e4f736ab96eefa29e', 
# 			'text' : msg
# 			}

# 	request = Request(url, urlencode(data).endcode())
# 	json = urlopen(request).read().decode()