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
        # pull the specific score, based on target. target is an integer that represents franchise id, and is determined from the message sender
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


def pull_live_standings():
    # Get the current week
    con = pymysql.connect(host=os.environ['DB_ACCESS_HOST'], user=os.environ['DB_ACCESS_USER'], password=os.environ['DB_ACCESS_PASSWORD'], database=os.environ['DB_ACCESS_DATABASE'])
    cur = con.cursor()
    cur.execute("SELECT settings_week FROM settings WHERE description='main';")
    current_week = cur.fetchall()
    con.commit()

    week = int(current_week[0][0])

    if week == 1:
        return("No games have been played yet. Standings will be released in week 2")
    elif week > 13:
        return("The postseason is here. Checkout the playoff bracket and consolation ladder.")

    con = pymysql.connect(host=os.environ['DB_ACCESS_HOST'], user=os.environ['DB_ACCESS_USER'], password=os.environ['DB_ACCESS_PASSWORD'], database=os.environ['DB_ACCESS_DATABASE'])
    cur = con.cursor()
    cur.execute("DROP TABLE temporary_intermediate_standings;")
    con.commit()
    cur.execute("CREATE TABLE temporary_intermediate_standings (franchise INT, intermediate_points DECIMAL(4,1), intermediate_result VARCHAR(10), PRIMARY KEY(franchise));")
    con.commit()
    cur.execute("DROP TABLE temporary_live_standings;")
    con.commit()
    cur.execute("CREATE TABLE temporary_live_standings (franchise INT, live_win_pct DECIMAL(6,5), live_points DECIMAL(5,1), live_wins INT, live_losses INT, live_ties INT, PRIMARY KEY(franchise));")
    con.commit()



    con = pymysql.connect(host=os.environ['DB_ACCESS_HOST'], user=os.environ['DB_ACCESS_USER'], password=os.environ['DB_ACCESS_PASSWORD'], database=os.environ['DB_ACCESS_DATABASE'])
    cur = con.cursor()
    cur.execute("SELECT * FROM temporary_scraped_matchups ORDER BY game asc;")
    all_scores = cur.fetchall()
    con.commit()


    for i in range(0,len(all_scores)):
        if i % 2 == 0:
            opponent_index = i + 1
        else:
            opponent_index = i - 1
        
        if all_scores[i][2] > all_scores[opponent_index][2]:
            live_result = 'W'
        elif all_scores[i][2] < all_scores[opponent_index][2]:
            live_result = 'L'
        elif all_scores[i][2] == all_scores[opponent_index][2]:
            live_result = 'T'

        cur.execute("INSERT INTO temporary_intermediate_standings (franchise, intermediate_points, intermediate_result) VALUES (%s, %s, %s);", (all_scores[i][1], all_scores[i][2], live_result))
        con.commit()

    for franchise in range(1,13):
	    
        cur.execute("SELECT intermediate_points, intermediate_result FROM temporary_intermediate_standings WHERE franchise=%s;", (franchise))
        data_tuple = cur.fetchall()[0]
        con.commit()

        intermediate_points = data_tuple[0]
        intermediate_result = data_tuple[1]

        cur.execute("SELECT wins, losses, ties, sum_points FROM temporary_scrape_standings WHERE franchise=%s;", (franchise))
        weekly_scrape_tuple = cur.fetchall()[0]
        con.commit()

        old_wins = weekly_scrape_tuple[0]
        old_losses = weekly_scrape_tuple[1]
        old_ties = weekly_scrape_tuple[2]
        old_sum_points = weekly_scrape_tuple[3]

        if intermediate_result == 'W':
            wins = old_wins + 1
            losses = old_losses
            ties = old_ties
        elif intermediate_result == 'L':
            wins = old_wins
            losses = old_losses + 1
            ties = old_ties
        elif intermediate_result == 'T':
            wins = old_wins
            losses = old_losses
            ties = old_ties + 1

        live_win_pct = (wins + (ties * 0.5)) / (wins + losses + ties)
        live_points = old_sum_points + intermediate_points

        cur.execute("INSERT INTO temporary_live_standings (franchise, live_win_pct, live_points, live_wins, live_losses, live_ties) VALUES (%s, %s, %s, %s, %s, %s);", (franchise, "%.5f"%live_win_pct, live_points, wins, losses, ties))
        con.commit()

	    
    cur.execute("SELECT franchise, live_wins, live_losses, live_ties, live_points FROM temporary_live_standings ORDER BY live_win_pct, live_points;")
    standings_tuple = cur.fetchall()
    con.commit()

    con.close()

    rankings_headers = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    live_standings = '^v^v^v^ Live Standings ^v^v^v^\nbased on current live scores\n\n'
    for i in range(11,-1,-1):
        live_standings = live_standings + '{}. {} {}-{}-{} ({})\n'.format(rankings_headers[i], get_franchise_name(standings_tuple[i][0]), standings_tuple[i][1], standings_tuple[i][2], standings_tuple[i][3], standings_tuple[i][4])
        
        if i == 10:
            live_standings = live_standings + '----- Top 2 = Byes -----\n'
        if i == 6:
            live_standings = live_standings + '=====  Playoff cut line  =====\n'

    return(live_standings)