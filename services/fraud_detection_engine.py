import os
import sys
import pickle
import streamlit as st

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from lib import utils


class FDE:
    def __init__(self, model_name):
        self.model_name = model_name
        with open(utils.get_path_env("MODEL_DIR", self.model_name), 'rb') as file:
            self.model = pickle.load(file)

    def test_fraud(self, amount):
        if amount > 500:
            return True
        return False
    
    def predict(self, step, amount, sender_opening_balance, sender_closing_balance, receiver_opening_balance, receiver_closing_balance, isFlaggedFraud, cash_out, debit, payment, transfer):
        features = [[step, amount, sender_opening_balance, sender_closing_balance, receiver_opening_balance, receiver_closing_balance, isFlaggedFraud, cash_out, debit, payment, transfer]]
        model_prediction = self.model.predict(features)
        isFraud = True if model_prediction[0] == 1 else False
        return isFraud
    
    
        