import os
import sys
import streamlit as st

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from lib.db_methods import sqlite_db

class AMS:
    
    def __init__(self, email = None, account_number = None):
        self.db = sqlite_db()
        self.email_id = email
        self.account_number = account_number
        
        if email is not None:
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
            self.accounts = self.df_account["ACCOUNT_NUMBER"].to_list()
            
            # self.df_transaction_history = self.get_statement(st.session_state.n_records if "n_records" in st.session_state else 5, mode = "df")
        
        if account_number is not None:
            customer_details_query = f"""SELECT
                        BANK_DIM.BANK_NAME,
                        BANK_DIM.BANK_ID,
                        BANK_ACCOUNTS.CUSTOMER_ID,
                        CUSTOMER.FIRST_NAME, 
                        CUSTOMER.LAST_NAME, 
                        CUSTOMER.ROLE, 
                        CUSTOMER.EMAIL_ID, 
                        CUSTOMER.PHONE_NUMBER, 
                        CUSTOMER.ADDRESS, 
                        CUSTOMER.GEO_LOCATION_ID, 
                        CUSTOMER.DEVICE_ID,
                        BANK_ACCOUNTS.ACCOUNT_NUMBER, 
                        BANK_ACCOUNTS.ACCOUNT_TYPE, 
                        BANK_ACCOUNTS.ACCOUNT_BALANCE
                    FROM BANK_ACCOUNTS 
                    INNER JOIN BANK_DIM
                    ON (BANK_ACCOUNTS.BANK_ID = BANK_DIM.BANK_ID)
                    INNER JOIN CUSTOMER
                    ON (BANK_ACCOUNTS.CUSTOMER_ID = CUSTOMER.CUSTOMER_ID)
                    WHERE BANK_ACCOUNTS.ACCOUNT_NUMBER = '{self.account_number}'"""

            df_customer = self.db.select_df(customer_details_query)
            
            self.customer_id = str(df_customer['CUSTOMER_ID'][0])
            self.name = f"{str(df_customer['FIRST_NAME'][0])} {str(df_customer['LAST_NAME'][0])}"
            self.role = str(df_customer['ROLE'][0])
            self.phone_number = str(df_customer['PHONE_NUMBER'][0])
            self.address = str(df_customer['ADDRESS'][0])
            self.geo_location_id = str(df_customer['GEO_LOCATION_ID'][0])
            self.device_id = str(df_customer['DEVICE_ID'][0])
            self.account_type = str(df_customer['ACCOUNT_TYPE'][0])
            self.account_balance = str(df_customer['ACCOUNT_BALANCE'][0])
            self.bank_name = str(df_customer['BANK_NAME'][0])
            self.bank_id = str(df_customer['BANK_ID'][0])
        
        
    def check_balance(self, account_number, amount = None):
        balance_query = f"SELECT ACCOUNT_BALANCE FROM BANK_ACCOUNTS WHERE ACCOUNT_NUMBER = '{account_number}'"
        balance = self.db.select_df(balance_query)["ACCOUNT_BALANCE"][0]
        balance = float(balance)
        
        
        
        if amount is None:
            return balance
        else:
            amount = float(amount)
            balance_check = True if amount <= balance else False
            return balance, balance_check
    
    
    def get_statement(self, account_number, n_transactions = None, period = None, from_date = None, to_date = None, mode = None):
        
        filter_condition = ""
        limit_condition = ""
        
        if period == 1:
            filter_condition = "WHERE TRANSACTION_TIME >= DATE('now', 'start of month')"
        elif period == 2:
            filter_condition = "WHERE TRANSACTION_TIME >= DATE('now', 'start of month', '-1 month') AND TRANSACTION_TIME < DATE('now', 'start of month')"
        elif period == 3:
            filter_condition = "WHERE TRANSACTION_TIME >= DATE('now', 'start of month', '-3 months')"
        elif from_date is not None and to_date is not None:
            filter_condition = f"WHERE TRANSACTION_TIME >= DATE('{from_date.strftime('%Y-%m-%d')}') AND TRANSACTION_TIME <= DATE('{to_date.strftime('%Y-%m-%d')}')"
                
        if n_transactions is not None:
            limit_condition = f"LIMIT {n_transactions if n_transactions is not None else st.session_state.n_records if 'n_records' in st.session_state else 5}"
        
        transaction_query = f"""
                                SELECT
                                    TRANSACTION_TIME AS DATE,
                                    DESCRIPTION,
                                    TRANSACTION_ID AS REF,
                                    CASE WHEN TYPE = 'DEBIT' THEN CAST(AMOUNT AS CHAR) ELSE '' END AS WITHDRAWAL,
                                    CASE WHEN TYPE = 'CREDIT' THEN CAST(AMOUNT AS CHAR) ELSE '' END AS DEPOSIT,
                                    CAST(SOURCE_CLOSING_BALANCE AS CHAR) AS BALANCE
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
                                    WHERE SOURCE_ACCOUNT_NUMBER = '{account_number}'
                                    UNION ALL
                                    SELECT
                                        TRANSACTION_ID,
                                        SOURCE_ACCOUNT_NUMBER,
                                        TARGET_ACCOUNT_NUMBER,
                                        DESCRIPTION,
                                        AMOUNT,
                                        'CREDIT' AS TYPE,
                                        TARGET_OPENING_BALANCE,
                                        TARGET_CLOSING_BALANCE,
                                        TRANSACTION_TIME
                                    FROM TRANSACTION_HISTORY
                                    WHERE TARGET_ACCOUNT_NUMBER = '{account_number}'
                                )
                                """ + filter_condition + " ORDER BY TRANSACTION_TIME DESC" + " " + limit_condition
        
        if mode == "df":
            statement = self.db.select_df(transaction_query)
        else:
            statement = self.db.select(transaction_query)
        
        return statement
    
    
    def generate_statement_pdf(self, account_number, n_transactions = None, period = None, from_date = None, to_date = None):
        from fpdf import FPDF
        
        statement, columns = self.get_statement(account_number, n_transactions, period = period, from_date = from_date, to_date = to_date)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size = 15)
        pdf.cell(200, 10, txt = self.name, ln = 1, align = 'C')
        pdf.cell(200, 10, txt = f'Account: {account_number}', ln = 1, align = 'C')
        pdf.set_font("Arial", size = 5)
        pdf.cell(100, 5, txt = str('\t\t\t\t|\t\t'.join(columns)), ln = 1, align = 'C', border = 1)
        for row in statement:
            pdf.cell(100, 5, txt = str('\t\t\t\t|\t\t'.join(row)), ln = 1, align = 'L', border = 1)
        
        output_file = f"{os.getenv('HOME_DIR')}/landing/statement.pdf"
        pdf.output(output_file)
        return output_file
        
    def get_beneficiaries(self):
        # account_query = f"""SELECT 
        #                         CUSTOMER.FIRST_NAME || ' - ' || BANK_ACCOUNTS.ACCOUNT_NUMBER || ' (' || BANK_DIM.BANK_NAME || ')' AS BENEFICIARY
        #                     FROM BANK_ACCOUNTS
        #                     INNER JOIN CUSTOMER
        #                     ON BANK_ACCOUNTS.CUSTOMER_ID = CUSTOMER.CUSTOMER_ID
        #                     INNER JOIN BANK_DIM
        #                     ON BANK_ACCOUNTS.BANK_ID = BANK_DIM.BANK_ID"""
        
        account_query = f"""SELECT 
                                ACCOUNT_NUMBER AS BENEFICIARY
                            FROM BANK_ACCOUNTS"""
        
        beneficiaries = self.db.select_df(account_query)["BENEFICIARY"].to_list()
        return beneficiaries