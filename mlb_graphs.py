import sqlite3
import matplotlib.pyplot as plt
import pandas as pd

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
    
    # order for plot
    order = ['P','C','1B','2B','3B','SS','LF','CF','RF','OF','DH','2-Way']
    pos_df['Position'] = pd.Categorical(pos_df['Position'], categories=order, ordered=True)
    pos_df = pos_df.sort_values('Position')

    return pos_df

def create_boxplot(data):
    # fig = plt.boxplot(data['Position'], )
    pass

def main():
    try:
        # create a connection
        with sqlite3.connect("final_proj.db") as conn:
            print('Connection open')
            # create a cursor
            cur = conn.cursor()
            pos_df = get_data_by_pos(cur)
            # Create subplots
            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6), sharey=False)

            # Create boxplots for Weight in the first subplot
            pos_df.boxplot(column='Weight', by='Position', ax=axes[0], grid=False)
            axes[0].set_title('Weight by Position')
            axes[0].set_xlabel('Position')
            axes[0].set_ylabel('Weight')

            # Create boxplots for Height in the second subplot
            pos_df.boxplot(column='Height', by='Position', ax=axes[1], grid=False)
            axes[1].set_title('Height by Position')
            axes[1].set_xlabel('Position')
            axes[1].set_ylabel('Height')

            # Adjust layout
            plt.tight_layout()

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