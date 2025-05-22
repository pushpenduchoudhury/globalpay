import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from lib.db_methods import sqlite_db
from lib import utils

TABLE_NAME = "TRANSACTION_HISTORY"
file_name = "transaction_history.csv"
csv_data_file = utils.get_path_env("DATA_DIR", file_name)

########## Connect to Database ##########
try:
    print(f"Connecting to Database...")
    db = sqlite_db()

except Exception as e:
    print(f"Error: {str(e)}")
    
########## Drop table ##########
try:
    drop_table = f"DROP TABLE IF EXISTS {TABLE_NAME}"
    print(f"Executing Query: {drop_table}")
    db.execute(drop_table)
except Exception as e:
    print(f"Error: {str(e)}")

########## Create table ##########
try:
    create_table = f"""
CREATE TABLE {TABLE_NAME}
(
    TRANSACTION_ID VARCHAR(10),
    SOURCE_ACCOUNT_NUMBER VARCHAR(20),
    TARGET_ACCOUNT_NUMBER VARCHAR(20),
    SOURCE_BANK_ID VARCHAR(20),
    TARGET_BANK_ID VARCHAR(20),
    DESCRIPTION VARCHAR(200),
    AMOUNT FLOAT,
    SOURCE_OPENING_BALANCE FLOAT,
    SOURCE_CLOSING_BALANCE FLOAT,
    TARGET_OPENING_BALANCE FLOAT,
    TARGET_CLOSING_BALANCE FLOAT,
    TRANSACTION_TIME TIMESTAMP,
    STATUS VARCHAR(20),
    GEO_LOCATION_ID VARCHAR(20),
    DEVICE_ID VARCHAR(20),
    CREATED_AT TIMESTAMP,
    UPDATED_AT TIMESTAMP
)"""
    print(f"Executing Query: {create_table}")
    db.execute(create_table)

except Exception as e:
    print(f"Error: {str(e)}")


########## Insert data into table ##########
try:
    print(f"Inserting Data from file: {csv_data_file}")
    db.insert_csv(csv_file = csv_data_file, table_name = TABLE_NAME)

except Exception as e:
    print(f"Error: {str(e)}")