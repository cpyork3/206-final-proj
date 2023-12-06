import requests
from bs4 import BeautifulSoup
import json



def scrape_nba_players(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        player_table = soup.find('table', class_='players-list')
        if player_table:
            nba_players = []

            for row in player_table.find_all('tr')[1:]:
                columns = row.find_all('td')
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

            nba_players_json = json.dumps(nba_players, indent=2)

            output_file = 'nba_players.json'  

            with open(output_file, 'w') as json_file:
                json_file.write(nba_players_json)

def main():
    players_url = f'https://www.nba.com/players'
    scrape_nba_players(players_url)

    # test if json loads correctly
    with open('nba_players.json') as file:
        test_dict = json.load(file)
        print(type(test_dict))


if __name__ == "__main__":
    main()