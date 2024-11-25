# api_connector.py
# Handles API connections and order execution for the crypto trading bot

import ccxt
import os
import logging
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_fixed

class APIConnector:
    def __init__(self, exchange='binance'):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        try:
            self.exchange = getattr(ccxt, exchange)({
                'apiKey': os.environ.get('BINANCE_API_KEY'),
                'secret': os.environ.get('BINANCE_SECRET_KEY'),
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future'  # use futures, change to 'spot' if you want to use spot trading
                }
            })
            self.logger.info(f"Successfully initialized {exchange} API connector")
        except ccxt.ExchangeError as e:
            self.logger.error(f"Failed to initialize {exchange} API connector: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_balance(self) -> Dict[str, float]:
        try:
            balance = self.exchange.fetch_balance()
            self.logger.info("Successfully fetched balance")
            return {
                'free': balance['free'],
                'used': balance['used'],
                'total': balance['total']
            }
        except ccxt.NetworkError as e:
            self.logger.error(f"Network error while fetching balance: {str(e)}")
            raise
        except ccxt.ExchangeError as e:
            self.logger.error(f"Exchange error while fetching balance: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while fetching balance: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def place_order(self, symbol: str, order_type: str, side: str, amount: float, price: float = None) -> Dict[str, Any]:
        try:
            if order_type == 'market':
                order = self.exchange.create_market_order(symbol, side, amount)
            elif order_type == 'limit':
                order = self.exchange.create_limit_order(symbol, side, amount, price)
            else:
                raise ValueError(f"Invalid order type: {order_type}")
            
            self.logger.info(f"Successfully placed {order_type} {side} order for {amount} {symbol}")
            return order
        except ccxt.InsufficientFunds as e:
            self.logger.error(f"Insufficient funds to place order: {str(e)}")
            raise
        except ccxt.InvalidOrder as e:
            self.logger.error(f"Invalid order: {str(e)}")
            raise
        except ccxt.NetworkError as e:
            self.logger.error(f"Network error while placing order: {str(e)}")
            raise
        except ccxt.ExchangeError as e:
            self.logger.error(f"Exchange error while placing order: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while placing order: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_open_orders(self, symbol: str = None) -> list:
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            self.logger.info(f"Successfully fetched open orders for {symbol if symbol else 'all symbols'}")
            return orders
        except ccxt.NetworkError as e:
            self.logger.error(f"Network error while fetching open orders: {str(e)}")
            raise
        except ccxt.ExchangeError as e:
            self.logger.error(f"Exchange error while fetching open orders: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while fetching open orders: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        try:
            self.exchange.cancel_order(order_id, symbol)
            self.logger.info(f"Successfully cancelled order {order_id} for {symbol}")
            return True
        except ccxt.OrderNotFound as e:
            self.logger.warning(f"Order not found: {str(e)}")
            return False
        except ccxt.NetworkError as e:
            self.logger.error(f"Network error while cancelling order: {str(e)}")
            raise
        except ccxt.ExchangeError as e:
            self.logger.error(f"Exchange error while cancelling order: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while cancelling order: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_portfolio_value(self) -> float:
        try:
            balance = self.get_balance()
            total_value = 0
            for currency, amount in balance['total'].items():
                if amount > 0:
                    if currency != 'USDT':
                        ticker = self.exchange.fetch_ticker(f"{currency}/USDT")
                        value = amount * ticker['last']
                    else:
                        value = amount
                    total_value += value
            self.logger.info(f"Successfully calculated portfolio value: {total_value} USDT")
            return total_value
        except ccxt.NetworkError as e:
            self.logger.error(f"Network error while calculating portfolio value: {str(e)}")
            raise
        except ccxt.ExchangeError as e:
            self.logger.error(f"Exchange error while calculating portfolio value: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while calculating portfolio value: {str(e)}")
            raise

    def get_historical_data(self, symbol: str, timeframe: str, since: int, limit: int = None) -> list:
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            self.logger.info(f"Successfully fetched historical data for {symbol}")
            return ohlcv
        except ccxt.NetworkError as e:
            self.logger.error(f"Network error while fetching historical data: {str(e)}")
            raise
        except ccxt.ExchangeError as e:
            self.logger.error(f"Exchange error while fetching historical data: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while fetching historical data: {str(e)}")
            raise