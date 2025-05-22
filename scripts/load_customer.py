import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from lib.db_methods import sqlite_db
from lib import utils

TABLE_NAME = "CUSTOMER"
file_name = "customer.csv"
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
    CUSTOMER_ID VARCHAR(10),
    FIRST_NAME VARCHAR(100),
    LAST_NAME VARCHAR(100),
    ROLE VARCHAR(10),
    EMAIL_ID VARCHAR(50),
    PHONE_NUMBER VARCHAR(15),
    ADDRESS VARCHAR(500),
    GEO_LOCATION_ID VARCHAR(20),
    DEVICE_ID VARCHAR(20)
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

