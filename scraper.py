from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
import selenium.webdriver.chrome.service as service
import re
import pymysql
import os
from time import sleep

def scrape_scores(added_delay):
    # Get the current week
    con = pymysql.connect(host=os.environ['DB_ACCESS_HOST'], user=os.environ['DB_ACCESS_USER'], password=os.environ['DB_ACCESS_PASSWORD'], database=os.environ['DB_ACCESS_DATABASE'])
    cur = con.cursor()
    cur.execute("SELECT settings_week FROM settings WHERE description='main';")
    current_week = cur.fetchall()
    con.commit()
    con.close()
    week = int(current_week[0][0])

        
    # delay = 12
    delay = 4 + added_delay
    
    website = "https://fantasy.espn.com/football/league/scoreboard?leagueId=133377&matchupPeriodId={}&mSPID={}".format(week, week)
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=os.environ['CHROMEDRIVER_PATH'], chrome_options=chrome_options)
    driver.get(website)
    sleep(delay)
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    driver.close()

    final = str(soup)

    all_franchises = ','.join(re.findall(r'(?<=teamId=)[0-9]*', final))
    franchises = all_franchises.split(",")
    all_projected = ','.join(re.findall(r'(?<=Proj Total:<span class="statusValue fw-bold">)[^<]*', final))
    projected = all_projected.split(",")
    all_scores = ','.join(re.findall(r'(?<=Score h4 clr-gray-01 fw-heavy tar ScoreCell_Score--scoreboard pl2">)[^<]*', final))
    scores = all_scores.split(",")

    matchups = franchises[12::3]

    con = pymysql.connect(host=os.environ['DB_ACCESS_HOST'], user=os.environ['DB_ACCESS_USER'], password=os.environ['DB_ACCESS_PASSWORD'], database=os.environ['DB_ACCESS_DATABASE'])
    cur = con.cursor()
    cur.execute("DROP TABLE temporary_scraped_matchups;")
    con.commit()
    cur.execute("CREATE TABLE temporary_scraped_matchups (game INT, franchise INT, points DECIMAL(4,1), projected DECIMAL(4,1), PRIMARY KEY(franchise));")
    con.commit()

    for i in range(0,len(matchups)):
        cur.execute("INSERT INTO temporary_scraped_matchups VALUES(%s, %s, %s, %s);", (i, matchups[i], scores[i], projected[i]))
        con.commit()

    ## Test to make sure it scraped all matchups. If not, add to the delay time to give it extra scrape time in the next try
    cur.execute("SELECT * FROM temporary_scraped_matchups;")
    successful_scrape_test = cur.fetchall()
    con.commit()

    con.close()


    if len(successful_scrape_test) < 9:
        scrape_scores(4)
    else:
        return('ok', 200)