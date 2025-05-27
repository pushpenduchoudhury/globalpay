import os
import sys
import streamlit as st

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from lib import utils


class FDE:
    def __init__(self, model):
        self.model = model
        self.model_dir = utils.get_path_env("MODEL_DIR")

    
    def detect_fraud(self, amount):
        if amount > 500:  # Example threshold
            return True  # Fraud detected
        return False  # No fraud detected