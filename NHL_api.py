import unittest
import sqlite3
import json
import os
import urllib.request
import matplotlib.pyplot as plt

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

        conn.commit()

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")


#create the table with the players height and weight
def create_nhl_heightweight_table(cur, conn):
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS nhl_height_weight (
        playerId INTEGER PRIMARY KEY, draft_year INTEGER, height INTEGER, weight INTEGER
        )
        '''


    )
    conn.commit()


#fill the table with the information from the json storing the api data
# the height and weight table will only have players after 2013

def add_height_weight(filename, cur, conn):
            
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), filename))) as f:
        file_data = f.read()

    try:
        players = json.loads(file_data)
        for data in players['data']:
            draft_year = data.get('draftYear', 0)
            if draft_year > 2018:
                player_id = data['playerId']
                draft_year = data['draftYear']
                height = data['height']
                weight = data['weight']
            

                cur.execute(
                    """
                    INSERT OR IGNORE 
                    INTO nhl_height_weight (playerId, draft_year, height, weight)
                    VALUES (?, ?, ?, ?)
                    """,
                    (player_id, draft_year, height, weight)
                )

        
        conn.commit()

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")


#this calculates the average height and weight from the height_weight table
# this is based on the players drafted in the past 5 years [2019-2023]
def calculate_average_height_weight_all_players(cur):
    try:
        cur.execute('''
            SELECT AVG(height) AS avg_height, AVG(weight) AS avg_weight
            FROM nhl_height_weight
        ''')
        result = cur.fetchone()
        return {'avg_height': result[0], 'avg_weight': result[1]} if result else None
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None
    
def calculate_average_height_weight_by_position(cur):
    try:
        cur.execute('''
            SELECT nhlplayers.position,
                   AVG(nhl_height_weight.height) AS avg_height,
                   AVG(nhl_height_weight.weight) AS avg_weight
            FROM nhlplayers
            JOIN nhl_height_weight ON nhlplayers.playerId = nhl_height_weight.playerId
            WHERE nhlplayers.position IN ('D', 'RW', 'LW', 'C', 'G')
            GROUP BY nhlplayers.position
        ''')
        results = cur.fetchall()
        if not results:
            print("No data to calculate averages by position.")
            return []
        return [{'position': row[0], 'avg_height': row[1], 'avg_weight': row[2]} for row in results]
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None
    

def visualize_data(avg_all_players, avg_by_position):
    # Plot horizontal lines for average height and weight of all players
    plt.axhline(y=avg_all_players['avg_height'], color='blue', linestyle='--', label='Avg Height (All Players)')
    plt.axhline(y=avg_all_players['avg_weight'], color='red', linestyle='--', label='Avg Weight (All Players)')

    # Plot points for average height and weight by position
    positions = [entry['position'] for entry in avg_by_position]
    avg_heights = [entry['avg_height'] for entry in avg_by_position]
    avg_weights = [entry['avg_weight'] for entry in avg_by_position]

    plt.scatter(positions, avg_heights, color='blue', label='Avg Height by Position', marker='o')
    plt.scatter(positions, avg_weights, color='red', label='Avg Weight by Position', marker='o')

    # Labeling and formatting
    plt.xlabel('Position')
    plt.ylabel('Height (Inches) and Weight (Pounds)')
    plt.title('Average Height and Weight of NHL Players')
    plt.legend()
    plt.grid(True)
    plt.show()

avg_all_players = {'avg_height': 72.76, 'avg_weight': 184.56}
avg_by_position = [{'position': 'C', 'avg_height': 72.16, 'avg_weight': 181.89},
                   {'position': 'D', 'avg_height': 73.25, 'avg_weight': 188.46},
                   {'position': 'G', 'avg_height': 74.86, 'avg_weight': 186.05},
                   {'position': 'LW', 'avg_height': 72.35, 'avg_weight': 182.70},
                   {'position': 'RW', 'avg_height': 71.90, 'avg_weight': 182.23}]

visualize_data(avg_all_players, avg_by_position)


def main():
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('final_proj.db')
    create_nhlplayerstable(cur, conn)

    add_players("nhlapi.json", cur, conn)

    create_nhl_heightweight_table(cur,conn)

    add_height_weight("nhlapi.json", cur, conn)

        # Calculate and print average height and weight of all players
    avg_all_players = calculate_average_height_weight_all_players(cur)
    if avg_all_players:
        print("Average height and weight of all players:")
        print(f"Average Height: {avg_all_players['avg_height']:.2f} inches")
        print(f"Average Weight: {avg_all_players['avg_weight']:.2f} pounds")


     # Calculate and print average height and weight by position
    avg_by_position = calculate_average_height_weight_by_position(cur)
    if avg_by_position:
        print("\nAverage height and weight by position:")
        for result in avg_by_position:
            position = result['position']
            avg_height = result['avg_height']
            avg_weight = result['avg_weight']
            print(f"{position}: Avg Height: {avg_height:.2f} inches, Avg Weight: {avg_weight:.2f} pounds")

if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)