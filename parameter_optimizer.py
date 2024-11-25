# parameter_optimizer.py
# Implements parameter optimization for the crypto trading bot using Optuna

import optuna
from typing import Dict, Any
from backtester import Backtester
from trading_strategy import AdvancedTradingStrategy
from risk_management import RiskManager

class ParameterOptimizer:
    def __init__(self, backtester: Backtester, trading_strategy: AdvancedTradingStrategy, risk_manager: RiskManager):
        self.backtester = backtester
        self.trading_strategy = trading_strategy
        self.risk_manager = risk_manager

    def optimize(self, start_date: str, end_date: str, n_trials: int = 100) -> Dict[str, Any]:
        def objective(trial):
            # Define the hyperparameters to optimize
            params = {
                'sma_short': trial.suggest_int('sma_short', 5, 50),
                'sma_long': trial.suggest_int('sma_long', 20, 200),
                'rsi_period': trial.suggest_int('rsi_period', 7, 21),
                'rsi_overbought': trial.suggest_int('rsi_overbought', 65, 80),
                'rsi_oversold': trial.suggest_int('rsi_oversold', 20, 35),
                'max_position_size': trial.suggest_float('max_position_size', 0.05, 0.2),
                'stop_loss_pct': trial.suggest_float('stop_loss_pct', 0.01, 0.05),
                'take_profit_pct': trial.suggest_float('take_profit_pct', 0.02, 0.1)
            }

            # Update trading strategy and risk manager with the suggested parameters
            self.trading_strategy.update_parameters(params)
            self.risk_manager.set_parameters(params)

            # Run backtester with the current parameters
            backtest_results = self.backtester.run(start_date, end_date)

            # Return the metric to optimize (e.g., total return)
            return backtest_results['total_return']

        # Create a study object and optimize the objective function
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials)

        # Get the best parameters
        best_params = study.best_params
        best_value = study.best_value

        return {
            'best_params': best_params,
            'best_value': best_value
        }

    def apply_best_parameters(self, best_params: Dict[str, Any]):
        self.trading_strategy.update_parameters(best_params)
        self.risk_manager.set_parameters(best_params)