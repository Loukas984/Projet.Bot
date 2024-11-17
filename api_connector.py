# api_connector.py
# Handles API connections and order execution for the crypto trading bot

import ccxt
import os
from typing import Dict, Any

class APIConnector:
    def __init__(self, exchange='binance'):
        self.exchange = getattr(ccxt, exchange)({
            'apiKey': os.environ.get('BINANCE_API_KEY'),
            'secret': os.environ.get('BINANCE_SECRET_KEY'),
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future'  # use futures, change to 'spot' if you want to use spot trading
            }
        })

    def get_balance(self) -> Dict[str, float]:
        try:
            balance = self.exchange.fetch_balance()
            return {
                'free': balance['free'],
                'used': balance['used'],
                'total': balance['total']
            }
        except Exception as e:
            print(f"Error fetching balance: {str(e)}")
            return {}

    def place_order(self, symbol: str, order_type: str, side: str, amount: float, price: float = None) -> Dict[str, Any]:
        try:
            if order_type == 'market':
                order = self.exchange.create_market_order(symbol, side, amount)
            elif order_type == 'limit':
                order = self.exchange.create_limit_order(symbol, side, amount, price)
            else:
                raise ValueError(f"Invalid order type: {order_type}")
            
            return order
        except Exception as e:
            print(f"Error placing order: {str(e)}")
            return {}

    def get_open_orders(self, symbol: str = None) -> list:
        try:
            return self.exchange.fetch_open_orders(symbol)
        except Exception as e:
            print(f"Error fetching open orders: {str(e)}")
            return []

    def cancel_order(self, order_id: str, symbol: str) -> bool:
        try:
            self.exchange.cancel_order(order_id, symbol)
            return True
        except Exception as e:
            print(f"Error cancelling order: {str(e)}")
            return False

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
            return total_value
        except Exception as e:
            print(f"Error calculating portfolio value: {str(e)}")
            return 0.0