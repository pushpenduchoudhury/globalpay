import sys
import os
import streamlit as st

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from lib.db_methods import sqlite_db

class AMS:
    
    def __init__(self, email):
        self.db = sqlite_db()
        self.email_id = email
        
        customer_query = f"""SELECT 
                                CUSTOMER_ID, 
                                FIRST_NAME, 
                                LAST_NAME, 
                                ROLE, 
                                EMAIL_ID, 
                                PHONE_NUMBER, 
                                ADDRESS, 
                                GEO_LOCATION_ID, 
                                DEVICE_ID 
                            FROM CUSTOMER 
                            WHERE EMAIL_ID = '{self.email_id}'"""
        print(customer_query)
        df_customer = self.db.select_df(customer_query)
        
        self.customer_id = str(df_customer['CUSTOMER_ID'][0])
        self.name = f"{str(df_customer['FIRST_NAME'][0])} {str(df_customer['LAST_NAME'][0])}"
        self.role = str(df_customer['ROLE'][0])
        self.phone_number = str(df_customer['PHONE_NUMBER'][0])
        self.address = str(df_customer['ADDRESS'][0])
        self.geo_location_id = str(df_customer['GEO_LOCATION_ID'][0])
        self.device_id = str(df_customer['DEVICE_ID'][0])
        
        
        account_query = f"""SELECT 
                                BANK_DIM.BANK_NAME,
                                BANK_ACCOUNTS.ACCOUNT_NUMBER, 
                                BANK_ACCOUNTS.ACCOUNT_TYPE, 
                                BANK_ACCOUNTS.ACCOUNT_BALANCE
                            FROM BANK_ACCOUNTS 
                            INNER JOIN BANK_DIM
                            ON (BANK_ACCOUNTS.BANK_ID = BANK_DIM.BANK_ID)
                            WHERE BANK_ACCOUNTS.CUSTOMER_ID = '{self.customer_id}'"""
        self.df_account = self.db.select_df(account_query)
        
        list_account_numbers = self.df_account["ACCOUNT_NUMBER"].to_list()
        
        
        transaction_query = f"""
                                SELECT
                                    TRANSACTION_TIME AS DATE,
                                    DESCRIPTION,
                                    TRANSACTION_ID AS REF,
                                    CASE WHEN TYPE = 'DEBIT' THEN AMOUNT ELSE '' END AS WITHDRAWAL,
                                    CASE WHEN TYPE = 'CREDIT' THEN AMOUNT ELSE '' END AS DEPOSIT,
                                    SOURCE_CLOSING_BALANCE AS BALANCE
                                FROM
                                (
                                    SELECT
                                        TRANSACTION_ID,
                                        SOURCE_ACCOUNT_NUMBER,
                                        TARGET_ACCOUNT_NUMBER,
                                        DESCRIPTION,
                                        AMOUNT,
                                        'DEBIT' AS TYPE,
                                        SOURCE_OPENING_BALANCE,
                                        SOURCE_CLOSING_BALANCE,
                                        TRANSACTION_TIME
                                    FROM TRANSACTION_HISTORY
                                    WHERE SOURCE_ACCOUNT_NUMBER IN ({', '.join(["'{}'".format(value) for value in list_account_numbers])})
                                    UNION ALL
                                    SELECT
                                        TRANSACTION_ID,
                                        SOURCE_ACCOUNT_NUMBER,
                                        TARGET_ACCOUNT_NUMBER,
                                        DESCRIPTION,
                                        AMOUNT,
                                        'CREDIT' AS TYPE,
                                        SOURCE_OPENING_BALANCE,
                                        SOURCE_CLOSING_BALANCE,
                                        TRANSACTION_TIME
                                    FROM TRANSACTION_HISTORY
                                    WHERE TARGET_ACCOUNT_NUMBER IN ({', '.join(["'{}'".format(value) for value in list_account_numbers])})
                                )
                                ORDER BY TRANSACTION_TIME DESC
                                LIMIT {st.session_state.n_records if "n_records" in st.session_state else 5}"""
        
        self.df_transaction_history = self.db.select_df(transaction_query)
        
        
        # for i in len(df_account):
            
        # self.account_details = {}
        # for account_number, account_balance in result:
        #     self.account_details[account_number] = self.account_details.get(account_number, []) + [account_balance]

        
    
    