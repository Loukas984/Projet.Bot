

import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, Tuple
from config import SYMBOL, TIMEFRAME, STRATEGY_PARAMS, MARKET_ANALYSIS_CONFIG, VOLATILITY_CONFIG


class AdvancedTradingStrategy:
    def __init__(self):
        self.symbol = SYMBOL
        self.timeframe = TIMEFRAME
        self.strategy_params = STRATEGY_PARAMS.copy()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.info(f"AdvancedTradingStrategy initialized for {self.symbol} with {self.timeframe} timeframe")

    def generate_signal(self, market_data: Dict[str, Any], sentiment: float, ml_prediction: float) -> Dict[str, Any]:
        try:
            if market_data['latest_data'].empty:
                self.logger.warning("Empty market data received")
                return {'action': 'HOLD'}

            current_price = market_data['current_price']
            volatility = market_data['volatility']
            trend = market_data['trend']
            regime = market_data['regime']
            support = market_data['support']
            resistance = market_data['resistance']
            bb = market_data['bollinger_bands']
            rsi = market_data['rsi']
            macd = market_data['macd']

            # Adjust strategy parameters based on market conditions
            self.adjust_strategy_params(volatility, trend, regime)

            # Generate signal based on multiple factors
            if (current_price < bb['lower'] and 
                rsi < self.strategy_params['RSI_OVERSOLD'] and 
                macd['macd'] > macd['signal'] and
                sentiment > self.strategy_params['SENTIMENT_THRESHOLD'] and 
                ml_prediction > current_price * (1 + self.strategy_params['ML_THRESHOLD']) and
                trend == "UPTREND"):
                action = 'BUY'
                stop_loss = max(support, current_price * (1 - self.strategy_params['STOP_LOSS_PCT']))
                take_profit = min(resistance, current_price * (1 + self.strategy_params['TAKE_PROFIT_PCT']))
            elif (current_price > bb['upper'] and 
                  rsi > self.strategy_params['RSI_OVERBOUGHT'] and 
                  macd['macd'] < macd['signal'] and
                  sentiment < -self.strategy_params['SENTIMENT_THRESHOLD'] and 
                  ml_prediction < current_price * (1 - self.strategy_params['ML_THRESHOLD']) and
                  trend == "DOWNTREND"):
                action = 'SELL'
                stop_loss = min(resistance, current_price * (1 + self.strategy_params['STOP_LOSS_PCT']))
                take_profit = max(support, current_price * (1 - self.strategy_params['TAKE_PROFIT_PCT']))
            else:
                action = 'HOLD'
                stop_loss = take_profit = None

            self.logger.info(f"Generated signal: {action} for {self.symbol}")
            return {
                'action': action,
                'stop_loss': stop_loss,
                'take_profit': take_profit
            }
        except Exception as e:
            self.logger.error(f"Error generating signal: {str(e)}")
            return {'action': 'HOLD'}

    def adjust_strategy_params(self, volatility: float, trend: str, regime: str):
        if regime == "HIGH_VOLATILITY":
            self.strategy_params['STOP_LOSS_PCT'] *= 1.5
            self.strategy_params['TAKE_PROFIT_PCT'] *= 1.5
        elif regime == "LOW_VOLATILITY":
            self.strategy_params['STOP_LOSS_PCT'] *= 0.75
            self.strategy_params['TAKE_PROFIT_PCT'] *= 0.75

        if trend == "UPTREND":
            self.strategy_params['RSI_OVERSOLD'] += 5
            self.strategy_params['RSI_OVERBOUGHT'] += 5
        elif trend == "DOWNTREND":
            self.strategy_params['RSI_OVERSOLD'] -= 5
            self.strategy_params['RSI_OVERBOUGHT'] -= 5

        self.logger.info(f"Adjusted strategy parameters: {self.strategy_params}")

    def update_parameters(self, new_params: Dict[str, Any]):
        self.strategy_params.update(new_params)
        self.logger.info(f"Strategy parameters updated: {self.strategy_params}")

    def get_current_parameters(self) -> Dict[str, Any]:
        return self.strategy_params.copy()


    def backtest(self, historical_data: pd.DataFrame, initial_balance: float = 10000) -> Tuple[pd.DataFrame, float]:
        """
        Backtest the strategy on historical data.
        
        Args:
            historical_data (pd.DataFrame): Historical market data with calculated indicators
            initial_balance (float): Initial balance for backtesting
        
        Returns:
            Tuple[pd.DataFrame, float]: DataFrame with trade history and final balance
        """
        balance = initial_balance
        position = 0
        trades = []

        for i in range(len(historical_data)):
            data = historical_data.iloc[:i+1]
            market_data = {
                'latest_data': data,
                'current_price': data['close'].iloc[-1],
                'volatility': data['close'].pct_change().std(),
                'trend': self.identify_trend(data),
                'regime': self.detect_market_regime(data),
                'support': data['low'].min(),
                'resistance': data['high'].max(),
                'bollinger_bands': self.calculate_bollinger_bands(data),
                'rsi': self.calculate_rsi(data).iloc[-1],
                'macd': self.calculate_macd(data)
            }
            signal = self.generate_signal(market_data, 0, data['close'].iloc[-1])  # Using price as ML prediction for simplicity

            if signal['action'] == 'BUY' and position == 0:
                position = balance / data['close'].iloc[-1]
                balance = 0
                trades.append({'date': data.index[-1], 'type': 'BUY', 'price': data['close'].iloc[-1], 'position': position, 'balance': balance})
            elif signal['action'] == 'SELL' and position > 0:
                balance = position * data['close'].iloc[-1]
                position = 0
                trades.append({'date': data.index[-1], 'type': 'SELL', 'price': data['close'].iloc[-1], 'position': position, 'balance': balance})

        if position > 0:
            balance = position * historical_data['close'].iloc[-1]

        trade_history = pd.DataFrame(trades)
        return trade_history, balance

    def identify_trend(self, data: pd.DataFrame) -> str:
        sma_short = data['close'].rolling(window=MARKET_ANALYSIS_CONFIG['TREND_WINDOW']['short']).mean()
        sma_long = data['close'].rolling(window=MARKET_ANALYSIS_CONFIG['TREND_WINDOW']['long']).mean()
        current_price = data['close'].iloc[-1]

        if current_price > sma_short.iloc[-1] > sma_long.iloc[-1]:
            return "UPTREND"
        elif current_price < sma_short.iloc[-1] < sma_long.iloc[-1]:
            return "DOWNTREND"
        else:
            return "SIDEWAYS"

    def detect_market_regime(self, data: pd.DataFrame) -> str:
        returns = data['close'].pct_change().dropna()
        if returns.std() > MARKET_ANALYSIS_CONFIG['REGIME_CHANGE_THRESHOLD']:
            return "HIGH_VOLATILITY"
        else:
            return "LOW_VOLATILITY"

    def calculate_bollinger_bands(self, data: pd.DataFrame) -> Dict[str, float]:
        window = MARKET_ANALYSIS_CONFIG['BOLLINGER_BANDS_WINDOW']
        num_std = MARKET_ANALYSIS_CONFIG['BOLLINGER_BANDS_STD']
        rolling_mean = data['close'].rolling(window=window).mean()
        rolling_std = data['close'].rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return {'upper': upper_band.iloc[-1], 'middle': rolling_mean.iloc[-1], 'lower': lower_band.iloc[-1]}

    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_macd(self, data: pd.DataFrame) -> Dict[str, float]:
        exp1 = data['close'].ewm(span=12, adjust=False).mean()
        exp2 = data['close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        return {'macd': macd.iloc[-1], 'signal': signal.iloc[-1], 'histogram': histogram.iloc[-1]}


