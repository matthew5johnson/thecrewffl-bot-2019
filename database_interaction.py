import pymysql
import os
from supporting_fxns import get_franchise_name
import re

def pull_scores(target):
    # Get the current week
    con = pymysql.connect(host=os.environ['DB_ACCESS_HOST'], user=os.environ['DB_ACCESS_USER'], password=os.environ['DB_ACCESS_PASSWORD'], database=os.environ['DB_ACCESS_DATABASE'])
    cur = con.cursor()
    cur.execute("SELECT settings_week FROM settings WHERE description='main';")
    current_week = cur.fetchall()
    con.commit()
    con.close()
    week = int(current_week[0][0])

    con = pymysql.connect(host=os.environ['DB_ACCESS_HOST'], user=os.environ['DB_ACCESS_USER'], password=os.environ['DB_ACCESS_PASSWORD'], database=os.environ['DB_ACCESS_DATABASE'])
    cur = con.cursor()
    cur.execute("SELECT * FROM temporary_scraped_matchups ORDER BY game asc;")
    all_scores = cur.fetchall()
    con.commit()
    con.close()

    if target == "none":
        # pull the full scoreboard
        live_scoreboard = '*** Week {} Live Scoreboard ***\n'.format(week)
        for i in range(0, len(all_scores), 2):
            opponent_index = i + 1
            live_scoreboard = live_scoreboard + '{} - {} | proj: {}\n{} - {} | proj: {}\n===== ===== =====\n'.format(all_scores[i][2], get_franchise_name(int(all_scores[i][1])), all_scores[i][3], all_scores[opponent_index][2], get_franchise_name(int(all_scores[opponent_index][1])), all_scores[opponent_index][3])

        return(live_scoreboard)

    else:
        # pull the specific score, based on target
        for i in range(0,len(all_scores)):
            if target == all_scores[i][1]:
                index = all_scores.index(all_scores[i])
                if index % 2 == 0:
                    opponent_index = index + 1
                else:
                    opponent_index = index - 1
                my_scoreboard = ""
                my_scoreboard = my_scoreboard + '{} - {} | proj: {}\n{} - {} | proj: {}\n'.format(all_scores[index][2], get_franchise_name(int(all_scores[index][1])), all_scores[index][3], all_scores[opponent_index][2], get_franchise_name(int(all_scores[opponent_index][1])), all_scores[opponent_index][3])
                
                return(my_scoreboard)
                break
        
        return('went through the specific score pathway in database_interaction')