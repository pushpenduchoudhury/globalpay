import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from lib.db_methods import sqlite_db

class AMS:
    
    def __init__(self, customer_id, account_number = None):
        self.db = sqlite_db()
        self.customer_id = customer_id
        self.account_number = account_number
        
        query_balance = f"SELECT ACCOUNT_BALANCE FROM BANK_ACCOUNTS WHERE CUSTOMER_ID = '{self.customer_id}'"
        df = self.db.select(query_balance)
        self.account_balance = df["ACCOUNT_BALANCE"][0]
    
    def get_statement(n_transactions):
        ...
    
    