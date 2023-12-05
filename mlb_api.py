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

# create players table
def create_table(conn, cur):
    pass

def main():
    # cur, conn = create_conn('final_proj.db')
    # print(cur, conn)
    players_url = '''https://statsapi.mlb.com/api/v1/sports/1/players?season=2022'''
    create_json(players_url, 'mlb_players.json')

    # test if json loads correctly
    with open('mlb_players.json') as file:
        test_dict = json.load(file)
        print(type(test_dict))


if __name__ == "__main__":
    main()