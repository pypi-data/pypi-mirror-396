
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch, mock_open
from mlfastopt.core.data import DataProcessor

@pytest.fixture
def mock_read_csv():
    with patch('pandas.read_csv') as mock:
        yield mock

@pytest.fixture
def mock_pl_scan():
    with patch('polars.scan_parquet') as mock:
        yield mock

def test_load_local_csv(ae_config, tmp_path, sample_data):
    """Test loading a local CSV file"""
    X, y = sample_data
    df = pd.concat([X, y], axis=1)
    
    csv_path = tmp_path / "test.csv"
    df.to_csv(csv_path, index=False)
    
    ae_config.DATA_PATH = str(csv_path)
    ae_config.FEATURES = list(X.columns)
    ae_config.LABEL_COLUMN = y.name
    
    processor = DataProcessor(ae_config)
    X_loaded, y_loaded, features = processor.load_and_preprocess_data()
    
    assert len(X_loaded) == len(X)
    assert features == ae_config.FEATURES

def test_load_gcs_path(ae_config, mock_read_csv):
    """Test loading from GCS path uses correct logic"""
    ae_config.DATA_PATH = "gs://bucket/data.csv"
    ae_config.FEATURES = ["f1", "f2"]
    
    # Mock gcsfs existence
    with patch.dict('sys.modules', {'gcsfs': MagicMock()}):
        # Mock checks to return valid data
        mock_df = pd.DataFrame({
            "f1": [1, 2], "f2": [3, 4], "target": [0, 1]
        })
        mock_read_csv.return_value = mock_df
        
        processor = DataProcessor(ae_config)
        X, y, feats = processor.load_and_preprocess_data()
        
        # Verify pandas was called with GCS path
        # Verify pandas was called with GCS path
        assert mock_read_csv.called
        args, kwargs = mock_read_csv.call_args
        assert args[0] == "gs://bucket/data.csv"
        assert set(kwargs['usecols']) == {"f1", "f2", "target"}

def test_load_http_path(ae_config, mock_read_csv):
    """Test loading from HTTP path uses correct logic"""
    ae_config.DATA_PATH = "https://example.com/data.csv"
    ae_config.FEATURES = ["f1"] 
    # Label is default 'target' in ae_config fixture usually, or we assume it
    # We need to make sure mock returns frame with label
    
    mock_df = pd.DataFrame({"f1": [1], "target": [0]})
    # Fix: mock_read_csv needs to return this df
    mock_read_csv.return_value = mock_df
    
    # Fix: ae_config.LABEL_COLUMN might be missing if not set in fixture explicitly to something known
    # Assuming fixture sets it to 'target' or similar. Let's set it explicitly.
    ae_config.LABEL_COLUMN = "target"
    
    processor = DataProcessor(ae_config)
    X, y, feats = processor.load_and_preprocess_data()
    
    assert mock_read_csv.called
    args, kwargs = mock_read_csv.call_args
    assert args[0] == "https://example.com/data.csv"
    assert "target" in kwargs['usecols']

def test_validation_errors(ae_config, tmp_path, sample_data):
    """Test validation logic"""
    X, y = sample_data
    df = pd.concat([X, y], axis=1)
    csv_path = tmp_path / "data.csv"
    df.to_csv(csv_path, index=False)
    
    ae_config.DATA_PATH = str(csv_path)
    
    # Test missing feature
    ae_config.FEATURES = ["non_existent"]
    processor = DataProcessor(ae_config)
    # Match either our custom error or Pandas usecols validation error
    with pytest.raises(ValueError, match="Missing features|Usecols do not match"):
        processor.load_and_preprocess_data()
