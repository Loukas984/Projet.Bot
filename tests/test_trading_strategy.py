import unittest
import pandas as pd
import numpy as np
from trading_strategy import AdvancedTradingStrategy
from config import SYMBOL, TIMEFRAME, STRATEGY_PARAMS

class TestAdvancedTradingStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = AdvancedTradingStrategy()
        self.data = pd.DataFrame({
            'open': [100, 101, 102, 103, 104],
            'high': [102, 103, 104, 105, 106],
            'low': [99, 100, 101, 102, 103],
            'close': [101, 102, 103, 104, 105],
            'volume': [1000, 1100, 1200, 1300, 1400]
        })
        self.data.index = pd.date_range(start='2023-01-01', periods=5, freq='D')

    def test_generate_signal(self):
        # Add necessary indicators to the data
        self.data['SMA_short'] = self.data['close'].rolling(window=2).mean()
        self.data['SMA_long'] = self.data['close'].rolling(window=3).mean()
        self.data['RSI'] = 50  # Mocking RSI value

        signal = self.strategy.generate_signal(self.data, sentiment=0.5, ml_prediction=106)
        self.assertIn(signal, ['BUY', 'SELL', 'HOLD'])

    def test_backtest(self):
        # Add necessary indicators to the data
        self.data['SMA_short'] = self.data['close'].rolling(window=2).mean()
        self.data['SMA_long'] = self.data['close'].rolling(window=3).mean()
        self.data['RSI'] = 50  # Mocking RSI value

        trades, final_balance = self.strategy.backtest(self.data)
        self.assertIsInstance(trades, pd.DataFrame, "trades should be a pandas DataFrame")
        self.assertTrue(isinstance(final_balance, (int, float)), f"final_balance should be a number, but got {type(final_balance)}")

if __name__ == '__main__':
    unittest.main()