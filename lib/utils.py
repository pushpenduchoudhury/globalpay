import os
import uuid
import base64
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pytz import timezone as tzone
from pathlib import Path
import streamlit_authenticator as stauth
import yaml


load_dotenv()

logger = logging.getLogger(__name__)
logging.getLogger("py4j").setLevel(logging.INFO)

TIMEZONE = os.getenv("TIMEZONE")
TZ = tzone(TIMEZONE)
HOME_DIR = os.getenv("HOME_DIR")
LOG_DIR = os.getenv("LOG_DIR")
DB_DIR = os.getenv("DB_DIR")


def get_path(path_str, file = None):
    path = Path(path_str) if file is None else Path(path_str, file)
    return path

def get_env(variable_name):
    return os.getenv(variable_name)
    
def get_path_env(variable_name, file_name = None):
    path = get_path(os.getenv(variable_name)) if file_name is None else get_path(os.getenv(variable_name), file_name)
    return path

def get_logger(log_name, log_level):

    def timetz(*args):
        return datetime.now(TZ).timetuple()
    
    log_path = LOG_DIR
    logfilename = log_path + '/' + log_name + '_' + str(datetime.now(TZ).strftime("%Y_%m_%d-%I_%M_%S_%p")) + '.log'
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logging.Formatter.converter = timetz
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    file_handler = logging.FileHandler(logfilename, mode = 'w')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    # Set Log Level
    if (str(log_level).upper() == "DEBUG"):
        stream_handler.setLevel(logging.DEBUG)
    elif (str(log_level).upper() == "INFO"):
        stream_handler.setLevel(logging.INFO)
    elif (str(log_level).upper() == "WARN"):
        stream_handler.setLevel(logging.WARN)
    elif (str(log_level).upper() == "ERROR"):
        stream_handler.setLevel(logging.ERROR)
    else:
        stream_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def get_config():
    with open(Path(HOME_DIR, "creds.yaml")) as file:
        config = yaml.safe_load(file)
    return config


def base64_encode(string):
    base64_bytes = str(string).encode("ascii")
    encode_string_bytes = base64.b64encode(base64_bytes)
    encoded_string = encode_string_bytes.decode("ascii")
    return encoded_string


def base64_decode(encoded_string):
    base64_bytes = str(encoded_string).encode("ascii")
    decode_string_bytes = base64.b64decode(base64_bytes)
    decoded_string = decode_string_bytes.decode("ascii")
    return decoded_string

def generate_customer_id():
    return uuid.uuid4().int

def generate_account_number():
    ...
    
def hash_password(password):
    hashed_password = stauth.Hasher.hash(password = password)
    return hashed_password

def check_password(email_id, str_password) -> bool:
    config = get_config()
    hashed_password = config["credentials"]["usernames"][email_id]['password']
    is_valid = stauth.Hasher.check_pw(password = str_password, hashed_password = hashed_password)
    return is_valid

