
import pandas as pd
import numpy as np
from trading_strategy import AdvancedTradingStrategy
from market_analyzer import MarketAnalyzer
from data_handler import DataHandler
from api_connector import APIConnector
from config import API_KEY, API_SECRET, SYMBOL, TIMEFRAME

def test_trading_strategy():
    # Initialize components
    api_connector = APIConnector(API_KEY, API_SECRET)
    data_handler = DataHandler(api_connector)
    market_analyzer = MarketAnalyzer(data_handler)
    trading_strategy = AdvancedTradingStrategy()

    # Fetch some historical data
    historical_data = data_handler.get_historical_data(SYMBOL, TIMEFRAME, limit=100)

    # Prepare market data
    market_data = market_analyzer.analyze_market(SYMBOL, TIMEFRAME)

    # Test generate_signal method
    signal = trading_strategy.generate_signal(market_data, sentiment=0.5, ml_prediction=market_data['current_price'] * 1.01)
    print(f"Generated signal: {signal}")

    # Test backtest method
    trade_history, final_balance = trading_strategy.backtest(historical_data)
    print(f"Backtest results: Final balance: {final_balance}, Number of trades: {len(trade_history)}")

    # Test adjust_strategy_params method
    trading_strategy.adjust_strategy_params(volatility=0.05, trend="UPTREND", regime="HIGH_VOLATILITY")
    print(f"Adjusted strategy parameters: {trading_strategy.get_current_parameters()}")

if __name__ == "__main__":
    test_trading_strategy()
