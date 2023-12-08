import requests
from bs4 import BeautifulSoup
import json
import sqlite3
from string import ascii_lowercase
import matplotlib.pyplot as plt


def scrape_nba_players_info(url = 'https://www.basketball-reference.com/players/'):
    # Create a dictionary for each player
    nba_players = []

    for letter in ascii_lowercase:
        url = f'https://www.basketball-reference.com/players/{letter}/'
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            player_table = soup.find('table', id= 'players')

            if player_table:
                for row in player_table.find_all('tr')[1:]:
                    columns = row.find_all(['th','td'])
                    player_name = columns[0].text.strip()
                    position = columns[3].text.strip()
                    height = columns[4].text.strip()
                    weight = columns[5].text.strip()

                    player_info = {
                    'player_name': player_name,
                    'position': position,
                    'height': height,
                    'weight': weight
                    }

                    nba_players.append(player_info)
                    # print(nba_players)

                nba_players_json = json.dumps(nba_players, indent=2)

                output_file = 'nba_players.json'

                with open(output_file, 'w', encoding='utf-8') as json_file:
                    json_file.write(nba_players_json)



def insert_json_into_sql(json_file):
    conn = sqlite3.connect('final_proj.db')
    cur = conn.cursor()

    # cur.execute('''DROP TABLE IF EXISTS nba_players;''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS nba_players (
            player_name TEXT,
            position TEXT,
            height TEXT,
            weight TEXT
        )
    ''')

    with open(json_file, 'r') as file:
        nba_players_data = json.load(file)

    cur.execute('SELECT COUNT(player_name) FROM nba_players')
    num_rows = cur.fetchone()[0]

    if num_rows == None:
        num_rows = 0
    print('Number of rows in nba_players: ', num_rows)

    # can stop limiting after 4 runs
    if num_rows < 100:
        for player_info in nba_players_data[num_rows:num_rows+25]:
            cur.execute('''
                INSERT OR IGNORE INTO nba_players (player_name, position, height, weight)
                VALUES (?, ?, ?, ?)
            ''', (player_info['player_name'], player_info['position'], player_info['height'], player_info['weight']))

    else:
        for player_info in nba_players_data[num_rows:]:
            cur.execute('''
                INSERT OR IGNORE INTO nba_players (player_name, position, height, weight)
                VALUES (?, ?, ?, ?)
            ''', (player_info['player_name'], player_info['position'], player_info['height'], player_info['weight']))

    conn.commit()
    conn.close()


def main():
    scrape_nba_players_info()
    insert_json_into_sql('nba_players.json')

if __name__ == "__main__":
    main()