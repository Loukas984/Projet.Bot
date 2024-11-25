# bot_controller.py
# Implements the main controller for the crypto trading bot

import logging
import time
import yaml
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

class BotController:
    def __init__(self):
        self.config = self._load_config()
        self.logger = self._setup_logger()
        self.simulation_mode = False
        try:
            if 'api_key' not in self.config or 'api_secret' not in self.config:
                self.logger.warning("API keys not found in config. Running in simulation mode.")
                self.simulation_mode = True
                self.api_connector = None
            else:
                self.api_connector = APIConnector(self.config['api_key'], self.config['api_secret'])
            
            self.data_handler = DataHandler(self.config['symbol'], self.config['timeframe'])
            self.trading_strategy = AdvancedTradingStrategy(self.config['symbol'], self.config['timeframe'])
            self.risk_manager = RiskManager(
                self.config['max_position_size'],
                self.config['stop_loss_pct'],
                self.config['take_profit_pct']
            )
            self.order_executor = OrderExecutor(self.api_connector, self.config['symbol'])
            self.backtester = Backtester(self.data_handler, self.trading_strategy, self.risk_manager)
            self.dynamic_optimizer = DynamicOptimizer(self.backtester)
            self.ml_optimizer = MLOptimizer(self.backtester)
            self.parameter_optimizer = ParameterOptimizer(self.backtester)
            self.sentiment_analyzer = SentimentAnalyzer()
            self.performance_tracker = PerformanceTracker()
            self.is_running = False
        except Exception as e:
            self.logger.error(f"Error initializing BotController: {str(e)}")
            raise

    def _load_config(self):
        try:
            with open('config.yaml', 'r') as file:
                config = yaml.safe_load(file)
            self._validate_config(config)
            return config
        except FileNotFoundError:
            self.logger.error("Configuration file 'config.yaml' not found.")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing configuration file: {str(e)}")
            raise
        except ValueError as e:
            self.logger.error(f"Invalid configuration: {str(e)}")
            raise

    def _validate_config(self, config):
        required_keys = ['symbol', 'timeframe', 'max_position_size', 'stop_loss_pct', 'take_profit_pct']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        # Add more specific validations as needed
        if config.get('simulation_mode') is None:
            config['simulation_mode'] = False

    def _setup_logger(self):
        logger = logging.getLogger('CryptoTradingBot')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def start_trading(self):
        self.logger.info("Starting trading bot...")
        if self.simulation_mode:
            self.logger.info("Running in simulation mode. No real trades will be executed.")
        self.is_running = True
        while self.is_running:
            try:
                market_data = self.data_handler.fetch_market_data()
                sentiment = self.sentiment_analyzer.analyze()
                ml_prediction = self.ml_optimizer.predict(market_data)
                
                signal = self.trading_strategy.generate_signal(market_data, sentiment, ml_prediction)
                evaluated_signal = self.risk_manager.evaluate_signal(signal, self.order_executor.get_portfolio_value(), market_data['close'].iloc[-1])
                
                if evaluated_signal and not self.simulation_mode:
                    order = self.order_executor.execute_order(evaluated_signal)
                    if order:
                        self.performance_tracker.add_trade(order)
                elif evaluated_signal and self.simulation_mode:
                    self.logger.info(f"Simulated trade: {evaluated_signal}")
                
                self.performance_tracker.update(market_data, self.order_executor.get_portfolio_value())
                
                # Log current status
                self.logger.info(f"Current portfolio value: {self.order_executor.get_portfolio_value()} USDT")
                self.logger.info(f"Performance metrics: {self.performance_tracker.get_metrics()}")
                
                time.sleep(60)  # Wait for 1 minute before next iteration
                
            except Exception as e:
                self.logger.error(f"An error occurred in the trading loop: {str(e)}")

    def stop_trading(self):
        self.logger.info("Stopping trading bot...")
        self.is_running = False

    def run_backtest(self, start_date, end_date):
        self.logger.info(f"Running backtest from {start_date} to {end_date}...")
        try:
            results = self.backtester.run(start_date, end_date)
            self.logger.info(f"Backtest results: {results}")
            return results
        except Exception as e:
            self.logger.error(f"Error during backtesting: {str(e)}")
            return None

    def optimize_parameters(self, start_date, end_date):
        self.logger.info("Optimizing parameters...")
        try:
            results = self.parameter_optimizer.optimize(start_date, end_date)
            self.logger.info(f"Optimization results: {results}")
            self.parameter_optimizer.apply_best_parameters(results['best_params'])
            return results
        except Exception as e:
            self.logger.error(f"Error during parameter optimization: {str(e)}")
            return None

    def run_dynamic_optimization(self, start_date, end_date):
        self.logger.info("Running dynamic optimization...")
        try:
            results = self.dynamic_optimizer.optimize(start_date, end_date)
            self.logger.info(f"Dynamic optimization results: {results}")
            return results
        except Exception as e:
            self.logger.error(f"Error during dynamic optimization: {str(e)}")
            return None

    def get_performance_metrics(self):
        return self.performance_tracker.get_metrics()

def main():
    bot = BotController()
    try:
        print("Starting Crypto Trading Bot")
        bot.start_trading()
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Stopping the bot...")
        bot.stop_trading()
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
    finally:
        logging.info("Bot stopped. Final performance metrics:")
        logging.info(bot.get_performance_metrics())

if __name__ == "__main__":
    main()