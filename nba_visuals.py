import sqlite3
import json
import matplotlib.pyplot as plt

def calculate_avg_height_weight_by_position(db_file):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    # Select all athletes from the table
    cursor.execute('SELECT * FROM nba_players')
    players = cursor.fetchall()

    # Create a dictionary to store height and weight for each position
    position_data = {}

    # Iterate through players and store height and weight for each position
    for player in players:
        position = player[1]
        height = player[2]
        weight_str = player[3]

        # Check if weight is a valid numeric value
        if weight_str and weight_str.isdigit():
            weight = int(weight_str)  # Convert weight to integer

            # Convert height to inches for easier calculations (assuming format like '6-8')
            height_inches = int(height.split('-')[0]) * 12 + int(height.split('-')[1])

            if position not in position_data:
                position_data[position] = {'height': [], 'weight': []}

            position_data[position]['height'].append(height_inches)
            position_data[position]['weight'].append(weight)

    # Calculate average height and weight for each position
    avg_data = {}
    for position, data in position_data.items():
        avg_height = sum(data['height']) / len(data['height'])
        avg_weight = sum(data['weight']) / len(data['weight'])

        avg_data[position] = {'average_height': avg_height, 'average_weight': avg_weight}

    return avg_data

def write_avg_data_to_file(avg_data, output_file='avg_data.txt'):
    with open(output_file, 'w') as file:
        file.write(json.dumps(avg_data, indent=2))

def plot_bar_charts(position_data):
    # Create bar charts for height and weight
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 6))
    
    axes[0].bar(position_data.keys(), [data['average_height'] for data in position_data.values()])
    axes[0].set_title('Bar Chart of Average Height by Position')
    axes[0].set_ylabel('Average Height (inches)')
    axes[0].set_ylim([65, 85])

    axes[1].bar(position_data.keys(), [data['average_weight'] for data in position_data.values()])
    axes[1].set_title('Bar Chart of Average Weight by Position')
    axes[1].set_ylabel('Average Weight (lbs)')
    axes[1].set_ylim([150,250])

    plt.tight_layout()
    plt.show()

def scatter_plot_height_weight_by_position(db_file):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM nba_players')
    players = cursor.fetchall()

    positions = set(player[1] for player in players)  # Get unique positions

    # Dictionary to store data points for each position
    position_data = {position: {'height': [], 'weight': []} for position in positions}

    for player in players:
        position = player[1]
        height = int(player[2].split('-')[0]) * 12 + int(player[2].split('-')[1])  # Convert height to inches

        # Check if weight is a valid integer
        weight_str = player[3]
        try:
            weight = int(weight_str)
        except ValueError:
            continue

        position_data[position]['height'].append(height)
        position_data[position]['weight'].append(weight)

    plt.figure(figsize=(10, 6))

    for position, data in position_data.items():
        plt.scatter(data['height'], data['weight'], label=position)

    plt.xlabel('Height (inches)')
    plt.ylabel('Weight (lbs)')
    plt.title('Scatter Plot of Height and Weight by Position')
    plt.legend()
    plt.grid(True)
    plt.yticks(range(100, 400, 20))

    plt.show()

def main():
    db_file = 'final_proj.db'

    # Calculate average height and weight by position
    avg_data = calculate_avg_height_weight_by_position(db_file)

    # Write the calculated data to a text file
    write_avg_data_to_file(avg_data)

    # Plot bar charts
    plot_bar_charts(avg_data)

    # Plot scatter plot
    scatter_plot_height_weight_by_position(db_file)
    
if __name__ == "__main__":
    main()