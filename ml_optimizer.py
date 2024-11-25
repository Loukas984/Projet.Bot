

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib
import os
import logging
import itertools
import time
from config import ML_MODEL_TYPE, ML_TRAIN_TEST_SPLIT, ML_FEATURES


from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, r2_score
import numpy as np

class MLOptimizer:
    # ... (existing code remains)

    def continuous_optimization(self, interval_hours=24):
        """Continuously optimize the model at regular intervals."""
        while True:
            end_date = pd.Timestamp.now()
            start_date = end_date - pd.Timedelta(days=30)
            self.optimize(start_date, end_date)
            time.sleep(interval_hours * 3600)

    def analyze_feature_importance(self, X, y):
        """Analyze and return the importance of each feature."""
        selector = SelectKBest(score_func=f_regression, k='all')
        selector.fit(X, y)
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': selector.scores_
        }).sort_values('importance', ascending=False)
        return feature_importance

    def evaluate_recent_performance(self, days=7):
        """Evaluate the model's performance on recent data."""
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=days)
        recent_data = self.backtester.data_handler.fetch_historical_data(start_date, end_date)
        X = self._prepare_features(recent_data)
        y = self._prepare_target(recent_data)
        y_pred = self.model.predict(X)
        mae = mean_absolute_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        return {'mae': mae, 'r2': r2}

    def detect_regime_change(self, window=30):
        """Detect changes in market regime using rolling statistics."""
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=window*2)
        data = self.backtester.data_handler.fetch_historical_data(start_date, end_date)
        returns = data['close'].pct_change().dropna()
        rolling_mean = returns.rolling(window=window).mean()
        rolling_std = returns.rolling(window=window).std()
        z_score = (returns - rolling_mean) / rolling_std
        regime_change = abs(z_score) > 2  # Threshold for regime change
        return regime_change.any()

    def optimize(self, start_date, end_date):
        try:
            data = self.backtester.data_handler.fetch_historical_data(start_date, end_date)
            X = self._prepare_features(data)
            y = self._prepare_target(data)
            
            # Use TimeSeriesSplit for time series data
            tscv = TimeSeriesSplit(n_splits=5)
            
            param_grid = self._get_param_grid()
            
            grid_search = GridSearchCV(self.model, param_grid, cv=tscv, scoring='neg_mean_squared_error', n_jobs=-1)
            grid_search.fit(X, y)
            
            self.model = grid_search.best_estimator_
            
            mse = -grid_search.best_score_
            rmse = np.sqrt(mse)
            
            feature_importance = self.analyze_feature_importance(X, y)
            recent_performance = self.evaluate_recent_performance()
            regime_change = self.detect_regime_change()
            
            optimized_params = self._optimize_strategy_params(data)
            
            self.logger.info(f"ML optimization completed. RMSE: {rmse}")
            self.logger.info(f"Recent performance: MAE: {recent_performance['mae']}, R2: {recent_performance['r2']}")
            self.logger.info(f"Regime change detected: {regime_change}")
            self.save_model()
            
            return {
                'rmse': rmse,
                'optimized_params': optimized_params,
                'feature_importance': feature_importance,
                'recent_performance': recent_performance,
                'regime_change': regime_change
            }
        except Exception as e:
            self.logger.error(f"Error in ML optimization: {str(e)}")
            return None

    # ... (rest of the existing code remains)



    def predict(self, current_data):
        try:
            features = self._prepare_features(current_data)
            return self.model.predict(features)
        except Exception as e:
            self.logger.error(f"Error in ML prediction: {str(e)}")
            return None
