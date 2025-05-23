import sqlite3
from lib import utils
import pandas as pd


class sqlite_db:
    
    def __init__(self):
        self.DB_NAME = utils.get_path_env("DB_NAME")

    def get_connection(self):
        conn = sqlite3.connect(self.DB_NAME)
        return conn

    def execute(self, query):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        
    def select_df(self, query):
        conn = self.get_connection()
        df = pd.read_sql(sql = query, con = conn)
        return df

    def select(self, query):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return rows, column_names
    
    def insert_csv(self, csv_file, table_name):
        import csv
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            with open(csv_file, 'r') as file:
                reader = csv.reader(file)
                header = next(reader)

                placeholders = ', '.join(['?'] * len(header))

                # Insert data row by row
                for row in reader:
                    print(f"Record: {row}")
                    cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row)
            
            conn.commit()
            print(f"Data from '{csv_file}' inserted into table '{table_name}' successfully.")
        
        except Exception as e:
            print(f"An error occurred: {e}")
        
        finally:
            if conn:
                conn.close()