# trading_strategy.py
import numpy as np
import pandas as pd
import logging
from config import SMA_SHORT, SMA_LONG, RSI_PERIOD, RSI_OVERBOUGHT, RSI_OVERSOLD
from typing import Dict, Any

class AdvancedTradingStrategy:
    def __init__(self, symbol: str, timeframe: str, config: Dict[str, Any] = None):
        self.symbol = symbol
        self.timeframe = timeframe
        if config:
            self.strategy_params = config.get('strategy_params', {})
        else:
            self.strategy_params = {
                'sma_short': SMA_SHORT,
                'sma_long': SMA_LONG,
                'rsi_period': RSI_PERIOD,
                'rsi_overbought': RSI_OVERBOUGHT,
                'rsi_oversold': RSI_OVERSOLD
            }
        self.logger = logging.getLogger(__name__)

    def generate_signal(self, market_data: pd.DataFrame, sentiment: float, ml_prediction: float) -> str:
        # Calculate technical indicators
        sma_short = self._calculate_sma(market_data, self.strategy_params['sma_short'])
        sma_long = self._calculate_sma(market_data, self.strategy_params['sma_long'])
        rsi = self._calculate_rsi(market_data, self.strategy_params['rsi_period'])

        # Get the latest price
        current_price = market_data['close'].iloc[-1]

        # Generate signal based on technical indicators, sentiment, and ML prediction
        if (sma_short.iloc[-1] > sma_long.iloc[-1] and 
            rsi.iloc[-1] < self.strategy_params['rsi_oversold'] and 
            sentiment > 0 and 
            ml_prediction > current_price):
            return 'BUY'
        elif (sma_short.iloc[-1] < sma_long.iloc[-1] and 
              rsi.iloc[-1] > self.strategy_params['rsi_overbought'] and 
              sentiment < 0 and 
              ml_prediction < current_price):
            return 'SELL'
        else:
            return 'HOLD'

    def _calculate_sma(self, data: pd.DataFrame, period: int) -> pd.Series:
        return data['close'].rolling(window=period).mean()

    def _calculate_rsi(self, data: pd.DataFrame, period: int) -> pd.Series:
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def update_parameters(self, new_params: Dict[str, Any]):
        self.strategy_params.update(new_params)
        self.logger.info(f"Strategy parameters updated: {self.strategy_params}")