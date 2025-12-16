# MLFastOpt

[![PyPI version](https://badge.fury.io/py/mlfastopt.svg)](https://badge.fury.io/py/mlfastopt)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MLFastOpt is a high-speed ensemble optimization system for Bayesian hyperparameter tuning of **LightGBM, XGBoost, and Random Forest models**.

## Features

- 🚀 **Fast Optimization**: Advanced Bayesian optimization algorithms (Sobol + BoTorch).
- 🧩 **Multi-Model Support**: Tune LightGBM, XGBoost, or Random Forest ensembles.
- ⚙️ **Simple Config**: Hierarchical JSON configuration and YAML/Python search spaces.
- 📊 **Rich Analytics**: Built-in web dashboards and visualization tools.

### Prerequisites

- Python 3.9+
- **macOS Users**: You must install `openmp` for LightGBM/XGBoost to work:
  ```bash
  brew install libomp
  ```

## Installation

1.  **Activate Virtual Environment**:
    ```bash
    source .venv/bin/activate
    # OR if you haven't created one yet:
    # python3.12 -m venv .venv && source .venv/bin/activate
    ```

2.  **Install Package**:
    ```bash
    pip install -e .[dev]
    ```

## Quick Start (End Users)

If you installed the package via `pip install mlfastopt`, follow these steps:

1.  **Create Configuration Files**:
    You need a `config.json` and a hyperparameter space file (e.g., `hyperparameters.yaml`).
    
    *config.json*:
    ```json
    {
      "data": { "path": "train.parquet", "label_column": "target", "features": "features.yaml" },
      "model": { "type": "xgboost", "hyperparameter_path": "config/hyperparameters/xgboost.yaml" },
      "training": { "metric": "f1", "total_trials": 20 },
      "output": { "dir": "outputs" }
    }
    ```

2.  **Run Optimization**:
    ```bash
    export OMP_NUM_THREADS=1
    mlfastopt-optimize --config config.json
    ```

## Quick Start (Developers)

**Prerequisite**: Input data must be preprocessed and numerical. Handle all categorical encoding (e.g., one-hot, label encoding) before using MLFastOpt (except for LightGBM/XGBoost which have some categorical support).

### 1. Setup
Create the required directory structure:
```bash
mkdir -p config/hyperparameters data
```

### 2. Define Parameter Space
We recommend using YAML for parameter spaces. Create `config/hyperparameters/my_space.yaml`:

```yaml
parameters:
  - name: learning_rate
    type: range
    bounds: [0.01, 0.3]
    value_type: float
    log_scale: true

  - name: max_depth
    type: range
    bounds: [3, 10]
    value_type: int
```

### 3. Configure
Create `my_config.json` using the nested structure:

```json
{
  "data": {
    "path": "data/your_dataset.parquet",
    "label_column": "target",
    "features": ["feature1", "feature2"],
    "class_weight": { "0": 1, "1": 5 },
    "under_sample_majority_ratio": 1.0
  },
  "model": {
    "type": "lightgbm",
    "hyperparameter_path": "config/hyperparameters/my_space.yaml",
    "ensemble_size": 5
  },
  "training": {
    "total_trials": 20,
    "sobol_trials": 5,
    "metric": "soft_recall",
    "parallel": true,
    "n_jobs": -1
  },
  "output": {
    "dir": "outputs/runs"
  }
}
```

### 4. Run
Execute optimization (ensure single-threading for LightGBM/XGBoost to avoid deadlocks):

```bash
OMP_NUM_THREADS=1 python -m mlfastopt.cli --config my_config.json
```

## Configuration Reference

### Data Section (`data`)
| Parameter | Description | Default |
|-----------|-------------|---------|
| `path` | Path to dataset (CSV/Parquet). | Required |
| `label_column` | Name of target column. | Required |
| `features` | List of features or path to YAML file. | Required |
| `class_weight` | Dictionary of class weights (e.g., `{"0": 1, "1": 10}`). | `None` |

### Model Section (`model`)
| Parameter | Description | Default |
|-----------|-------------|---------|
| `type` | Model type: `lightgbm`, `xgboost`, `random_forest`. | `lightgbm` |
| `hyperparameter_path` | Path to parameter space file. | Required |
| `ensemble_size` | Models per ensemble. | `1` |

### Training Section (`training`)
| Parameter | Description | Default |
|-----------|-------------|---------|
| `total_trials` | Total optimization trials. | `20` |
| `metric` | Metric to maximize (`soft_recall`, `soft_f1_score`, etc). | `soft_recall` |
| `parallel` | Enable parallel training of ensemble members. | `false` |

## Outputs

Results are saved to `outputs/`:
- **`runs/`**: Detailed logs and models for each run.
- **`best_trials/`**: JSON configurations of the best performing trials.
- **`visualizations/`**: Generated plots.
