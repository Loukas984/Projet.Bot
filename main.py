
"""
Main entry point for the advanced crypto trading bot.

This script initializes and runs the trading bot, including data handling,
strategy execution, risk management, and performance tracking. It also
includes functionality for bot optimization and backtesting.
"""

import time
import schedule
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
import sys

from config import *
from data_handler import DataHandler
from api_connector import APIConnector
from trading_strategy import AdvancedTradingStrategy
from order_executor import OrderExecutor
from risk_management import RiskManager
from backtester import Backtester
from dynamic_optimizer import DynamicOptimizer
from ml_optimizer import MLOptimizer
from parameter_optimizer import ParameterOptimizer
from sentiment_analyzer import SentimentAnalyzer
from performance_tracker import PerformanceTracker
from cache_manager import CacheManager

# Initialize CacheManager
cache_manager = CacheManager()

def setup_logger():
    """Set up and configure the logger."""
    logger = logging.getLogger()
    logger.setLevel(logging.getLevelName(LOG_LEVEL))

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def paper_trading(order):
    """
    Simulate the execution of an order in paper trading mode.
    
    Args:
        order (dict): The order to be simulated.
    
    Returns:
        dict: A simulated order execution result.
    """
    logger = logging.getLogger()
    logger.info(f"Paper trading order: {order}")
    return {
        'id': 'paper_' + str(int(time.time())),
        'status': 'closed',
        'amount': order['amount'],
        'price': order['price'],
        'cost': order['amount'] * order['price'],
        'fee': {'cost': 0, 'currency': 'USDT'}
    }


from market_analyzer import MarketAnalyzer

def trading_loop(data_handler, trading_strategy, risk_manager, order_executor, sentiment_analyzer, performance_tracker, ml_optimizer, market_analyzer, paper_trade=True):
    """
    Main trading loop of the bot.

    This function continuously fetches market data, generates trading signals,
    evaluates risks, and executes trades based on the defined strategy and
    risk parameters.

    Args:
        data_handler (DataHandler): Handles market data retrieval.
        trading_strategy (AdvancedTradingStrategy): Generates trading signals.
        risk_manager (RiskManager): Manages trading risks.
        order_executor (OrderExecutor): Executes trading orders.
        sentiment_analyzer (SentimentAnalyzer): Analyzes market sentiment.
        performance_tracker (PerformanceTracker): Tracks bot performance.
        ml_optimizer (MLOptimizer): Handles machine learning predictions.
        market_analyzer (MarketAnalyzer): Analyzes market conditions.
        paper_trade (bool): If True, run in paper trading mode.
    """
    logger = logging.getLogger()

    while True:
        try:
            # Fetch latest market data
            market_data = cache_manager.get_or_set('market_data', lambda: data_handler.get_latest_data(SYMBOL, TIMEFRAME), expiry=60)

            # Analyze market conditions
            market_analysis = market_analyzer.analyze_market(SYMBOL, TIMEFRAME)

            # Get ML prediction
            ml_prediction = cache_manager.get_or_set('ml_prediction', lambda: ml_optimizer.predict(market_data), expiry=300)

            # Analyze sentiment
            sentiment = cache_manager.get_or_set(f'sentiment_{SYMBOL}', lambda: sentiment_analyzer.analyze(SYMBOL), expiry=3600)

            # Generate trading signal
            signal = trading_strategy.generate_signal(market_data, sentiment, ml_prediction, market_analysis)

            # Evaluate risk
            risk_evaluation = risk_manager.evaluate_signal(signal, performance_tracker.get_portfolio_value(), market_analysis)

            # Execute order if signal is not HOLD and risk is acceptable
            if signal['action'] != 'HOLD' and risk_evaluation['acceptable']:
                order = {
                    'symbol': SYMBOL,
                    'type': 'market',
                    'side': signal['action'],
                    'amount': risk_evaluation['position_size']
                }

                if paper_trade:
                    execution_result = paper_trading(order)
                else:
                    execution_result = order_executor.execute_order(order)

                # Update performance metrics
                performance_tracker.update(execution_result)

                # Set stop-loss and take-profit
                if execution_result['status'] == 'closed':
                    order_executor.set_stop_loss(SYMBOL, signal['stop_loss'])
                    order_executor.set_take_profit(SYMBOL, signal['take_profit'])

            # Update trailing stop if applicable
            order_executor.update_trailing_stop(SYMBOL, market_data['close'][-1], market_analysis['volatility'])

            # Log performance metrics
            logger.info(f"Current portfolio value: {performance_tracker.get_portfolio_value()}")
            logger.info(f"Market analysis: {market_analysis}")

            # Sleep for the defined interval
            time.sleep(TRADING_INTERVAL)

        except Exception as e:
            logger.error(f"Error in trading loop: {str(e)}")
            time.sleep(ERROR_SLEEP_TIME)


def optimize_parameters():
    """
    Optimize trading parameters and ML model.
    """
    logger = logging.getLogger()
    try:
        parameter_optimizer.optimize()
        ml_optimizer.optimize(start_date=datetime.now() - timedelta(days=30), end_date=datetime.now())
        logger.info("Parameters optimized successfully")
    except Exception as e:
        logger.error(f"Error in parameter optimization: {str(e)}")


def main():
    """
    Main function to run the trading bot.
    """
    logger = setup_logger()
    logger.info("Starting the trading bot...")

    try:
        # Initialize components
        api_connector = APIConnector(API_KEY, API_SECRET)
        data_handler = DataHandler(api_connector)
        trading_strategy = AdvancedTradingStrategy()
        risk_manager = RiskManager(MAX_RISK_PER_TRADE)
        order_executor = OrderExecutor(api_connector)
        sentiment_analyzer = SentimentAnalyzer()
        performance_tracker = PerformanceTracker()
        market_analyzer = MarketAnalyzer(data_handler)

        # Initialize optimization components
        backtester = Backtester(data_handler, trading_strategy, risk_manager)
        dynamic_optimizer = DynamicOptimizer(backtester)
        ml_optimizer = MLOptimizer(backtester, trading_strategy, risk_manager)
        parameter_optimizer = ParameterOptimizer(backtester)

        # Perform initial optimization
        optimize_parameters()

        # Schedule periodic tasks
        schedule.every().day.at("00:00").do(performance_tracker.reset_daily_stats)
        schedule.every().hour.do(dynamic_optimizer.optimize, trading_strategy)
        schedule.every().day.at("01:00").do(optimize_parameters)

        # Start trading loop
        trading_loop(data_handler, trading_strategy, risk_manager, order_executor,
                     sentiment_analyzer, performance_tracker, ml_optimizer, market_analyzer, PAPER_TRADING)

    except KeyboardInterrupt:
        logger.info("Stopping the trading bot...")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()


