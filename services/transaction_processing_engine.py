import os
import sys
import time
import streamlit as st

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from lib.db_methods import sqlite_db
from .account_management_system import AMS
from .fraud_detection_engine import FDE

class TPE:
    
    def __init__(self, from_account, to_account, amount, description, location = None, device = None, step = 1):
        self.db = sqlite_db()
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount
        self.description = description
        self.location = location
        self.device = device
        self.step = step
        
        self.sender = AMS(account_number = self.from_account)
        self.receiver = AMS(account_number = self.to_account)
        
    
    def debit_balance(self, account_number, amount):
        self.sender_opening_balance = float(self.sender.account_balance)
        self.sender_closing_balance = float(self.sender.account_balance) - amount
        debit_query = f"UPDATE BANK_ACCOUNTS SET ACCOUNT_BALANCE = {self.sender_closing_balance} WHERE ACCOUNT_NUMBER = {account_number}"
        status = self.db.execute(debit_query)
        return status
    
    def credit_balance(self, account_number, amount):
        self.receiver_opening_balance = float(self.receiver.account_balance)
        self.receiver_closing_balance = float(self.receiver.account_balance) + amount
        credit_query = f"UPDATE BANK_ACCOUNTS SET ACCOUNT_BALANCE = {self.receiver_closing_balance} WHERE ACCOUNT_NUMBER = {account_number}"
        status = self.db.execute(credit_query)
        return status
    
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
        
        status = self.db.execute(insert_query)
        return next_transaction_id, status
        
    
    def log_receive_transaction(self, transaction_id):
        update_query = f"""UPDATE TRANSACTION_HISTORY SET 
                            TARGET_OPENING_BALANCE = {self.receiver_opening_balance},
                            TARGET_CLOSING_BALANCE = {self.receiver_closing_balance},
                            STATUS = 'SUCCESS',
                            UPDATED_AT = CURRENT_TIMESTAMP
                        WHERE TRANSACTION_ID = '{transaction_id}'"""
        status = self.db.execute(update_query)
        return status
        
        
    def send_money(self, amount):
        # Check Balance
        balance, sufficient_balance = self.sender.check_balance(self.sender.account_number, amount)
        fraud_detection_model = FDE(st.session_state.fraud_detection_model)

        if sufficient_balance is True:            
            with st.status("Processing your transaction...", expanded = True, state = "running") as status:
                sleep = 1
                progress_step = 20
                percent_complete = 0
                success = ":green[✔] - "
                fail = ":red[✖] - "
                alert = ":orange[⚠︎] - "
                
                progress_bar = st.progress(percent_complete, text = ":grey[Processing transaction...]")
                time.sleep(sleep)
                
                ####### Debit from sender #######
                progress_bar.progress(percent_complete+2, text = ":grey[Debiting amount from account]")
                response = self.debit_balance(account_number = self.from_account, amount = amount)
                time.sleep(sleep)
                if response:
                    st.markdown("###### Steps:")
                    st.markdown(success + ":grey[1. Debited amount from account...]")
                else:
                    st.markdown(fail + ":grey[1. Debiting amount from account...]")
                    status.update(label = "Error debiting from sender...!", state = "error", expanded = True)
                    st.button("OK", on_click = lambda: st.rerun)
                    st.stop()
                
                ####### Log Debit transaction #######    
                percent_complete += progress_step
                progress_bar.progress(percent_complete, text = ":grey[Logging debit transaction]")
                transaction_id, response = self.log_send_transaction()
                time.sleep(sleep)
                if response:
                    st.markdown(success + ":grey[2. Debit transaction logged...]")
                else:
                    st.markdown(fail + ":grey[2. Logging debit transaction...]")
                    status.update(label = "Error in transaction...!", state = "error", expanded = True)
                    st.button("OK", on_click = lambda: st.rerun)
                    st.stop()
                    
                ####### Credit to receiver #######    
                percent_complete += progress_step
                progress_bar.progress(percent_complete, text = ":grey[Crediting amount to receiver]")
                response = self.credit_balance(account_number = self.to_account, amount = amount)
                time.sleep(sleep)
                if response:
                    st.markdown(success + ":grey[3. Credited amount to receiver...]")
                else:
                    st.markdown(fail + ":grey[3. Crediting amount to receiver...]")
                    status.update(label = "Error crediting to receiver...!", state = "error", expanded = True)
                    st.button("OK", on_click = lambda: st.rerun)
                    st.stop()
                    
                ####### Log credit transaction #######    
                percent_complete += progress_step
                progress_bar.progress(percent_complete, text = ":grey[Logging credit transaction]")
                response = False #self.log_receive_transaction(transaction_id)
                time.sleep(sleep)
                if response:
                    st.markdown(success + ":grey[4. Credit transaction logged...]")
                else:
                    st.markdown(fail + ":grey[4. Logging credit transaction...]")
                    status.update(label = "Error in transaction...!", state = "error", expanded = True)
                    st.button("OK", on_click = lambda: st.rerun)
                    st.stop()
                    
                ####### Fraud detection #######    
                percent_complete += progress_step
                progress_bar.progress(percent_complete, text = ":grey[Checking for fradulent activity]")
                model_features = [self.step, self.amount,
                                  self.sender_opening_balance, self.sender_closing_balance,
                                  self.receiver_opening_balance, self.receiver_closing_balance,
                                  0, False, False, False, True]
                is_fraud = fraud_detection_model.predict(*model_features)
                time.sleep(sleep)
                if not is_fraud:
                    st.markdown(success + ":grey[5. No fradulent activity detected...!]")                    
                    percent_complete += progress_step
                    status.update(label = "Transaction complete...!", state = "complete", expanded = True)
                    progress_bar.progress(percent_complete, text = ":green[Success...!]")
                    st.success(f"Amount of {self.amount} Rs transferred to account {self.to_account} successfully.")
                else:
                    st.markdown(alert + ":grey[5. Fradulent activity detected...!]")
                    status.update(label = "Potential fraud detected...!", state = "error", expanded = True)
                    st.warning(f"Potential fraud detected in this transaction...!")
                    
                st.button("OK", on_click = lambda: st.rerun)
            #     time.sleep(sleep + 30)

            # st.rerun()
            
        else:
            st.error(f"Insufficient Balance..! Account has {self.sender.account_balance} Rs balance. Cannot transfer amount Rs {self.amount} Rs.")
    

