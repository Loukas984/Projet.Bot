# ml_optimizer.py
# Implements machine learning optimization for the crypto trading bot

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from config import ML_MODEL_TYPE, ML_TRAIN_TEST_SPLIT, ML_FEATURES

class MLOptimizer:
    def __init__(self, backtester, trading_strategy, risk_manager):
        self.backtester = backtester
        self.trading_strategy = trading_strategy
        self.risk_manager = risk_manager
        self.model = self._create_model()

    def _create_model(self):
        if ML_MODEL_TYPE == 'RandomForest':
            return RandomForestRegressor(n_estimators=100, random_state=42)
        # Add more model types here as needed
        else:
            raise ValueError(f"Unsupported model type: {ML_MODEL_TYPE}")

    def optimize(self, start_date, end_date):
        # Fetch historical data
        data = self.backtester.data_handler.fetch_historical_data(start_date, end_date)
        
        # Prepare features and target
        X = self._prepare_features(data)
        y = self._prepare_target(data)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1-ML_TRAIN_TEST_SPLIT, random_state=42)
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = self.model.predict(X_test)
        
        # Calculate performance
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        # Use the model to optimize strategy parameters
        optimized_params = self._optimize_strategy_params(data)
        
        return {
            'rmse': rmse,
            'optimized_params': optimized_params
        }

    def _prepare_features(self, data):
        # Prepare feature data based on ML_FEATURES config
        features = pd.DataFrame()
        for feature in ML_FEATURES:
            if feature in data.columns:
                features[feature] = data[feature]
            elif hasattr(self.trading_strategy, f'calculate_{feature}'):
                features[feature] = getattr(self.trading_strategy, f'calculate_{feature}')(data)
        return features

    def _prepare_target(self, data):
        # Prepare target variable (e.g., future returns)
        return data['close'].pct_change().shift(-1).dropna()

    def _optimize_strategy_params(self, data):
        # Use the trained model to find optimal strategy parameters
        # This is a placeholder implementation
        return {
            'sma_short': 10,
            'sma_long': 30,
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30
        }

    def predict(self, current_data):
        # Use the trained model to make predictions
        features = self._prepare_features(current_data)
        return self.model.predict(features)