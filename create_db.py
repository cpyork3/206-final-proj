import sqlite3
import os

def create_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn

def main():
    cur, conn = create_database('final_proj.db')
    print(cur, conn)

if __name__ == "__main__":
    main()