import pymysql
import os

def change_week(direction):
    con = pymysql.connect(host=os.environ['DB_ACCESS_HOST'], user=os.environ['DB_ACCESS_USER'], password=os.environ['DB_ACCESS_PASSWORD'], database=os.environ['DB_ACCESS_DATABASE'])
    cur = con.cursor()
    cur.execute("SELECT settings_week FROM settings WHERE description='main';")
    current_week = cur.fetchall()
    con.commit()

    if direction == 'next':
        week = int(current_week[0][0]) + 1
    elif direction == 'last':
        week = int(current_week[0][0]) - 1

    cur.execute("UPDATE settings SET settings_week=%s WHERE description='main';", (week))
    con.commit()
    con.close()

    if direction == 'next':
        return("Welcome to week {}.".format(week))
    elif direction == 'last':
        return("Going back to week {}.".format(week))

 
 
    
    
    

# 	con = pymysql.connect(host=os.environ['DB_ACCESS_HOST'], user=os.environ['DB_ACCESS_USER'], password=os.environ['DB_ACCESS_PASSWORD'], database=os.environ['DB_ACCESS_DATABASE'])
# 	cur = con.cursor()
# 	cur.execute("UPDATE settings SET settings_week=%s WHERE description='main';", (week))
# 	con.commit()
# 	con.close()
# 	return('Week updated to %s') % (week)

# def database_remove_bob():
# 	rb_votes = database_access('settings', 'rb')
# 	rb_votes += 1

# 	con = pymysql.connect(host=os.environ['DB_ACCESS_HOST'], user=os.environ['DB_ACCESS_USER'], password=os.environ['DB_ACCESS_PASSWORD'], database=os.environ['DB_ACCESS_DATABASE'])
# 	cur = con.cursor()
# 	cur.execute("UPDATE settings SET settings_rbvotes=%s WHERE description='main';", (rb_votes))
# 	con.commit()
# 	con.close()
# 	return('Total #RB votes: %s') % (rb_votes)


def text_id_franchise(text):
	if re.search('mattjohn', text, re.I) or re.search('matt john', text, re.I) or re.search('gilhop', text, re.I) or re.search('jordan', text, re.I) or re.search('bob', text, re.I) or re.search('rtro', text, re.I) or re.search('retro', text, re.I):
		return(9)
	elif re.search('matt', text, re.I) or re.search('ross', text, re.I) or re.search('butler', text, re.I):
		return(1)
	elif re.search('scott', text, re.I) or re.search('james', text, re.I) or re.search('choice', text, re.I) or re.search('tpc', text, re.I):
		return(2)
	elif re.search('doug', text, re.I) or re.search('coach o', text, re.I) or re.search('face', text, re.I):
		return(3)
	elif re.search('crocket', text, re.I) or re.search('taylor', text, re.I):
		return(4)
	elif re.search('blake', text, re.I) or re.search('marmalade', text, re.I):
		return(5)
	elif re.search('kfish', text, re.I) or re.search('kmish', text, re.I) or re.search('kevin', text, re.I) or re.search('fischer', text, re.I):
		return(6)
	elif re.search('kyle', text, re.I) or re.search('dttw', text, re.I) or re.search('douille', text, re.I):
		return(7)
	elif re.search('gaudet', text, re.I) or re.search('cameron', text, re.I) or re.search('john', text, re.I) or re.search('zj', text, re.I):
		return(8)
	elif re.search('mitch', text, re.I):
		return(10)
	elif re.search('nick', text, re.I) or re.search('mickey', text, re.I):
		return(11)
	elif re.search('joseph', text, re.I) or re.search('craig', text, re.I) or re.search('mike', text, re.I) or re.search('black', text, re.I) or re.search('trading', text, re.I) or re.search('tbh', text, re.I):
		return(12)
	else: 
		return('none')


def get_franchise_number(input):
	# These inputs correspond to groupme ids as of 10/12/18
	if input == '3491271' or input == '7435976':
		return(1)
	elif input == '7435971' or input == '3931770' or input == 2:
		return(2)
	elif input == '7435973' or input == 3:
		return(3)
	elif input == '7435977' or input == 4:
		return(4)
	elif input == '12610331' or input == 5:
		return(5)
	elif input == '7435975' or input == 6:
		return(6)
	elif input == '7435974' or input == 7:
		return(7)
	elif input == '22905' or input == 8:
		return(8)
	elif input == '4747679' or input == '29542085' or input == '3054470' or input == '7435972' or input == 9:
		return(9)
	elif input == '7435969' or input == 10:
		return(10)
	elif input == '3165727' or input == '3159027' or input == 11:
		return(11)
	elif input == '6602218' or input == '55209013' or input == 12:
		return(12)

def get_franchise_name(franchise):
	if franchise == 1:
		return('Matt & Ross')
	elif franchise == 2:
		return('Scott & James')
	elif franchise == 3:
		return('Doug')
	elif franchise == 4:
		return('Crockett')
	elif franchise == 5:
		return('Blake')
	elif franchise == 6:
		return('Kfish')
	elif franchise == 7:
		return('Kyle')
	elif franchise == 8:
		return('Gaudet & Cameron')
	elif franchise == 9:
		return('RTRO')
	elif franchise == 10:
		return('Mitch')
	elif franchise == 11:
		return('Nick & Mickey')
	elif franchise == 12:
		return('Joseph & Mike')

