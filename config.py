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


# API credentials (loaded from environment variables or use dummy values for testing)
API_KEY = os.getenv('API_KEY', 'dummy_api_key')
API_SECRET = os.getenv('API_SECRET', 'dummy_api_secret')

# Comment out or remove the following lines
# if not API_KEY or not API_SECRET:
#     raise ValueError("API_KEY and API_SECRET must be set in the .env file")


# Risk management parameters
RISK_CONFIG = {
    'MAX_POSITION_SIZE': float(os.getenv('MAX_POSITION_SIZE', '0.1')),  # 10% of portfolio
    'STOP_LOSS_PCT': float(os.getenv('STOP_LOSS_PCT', '0.02')),  # 2% stop loss
    'TAKE_PROFIT_PCT': float(os.getenv('TAKE_PROFIT_PCT', '0.05')),  # 5% take profit
    'MAX_ASSETS': int(os.getenv('MAX_ASSETS', '5')),  # Maximum number of assets to hold simultaneously
    'CORRELATION_THRESHOLD': float(os.getenv('CORRELATION_THRESHOLD', '0.7'))  # Threshold for considering assets correlated
}

# Optimization parameters
OPTIMIZATION_CONFIG = {
    'INTERVAL': int(os.getenv('OPTIMIZATION_INTERVAL', '24')),  # hours
    'DAYS': int(os.getenv('OPTIMIZATION_DAYS', '30')),  # days to use for optimization
}

# Logging
LOG_CONFIG = {
    'LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
    'FILE': os.getenv('LOG_FILE', 'trading_bot.log')
}

# Strategy parameters (initial values, will be optimized)
STRATEGY_PARAMS = {
    'SMA_SHORT': int(os.getenv('SMA_SHORT', '10')),
    'SMA_LONG': int(os.getenv('SMA_LONG', '30')),
    'RSI_PERIOD': int(os.getenv('RSI_PERIOD', '14')),
    'RSI_OVERBOUGHT': int(os.getenv('RSI_OVERBOUGHT', '70')),
    'RSI_OVERSOLD': int(os.getenv('RSI_OVERSOLD', '30'))
}

# Backtesting
BACKTEST_CONFIG = {
    'START_DATE': os.getenv('BACKTEST_START_DATE', '2023-01-01'),
    'END_DATE': os.getenv('BACKTEST_END_DATE', '2023-06-30')
}

# Performance metrics
PERFORMANCE_CONFIG = {
    'SHARPE_RATIO_RISK_FREE_RATE': float(os.getenv('SHARPE_RATIO_RISK_FREE_RATE', '0.02'))  # 2% risk-free rate for Sharpe ratio calculation
}

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

# Exchange specific parameters
EXCHANGE_CONFIG = {
    'NAME': os.getenv('EXCHANGE', 'binance'),
    'ORDER_TYPE': os.getenv('ORDER_TYPE', 'market')  # Options: 'market', 'limit'
}


# Volatility parameters
VOLATILITY_CONFIG = {
    'WINDOW': int(os.getenv('VOLATILITY_WINDOW', '20')),  # Number of periods for volatility calculation
    'HIGH_VOLATILITY_THRESHOLD': float(os.getenv('HIGH_VOLATILITY_THRESHOLD', '0.05')),  # 5% threshold for high volatility
    'LOW_VOLATILITY_THRESHOLD': float(os.getenv('LOW_VOLATILITY_THRESHOLD', '0.02')),  # 2% threshold for low volatility
}


# Trading loop parameters
LOOP_CONFIG = {
    'INTERVAL': int(os.getenv('TRADING_INTERVAL', '60')),  # seconds
    'ERROR_SLEEP_TIME': int(os.getenv('ERROR_SLEEP_TIME', '300'))  # seconds
}


# Market Analysis parameters
MARKET_ANALYSIS_CONFIG = {
    'TREND_WINDOW': {
        'short': int(os.getenv('TREND_WINDOW_SHORT', '20')),
        'long': int(os.getenv('TREND_WINDOW_LONG', '50'))
    },
    'REGIME_CHANGE_THRESHOLD': float(os.getenv('REGIME_CHANGE_THRESHOLD', '0.03')),  # 3% threshold for regime change
    'SUPPORT_RESISTANCE_WINDOW': int(os.getenv('SUPPORT_RESISTANCE_WINDOW', '20')),
    'BOLLINGER_BANDS_WINDOW': int(os.getenv('BOLLINGER_BANDS_WINDOW', '20')),
    'BOLLINGER_BANDS_STD': float(os.getenv('BOLLINGER_BANDS_STD', '2.0'))
}

# Dynamic Optimization parameters
DYNAMIC_OPTIMIZATION_CONFIG = {
    'INTERVAL': int(os.getenv('DYNAMIC_OPTIMIZATION_INTERVAL', '6')),  # hours
    'PERFORMANCE_THRESHOLD': float(os.getenv('DYNAMIC_OPTIMIZATION_PERFORMANCE_THRESHOLD', '0.05'))  # 5% performance change to trigger optimization
}

# Machine Learning Optimization parameters
ML_OPTIMIZATION_CONFIG = {
    'INTERVAL': int(os.getenv('ML_OPTIMIZATION_INTERVAL', '24')),  # hours
    'RETRAINING_INTERVAL': int(os.getenv('ML_RETRAINING_INTERVAL', '168')),  # hours (1 week)
    'FEATURE_SELECTION_METHOD': os.getenv('ML_FEATURE_SELECTION_METHOD', 'recursive')  # Options: 'recursive', 'lasso', 'random'
}

# Cache parameters
CACHE_CONFIG = {
    'EXPIRY': {
        'market_data': int(os.getenv('CACHE_EXPIRY_MARKET_DATA', '60')),  # seconds
        'ml_prediction': int(os.getenv('CACHE_EXPIRY_ML_PREDICTION', '300')),  # seconds
        'sentiment': int(os.getenv('CACHE_EXPIRY_SENTIMENT', '3600'))  # seconds
    }
}

# Paper Trading parameters
PAPER_TRADING = os.getenv('PAPER_TRADING', 'True').lower() == 'true'
PAPER_TRADING_BALANCE = float(os.getenv('PAPER_TRADING_BALANCE', '10000'))  # Initial balance for paper trading

# Trailing Stop parameters
TRAILING_STOP_CONFIG = {
    'ACTIVATION_PERCENTAGE': float(os.getenv('TRAILING_STOP_ACTIVATION_PERCENTAGE', '0.01')),  # 1% price movement to activate
    'TRAIL_PERCENTAGE': float(os.getenv('TRAILING_STOP_TRAIL_PERCENTAGE', '0.005'))  # 0.5% trailing stop
}

# Asserts for validation
assert 0 < RISK_CONFIG['MAX_POSITION_SIZE'] <= 1, "MAX_POSITION_SIZE must be between 0 and 1"
assert 0 < RISK_CONFIG['STOP_LOSS_PCT'] < RISK_CONFIG['TAKE_PROFIT_PCT'], "STOP_LOSS_PCT must be less than TAKE_PROFIT_PCT"
assert OPTIMIZATION_CONFIG['INTERVAL'] > 0, "OPTIMIZATION_INTERVAL must be positive"
assert OPTIMIZATION_CONFIG['DAYS'] > 0, "OPTIMIZATION_DAYS must be positive"
assert 0 < ML_CONFIG['TRAIN_TEST_SPLIT'] < 1, "ML_TRAIN_TEST_SPLIT must be between 0 and 1"
assert VOLATILITY_CONFIG['LOW_VOLATILITY_THRESHOLD'] < VOLATILITY_CONFIG['HIGH_VOLATILITY_THRESHOLD'], "LOW_VOLATILITY_THRESHOLD must be less than HIGH_VOLATILITY_THRESHOLD"
assert MARKET_ANALYSIS_CONFIG['TREND_WINDOW']['short'] < MARKET_ANALYSIS_CONFIG['TREND_WINDOW']['long'], "Short trend window must be smaller than long trend window"
assert DYNAMIC_OPTIMIZATION_CONFIG['INTERVAL'] > 0, "DYNAMIC_OPTIMIZATION_INTERVAL must be positive"
assert ML_OPTIMIZATION_CONFIG['INTERVAL'] > 0, "ML_OPTIMIZATION_INTERVAL must be positive"
assert ML_OPTIMIZATION_CONFIG['RETRAINING_INTERVAL'] > ML_OPTIMIZATION_CONFIG['INTERVAL'], "ML_RETRAINING_INTERVAL must be greater than ML_OPTIMIZATION_INTERVAL"
assert all(expiry > 0 for expiry in CACHE_CONFIG['EXPIRY'].values()), "All cache expiry times must be positive"
assert 0 < TRAILING_STOP_CONFIG['ACTIVATION_PERCENTAGE'] < 1, "TRAILING_STOP_ACTIVATION_PERCENTAGE must be between 0 and 1"
assert 0 < TRAILING_STOP_CONFIG['TRAIL_PERCENTAGE'] < TRAILING_STOP_CONFIG['ACTIVATION_PERCENTAGE'], "TRAILING_STOP_TRAIL_PERCENTAGE must be less than ACTIVATION_PERCENTAGE"

assert LOOP_CONFIG['INTERVAL'] > 0, "LOOP_INTERVAL must be positive"
assert LOOP_CONFIG['ERROR_SLEEP_TIME'] > 0, "ERROR_SLEEP_TIME must be positive"
