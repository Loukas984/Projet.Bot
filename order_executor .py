# order_executor.py
# Implements order execution for the crypto trading bot

from config import ORDER_TYPE
import logging
from tenacity import retry, stop_after_attempt, wait_fixed
import ccxt

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
        """
        Initialise l'exécuteur d'ordres.

        Args:
            api_connector: Connecteur API pour interagir avec l'exchange.
            symbol (str): Symbole de trading.
        """
        self.api_connector = api_connector
        self.symbol = symbol
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def check_balance(self, amount, side):
        """
        Vérifie si le solde est suffisant pour exécuter l'ordre.

        Args:
            amount (float): Montant de l'ordre.
            side (str): 'buy' ou 'sell'.

        Returns:
            bool: True si le solde est suffisant, False sinon.
        """
        try:
            balance = self.api_connector.fetch_balance()
            base, quote = self.symbol.split('/')
            if side == 'buy':
                available = balance[quote]['free']
                required = amount * self._get_current_price()
            else:  # sell
                available = balance[base]['free']
                required = amount

            if available < required:
                self.logger.warning(f"Insufficient balance. Available: {available}, Required: {required}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error checking balance: {str(e)}")
            return False

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def execute_order(self, order):
        """
        Exécute un ordre de trading.

        Args:
            order (dict): Dictionnaire contenant les détails de l'ordre.

        Returns:
            dict: Détails de l'ordre exécuté ou None en cas d'échec.
        """
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

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _execute_buy_order(self, order):
        """
        Exécute un ordre d'achat.

        Args:
            order (dict): Dictionnaire contenant les détails de l'ordre d'achat.

        Returns:
            dict: Détails de l'ordre exécuté.

        Raises:
            OrderExecutionError: Si l'exécution de l'ordre échoue.
        """
        try:
            amount = order['amount']
            price = self._get_current_price()

            if not self.check_balance(amount, 'buy'):
                raise OrderExecutionError("Insufficient balance for buy order")

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
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in buy order execution: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _execute_sell_order(self, order):
        """
        Exécute un ordre de vente.

        Args:
            order (dict): Dictionnaire contenant les détails de l'ordre de vente.

        Returns:
            dict: Détails de l'ordre exécuté.

        Raises:
            OrderExecutionError: Si l'exécution de l'ordre échoue.
        """
        try:
            amount = order['amount']
            price = self._get_current_price()

            if not self.check_balance(amount, 'sell'):
                raise OrderExecutionError("Insufficient balance for sell order")

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
                'price': executed_order['price'],
                'stop_loss': order.get('stop_loss'),
                'take_profit': order.get('take_profit')
            }
        except OrderExecutionError as e:
            self.logger.error(str(e))
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in sell order execution: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _get_current_price(self):
        """
        Obtient le prix actuel du marché.

        Returns:
            float: Prix actuel du marché.

        Raises:
            OrderExecutionError: Si la récupération du prix échoue.
        """
        try:
            ticker = self.api_connector.fetch_ticker(self.symbol)
            return ticker['last']
        except Exception as e:
            self.logger.error(f"Error fetching current price: {str(e)}")
            raise OrderExecutionError("Unable to fetch current price")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def cancel_order(self, order_id):
        """
        Annule un ordre spécifique.

        Args:
            order_id (str): ID de l'ordre à annuler.

        Returns:
            bool: True si l'annulation a réussi, False sinon.
        """
        try:
            self.api_connector.cancel_order(order_id, self.symbol)
            self.logger.info(f"Order {order_id} cancelled successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {str(e)}")
            return False

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_order_status(self, order_id):
        """
        Obtient le statut d'un ordre spécifique.

        Args:
            order_id (str): ID de l'ordre.

        Returns:
            str: Statut de l'ordre.
        """
        try:
            order = self.api_connector.fetch_order(order_id, self.symbol)
            return order['status']
        except Exception as e:
            self.logger.error(f"Error fetching order status for {order_id}: {str(e)}")
            return None

    def cancel_all_orders(self):
        """
        Annule tous les ordres ouverts pour le symbole actuel.

        Returns:
            bool: True si tous les ordres ont été annulés avec succès, False sinon.
        """
        try:
            open_orders = self.api_connector.fetch_open_orders(self.symbol)
            for order in open_orders:
                self.cancel_order(order['id'])
            self.logger.info(f"All open orders for {self.symbol} cancelled successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error cancelling all orders for {self.symbol}: {str(e)}")
            return False

    def handle_partial_fill(self, order_id):
        """
        Gère les ordres partiellement exécutés.

        Args:
            order_id (str): ID de l'ordre partiellement exécuté.

        Returns:
            dict: Détails de l'ordre mis à jour.
        """
        try:
            order = self.api_connector.fetch_order(order_id, self.symbol)
            if order['status'] == 'partially filled':
                remaining = order['remaining']
                if ORDER_TYPE == 'market':
                    updated_order = self.api_connector.create_market_order(self.symbol, order['side'], remaining)
                elif ORDER_TYPE == 'limit':
                    updated_order = self.api_connector.create_limit_order(self.symbol, order['side'], remaining, order['price'])
                self.logger.info(f"Partially filled order {order_id} updated: {updated_order}")
                return updated_order
            return order
        except Exception as e:
            self.logger.error(f"Error handling partially filled order {order_id}: {str(e)}")
            return None

    def set_stop_loss(self, order_id, stop_price):
        """
        Définit un stop loss pour un ordre existant.

        Args:
            order_id (str): ID de l'ordre.
            stop_price (float): Prix du stop loss.

        Returns:
            dict: Détails de l'ordre stop loss.
        """
        try:
            order = self.api_connector.fetch_order(order_id, self.symbol)
            amount = order['amount']
            side = 'sell' if order['side'] == 'buy' else 'buy'
            stop_loss_order = self.api_connector.create_stop_market_order(self.symbol, side, amount, stop_price)
            self.logger.info(f"Stop loss set for order {order_id}: {stop_loss_order}")
            return stop_loss_order
        except Exception as e:
            self.logger.error(f"Error setting stop loss for order {order_id}: {str(e)}")
            return None

    def set_take_profit(self, order_id, take_profit_price):
        """
        Définit un take profit pour un ordre existant.

        Args:
            order_id (str): ID de l'ordre.
            take_profit_price (float): Prix du take profit.

        Returns:
            dict: Détails de l'ordre take profit.
        """
        try:
            order = self.api_connector.fetch_order(order_id, self.symbol)
            amount = order['amount']
            side = 'sell' if order['side'] == 'buy' else 'buy'
            take_profit_order = self.api_connector.create_limit_order(self.symbol, side, amount, take_profit_price)
            self.logger.info(f"Take profit set for order {order_id}: {take_profit_order}")
            return take_profit_order
        except Exception as e:
            self.logger.error(f"Error setting take profit for order {order_id}: {str(e)}")
            return None