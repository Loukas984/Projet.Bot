import unittest

# Importer tous les tests
from tests.test_trading_strategy import TestAdvancedTradingStrategy
from tests.test_components import TestDataHandler, TestTradingStrategy, TestRiskManager, TestOrderExecutor, TestBacktester

if __name__ == '__main__':
    # Créer une suite de tests
    test_suite = unittest.TestSuite()
    
    # Ajouter les tests à la suite
    test_suite.addTest(unittest.makeSuite(TestAdvancedTradingStrategy))
    test_suite.addTest(unittest.makeSuite(TestDataHandler))
    test_suite.addTest(unittest.makeSuite(TestTradingStrategy))
    test_suite.addTest(unittest.makeSuite(TestRiskManager))
    test_suite.addTest(unittest.makeSuite(TestOrderExecutor))
    test_suite.addTest(unittest.makeSuite(TestBacktester))
    
    # Exécuter les tests
    runner = unittest.TextTestRunner()
    runner.run(test_suite)