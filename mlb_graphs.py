import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

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

def main():
    try:
        # create a connection
        with sqlite3.connect("final_proj.db") as conn:
            print('Connection open')
            # create a cursor
            cur = conn.cursor()
            pos_df = get_data_by_pos(cur)
            sns.set_palette("pastel")

            # Create subplots
            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

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