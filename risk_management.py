# risk_management.py
from typing import Dict, Any

class RiskManager:
    def __init__(self, config: Dict[str, Any]):
        self.max_position_size = config['max_position_size']
        self.stop_loss_pct = config['stop_loss_pct']
        self.take_profit_pct = config['take_profit_pct']

    def evaluate_signal(self, signal: str, portfolio_value: float, current_price: float) -> Dict[str, Any]:
        if signal == 'BUY':
            position_size = min(portfolio_value * self.max_position_size, portfolio_value)
            quantity = position_size / current_price
            stop_loss = current_price * (1 - self.stop_loss_pct)
            take_profit = current_price * (1 + self.take_profit_pct)
            
            return {
                'action': 'BUY',
                'quantity': quantity,
                'stop_loss': stop_loss,
                'take_profit': take_profit
            }
        elif signal == 'SELL':
            # Assuming we're selling all of our position
            quantity = portfolio_value / current_price
            stop_loss = current_price * (1 + self.stop_loss_pct)
            take_profit = current_price * (1 - self.take_profit_pct)
            
            return {
                'action': 'SELL',
                'quantity': quantity,
                'stop_loss': stop_loss,
                'take_profit': take_profit
            }
        else:
            return {'action': 'HOLD'}

    def update_parameters(self, new_params: Dict[str, Any]):
        if 'max_position_size' in new_params:
            self.max_position_size = new_params['max_position_size']
        if 'stop_loss_pct' in new_params:
            self.stop_loss_pct = new_params['stop_loss_pct']
        if 'take_profit_pct' in new_params:
            self.take_profit_pct = new_params['take_profit_pct']