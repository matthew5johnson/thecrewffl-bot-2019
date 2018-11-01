import os
import json
import sys
# import requests
# requests==2.19.1
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from flask import Flask, request
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options 
# import selenium.webdriver.chrome.service as service
import re
import pymysql



def get_scores(franchise_number, message_type, games_over):
	########## Get from ClearDb
	con = pymysql.connect(host='us-cdbr-iron-east-01.cleardb.net', user='bc01d34543e31a', password='02cdeb05', database='heroku_29a4da67c47b565')
	cur = con.cursor()

	###### Get single score
	if message_type == 1:
		cur.execute("SELECT game, franchise, points, projected FROM temporary_scraped_matchups WHERE franchise=%s", (franchise_number))
		franchise_data = cur.fetchall()[0]
		con.commit()
		game_number = franchise_data[0]

		if game_number % 2 == 0:
			opponent_game = game_number + 1
			# sys.stdout.write('even index')
		else: 
			opponent_game = game_number - 1
			# sys.stdout.write('odd index')

		cur.execute("SELECT game, franchise, points, projected FROM temporary_scraped_matchups WHERE game=%s", (opponent_game))
		opponent_data = cur.fetchall()[0]
		con.commit()

		con.close()

		# create_game_data_message_single(franchise_data, opponent_data, games_over)
		return('ok',200)

	######### For whole scoreboard
	elif message_type == 2:
		if games_over == 'yes':
			week = database_access('settings', 'week')
			final_scoreboard = '*** Week %i Final Scoreboard ***\n' % week
			for i in range(0,12)[::2]:
				cur.execute("SELECT game, franchise, points, projected FROM temporary_scraped_matchups WHERE game=%s;", (i))
				first_line_raw = cur.fetchall()[0]
				con.commit()
				cur.execute("SELECT game, franchise, points, projected FROM temporary_scraped_matchups WHERE game=%s;", (i+1))
				second_line_raw = cur.fetchall()[0]
				con.commit()
				final_scoreboard = final_scoreboard + '{} - {}\n{} - {}\n===== ===== =====\n'.format(first_line_raw[2], get_franchise_name(first_line_raw[1]), second_line_raw[2], get_franchise_name(second_line_raw[1]))
			
			con.close()
			return(final_scoreboard)
			# return('ok',200)
		
		elif games_over == 'no':
			week = database_access('settings', 'week')
			live_scoreboard = '*** Week %i Live Scoreboard ***\n' % week
			for i in range(0,12)[::2]:
				cur.execute("SELECT game, franchise, points, projected FROM temporary_scraped_matchups WHERE game=%s;", (i))
				first_line_raw = cur.fetchall()[0]
				con.commit()
				cur.execute("SELECT game, franchise, points, projected FROM temporary_scraped_matchups WHERE game=%s;", (i+1))
				second_line_raw = cur.fetchall()[0]
				con.commit()
				live_scoreboard = live_scoreboard + '{} - {} | proj: {}\n{} - {} | proj: {}\n===== ===== =====\n'.format(first_line_raw[2], get_franchise_name(first_line_raw[1]), first_line_raw[3], second_line_raw[2], get_franchise_name(second_line_raw[1]), second_line_raw[3])
			
			con.close()
			return(live_scoreboard)
			# return('ok',200)

def create_game_data_message_single(franchise, opponent, games_over):
	if games_over == 'yes':
		first_line = '{} - {}'.format(franchise[2], get_franchise_name(franchise[1]))
		second_line = '{} - {}'.format(opponent[2], get_franchise_name(opponent[1]))
		single_game_final_score = '{}\n{}'.format(first_line, second_line)
		send_message(single_game_final_score)
		return('ok',200)
		# WORKED B
	else:
		first_line = '{} - {}'.format(franchise[2], get_franchise_name(franchise[1]))
		second_line = '{} - {}'.format(opponent[2], get_franchise_name(opponent[1]))
		single_game_ongoing_score = '{} | proj: {}\n{} | proj: {}'.format(first_line, franchise[3], second_line, opponent[3])
		send_message(single_game_ongoing_score)
		return('ok',200)