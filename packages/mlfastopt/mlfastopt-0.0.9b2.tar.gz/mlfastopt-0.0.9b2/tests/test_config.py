
import pytest
import json
import os
from mlfastopt.core.config import AEConfig

def test_load_nested_config(test_config_path):
    """Test loading a nested configuration file"""
    config = AEConfig.from_file(test_config_path)
    
    assert config.DATA_PATH == "test_data.csv"
    assert config.LABEL_COLUMN == "target"
    assert config.N_ENSEMBLE_GROUP_NUMBER == 2
    assert config.AE_NUM_TRIALS == 5
    assert config.OUTPUT_DIR.endswith("outputs")

def test_load_legacy_config(tmp_path):
    """Test loading a legacy flat configuration file"""
    legacy_data = {
        "DATA_PATH": "legacy_data.csv",
        "FEATURES": ["f1"],
        "LABEL_COLUMN": "target",
        "CLASS_WEIGHT": {"0": 1, "1": 1},
        "UNDER_SAMPLE_MAJORITY_RATIO": 1,
        "AE_NUM_TRIALS": 10,
        "N_ENSEMBLE_GROUP_NUMBER": 5,
        "SOFT_PREDICTION_THRESHOLD": 0.5,
        "MIN_RECALL_THRESHOLD": 0.8,
        "NUM_SOBOL_TRIALS": 5,
        "RANDOM_SEED": 123,
        "PARALLEL_TRAINING": False,
        "N_JOBS": 1
    }
    
    config_file = tmp_path / "legacy_config.json"
    with open(config_file, 'w') as f:
        json.dump(legacy_data, f)
        
    config = AEConfig.from_file(str(config_file))
    
    assert config.DATA_PATH == "legacy_data.csv"
    assert config.AE_NUM_TRIALS == 10
    assert config.N_ENSEMBLE_GROUP_NUMBER == 5

def test_missing_required_params(tmp_path):
    """Test validation of missing parameters"""
    incomplete_data = {
        "data": {"path": "test.csv"} # Missing other required fields
    }
    
    config_file = tmp_path / "incomplete.json"
    with open(config_file, 'w') as f:
        json.dump(incomplete_data, f)
        
    with pytest.raises(ValueError, match="Missing required configuration parameters"):
        AEConfig.from_file(str(config_file))

def test_load_external_features_json(tmp_path):
    """Test loading features from external JSON file"""
    features = ["col1", "col2", "col3"]
    feature_file = tmp_path / "features.json"
    
    # Test list format
    with open(feature_file, 'w') as f:
        json.dump(features, f)
        
    config_data = {
        "meta": {}, 
        "data": {"features": str(feature_file), "path": "p", "label_column": "l", "under_sample_majority_ratio": 1},
        "model": {"hyperparameter_path": "h", "ensemble_size": 1, "soft_prediction_threshold": 0.5, "min_recall_threshold": 0.8},
        "training": {"total_trials": 1, "sobol_trials": 1, "random_seed": 42, "parallel": False, "n_jobs": 1}
    }
    # Add CLASS_WEIGHT which is special
    config_data["data"]["class_weight"] = {"0": 1, "1": 1}
    
    config_file = tmp_path / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)
        
    config = AEConfig.from_file(str(config_file))
    assert config.FEATURES == features

def test_load_external_features_yaml(tmp_path):
    """Test loading features from external YAML file"""
    features = ["colA", "colB"]
    feature_file = tmp_path / "features.yaml"
    
    # Test dict format
    import yaml
    with open(feature_file, 'w') as f:
        yaml.dump({"features": features}, f)
        
    config_data = {
        "meta": {}, 
        "data": {"features": str(feature_file), "path": "p", "label_column": "l", "under_sample_majority_ratio": 1},
        "model": {"hyperparameter_path": "h", "ensemble_size": 1, "soft_prediction_threshold": 0.5, "min_recall_threshold": 0.8},
        "training": {"total_trials": 1, "sobol_trials": 1, "random_seed": 42, "parallel": False, "n_jobs": 1}
    }
    config_data["data"]["class_weight"] = {"0": 1, "1": 1}

    config_file = tmp_path / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)
        
    config = AEConfig.from_file(str(config_file))
    assert config.FEATURES == features
