# order_executor.py
# Implements order execution for the crypto trading bot

from config import ORDER_TYPE
import logging

# Exceptions personnalisées
class OrderExecutorError(Exception):
    """Exception de base pour les erreurs dans OrderExecutor."""
    pass

class InvalidOrderError(OrderExecutorError):
    """Exception levée pour des ordres invalides."""
    pass

class OrderExecutionError(OrderExecutorError):
    """Exception levée lors d'erreurs dans l'exécution des ordres."""
    pass

class OrderExecutor:
    def __init__(self, api_connector, symbol):
        self.api_connector = api_connector
        self.symbol = symbol
        self.logger = logging.getLogger(__name__)

    def execute_order(self, order):
        try:
            if not isinstance(order, dict) or 'action' not in order:
                raise InvalidOrderError("Invalid order format")

            if order['action'] == 'BUY':
                return self._execute_buy_order(order)
            elif order['action'] == 'SELL':
                return self._execute_sell_order(order)
            else:
                raise InvalidOrderError(f"Invalid order action: {order['action']}")
        except InvalidOrderError as e:
            self.logger.warning(str(e))
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error executing order: {str(e)}")
            return None

    def _execute_buy_order(self, order):
        try:
            amount = order['amount']
            price = self._get_current_price()

            if ORDER_TYPE == 'market':
                executed_order = self.api_connector.create_market_buy_order(self.symbol, amount)
            elif ORDER_TYPE == 'limit':
                executed_order = self.api_connector.create_limit_buy_order(self.symbol, amount, price)
            else:
                raise OrderExecutionError(f"Unsupported order type: {ORDER_TYPE}")

            if not executed_order:
                raise OrderExecutionError("Failed to execute buy order")

            self.logger.info(f"Buy order executed: {executed_order}")
            return {
                'id': executed_order['id'],
                'action': 'BUY',
                'amount': amount,
                'price': executed_order['price'],
                'stop_loss': order.get('stop_loss'),
                'take_profit': order.get('take_profit')
            }
        except OrderExecutionError as e:
            self.logger.error(str(e))
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in buy order execution: {str(e)}")
            return None

    def _execute_sell_order(self, order):
        try:
            amount = order['amount']
            price = self._get_current_price()

            if ORDER_TYPE == 'market':
                executed_order = self.api_connector.create_market_sell_order(self.symbol, amount)
            elif ORDER_TYPE == 'limit':
                executed_order = self.api_connector.create_limit_sell_order(self.symbol, amount, price)
            else:
                raise OrderExecutionError(f"Unsupported order type: {ORDER_TYPE}")

            if not executed_order:
                raise OrderExecutionError("Failed to execute sell order")

            self.logger.info(f"Sell order executed: {executed_order}")
            return {
                'id': executed_order['id'],
                'action': 'SELL',
                'amount': amount,
                'price': executed_order['price']
            }
        except OrderExecutionError as e:
            self.logger.error(str(e))
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in sell order execution: {str(e)}")
            return None

    def _get_current_price(self):
        try:
            ticker = self.api_connector.fetch_ticker(self.symbol)
            return ticker['last']
        except Exception as e:
            self.logger.error(f"Error fetching current price: {str(e)}")
            raise OrderExecutorError("Unable to get current price")

    def get_portfolio_value(self):
        try:
            balance = self.api_connector.fetch_balance()
            total_value = 0
            for currency, amount in balance['total'].items():
                if amount > 0:
                    if currency != 'USDT':
                        ticker = self.api_connector.fetch_ticker(f"{currency}/USDT")
                        value = amount * ticker['last']
                    else:
                        value = amount
                    total_value += value
            return total_value
        except Exception as e:
            self.logger.error(f"Error calculating portfolio value: {str(e)}")
            return 0

    def get_open_positions(self):
        try:
            open_positions = self.api_connector.fetch_open_positions(self.symbol)
            return [{
                'symbol': position['symbol'],
                'amount': position['amount'],
                'entry_price': position['entryPrice'],
                'unrealized_pnl': position['unrealizedPnl']
            } for position in open_positions]
        except Exception as e:
            self.logger.error(f"Error fetching open positions: {str(e)}")
            return []