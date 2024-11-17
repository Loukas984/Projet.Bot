import unittest
import pandas as pd
from trading_strategy import AdvancedTradingStrategy

class MockDataHandler:
    def __init__(self, symbol, interval):
        self.symbol = symbol
        self.interval = interval

    def get_recent_data(self, limit=100):
        # Create mock data for testing
        dates = pd.date_range(start='1/1/2020', periods=limit)
        data = pd.DataFrame({
            'open': range(100, 100 + limit),
            'high': range(110, 110 + limit),
            'low': range(90, 90 + limit),
            'close': range(105, 105 + limit),
            'volume': [1000000] * limit
        }, index=dates)
        return data

    def calculate_rsi(self, data, period=14):
        # Simplified RSI calculation for testing
        return pd.Series([50] * len(data), index=data.index)

class TestAdvancedTradingStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = AdvancedTradingStrategy('BTCUSDT', '1h')
        self.strategy.data_handler = MockDataHandler('BTCUSDT', '1h')

    def test_calculate_ema(self):
        data = self.strategy.data_handler.get_recent_data()
        ema = self.strategy.calculate_ema(data, period=10)
        self.assertEqual(len(ema), len(data))
        self.assertIsInstance(ema, pd.Series)

    def test_calculate_macd(self):
        data = self.strategy.data_handler.get_recent_data()
        macd_line, signal_line = self.strategy.calculate_macd(data)
        self.assertEqual(len(macd_line), len(data))
        self.assertEqual(len(signal_line), len(data))
        self.assertIsInstance(macd_line, pd.Series)
        self.assertIsInstance(signal_line, pd.Series)

    def test_calculate_bollinger_bands(self):
        data = self.strategy.data_handler.get_recent_data()
        upper_band, lower_band = self.strategy.calculate_bollinger_bands(data)
        self.assertEqual(len(upper_band), len(data))
        self.assertEqual(len(lower_band), len(data))
        self.assertIsInstance(upper_band, pd.Series)
        self.assertIsInstance(lower_band, pd.Series)

    def test_generate_signal(self):
        signal = self.strategy.generate_signal()
        self.assertIn(signal, ['BUY', 'SELL', 'HOLD'])

    def test_get_current_price(self):
        price = self.strategy.get_current_price()
        self.assertIsInstance(price, float)

if __name__ == '__main__':
    unittest.main()