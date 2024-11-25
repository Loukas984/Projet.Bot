# risk_management.py
from typing import Dict, Any
import logging
import numpy as np
import pandas as pd

class RiskManager:
    def __init__(self, config: Dict[str, Any]):
        self.max_position_size = config.get('max_position_size', 0.1)
        self.stop_loss_pct = config.get('stop_loss_pct', 0.02)
        self.take_profit_pct = config.get('take_profit_pct', 0.05)
        self.max_risk_per_trade = config.get('max_risk_per_trade', 0.01)
        self.max_drawdown = config.get('max_drawdown', 0.2)
        self.volatility_lookback = config.get('volatility_lookback', 20)
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        self.logger.info(f"RiskManager initialized with parameters: {self.__dict__}")

    def evaluate_signal(self, signal: str, portfolio_value: float, current_price: float, current_position: float = 0, historical_data: pd.DataFrame = None) -> Dict[str, Any]:
        try:
            if historical_data is not None:
                current_volatility = self.calculate_volatility(historical_data)
                self.adjust_risk_parameters(current_volatility)

            if signal == 'BUY':
                max_position_value = portfolio_value * self.max_position_size
                max_risk_value = portfolio_value * self.max_risk_per_trade
                stop_loss = current_price * (1 - self.stop_loss_pct)
                take_profit = current_price * (1 + self.take_profit_pct)
                
                quantity = self.calculate_position_size(current_price, stop_loss, max_risk_value)
                quantity = min(quantity, (max_position_value - current_position) / current_price)
                quantity = max(0, quantity)  # Ensure non-negative quantity
                
                return {
                    'action': 'BUY',
                    'quantity': quantity,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit
                }
            elif signal == 'SELL':
                stop_loss = current_price * (1 + self.stop_loss_pct)
                take_profit = current_price * (1 - self.take_profit_pct)
                
                return {
                    'action': 'SELL',
                    'quantity': current_position,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit
                }
            else:
                return {'action': 'HOLD'}
        except Exception as e:
            self.logger.error(f"Error in evaluate_signal: {str(e)}")
            return {'action': 'HOLD'}

    def calculate_position_size(self, current_price: float, stop_loss: float, max_risk_value: float) -> float:
        risk_per_unit = abs(current_price - stop_loss)
        if risk_per_unit == 0:
            return 0
        return max_risk_value / risk_per_unit

    def check_risk_limits(self, position_size: float, portfolio_value: float) -> bool:
        return position_size <= (portfolio_value * self.max_position_size)

    def calculate_volatility(self, historical_data: pd.DataFrame) -> float:
        returns = historical_data['close'].pct_change().dropna()
        return returns.rolling(window=self.volatility_lookback).std().iloc[-1]

    def adjust_risk_parameters(self, current_volatility: float):
        if not hasattr(self, 'base_volatility'):
            self.base_volatility = current_volatility
        volatility_factor = current_volatility / self.base_volatility
        self.stop_loss_pct = min(0.05, self.stop_loss_pct * volatility_factor)
        self.take_profit_pct = max(0.02, self.take_profit_pct * volatility_factor)
        self.max_risk_per_trade = min(0.02, self.max_risk_per_trade * volatility_factor)
        self.logger.info(f"Risk parameters adjusted for volatility: {self.__dict__}")

    def update_parameters(self, new_params: Dict[str, Any]):
        for param, value in new_params.items():
            if hasattr(self, param):
                setattr(self, param, value)
        self.logger.info(f"Risk parameters updated: {self.__dict__}")

    def get_current_parameters(self) -> Dict[str, Any]:
        return {
            'max_position_size': self.max_position_size,
            'stop_loss_pct': self.stop_loss_pct,
            'take_profit_pct': self.take_profit_pct,
            'max_risk_per_trade': self.max_risk_per_trade,
            'max_drawdown': self.max_drawdown,
            'volatility_lookback': self.volatility_lookback
        }

    def check_drawdown(self, current_value: float, peak_value: float) -> bool:
        drawdown = (peak_value - current_value) / peak_value
        if drawdown > self.max_drawdown:
            self.logger.warning(f"Maximum drawdown exceeded: {drawdown:.2%}")
            return False
        return True