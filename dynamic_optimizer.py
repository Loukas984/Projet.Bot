# dynamic_optimizer.py
# Implements dynamic optimization for the crypto trading bot

import numpy as np
from typing import Dict, Any, List
from backtester import Backtester
from trading_strategy import AdvancedTradingStrategy
from risk_management import RiskManager

class DynamicOptimizer:
    def __init__(self, backtester: Backtester, trading_strategy: AdvancedTradingStrategy, risk_manager: RiskManager):
        self.backtester = backtester
        self.trading_strategy = trading_strategy
        self.risk_manager = risk_manager

    def optimize(self, start_date: str, end_date: str, optimization_period: int = 30) -> List[Dict[str, Any]]:
        date_range = pd.date_range(start=start_date, end=end_date)
        optimization_results = []

        for i in range(0, len(date_range), optimization_period):
            period_start = date_range[i].strftime('%Y-%m-%d')
            period_end = date_range[min(i + optimization_period, len(date_range) - 1)].strftime('%Y-%m-%d')

            # Run backtester for the current period
            backtest_results = self.backtester.run(period_start, period_end)

            # Optimize parameters based on backtest results
            optimized_params = self.optimize_parameters(backtest_results)

            # Update trading strategy and risk manager with optimized parameters
            self.update_parameters(optimized_params)

            optimization_results.append({
                'period_start': period_start,
                'period_end': period_end,
                'backtest_results': backtest_results,
                'optimized_params': optimized_params
            })

        return optimization_results

    def optimize_parameters(self, backtest_results: Dict[str, Any]) -> Dict[str, Any]:
        current_return = backtest_results['total_return']
        current_win_rate = backtest_results['win_rate']

        # Adjust SMA windows based on performance
        if current_return < 0:
            self.trading_strategy.sma_short = max(5, self.trading_strategy.sma_short - 1)
            self.trading_strategy.sma_long = min(200, self.trading_strategy.sma_long + 2)
        else:
            self.trading_strategy.sma_short = min(50, self.trading_strategy.sma_short + 1)
            self.trading_strategy.sma_long = max(20, self.trading_strategy.sma_long - 2)

        # Adjust RSI parameters based on win rate
        if current_win_rate < 0.5:
            self.trading_strategy.rsi_period = max(7, self.trading_strategy.rsi_period - 1)
            self.trading_strategy.rsi_overbought = min(80, self.trading_strategy.rsi_overbought + 1)
            self.trading_strategy.rsi_oversold = max(20, self.trading_strategy.rsi_oversold - 1)
        else:
            self.trading_strategy.rsi_period = min(21, self.trading_strategy.rsi_period + 1)
            self.trading_strategy.rsi_overbought = max(65, self.trading_strategy.rsi_overbought - 1)
            self.trading_strategy.rsi_oversold = min(35, self.trading_strategy.rsi_oversold + 1)

        # Adjust risk management parameters
        if current_return < 0:
            self.risk_manager.max_position_size = max(0.05, self.risk_manager.max_position_size - 0.01)
            self.risk_manager.stop_loss_pct = min(0.05, self.risk_manager.stop_loss_pct + 0.005)
            self.risk_manager.take_profit_pct = max(0.02, self.risk_manager.take_profit_pct - 0.005)
        else:
            self.risk_manager.max_position_size = min(0.2, self.risk_manager.max_position_size + 0.01)
            self.risk_manager.stop_loss_pct = max(0.01, self.risk_manager.stop_loss_pct - 0.005)
            self.risk_manager.take_profit_pct = min(0.1, self.risk_manager.take_profit_pct + 0.005)

        return {
            'sma_short': self.trading_strategy.sma_short,
            'sma_long': self.trading_strategy.sma_long,
            'rsi_period': self.trading_strategy.rsi_period,
            'rsi_overbought': self.trading_strategy.rsi_overbought,
            'rsi_oversold': self.trading_strategy.rsi_oversold,
            'max_position_size': self.risk_manager.max_position_size,
            'stop_loss_pct': self.risk_manager.stop_loss_pct,
            'take_profit_pct': self.risk_manager.take_profit_pct
        }

    def update_parameters(self, optimized_params: Dict[str, Any]):
        self.trading_strategy.update_parameters(optimized_params)
        self.risk_manager.set_parameters(optimized_params)