# test_trading_bot.py
# Unit tests for the crypto trading bot components

import unittest
from unittest.mock import Mock, patch
import pandas as pd
from datetime import datetime

from data_handler import DataHandler
from trading_strategy import TradingStrategy
from risk_management import RiskManager
from order_executor import OrderExecutor
from backtester import Backtester

class TestDataHandler(unittest.TestCase):
    def setUp(self):
        self.mock_api_connector = Mock()
        self.data_handler = DataHandler(self.mock_api_connector, 'BTC/USDT', '1m')

    def test_fetch_market_data(self):
        mock_data = [
            [1625097600000, 35000, 35100, 34900, 35050, 100],
            [1625097660000, 35050, 35150, 34950, 35100, 120],
        ]
        self.mock_api_connector.fetch_ohlcv.return_value = mock_data
        result = self.data_handler.fetch_market_data()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertEqual(list(result.columns), ['timestamp', 'open', 'high', 'low', 'close', 'volume'])

class TestTradingStrategy(unittest.TestCase):
    def setUp(self):
        self.trading_strategy = TradingStrategy()

    def test_generate_signals(self):
        mock_data = pd.DataFrame({
            'close': [34000, 35000, 36000, 35500, 35800],
            'volume': [100, 120, 150, 130, 140]
        })
        signals = self.trading_strategy.generate_signals(mock_data)
        self.assertIsInstance(signals, list)
        for signal in signals:
            self.assertIn('action', signal)
            self.assertIn('price', signal)

class TestRiskManager(unittest.TestCase):
    def setUp(self):
        self.risk_manager = RiskManager(max_position_size=0.1, stop_loss_pct=0.02, take_profit_pct=0.05)

    def test_evaluate_signal(self):
        signal = {'action': 'buy', 'price': 35000}
        portfolio_value = 100000
        current_price = 35000
        result = self.risk_manager.evaluate_signal(signal, portfolio_value, current_price)
        self.assertIsNotNone(result)
        self.assertIn('action', result)
        self.assertIn('amount', result)

class TestOrderExecutor(unittest.TestCase):
    def setUp(self):
        self.mock_api_connector = Mock()
        self.order_executor = OrderExecutor(self.mock_api_connector, 'BTC/USDT')

    @patch('order_executor.logging')
    def test_execute_order(self, mock_logging):
        signal = {'action': 'buy', 'amount': 0.1, 'price': 35000}
        self.mock_api_connector.create_market_buy_order.return_value = {'id': '123', 'status': 'closed'}
        result = self.order_executor.execute_order(signal)
        self.assertTrue(result)
        self.mock_api_connector.create_market_buy_order.assert_called_once_with('BTC/USDT', 0.1)

class TestBacktester(unittest.TestCase):
    def setUp(self):
        self.mock_data_handler = Mock()
        self.mock_trading_strategy = Mock()
        self.mock_risk_manager = Mock()
        self.backtester = Backtester(self.mock_data_handler, self.mock_trading_strategy, self.mock_risk_manager)

    def test_run(self):
        mock_data = pd.DataFrame({
            'timestamp': pd.date_range(start='2023-01-01', periods=5, freq='D'),
            'open': [34000, 35000, 36000, 35500, 35800],
            'high': [34100, 35100, 36100, 35600, 35900],
            'low': [33900, 34900, 35900, 35400, 35700],
            'close': [34000, 35000, 36000, 35500, 35800],
            'volume': [100, 120, 150, 130, 140]
        })
        self.mock_data_handler.fetch_historical_data.return_value = mock_data
        self.mock_trading_strategy.generate_signals.return_value = [{'action': 'buy', 'price': 35000}]
        self.mock_risk_manager.evaluate_signal.return_value = {'action': 'buy', 'amount': 0.1, 'price': 35000}

        result = self.backtester.run('2023-01-01', '2023-01-05')
        self.assertIsInstance(result, dict)
        self.assertIn('initial_balance', result)
        self.assertIn('final_balance', result)
        self.assertIn('total_pnl', result)
        self.assertIn('total_return', result)

if __name__ == '__main__':
    unittest.main()