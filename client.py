from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
from typing import Optional
import logging

# Set up basic logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BinanceDataFetcher:
    def __init__(
        self,
        use_us: bool = False,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
    ):
        self.use_us = use_us
        logger.info(
            f"Initializing BinanceDataFetcher with {'US' if use_us else 'COM'} endpoint"
        )
        # Initialize spot client
        self.client = Client(
            api_key=api_key,
            api_secret=api_secret,
            tld='us' if use_us else 'com',
        )
        # Initialize futures client
        if not use_us:  # Futures only available on binance.com
            self.futures_client = Client(
                api_key=api_key,
                api_secret=api_secret,
            )

    def get_symbol(self, base: str, quote: str = 'USDT') -> str:
        """Format symbol according to exchange requirements"""
        # if self.use_us and quote == 'USDT':
        #     quote = 'USD'  # Binance.US uses USD instead of USDT for most pairs
        return f"{base}{quote}"

    def get_klines(
        self,
        base: str,
        quote: str = 'USDT',
        interval: str = '1d',
        limit: int = 100,
    ):
        """
        Fetch kline/candlestick data with automatic error handling and retries
        """
        symbol = self.get_symbol(base, quote)
        logger.info(f"Fetching {interval} klines for {symbol}")

        try:
            klines = self.client.get_klines(
                symbol=symbol, interval=interval, limit=limit
            )
            logger.debug(
                f"Successfully fetched {len(klines)} klines for {symbol}"
            )

            df = pd.DataFrame(
                klines,
                columns=[
                    'timestamp',
                    'open',
                    'high',
                    'low',
                    'close',
                    'volume',
                    'close_time',
                    'quote_volume',
                    'trades',
                    'taker_buy_base',
                    'taker_buy_quote',
                    'ignore',
                ],
            )

            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Convert price and volume columns to float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)

            return df

        except BinanceAPIException as e:
            logger.warning(f"Error fetching klines for {symbol}: {str(e)}")
            if "Invalid symbol" in str(e):
                if quote == 'USDT' and not self.use_us:
                    logger.info(f"Retrying with USD quote currency for {base}")
            raise e

    def get_current_price(self, base: str, quote: str = 'USDT') -> float:
        """Get current price for a symbol"""
        symbol = self.get_symbol(base, quote)
        logger.info(f"Fetching current price for {symbol}")
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except BinanceAPIException as e:
            logger.warning(f"Error fetching price for {symbol}: {str(e)}")
            if "Invalid symbol" in str(e):
                if quote == 'USDT' and not self.use_us:
                    return self.get_current_price(base, quote='USD')
            raise e

    def get_futures_symbol(self, base: str, quote: str = 'USDT') -> str:
        """Format futures symbol according to exchange requirements"""
        # For Binance Futures, the format is simply BTCUSDT (no _PERP suffix)
        return f"{base}{quote}"

    def get_futures_klines(
        self,
        base: str,
        quote: str = 'USDT',
        interval: str = '1d',
        limit: int = 100,
        contract_type: str = 'PERPETUAL',
    ):
        """
        Fetch futures kline/candlestick data
        """
        if self.use_us:
            raise BinanceAPIException(
                "Futures trading not available on Binance.US"
            )

        symbol = self.get_futures_symbol(base, quote)
        logger.info(f"Fetching futures {interval} klines for {symbol}")

        try:
            klines = self.futures_client.futures_klines(
                symbol=symbol, interval=interval, limit=limit
            )
            logger.debug(
                f"Successfully fetched {len(klines)} futures klines for {symbol}"
            )

            df = pd.DataFrame(
                klines,
                columns=[
                    'timestamp',
                    'open',
                    'high',
                    'low',
                    'close',
                    'volume',
                    'close_time',
                    'quote_volume',
                    'trades',
                    'taker_buy_base',
                    'taker_buy_quote',
                    'ignore',
                ],
            )

            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Convert price and volume columns to float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)

            return df

        except BinanceAPIException as e:
            logger.warning(
                f"Error fetching futures klines for {symbol}: {str(e)}"
            )
            raise e


# For Binance.com (default)
fetcher = BinanceDataFetcher()
btc_data = fetcher.get_klines('BTC')

# For Binance.US
us_fetcher = BinanceDataFetcher(use_us=True)
btc_data_us = us_fetcher.get_klines('BTC')


# Try both automatically
def get_best_available_data(base: str = 'BTC'):
    logger.info(f"Attempting to fetch data for {base} from available exchanges")
    # for use_us in [True, False]:
    for use_us in [False, True]:
        try:
            fetcher = BinanceDataFetcher(use_us=use_us)
            return fetcher.get_klines(base)
        except BinanceAPIException:
            logger.warning(
                f"Failed to fetch from {'Binance.US' if use_us else 'Binance.com'}"
            )
            continue
    logger.error(
        f"Failed to fetch data for {base} from all available exchanges"
    )
    raise Exception(
        "Could not fetch data from either Binance.com or Binance.US"
    )


if __name__ == '__main__':
    df = get_best_available_data()
    print(df)
