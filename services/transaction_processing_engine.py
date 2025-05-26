import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from lib.db_methods import sqlite_db
from account_management_system import AMS

class TPE:
    
    def __init__(self, from_account, to_account, amount, location = None, device = None):
        self.db = sqlite_db()
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount
        self.location = location
        self.device = device
        
        sender_customer = AMS(account_number = self.from_account)
        receiver_customer = AMS(account_number = self.to_account)
        
      
    
    def send_money(n_transactions):
        ...
    
    