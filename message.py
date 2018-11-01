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


def database_access(table, command):
	con = pymysql.connect(host='us-cdbr-iron-east-01.cleardb.net', user='bc01d34543e31a', password='02cdeb05', database='heroku_29a4da67c47b565')
	cur = con.cursor()


	##########  SETTINGS
	if table == 'settings':
		cur.execute("SELECT settings_rbvotes, settings_week FROM settings WHERE description='main';")
		settings_tuple = cur.fetchall()
		con.commit()
		con.close()
		if command == 'week':
			week = int(settings_tuple[0][1])
			return(week)
		elif command == 'rb':
			rb_votes = int(settings_tuple[0][0])
			return(rb_votes)
	
	#########   RECORDS		
	elif table == 'records':
		if command == 'all':
			# Highest single game score
			cur.execute("SELECT weekly_points, franchise, season, week, opponent FROM weekly_records WHERE type=1 ORDER BY weekly_points desc LIMIT 1;")
			weekly_highscore_tuple = cur.fetchall()
			con.commit()
			# Lowest single game score
			cur.execute("SELECT weekly_points, franchise, season, week, opponent FROM weekly_records WHERE type=2 ORDER BY weekly_points asc LIMIT 1;")
			weekly_lowcore_tuple = cur.fetchall()
			con.commit()
			# Biggest blowout
			cur.execute("SELECT weekly_margin, franchise, season, week, opponent FROM weekly_records WHERE type=3 ORDER BY weekly_margin desc LIMIT 1;")
			weekly_blowout_tuple = cur.fetchall()
			con.commit()
			# Closest game
			cur.execute("SELECT weekly_margin, franchise, season, week, opponent FROM weekly_records WHERE type=4 ORDER BY weekly_margin asc LIMIT 1;")
			weekly_closest_tuple = cur.fetchall()
			con.commit()
			# Most PPG Season
			cur.execute("SELECT season_ppg, franchise, season FROM season_records WHERE type=5 ORDER BY season_ppg desc LIMIT 1;")
			season_highppg_tuple = cur.fetchall()
			con.commit()
			# Fewest PPG Season
			cur.execute("SELECT season_ppg, franchise, season FROM season_records WHERE type=6 ORDER BY season_ppg asc LIMIT 1;")
			season_lowppg_tuple = cur.fetchall()
			con.commit()
			# Most WINS
			cur.execute("SELECT season_wins, franchise, season FROM season_records WHERE type=7 ORDER BY season_wins desc LIMIT 1;")
			season_highwins_tuple = cur.fetchall()
			con.commit()
			# Fewest WINS
			cur.execute("SELECT season_wins, franchise, season FROM season_records WHERE type=8 ORDER BY season_wins asc LIMIT 1;")
			season_lowwins_tuple = cur.fetchall()
			con.commit()
			# Highest avg margin of victory
			cur.execute("SELECT season_margin, franchise, season FROM season_records WHERE type=9 ORDER BY season_margin desc LIMIT 1;")
			season_highmargin_tuple = cur.fetchall()
			con.commit()

			con.close()
			# weekly_points = weekly_highscore_tuple[0][0]
			# franchise = weekly_highscore_tuple[0][1]
			# season = weekly_highscore_tuple[0][2]
			# week = weekly_highscore_tuple[0][3]
			# opponent = weekly_highscore_tuple[0][4]
			return(weekly_highscore_tuple, weekly_lowcore_tuple, weekly_blowout_tuple, weekly_closest_tuple, season_highppg_tuple, season_lowppg_tuple, season_highwins_tuple, season_lowwins_tuple, season_highmargin_tuple)
			# return(weekly_points, franchise, season, week, opponent)
		else: 
			return('none',200)
	else:
		con.close()
		sys.stdout.write('entered db access but no relevant command')
		return('ok',200)


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