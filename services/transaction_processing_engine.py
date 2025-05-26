import sys
import os
import streamlit as st

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from lib.db_methods import sqlite_db
from .account_management_system import AMS

class TPE:
    
    def __init__(self, from_account, to_account, amount, description, location = None, device = None):
        self.db = sqlite_db()
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount
        self.description = description
        self.location = location
        self.device = device
        
        self.sender = AMS(account_number = self.from_account)
        self.receiver = AMS(account_number = self.to_account)
        
    
    def debit_balance(self, account_number, amount):
        self.sender = AMS(account_number = self.from_account)
        self.sender_opening_balance = float(self.sender.account_balance)
        self.sender_closing_balance = float(self.sender.account_balance) - amount
        debit_query = f"UPDATE BANK_ACCOUNTS SET ACCOUNT_BALANCE = {self.sender_closing_balance} WHERE ACCOUNT_NUMBER = {account_number}"
        self.db.execute(debit_query)
    
    def credit_balance(self, account_number, amount):
        self.receiver = AMS(account_number = self.to_account)
        self.receiver_opening_balance = float(self.receiver.account_balance)
        self.receiver_closing_balance = float(self.receiver.account_balance) + amount
        credit_query = f"UPDATE BANK_ACCOUNTS SET ACCOUNT_BALANCE = {self.receiver_closing_balance} WHERE ACCOUNT_NUMBER = {account_number}"
        self.db.execute(credit_query)
    
    def next_transaction_id(self):
        last_transaction_id_query = "SELECT MAX(TRANSACTION_ID) AS TRANSACTION_ID FROM TRANSACTION_HISTORY"
        last_transaction_id = str(self.db.select_df(last_transaction_id_query)["TRANSACTION_ID"][0])
        next_transaction_id = "TRANS" + str(int(last_transaction_id[5:]) + 1).rjust(7, '0')
        return next_transaction_id
    
    def log_send_transaction(self):
        next_transaction_id = self.next_transaction_id()
        insert_query = f"""INSERT INTO TRANSACTION_HISTORY 
                        VALUES(
                                '{next_transaction_id}', 
                                '{self.from_account}', 
                                '{self.to_account}', 
                                '{self.sender.bank_id}', 
                                '{self.receiver.bank_id}', 
                                '{self.description}', 
                                {self.amount},
                                {self.sender_opening_balance},
                                {self.sender_closing_balance},
                                NULL,
                                NULL,
                                current_timestamp,
                                'IN TRANSIT',
                                '{self.location}',
                                '{self.device}',
                                current_timestamp,
                                current_timestamp
                            )"""
        
        self.db.execute(insert_query)
        return next_transaction_id
        
    
    def log_receive_transaction(self, transaction_id):
        update_query = f"""UPDATE TRANSACTION_HISTORY SET 
                            TARGET_OPENING_BALANCE = {self.receiver_opening_balance},
                            TARGET_CLOSING_BALANCE = {self.receiver_closing_balance},
                            STATUS = 'SUCCESS',
                            UPDATED_AT = CURRENT_TIMESTAMP
                        WHERE TRANSACTION_ID = '{transaction_id}'"""
        self.db.execute(update_query)
        
        
    def send_money(self, amount):
        # Check Balance
        balance, sufficient_balance = self.sender.check_balance(self.sender.account_number, amount)
        
        if sufficient_balance is True:
            self.debit_balance(account_number = self.from_account, amount = amount)
            transaction_id = self.log_send_transaction()
            self.credit_balance(account_number = self.to_account, amount = amount)
            self.log_receive_transaction(transaction_id)
            st.success(f"Amount of {self.amount} Rs transferred to account {self.to_account} successfully.")
            st.rerun()
            
        else:
            st.error(f"Insufficient Balance..! Account has {self.sender.account_balance} Rs balance. Cannot transfer amount Rs {self.amount} Rs.")
    
    