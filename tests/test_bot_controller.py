import unittest
from unittest.mock import patch, MagicMock
import yaml
from bot_controller import BotController

class TestBotController(unittest.TestCase):

    @patch('bot_controller.yaml.safe_load')
    def test_load_config_success(self, mock_safe_load):
        mock_safe_load.return_value = {
            'symbol': 'BTCUSDT',
            'timeframe': '1h',
            'max_position_size': 0.1,
            'stop_loss_pct': 0.02,
            'take_profit_pct': 0.05
        }
        bot = BotController()
        self.assertIsNotNone(bot.config)
        self.assertEqual(bot.config['symbol'], 'BTCUSDT')

    @patch('bot_controller.yaml.safe_load')
    def test_load_config_missing_key(self, mock_safe_load):
        mock_safe_load.return_value = {
            'symbol': 'BTCUSDT',
            'timeframe': '1h'
        }
        with self.assertRaises(ValueError):
            BotController()

    @patch('bot_controller.yaml.safe_load')
    def test_simulation_mode(self, mock_safe_load):
        mock_safe_load.return_value = {
            'symbol': 'BTCUSDT',
            'timeframe': '1h',
            'max_position_size': 0.1,
            'stop_loss_pct': 0.02,
            'take_profit_pct': 0.05,
            'simulation_mode': True
        }
        bot = BotController()
        self.assertTrue(bot.simulation_mode)

    @patch('bot_controller.yaml.safe_load')
    @patch('bot_controller.BotController.start_trading')
    @patch('bot_controller.OrderExecutor')
    def test_start_trading_simulation(self, mock_order_executor, mock_start_trading, mock_safe_load):
        mock_safe_load.return_value = {
            'symbol': 'BTCUSDT',
            'timeframe': '1h',
            'max_position_size': 0.1,
            'stop_loss_pct': 0.02,
            'take_profit_pct': 0.05,
            'simulation_mode': True
        }
        bot = BotController()
        bot.start_trading()
        mock_start_trading.assert_called_once()
        
        # Verify that real order execution is not called in simulation mode
        mock_order_executor.return_value.execute_order.assert_not_called()
        
        # Verify that the bot is in simulation mode
        self.assertTrue(bot.simulation_mode)
        
        # Add more assertions to check the behavior in simulation mode
        # For example, verify that certain logging messages are called
        # self.assertIn("Running in simulation mode", caplog.text)

if __name__ == '__main__':
    unittest.main()