import os

from binance.client import Client
from conf import BINANCE_SECRET_KEY, BINANCE_API_KEY


def get_client(env='DEV'):
    if env == 'DEV':
        api_key = BINANCE_API_KEY
        api_secret = BINANCE_SECRET_KEY
    elif env == 'PROD':
        api_key = os.environ.get('binance_api')
        api_secret = os.environ.get('binance_secret')
    client = Client(api_key, api_secret)
    if env == 'DEV':
        client.API_URL = 'https://api.binance.us'
    return client
