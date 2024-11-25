
import pandas as pd
from typing import Dict, Any
import ccxt
import logging
from config import SYMBOL, TIMEFRAME, EXCHANGE_CONFIG, VOLATILITY_CONFIG
import pandas_ta as ta
import redis
import json
from datetime import datetime, timedelta

class DataHandler:
    def __init__(self):
        self.symbol = SYMBOL
        self.timeframe = TIMEFRAME
        self.exchange = getattr(ccxt, EXCHANGE_CONFIG['NAME'])()
        self.logger = logging.getLogger(__name__)
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    # ... (keep existing methods)

    def get_realtime_data(self) -> pd.DataFrame:
        """Get real-time data for the symbol."""
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            df = pd.DataFrame([ticker], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            self.logger.error(f"Error fetching real-time data: {str(e)}")
            return pd.DataFrame()


    def get_historical_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get historical data for the symbol."""
        try:
            start_timestamp = self.exchange.parse8601(start_date)
            end_timestamp = self.exchange.parse8601(end_date)
            
            all_ohlcv = []
            while start_timestamp < end_timestamp:
                ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, since=start_timestamp, limit=1000)
                if len(ohlcv) == 0:
                    break
                all_ohlcv.extend(ohlcv)
                start_timestamp = ohlcv[-1][0] + 1
            
            df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df[df.index <= end_date]
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {str(e)}")
            return pd.DataFrame()


    def get_cached_data(self, key: str) -> pd.DataFrame:
        """Retrieve data from Redis cache."""
        cached_data = self.redis_client.get(key)
        if cached_data:
            return pd.read_json(cached_data)
        return None

    def set_cached_data(self, key: str, data: pd.DataFrame, expiry: int = 300):
        """Store data in Redis cache with expiry in seconds."""
        self.redis_client.setex(key, expiry, data.to_json())

    def get_latest_data_with_cache(self, limit: int = 100) -> pd.DataFrame:
        """Get the latest data with caching."""
        cache_key = f"{self.symbol}_{self.timeframe}_{limit}"
        cached_data = self.get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data

        df = self.get_latest_data(limit)
        self.set_cached_data(cache_key, df)
        return df

    def identify_trend(self, data: pd.DataFrame) -> str:
        """Identify the current trend using SMA."""
        sma_short = data['close'].rolling(window=20).mean()
        sma_long = data['close'].rolling(window=50).mean()
        current_price = data['close'].iloc[-1]

        if current_price > sma_short.iloc[-1] > sma_long.iloc[-1]:
            return "UPTREND"
        elif current_price < sma_short.iloc[-1] < sma_long.iloc[-1]:
            return "DOWNTREND"
        else:
            return "SIDEWAYS"


    def get_latest_data(self, limit: int = 100) -> pd.DataFrame:
        """Get the latest data for the symbol."""
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            self.logger.error(f"Error fetching latest data: {str(e)}")
            return pd.DataFrame()

    def calculate_adaptive_volatility(self, data: pd.DataFrame) -> float:
        """Calculate adaptive volatility based on recent price movements."""
        returns = data['close'].pct_change().dropna()
        short_vol = returns.rolling(window=VOLATILITY_CONFIG['SHORT_WINDOW']).std().iloc[-1]
        long_vol = returns.rolling(window=VOLATILITY_CONFIG['LONG_WINDOW']).std().iloc[-1]
        return (short_vol + long_vol) / 2

    def get_market_data(self) -> Dict[str, Any]:
        """Get comprehensive market data including real-time data, volatility, and trend."""
        latest_data = self.get_latest_data_with_cache()
        realtime_data = self.get_realtime_data()

        if not latest_data.empty and not realtime_data.empty:
            volatility = self.calculate_adaptive_volatility(latest_data)
            trend = self.identify_trend(latest_data)
            
            # Calculate additional technical indicators
            latest_data['RSI'] = ta.rsi(latest_data['close'])
            latest_data['MACD'] = ta.macd(latest_data['close'])['MACD_12_26_9']
            latest_data['Signal'] = ta.macd(latest_data['close'])['MACDs_12_26_9']

            return {
                "latest_data": latest_data,
                "realtime_data": realtime_data,
                "volatility": volatility,
                "trend": trend,
                "current_price": realtime_data['close'].iloc[-1],
                "24h_volume": realtime_data['volume'].iloc[-1],
                "rsi": latest_data['RSI'].iloc[-1],
                "macd": latest_data['MACD'].iloc[-1],
                "macd_signal": latest_data['Signal'].iloc[-1]
            }
        else:
            self.logger.error("Failed to fetch market data")
            return {}


