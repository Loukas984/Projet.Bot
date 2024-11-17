"""
Configuration file for the advanced crypto trading bot.

This file contains all the configurable parameters for the trading bot.
Sensitive information like API keys should be set as environment variables.
Other parameters can be adjusted here to modify the bot's behavior.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Trading parameters
SYMBOL = os.getenv('SYMBOL', 'HMSTR/USDT')
TIMEFRAME = os.getenv('TIMEFRAME', '1m')
INITIAL_BALANCE = float(os.getenv('INITIAL_BALANCE', '10'))  # USDT

# API credentials (loaded from environment variables)
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

if not API_KEY or not API_SECRET:
    raise ValueError("API_KEY and API_SECRET must be set in the .env file")

# Risk management parameters
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '0.1'))  # 10% of portfolio
STOP_LOSS_PCT = float(os.getenv('STOP_LOSS_PCT', '0.02'))  # 2% stop loss
TAKE_PROFIT_PCT = float(os.getenv('TAKE_PROFIT_PCT', '0.05'))  # 5% take profit

# Optimization parameters
OPTIMIZATION_INTERVAL = int(os.getenv('OPTIMIZATION_INTERVAL', '24'))  # hours
OPTIMIZATION_DAYS = int(os.getenv('OPTIMIZATION_DAYS', '30'))  # days to use for optimization

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'trading_bot.log')

# Strategy parameters (initial values, will be optimized)
STRATEGY_PARAMS = {
    'SMA_SHORT': int(os.getenv('SMA_SHORT', '10')),
    'SMA_LONG': int(os.getenv('SMA_LONG', '30')),
    'RSI_PERIOD': int(os.getenv('RSI_PERIOD', '14')),
    'RSI_OVERBOUGHT': int(os.getenv('RSI_OVERBOUGHT', '70')),
    'RSI_OVERSOLD': int(os.getenv('RSI_OVERSOLD', '30'))
}

# Backtesting
BACKTEST_START_DATE = os.getenv('BACKTEST_START_DATE', '2023-01-01')
BACKTEST_END_DATE = os.getenv('BACKTEST_END_DATE', '2023-06-30')

# Performance metrics
SHARPE_RATIO_RISK_FREE_RATE = float(os.getenv('SHARPE_RATIO_RISK_FREE_RATE', '0.02'))  # 2% risk-free rate for Sharpe ratio calculation

# Machine Learning parameters
ML_CONFIG = {
    'MODEL_TYPE': os.getenv('ML_MODEL_TYPE', 'RandomForest'),  # Options: 'RandomForest', 'XGBoost', 'LSTM'
    'TRAIN_TEST_SPLIT': float(os.getenv('ML_TRAIN_TEST_SPLIT', '0.8')),  # 80% training data, 20% testing data
    'FEATURES': os.getenv('ML_FEATURES', 'close,volume,rsi,macd,bollinger_bands').split(',')
}

# Sentiment Analysis parameters
SENTIMENT_CONFIG = {
    'SOURCES': os.getenv('SENTIMENT_SOURCES', 'twitter,reddit,news').split(','),
    'KEYWORDS': os.getenv('SENTIMENT_KEYWORDS', 'crypto,bitcoin,ethereum,HMSTR').split(',')
}

# Advanced Trading parameters
PORTFOLIO_REBALANCE_INTERVAL = int(os.getenv('PORTFOLIO_REBALANCE_INTERVAL', '24'))  # hours
MAX_ASSETS = int(os.getenv('MAX_ASSETS', '5'))  # Maximum number of assets to hold simultaneously
CORRELATION_THRESHOLD = float(os.getenv('CORRELATION_THRESHOLD', '0.7'))  # Threshold for considering assets correlated

# Exchange specific parameters
EXCHANGE = os.getenv('EXCHANGE', 'binance')
ORDER_TYPE = os.getenv('ORDER_TYPE', 'market')  # Options: 'market', 'limit'