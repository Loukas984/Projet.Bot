





import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.stattools import adfuller
from config import MARKET_ANALYSIS_CONFIG, VOLATILITY_CONFIG

class MarketAnalyzer:
    def __init__(self, data_handler):
        self.data_handler = data_handler

    # ... (rest of the code remains the same)


    def analyze_market(self, symbol, timeframe):
        data = self.data_handler.get_historical_data(symbol, timeframe)
        volatility = self.calculate_volatility(data)
        trend = self.identify_trend(data)
        regime = self.detect_market_regime(data)
        support, resistance = self.detect_support_resistance(data)
        upper_bb, middle_bb, lower_bb = self.calculate_bollinger_bands(data)
        rsi = self.calculate_rsi(data)
        macd, signal, histogram = self.calculate_macd(data)
        return {
            'volatility': volatility,
            'trend': trend,
            'regime': regime,
            'support': support,
            'resistance': resistance,
            'bollinger_bands': {
                'upper': upper_bb.iloc[-1],
                'middle': middle_bb.iloc[-1],
                'lower': lower_bb.iloc[-1]
            },
            'rsi': rsi.iloc[-1],
            'macd': {
                'macd': macd.iloc[-1],
                'signal': signal.iloc[-1],
                'histogram': histogram.iloc[-1]
            }
        }

    def calculate_volatility(self, data):
        returns = data['close'].pct_change().dropna()
        volatility = returns.rolling(window=VOLATILITY_CONFIG['WINDOW']).std().iloc[-1]
        return volatility

    def identify_trend(self, data):
        sma_short = data['close'].rolling(window=MARKET_ANALYSIS_CONFIG['TREND_WINDOW']['short']).mean()
        sma_long = data['close'].rolling(window=MARKET_ANALYSIS_CONFIG['TREND_WINDOW']['long']).mean()
        current_price = data['close'].iloc[-1]

        if current_price > sma_short.iloc[-1] > sma_long.iloc[-1]:
            return "UPTREND"
        elif current_price < sma_short.iloc[-1] < sma_long.iloc[-1]:
            return "DOWNTREND"
        else:
            return "SIDEWAYS"

    def detect_market_regime(self, data):
        returns = data['close'].pct_change().dropna()
        
        # Perform Augmented Dickey-Fuller test
        adf_result = adfuller(returns)
        
        # Check for stationarity
        if adf_result[1] <= 0.05:
            # The series is stationary
            if returns.std() > MARKET_ANALYSIS_CONFIG['REGIME_CHANGE_THRESHOLD']:
                return "HIGH_VOLATILITY"
            else:
                return "LOW_VOLATILITY"
        else:
            # The series is non-stationary
            if returns.mean() > 0:
                return "BULL_MARKET"
            else:
                return "BEAR_MARKET"

    def detect_support_resistance(self, data):
        window = MARKET_ANALYSIS_CONFIG['SUPPORT_RESISTANCE_WINDOW']
        rolling_min = data['low'].rolling(window=window, center=True).min()
        rolling_max = data['high'].rolling(window=window, center=True).max()
        
        support_levels = rolling_min[rolling_min == data['low']]
        resistance_levels = rolling_max[rolling_max == data['high']]
        
        return support_levels.iloc[-1] if not support_levels.empty else None, resistance_levels.iloc[-1] if not resistance_levels.empty else None

    def calculate_bollinger_bands(self, data):
        window = MARKET_ANALYSIS_CONFIG['BOLLINGER_BANDS_WINDOW']
        num_std = MARKET_ANALYSIS_CONFIG['BOLLINGER_BANDS_STD']
        rolling_mean = data['close'].rolling(window=window).mean()
        rolling_std = data['close'].rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return upper_band, rolling_mean, lower_band

    def calculate_rsi(self, data, period=14):
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_macd(self, data, fast_period=12, slow_period=26, signal_period=9):
        exp1 = data['close'].ewm(span=fast_period, adjust=False).mean()
        exp2 = data['close'].ewm(span=slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        histogram = macd - signal
        return macd, signal, histogram


