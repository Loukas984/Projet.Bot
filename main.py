"""
Main entry point for the advanced crypto trading bot.

This script initializes and runs the trading bot, including data handling,
strategy execution, risk management, and performance tracking. It also
includes functionality for bot optimization and backtesting.

The bot operates in a continuous loop, fetching market data, generating
trading signals, evaluating risks, and executing trades based on the
defined strategy and risk parameters.
"""

import time
import schedule
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler

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

def setup_logger():
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

def optimize_bot(data_handler, trading_strategy, risk_manager, backtester, ml_optimizer):
    """
    Optimize the trading bot's parameters and strategy.

    This function performs three types of optimization:
    1. Dynamic optimization
    2. Machine Learning optimization
    3. Parameter optimization

    It uses historical data for a specified number of days (OPTIMIZATION_DAYS)
    to find the best parameters and update the trading strategy.

    Args:
        data_handler (DataHandler): Handles market data retrieval.
        trading_strategy (TradingStrategy): The trading strategy to be optimized.
        risk_manager (RiskManager): Manages trading risks.
        backtester (Backtester): Used for backtesting during optimization.
        ml_optimizer (MLOptimizer): Handles machine learning optimization.

    The function logs the results of each optimization step and any errors that occur.
    """
    logger = logging.getLogger()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=OPTIMIZATION_DAYS)

    logger.info("Starting bot optimization...")

    try:
        # Dynamic optimization
        dynamic_optimizer = DynamicOptimizer(backtester, trading_strategy, risk_manager)
        dynamic_results = dynamic_optimizer.optimize(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        logger.info(f"Dynamic optimization results: {dynamic_results}")

        # ML optimization
        ml_results = ml_optimizer.optimize(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        logger.info(f"ML optimization results: {ml_results}")

        # Parameter optimization
        param_optimizer = ParameterOptimizer(SYMBOL, TIMEFRAME, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        best_params = param_optimizer.optimize()
        logger.info(f"Best parameters found: {best_params}")

        # Update strategy with best parameters
        trading_strategy.update_parameters(best_params)
        logger.info("Bot optimization completed.")
    except Exception as e:
        logger.error(f"Error during optimization: {str(e)}")

def trading_loop(data_handler, trading_strategy, risk_manager, order_executor, sentiment_analyzer, performance_tracker):
    """
    Main trading loop of the bot.

    This function continuously fetches market data, generates trading signals,
    evaluates risks, executes trades, and updates performance metrics.

    Args:
        data_handler (DataHandler): Handles market data retrieval.
        trading_strategy (TradingStrategy): Generates trading signals.
        risk_manager (RiskManager): Evaluates and manages trading risks.
        order_executor (OrderExecutor): Executes trading orders.
        sentiment_analyzer (SentimentAnalyzer): Analyzes market sentiment.
        performance_tracker (PerformanceTracker): Tracks bot performance.

    The loop runs indefinitely, with a sleep time between iterations.
    """
    logger = logging.getLogger()
    while True:
        try:
            # Fetch latest market data
            market_data = data_handler.fetch_market_data()

            # Analyze market sentiment
            sentiment = sentiment_analyzer.analyze()

            # Generate trading signals
            signals = trading_strategy.generate_signal(market_data, sentiment)

            # Evaluate signals using risk management
            for signal in signals:
                approved_signal = risk_manager.evaluate_signal(signal, order_executor.get_portfolio_value(), market_data['close'].iloc[-1])
                if approved_signal:
                    # Execute the trade
                    order_executor.execute_order(approved_signal)

            # Update performance metrics
            performance_tracker.update(market_data, order_executor.get_portfolio_value())

            # Log current portfolio value and performance metrics
            portfolio_value = order_executor.get_portfolio_value()
            performance_metrics = performance_tracker.get_metrics()
            logger.info(f"Current portfolio value: {portfolio_value} USDT")
            logger.info(f"Performance metrics: {performance_metrics}")

            # Wait for the next candle
            time.sleep(60)  # Assuming 1-minute timeframe

        except Exception as e:
            logger.error(f"An error occurred in the trading loop: {str(e)}")
            time.sleep(60)  # Wait a minute before retrying

def main():
    logger = setup_logger()
    logger.info("Advanced Crypto Trading Bot Started")

    try:
        # Initialize components
        api_connector = APIConnector(API_KEY, API_SECRET)
        data_handler = DataHandler(SYMBOL, TIMEFRAME)
        trading_strategy = AdvancedTradingStrategy(SYMBOL, TIMEFRAME)
        risk_manager = RiskManager(MAX_POSITION_SIZE, STOP_LOSS_PCT, TAKE_PROFIT_PCT)
        order_executor = OrderExecutor(api_connector, SYMBOL)
        backtester = Backtester(data_handler, trading_strategy, risk_manager)
        ml_optimizer = MLOptimizer(backtester, trading_strategy, risk_manager)
        sentiment_analyzer = SentimentAnalyzer()
        performance_tracker = PerformanceTracker()

        # Schedule optimization
        schedule.every(OPTIMIZATION_INTERVAL).hours.do(
            optimize_bot, data_handler, trading_strategy, risk_manager, backtester, ml_optimizer
        )

        # Run initial optimization
        optimize_bot(data_handler, trading_strategy, risk_manager, backtester, ml_optimizer)

        # Start trading loop
        trading_loop(data_handler, trading_strategy, risk_manager, order_executor, sentiment_analyzer, performance_tracker)

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        logger.info("Advanced Crypto Trading Bot Stopped")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        import unittest
        from tests.test_bot_controller import TestBotController
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
    else:
        main()