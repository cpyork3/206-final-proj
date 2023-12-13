import sqlite3
import urllib.request
import json
import re
import os

# get api data as json file
def create_json(url, json_file):
    # get raw data
    response = urllib.request.urlopen(url)
    data_raw = response.read().decode('UTF-8')

    # create usable string
    list_str = re.split('people":', data_raw)[1]
    list_str = list_str.rstrip(list_str[-1])

    # write to file
    with open(json_file,"w") as file:
        file.write(list_str)

    print(f'JSON file {json_file} successfully created')

    return

# create 2 tables
    # playerinfo, playerid
def create_tables(conn, cur):
    
    # create table with player ids and names
    cur.execute('''CREATE TABLE IF NOT EXISTS mlb_playerids 
                (id INTEGER PRIMARY KEY, name TEXT)''')
    
    # create table with playerid, positionid, height, weight
    cur.execute('''CREATE TABLE IF NOT EXISTS mlb_playerinfo 
                (id INTEGER PRIMARY KEY, pos_id INTEGER, height INTEGER, weight INTEGER)''')
    
    # create position id table 
    position_dict = {1:'P', 2:'C', 3:'1B', 4:'2B', 5:'3B', 6:'SS', 7:'LF', 8:'CF', 9:'RF', 10:'DH', 11:'OF', 12:"2-Way"}
    cur.execute('CREATE TABLE IF NOT EXISTS mlb_pos_ids (id INTEGER PRIMARY KEY, pos TEXT)')
    for key, value in position_dict.items():
        cur.execute('''INSERT OR IGNORE INTO mlb_pos_ids (id, pos)
                VALUES (?, ?)''',
                (key, value))

    conn.commit()

    print('Created tables mlb_playerids, mlb_playerinfo, and mlb_pos_ids')
    return

# add values from json to database
def add_values(conn, cur, file_name):

    # set limit of 25 items at a time 
        # run query to select all ids from database, if player data id already in database, skip it

    # create list of dicts from json
    with open(file_name) as file:
        data = json.load(file)

        # get number of observations in table in db
        cur.execute('SELECT COUNT(id) FROM mlb_playerids')
        num_rows = cur.fetchone()[0]

        if num_rows == None:
            num_rows = 0
        print('Number of rows in mlb_playerids and mlb_playerinfo: ', num_rows)
    
        # can stop limiting after 4 runs
        if num_rows < 100:

            # loop through list, add data to each table
            for player in data[num_rows:num_rows+25]:

                # extract height in inches from height string
                temp = re.findall(r'\d+', player['height'])
                height = int(temp[0])*12 + int(temp[1])

                # add info to playerid table
                cur.execute('''INSERT OR IGNORE INTO mlb_playerids 
                            (id, name) 
                            VALUES (?,?)''',
                            (player['id'], player['fullName']))

                # add info to playerinfo table
                cur.execute('''INSERT OR IGNORE INTO mlb_playerinfo 
                            (id, pos_id, height, weight) 
                            VALUES (?,?,?,?)''',
                            (player['id'], player['primaryPosition']['code'], height, player['weight']))

                conn.commit() 
            
        else: # if already have 100 rows:
            for player in data[num_rows:]:

                # extract height in inches from height string
                temp = re.findall(r'\d+', player['height'])
                height = int(temp[0])*12 + int(temp[1])

                # add info to playerid table
                cur.execute('''INSERT OR IGNORE INTO mlb_playerids 
                            (id, name) 
                            VALUES (?,?)''',
                            (player['id'], player['fullName']))

                # add info to playerinfo table
                cur.execute('''INSERT OR IGNORE INTO mlb_playerinfo 
                            (id, pos_id, height, weight) 
                            VALUES (?,?,?,?)''',
                            (player['id'], player['primaryPosition']['code'], height, player['weight'])) 
                
                # update position ids that are not numeric
                cur.execute('''UPDATE mlb_playerinfo 
                            SET pos_id = 12 
                            WHERE pos_id = "Y"''')
                cur.execute('''UPDATE mlb_playerinfo 
                            SET pos_id = 11 
                            WHERE pos_id = "O"''')
                
                conn.commit()

    print(f'Inserted data from {file_name} into tables mlb_playerids and mlb_playerinfo')
    
    return

def main():
    try:
        # create a connection
        with sqlite3.connect("final_proj.db") as conn:
            # create a cursor
            cur = conn.cursor()
            # get url
            players_url = '''https://statsapi.mlb.com/api/v1/sports/1/players?season=2023'''
            # create json file
            json_file = 'mlb_players.json'
            # create json file
            check_file = os.path.exists('/'+json_file)
            if not check_file:
                create_json(players_url, json_file)
            # create tables in database
            create_tables(conn, cur)
            # add items to tables
            add_values(conn, cur, json_file)

        print('Connection closed')

    except sqlite3.Error as e:
        # Handle the error
        conn.close()
        print('Connection closed')
        print("SQLite error:", e)


if __name__ == "__main__":
    main()