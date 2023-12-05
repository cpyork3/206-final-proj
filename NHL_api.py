import unittest
import sqlite3
import json
import os
import urllib.request
import re

def load_nhljson(url, file_path):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = response.read().decode('UTF-8')

                with open(file_path, "w") as file:
                    file.write(data)

                print("Data written to file successfully.")
            else:
                print(f"HTTP Error {response.status}: {response.reason}")
                print(response.read().decode('UTF-8'))
    except Exception as e:
        print(f"Error: {e}")

url = 'https://records.nhl.com/site/api/draft'
file_path = 'nhlapi.json'
load_nhljson(url, file_path)

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def create_nhlplayerstable(cur, conn):
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS nhlplayers (
        playerId INTEGER PRIMARY KEY, position TEXT, firstName TEXT, lastName TEXT
        )
        '''

    )
    conn.commit()

def add_players(filename, cur, conn):
        # Load .json file and read job data
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), filename))) as f:
        file_data = f.read()

    try:
        players = json.loads(file_data)
        for data in players['data']:
            player_id = data['playerId']
            position = data['position']
            first_name = data['firstName']
            last_name = data['lastName']
            

            cur.execute(
                """
                INSERT OR IGNORE 
                INTO nhlplayers (playerId, position, firstName, lastName)
                VALUES (?, ?, ?, ?)
                """,
                (player_id, position, first_name, last_name)
            )

        # Commit the changes after the loop
        conn.commit()

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")


#create the table with the players height and weight
def create_nhl_heightweight_table(cur, conn):
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS nhl_height_weight (
        playerId INTEGER PRIMARY KEY, draft_year INTEGER, position TEXT, height INTEGER, weight INTEGER
        )
        '''


    )
    conn.commit()


#fill the table with the information from the json storing the api data
# the height and weight table will only have players after 2013

def add_height_weight(filename, cur, conn):
            # Load .json file and read job data
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), filename))) as f:
        file_data = f.read()

    try:
        players = json.loads(file_data)
        for data in players['data']:
            draft_year = data.get('draftYear', 0)
            if draft_year > 2018:
                player_id = data['playerId']
                draft_year = data['draftYear']
                position = data['position']
                height = data['height']
                weight = data['weight']
            

                cur.execute(
                    """
                    INSERT OR IGNORE 
                    INTO nhl_height_weight (playerId, draft_year, position, height, weight)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (player_id, draft_year, position, height, weight)
                )

        # Commit the changes after the loop
        conn.commit()

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")



def main():
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('final_proj.db')
    create_nhlplayerstable(cur, conn)

    add_players("nhlapi.json", cur, conn)

    create_nhl_heightweight_table(cur,conn)

    add_height_weight("nhlapi.json", cur, conn)

if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)