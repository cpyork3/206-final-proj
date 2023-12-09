import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import json
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# run SQL query, get data as pandas dataframe
def get_data_by_pos(cur):
    
    # get data from data base 
        # group by position
        # join with position id table to get position name
    cur.execute('''SELECT
                        mlb_playerinfo.pos_id,
                        mlb_playerinfo.height,
                        mlb_playerinfo.weight,
                        mlb_pos_ids.pos  
                    FROM
                        mlb_playerinfo
                    JOIN
                        mlb_pos_ids ON mlb_pos_ids.id = mlb_playerinfo.pos_id''')
    data_list = cur.fetchall()

    # convert to data frame for easier graphing
    pos_df = pd.DataFrame(data_list, 
                          columns = ['pos_id', 'Height', 'Weight', 'Position'])
    
    q = pos_df.groupby('pos_id').quantile(1).reset_index()
    print(q['Height'][0])
    
    # order for plot
    order = ['P','C','1B','2B','3B','SS','LF','CF','RF','OF','DH','2-Way']
    pos_df['Position'] = pd.Categorical(pos_df['Position'], categories=order, ordered=True)
    pos_df = pos_df.sort_values('Position')

    return pos_df

def write_data(df, file_name = 'mlb_calculations.json'):
    # get data for each quartile and median
    max_df = df.groupby('pos_id').max().reset_index()
    q3_df = df.groupby('pos_id').quantile(0.75).reset_index()
    q2_df = df.groupby('pos_id').quantile(0.5).reset_index()
    q1_df = df.groupby('pos_id').quantile(0.25).reset_index()
    min_df = df.groupby('pos_id').min().reset_index()

    # create dict for posiiton codes
    position_dict = {1:'P', 2:'C', 3:'1B', 4:'2B', 5:'3B', 6:'SS', 7:'LF', 8:'CF', 9:'RF', 10:'DH', 11:'OF', 12:"2-Way"}

    # create empty dict
    ranges = {}

    for i in range(0, 11):
        ranges[position_dict[max_df['pos_id'][i]]] = {'Height': 
                                                    {'Max': max_df['Height'][i],
                                                    'Q3': q3_df['Height'][i],
                                                    'Median': q2_df['Height'][i],
                                                    'Q1': q1_df['Height'][i],
                                                    'Min': min_df['Height'][i]},
                                                    'Weight':
                                                    {'Max': max_df['Weight'][i],
                                                    'Q3': q3_df['Weight'][i],
                                                    'Median': q2_df['Weight'][i],
                                                    'Q1': q1_df['Weight'][i],
                                                    'Min': min_df['Weight'][i]}}
        
        # make so able to write to json
        def convert_to_serializable(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            raise TypeError("Type not serializable")
        
        # dump dictionary
        with open(file_name, 'w') as file:
            json.dump(ranges, file, indent=2, default = convert_to_serializable)
    
    return

def main():
    try:
        # create a connection
        with sqlite3.connect("API_beasts.db") as conn:
            print('Connection open')
            # create a cursor
            cur = conn.cursor()

            # get data as pd df
            pos_df = get_data_by_pos(cur)

            # write data to txt file
            write_data(pos_df)

            # Create subplots
            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))
            sns.set_palette("pastel")

            # Create boxplots for Weight in the first subplot
            sns.boxplot(x='Position', y='Weight', data=pos_df, ax=axes[0], width=0.4, linewidth=1.5)
            axes[0].set_title('Weight by Position')
            axes[0].set_xlabel('Position')
            axes[0].set_ylabel('Weight (lb)')

            # Create boxplots for Height in the second subplot
            sns.boxplot(x='Position', y='Height', data=pos_df, ax=axes[1], width=0.4, linewidth=1.5)
            axes[1].set_title('Height by Position')
            axes[1].set_xlabel('Position')
            axes[1].set_ylabel('Height (in)')

            # Adjust layout
            plt.tight_layout(rect=[0, .03, 1, 0.96])

            # Add a title to the overall figure
            plt.suptitle('MLB Distribution of Weight and Height by Position (2023)', y=.99, fontsize=16)

            # Show the plot
            plt.show()

        print('Connection closed')

    except sqlite3.Error as e:
        # Handle the error
        conn.close()
        print('Connection closed')
        print("SQLite error:", e)

if __name__ == "__main__":
    main()