# MLFastOpt

[![PyPI version](https://badge.fury.io/py/mlfastopt.svg)](https://badge.fury.io/py/mlfastopt)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MLFastOpt is a high-speed ensemble optimization system for Bayesian hyperparameter tuning of **LightGBM models**.

## Features

- 🚀 **Fast Optimization**: Advanced Bayesian optimization algorithms.
- 🎯 **LightGBM Focused**: Automated ensemble creation and tuning.
- ⚙️ **Simple Config**: JSON-based configuration and Python-based search spaces.
- 📊 **Rich Analytics**: Built-in web dashboards and visualization tools.

## Installation

```bash
pip install mlfastopt
```

## Quick Start

**Prerequisite**: Input data must be preprocessed and numerical. Handle all categorical encoding (e.g., one-hot, label encoding) before using MLFastOpt.

### 1. Setup
Create the required directory structure:
```bash
mkdir -p config/hyperparameters data
```

### 2. Define Parameter Space
Create `config/hyperparameters/my_space.py`:

```python
PARAMETERS = [
    {"name": "num_leaves", "type": "range", "bounds": [20, 200], "value_type": "int"},
    {"name": "learning_rate", "type": "range", "bounds": [0.01, 0.3], "value_type": "float", "log_scale": True},
    {"name": "n_estimators", "type": "range", "bounds": [100, 300], "value_type": "int"},
    # Add other LightGBM parameters as needed
]

def get_parameter_space():
    return PARAMETERS
```

### 3. Configure
Create `my_config.json`:

```json
{
  "DATA_PATH": "data/your_dataset.parquet",
  "HYPERPARAMETER_PATH": "config/hyperparameters/my_space.py",
  "LABEL_COLUMN": "target",
  "FEATURES": ["feature1", "feature2"],
  "N_ENSEMBLE_GROUP_NUMBER": 5,
  "AE_NUM_TRIALS": 20,
  "PARALLEL_TRAINING": true,
  "N_JOBS": -1
}
```

### 4. Run
Execute optimization (ensure single-threading for LightGBM to avoid deadlocks):

```bash
export OMP_NUM_THREADS=1
python -m mlfastopt.cli --config my_config.json
```

## Configuration Reference

| Parameter | Description | Default |
|-----------|-------------|---------|
| `DATA_PATH` | Path to dataset (CSV/Parquet). | Required |
| `HYPERPARAMETER_PATH` | Path to parameter space file. | Required |
| `LABEL_COLUMN` | Name of target column. | Required |
| `FEATURES` | List of feature names. | Required |
| `N_ENSEMBLE_GROUP_NUMBER` | Models per ensemble. | `1` |
| `AE_NUM_TRIALS` | Total optimization trials. | `20` |
| `NUM_SOBOL_TRIALS` | Initial random trials. | `5` |
| `OPTIMIZATION_METRICS` | Metric to maximize (`soft_recall`, `soft_f1_score`, etc). | `soft_recall` |
| `SAVE_THRESHOLD_ENABLED` | Save only models exceeding metric threshold. | `false` |
| `ENABLE_DATA_IMPUTATION` | Simple median/mode imputation. | `false` |

## Outputs

Results are saved to `outputs/`:
- **`runs/`**: Detailed logs and models for each run.
- **`best_trials/`**: JSON configurations of the best performing trials.
- **`visualizations/`**: Generated plots.
