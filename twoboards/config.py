import os


def get_list(key):
    value = os.environ[key]
    return [item.strip() for item in os.environ[key].split(',')]


API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
TOKEN = os.environ['TOKEN']

PRODUCT_BOARD_ID = os.environ['PRODUCT_BOARD_ID']
TECH_BOARD_ID = os.environ['TECH_BOARD_ID']

PRE_PIPELINE = get_list('PRE_PIPELINE')
PIPELINE = get_list('PIPELINE')
POST_PIPELINE = get_list('POST_PIPELINE')
