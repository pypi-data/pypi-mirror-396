
import pytest
from unittest.mock import MagicMock, patch, call
import pandas as pd
import numpy as np
from mlfastopt.core.optimizer import AxOptimizer
from mlfastopt.core.callbacks import OptimizationCallback

class MockCallback(OptimizationCallback):
    def __init__(self):
        self.start_calls = 0
        self.trial_start_calls = 0
        self.trial_complete_calls = 0
        self.trial_error_calls = 0
        self.end_calls = 0
        
    def on_optimization_start(self, config):
        self.start_calls += 1
        
    def on_trial_start(self, trial_index, parameters):
        self.trial_start_calls += 1
        
    def on_trial_complete(self, trial_index, result, duration):
        self.trial_complete_calls += 1
        
    def on_trial_error(self, trial_index, error):
        self.trial_error_calls += 1
        
    def on_optimization_end(self, best_params, total_duration):
        self.end_calls += 1

@pytest.fixture
def mock_ax_client(ae_config):
    """Mock AxClient to simulate optimization process"""
    client = MagicMock()
    
    # Mock get_next_trial to return parameters and index
    client.get_next_trial.return_value = ({"param1": 1}, 0)
    
    # Mock get_pareto_optimal_parameters
    client.get_pareto_optimal_parameters.return_value = {
        0: ({"param1": 1}, {"soft_recall": 0.8, "soft_f1_score": 0.7, "cross_entropy": -0.5})
    }
    
    return client

def test_optimizer_init(ae_config):
    """Test optimizer initialization"""
    optimizer = AxOptimizer(ae_config)
    assert len(optimizer.callbacks) == 1  # Default LoggingCallback
    
    callback = MockCallback()
    optimizer = AxOptimizer(ae_config, callbacks=[callback])
    assert len(optimizer.callbacks) == 1
    assert optimizer.callbacks[0] == callback

def test_optimization_loop(ae_config, sample_data, mock_ax_client):
    """Test the full optimization loop with callbacks"""
    X, y = sample_data
    # Create simple train/test split
    X_train, X_test = X.iloc[:80], X.iloc[80:]
    y_train, y_test = y.iloc[:80], y.iloc[80:]
    
    callback = MockCallback()
    optimizer = AxOptimizer(ae_config, callbacks=[callback])
    
    # Inject mock ax client
    optimizer.ax_client = mock_ax_client
    
    # Mock internal methods to avoid actual training
    with patch.object(optimizer, 'setup_optimization', return_value=mock_ax_client), \
         patch.object(optimizer, 'train_and_evaluate_trial') as mock_train:
        
        # Setup mock return for training
        mock_train.return_value = (
            {"soft_recall": 0.8, "soft_f1_score": 0.7, "cross_entropy": -0.5, "optimization_metric": 0.8}, 
            [] # No models
        )
        
        best_params, results = optimizer.run_optimization(X_train, y_train, X_test, y_test)
        
        # Verify callback calls
        assert callback.start_calls == 1
        assert callback.trial_start_calls == ae_config.AE_NUM_TRIALS
        assert callback.trial_complete_calls == ae_config.AE_NUM_TRIALS
        assert callback.end_calls == 1
        
        # Verify results
        assert len(results) == ae_config.AE_NUM_TRIALS

def test_optimization_error_handling(ae_config, sample_data, mock_ax_client):
    """Test error handling in optimization loop"""
    X, y = sample_data
    X_train, X_test = X.iloc[:80], X.iloc[80:]
    y_train, y_test = y.iloc[:80], y.iloc[80:]
    
    callback = MockCallback()
    optimizer = AxOptimizer(ae_config, callbacks=[callback])
    optimizer.ax_client = mock_ax_client
    
    # Make training fail
    with patch.object(optimizer, 'setup_optimization', return_value=mock_ax_client), \
         patch.object(optimizer, 'train_and_evaluate_trial', side_effect=ValueError("Training failed")):
        
        optimizer.run_optimization(X_train, y_train, X_test, y_test)
        
        # Verify error callback was called
        assert callback.trial_error_calls == ae_config.AE_NUM_TRIALS
        assert callback.trial_complete_calls == 0
