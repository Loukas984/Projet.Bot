# performance_tracker.py
# Implements performance tracking for the crypto trading bot

import numpy as np
from config import SHARPE_RATIO_RISK_FREE_RATE

class PerformanceTracker:
    def __init__(self):
        self.portfolio_values = []
        self.returns = []
        self.trades = []

    def update(self, market_data, portfolio_value):
        self.portfolio_values.append(portfolio_value)
        if len(self.portfolio_values) > 1:
            returns = (portfolio_value - self.portfolio_values[-2]) / self.portfolio_values[-2]
            self.returns.append(returns)

    def add_trade(self, trade):
        self.trades.append(trade)

    def get_metrics(self):
        return {
            'total_return': self.calculate_total_return(),
            'sharpe_ratio': self.calculate_sharpe_ratio(),
            'max_drawdown': self.calculate_max_drawdown(),
            'win_rate': self.calculate_win_rate(),
        }

    def calculate_total_return(self):
        if len(self.portfolio_values) < 2:
            return 0
        return (self.portfolio_values[-1] - self.portfolio_values[0]) / self.portfolio_values[0]

    def calculate_sharpe_ratio(self):
        if len(self.returns) < 2:
            return 0
        excess_returns = np.array(self.returns) - SHARPE_RATIO_RISK_FREE_RATE
        return np.mean(excess_returns) / np.std(excess_returns, ddof=1) * np.sqrt(252)  # Annualized

    def calculate_max_drawdown(self):
        peak = self.portfolio_values[0]
        max_dd = 0
        for value in self.portfolio_values[1:]:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        return max_dd

    def calculate_win_rate(self):
        if not self.trades:
            return 0
        winning_trades = sum(1 for trade in self.trades if trade['profit'] > 0)
        return winning_trades / len(self.trades)