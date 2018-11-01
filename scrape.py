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

def update_scores(franchise_number, message_type):
	try:
		from bs4 import BeautifulSoup
		from urllib.request import urlopen

		season = 2018
		week = database_access('settings', 'week')

		url = 'http://games.espn.com/ffl/scoreboard?leagueId=133377&matchupPeriodId=%s&seasonId=%s' % (week, season)
		page = urlopen(url)
		page_content = page.read()
		soup = BeautifulSoup(page_content, "lxml")

		# This gives a list of franchise numbers in the order that they're matched up
		franchise_number_list = re.findall(r'(?<=id="teamscrg_)[0-9]*', str(soup)) # confirmed: this creates a list
		points_list = []
		projected_list = []

		# The if statement tests to see if the matchup is ongoing (returns true if so) or already completed (returns false if so)
		if re.search('tmTotalPts_', str(soup)):
			for i in franchise_number_list:
				points_list.append(soup.select_one('#tmTotalPts_%s' % (i)).text)
				projected_list.append(soup.select_one('#team_liveproj_%s' % (i)).text)
		else:
			points_list = re.findall(r'(?<=width="18%">)[0-9]*[.]?[0-9]', str(soup))
			projected_list = 'GAME COMPLETED'
			sys.stdout.write('nestled into a completed game. no projs')
	except:
		send_message('Error. Our combination of free cloud hosting + webdriver is lagging like a noob. Try a different command, or retry the same command in a few mintues.')
		return('get_data_no_webdriver failed')

	########## Put into ClearDb
	con = pymysql.connect(host='us-cdbr-iron-east-01.cleardb.net', user='bc01d34543e31a', password='02cdeb05', database='heroku_29a4da67c47b565')
	cur = con.cursor()

	cur.execute("DROP TABLE temporary_scraped_matchups;")
	con.commit()
	cur.execute("CREATE TABLE temporary_scraped_matchups (game INT, franchise INT, points DECIMAL(4,1), projected DECIMAL(4,1), PRIMARY KEY(game));")
	con.commit()

	if projected_list != 'GAME COMPLETED':
		for i in range(0,12):
			cur.execute("INSERT INTO  temporary_scraped_matchups VALUES(%s, %s, %s, %s);", (i, franchise_number_list[i], points_list[i], projected_list[i]))
			con.commit()
	else:
		for i in range(0,12):
			cur.execute("INSERT INTO temporary_scraped_matchups VALUES(%s, %s, %s, 999.9);", (i, franchise_number_list[i], points_list[i]))
			con.commit()

	con.close()

	if projected_list == 'GAME COMPLETED':
		games_over = 'yes'
	else:
		games_over = 'no'

	return(games_over)