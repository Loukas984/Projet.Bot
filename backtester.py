# backtester.py
# Implements backtesting functionality for the crypto trading bot

import pandas as pd
import numpy as np
from typing import Dict, Any
from config import INITIAL_BALANCE

class Backtester:
    def __init__(self, data_handler, trading_strategy, risk_manager):
        self.data_handler = data_handler
        self.trading_strategy = trading_strategy
        self.risk_manager = risk_manager
        self.initial_balance = INITIAL_BALANCE
        self.current_balance = self.initial_balance
        self.positions = {}
        self.trades = []

    def run(self, start_date: str, end_date: str) -> Dict[str, Any]:
        data = self.data_handler.fetch_historical_data(start_date, end_date)
        
        for index, row in data.iterrows():
            market_data = data.loc[:index]
            current_price = row['close']
            
            # Check for stop loss / take profit
            self._check_stop_loss_take_profit(current_price)
            
            # Generate trading signal
            signal = self.trading_strategy.generate_signal(market_data)
            
            # Evaluate signal using risk management
            evaluated_signal = self.risk_manager.evaluate_signal(signal, self.current_balance, current_price)
            
            if evaluated_signal:
                self._execute_trade(evaluated_signal, current_price, index)

        return self._generate_report()

    def _check_stop_loss_take_profit(self, current_price):
        for symbol, position in list(self.positions.items()):
            if current_price <= position['stop_loss'] or current_price >= position['take_profit']:
                self._close_position(symbol, current_price, 'Stop loss/Take profit')

    def _execute_trade(self, signal, price, timestamp):
        if signal['action'] == 'BUY':
            cost = signal['amount'] * price
            if cost <= self.current_balance:
                self.current_balance -= cost
                self.positions[self.data_handler.symbol] = {
                    'amount': signal['amount'],
                    'entry_price': price,
                    'stop_loss': signal['stop_loss'],
                    'take_profit': signal['take_profit']
                }
                self.trades.append({
                    'timestamp': timestamp,
                    'action': 'BUY',
                    'price': price,
                    'amount': signal['amount'],
                    'cost': cost
                })
        elif signal['action'] == 'SELL':
            if self.data_handler.symbol in self.positions:
                position = self.positions[self.data_handler.symbol]
                revenue = position['amount'] * price
                self.current_balance += revenue
                profit = revenue - (position['amount'] * position['entry_price'])
                self.trades.append({
                    'timestamp': timestamp,
                    'action': 'SELL',
                    'price': price,
                    'amount': position['amount'],
                    'revenue': revenue,
                    'profit': profit
                })
                del self.positions[self.data_handler.symbol]

    def _close_position(self, symbol, price, reason):
        position = self.positions[symbol]
        revenue = position['amount'] * price
        self.current_balance += revenue
        profit = revenue - (position['amount'] * position['entry_price'])
        self.trades.append({
            'timestamp': pd.Timestamp.now(),
            'action': 'SELL',
            'price': price,
            'amount': position['amount'],
            'revenue': revenue,
            'profit': profit,
            'reason': reason
        })
        del self.positions[symbol]

    def _generate_report(self) -> Dict[str, Any]:
        total_profit = sum(trade['profit'] for trade in self.trades if 'profit' in trade)
        total_trades = len(self.trades)
        winning_trades = sum(1 for trade in self.trades if 'profit' in trade and trade['profit'] > 0)
        losing_trades = sum(1 for trade in self.trades if 'profit' in trade and trade['profit'] <= 0)

        return {
            'initial_balance': self.initial_balance,
            'final_balance': self.current_balance,
            'total_profit': total_profit,
            'total_return': (self.current_balance - self.initial_balance) / self.initial_balance * 100,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'trades': self.trades
        }