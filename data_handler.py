# data_handler.py
import pandas as pd
from typing import Dict, Any
import ccxt

class DataHandler:
    def __init__(self, config: Dict[str, Any]):
        self.symbol = config['symbol']
        self.timeframe = config['timeframe']
        self.exchange = getattr(ccxt, config['exchange'])()

    def fetch_market_data(self) -> pd.DataFrame:
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df

    def get_latest_price(self) -> float:
        ticker = self.exchange.fetch_ticker(self.symbol)
        return ticker['last']

    def get_historical_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        start_timestamp = self.exchange.parse8601(start_date)
        end_timestamp = self.exchange.parse8601(end_date)
        
        all_ohlcv = []
        while start_timestamp < end_timestamp:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, since=start_timestamp)
            all_ohlcv.extend(ohlcv)
            if len(ohlcv) == 0:
                break
            start_timestamp = ohlcv[-1][0] + 1
        
        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df[df.index <= end_date]