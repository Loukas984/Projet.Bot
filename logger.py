import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# Main logger
main_logger = setup_logger('main', 'logs/main.log')

# Trading logger
trading_logger = setup_logger('trading', 'logs/trading.log')

# Performance logger
performance_logger = setup_logger('performance', 'logs/performance.log')

# Error logger
error_logger = setup_logger('error', 'logs/error.log', level=logging.ERROR)

def log_trade(action, symbol, amount, price):
    trading_logger.info(f"Trade: {action} {amount} {symbol} at {price}")

def log_performance(metrics):
    performance_logger.info(f"Performance: {metrics}")

def log_error(error):
    error_logger.error(f"Error: {str(error)}")