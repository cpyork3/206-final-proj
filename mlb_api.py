import sqlite3
import os
import urllib.request
import json
import re

# create connection
def create_conn(db_name):
    # parameters: name of database
    # returns: connection and cursor object
    conn = sqlite3.connect('final_proj.db')
    cur = conn.cursor()
    return cur, conn

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

    return

# create 3 tables
    # playerinfo, playerid, heightid
def create_tables(conn, cur):
    
    # create table with player ids and names
    cur.execute('''CREATE TABLE IF NOT EXISTS mlb_playerids 
                (id INTEGER PRIMARY KEY, name TEXT)''')
    
    # create table with playerid, positionid, height, weight
    cur.execute('''CREATE TABLE IF NOT EXISTS mlb_playerinfo 
                (id INTEGER PRIMARY KEY, pos_id INTEGER, height INTEGER, weight INTEGER)''')

    conn.commit()
    return

# add values from json to database
def add_values(conn, cur, file_name):

    # create list of dicts from json
    with open(file_name) as file:
        data = json.load(file)

        # loop through list, add data to each table
        for player in data:

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
    
    return

def main():
    cur, conn = create_conn('final_proj.db')
    players_url = '''https://statsapi.mlb.com/api/v1/sports/1/players?season=2022'''
    json_file = 'mlb_players.json'
    create_json(players_url, json_file)
    create_tables(conn, cur)
    add_values(conn, cur, json_file)
    print('done')


if __name__ == "__main__":
    main()