"""
Model components for AE optimization.

This module contains ensemble model training and evaluation classes.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any

import pandas as pd
import numpy as np
from sklearn.metrics import recall_score, f1_score, precision_score
from sklearn.inspection import permutation_importance
from lightgbm import LGBMClassifier

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    
from sklearn.ensemble import RandomForestClassifier

from .config import AEConfig
from sklearn.base import BaseEstimator, ClassifierMixin

# Parallel processing import (optional)
try:
    from joblib import Parallel, delayed
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    logging.warning("joblib not available. Parallel training will fall back to sequential mode.")


class BaseModelWrapper(ABC):
    """Abstract base class for model wrappers"""
    
    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, params: Dict[str, Any], class_weight: Dict = None) -> Any:
        pass
    
    @abstractmethod
    def predict_proba(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        pass
    
    @abstractmethod
    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        pass
    
    @abstractmethod
    def get_feature_importance(self, model: Any) -> np.ndarray:
        pass


class LightGBMWrapper(BaseModelWrapper):
    """Wrapper for LightGBM models"""
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, params: Dict[str, Any], class_weight: Dict = None) -> Any:
        # Extract LightGBM-specific parameters
        lgb_params = params.copy()
        
        # Filter out parameters that might be for other models if mixed (though unlikely in current setup)
        # For now, we assume params are clean or ignored by **kwargs if valid
        
        model = LGBMClassifier(
            **lgb_params,
            class_weight=class_weight,
            verbose=-1
        )
        model.fit(X_train, y_train)
        return model

    def predict_proba(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict_proba(X)[:, 1]

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)

    def get_feature_importance(self, model: Any) -> np.ndarray:
        return model.feature_importances_


class XGBoostWrapper(BaseModelWrapper):
    """Wrapper for XGBoost models"""
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, params: Dict[str, Any], class_weight: Dict = None) -> Any:
        if not XGBOOST_AVAILABLE:
            raise ImportError("XGBoost is not installed. Please install it with `pip install xgboost`.")
        
        # Handle class weights for XGBoost (scale_pos_weight is typical for binary)
        # But sklearn API supports sample_weight or scale_pos_weight
        # We will use the sklearn wrapper which supports scale_pos_weight
        
        xgb_params = params.copy()
        
        # Simple heuristic for scale_pos_weight from class_weight dict if provided
        scale_pos_weight = 1
        if class_weight and 1 in class_weight and 0 in class_weight:
             scale_pos_weight = class_weight[1] / class_weight[0]

        model = XGBClassifier(
            **xgb_params,
            scale_pos_weight=scale_pos_weight,
            use_label_encoder=False,
            eval_metric='logloss',
            verbosity=0,
            enable_categorical=True,
            tree_method="hist"
        )
        model.fit(X_train, y_train)
        return model

    def predict_proba(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict_proba(X)[:, 1]

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)

    def get_feature_importance(self, model: Any) -> np.ndarray:
        return model.feature_importances_


class RandomForestWrapper(BaseModelWrapper):
    """Wrapper for Random Forest models"""
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, params: Dict[str, Any], class_weight: Dict = None) -> Any:
        
        # Clean parameters for RF (remove unknown params that might be passed from a generic config)
        valid_params = RandomForestClassifier().get_params().keys()
        rf_params = {k: v for k, v in params.items() if k in valid_params}
        
        # Handle class_weight precedence: Tuned parameter > Config parameter
        final_class_weight = rf_params.pop('class_weight', class_weight)
        
        # Handle "None" string from YAML/JSON
        if isinstance(final_class_weight, str) and final_class_weight.lower() == "none":
            final_class_weight = None

        # Handle "None" for max_features
        if 'max_features' in rf_params:
            if isinstance(rf_params['max_features'], str) and rf_params['max_features'].lower() == "none":
                rf_params['max_features'] = None

        # RandomForest requires numerical input. We need to encode categorical columns.
        # Check for categorical columns
        cat_cols = X_train.select_dtypes(include=['category', 'object']).columns
        if len(cat_cols) > 0:
            # We must encode. Ideally this should be a persisted encoder, but for this wrapper scope
            # we will do a simple OrdinalEncoding.
            # NOTE: Sklearn trees can handle ordinal encoded categoricals reasonably well.
            X_train = X_train.copy()
            for col in cat_cols:
                X_train[col] = X_train[col].astype('category').cat.codes

        model = RandomForestClassifier(
            **rf_params,
            class_weight=final_class_weight,
            n_jobs=1 
        )
        model.fit(X_train, y_train)
        return model

    def _encode_for_rf(self, X: pd.DataFrame) -> pd.DataFrame:
        """Helper to encode categorical data for RF"""
        X_encoded = X.copy()
        cat_cols = X_encoded.select_dtypes(include=['category', 'object']).columns
        for col in cat_cols:
             # This assumes consistent category codes between train/test which is risky
             # but standard simple approach. Ideally we'd use a fitted OrdinalEncoder.
             if X_encoded[col].dtype.name == 'category':
                  X_encoded[col] = X_encoded[col].cat.codes
             else:
                  X_encoded[col] = X_encoded[col].astype('category').cat.codes
        return X_encoded

    def predict_proba(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        X_encoded = self._encode_for_rf(X)
        return model.predict_proba(X_encoded)[:, 1]

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        X_encoded = self._encode_for_rf(X)
        return model.predict(X_encoded)

    def get_feature_importance(self, model: Any) -> np.ndarray:
        return model.feature_importances_


class ModelFactory:
    """Factory to create model wrappers"""
    
    @staticmethod
    def get_model_wrapper(model_type: str) -> BaseModelWrapper:
        model_type = model_type.lower()
        if model_type == "lightgbm":
            return LightGBMWrapper()
        elif model_type == "xgboost":
            return XGBoostWrapper()
        elif model_type in ["random_forest", "rf"]:
            return RandomForestWrapper()
        else:
            raise ValueError(f"Unknown model type: {model_type}")


class EnsembleModel:
    """Ensemble model trainer and predictor"""
    
    def __init__(self, config: AEConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.models: List[Any] = []
        self.output_wrapper = ModelFactory.get_model_wrapper(self.config.MODEL_TYPE)
    
    def create_balanced_sample(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series, 
        minority_label: int = 1, 
        majority_label: int = 0
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Create balanced sample using undersampling"""
        try:
            # Combine features and target
            df = pd.concat([X_train, y_train], axis=1)
            
            minority_samples = df[df[self.config.LABEL_COLUMN] == minority_label]
            majority_samples = df[df[self.config.LABEL_COLUMN] == majority_label]
            
            # Calculate desired sample size
            desired_sample_size = int(len(minority_samples) * self.config.UNDER_SAMPLE_MAJORITY_RATIO)
            
            # Sample majority class
            if len(majority_samples) < desired_sample_size:
                self.logger.warning(
                    f"Requested {desired_sample_size} majority samples but only "
                    f"{len(majority_samples)} available. Using replacement."
                )
                sampled_majority = majority_samples.sample(
                    n=desired_sample_size, 
                    replace=True, 
                    random_state=self.config.RANDOM_SEED
                )
            else:
                sampled_majority = majority_samples.sample(
                    n=desired_sample_size, 
                    random_state=self.config.RANDOM_SEED
                )
            
            # Combine samples
            balanced_df = pd.concat([minority_samples, sampled_majority])
            
            # Split back into features and target
            X_balanced = balanced_df.drop(self.config.LABEL_COLUMN, axis=1)
            y_balanced = balanced_df[self.config.LABEL_COLUMN]
            
            # Calculate before/after statistics
            original_label_1 = len(minority_samples)
            original_label_0 = len(majority_samples)
            balanced_label_1 = len(minority_samples)
            balanced_label_0 = len(sampled_majority)
            
            reduction_ratio = original_label_0 / balanced_label_0 if balanced_label_0 > 0 else 1
            
            self.logger.info(f"📊 BALANCED SAMPLING APPLIED:")
            self.logger.info(f"   • Original training data: {len(X_train):,} rows")
            self.logger.info(f"     - Label=1: {original_label_1:,}, Label=0: {original_label_0:,}")
            self.logger.info(f"   • Balanced sample: {len(balanced_df):,} rows")
            self.logger.info(f"     - Label=1: {balanced_label_1:,}, Label=0: {balanced_label_0:,}")
            self.logger.info(f"   • Undersampling ratio: {reduction_ratio:.1f}:1 (majority class reduced)")
            self.logger.info(f"   • Final class balance: 1:1 (perfect balance achieved)")
            
            return X_balanced, y_balanced
            
        except Exception as e:
            self.logger.error(f"Error creating balanced sample: {e}")
            return X_train, y_train
    
    def _train_single_model(
        self, 
        model_index: int, 
        X_balanced: pd.DataFrame, 
        y_balanced: pd.Series, 
        parameters: Dict[str, Any]
    ) -> Optional[Any]:
        """Train a single model (generic)"""
        try:
            # Inject random_state into parameters if not present, to ensure diversity in ensemble
            trial_params = parameters.copy()
            if 'random_state' not in trial_params:
                trial_params['random_state'] = self.config.RANDOM_SEED + model_index
            
            model = self.output_wrapper.train(
                X_balanced, 
                y_balanced, 
                trial_params, 
                class_weight=self.config.CLASS_WEIGHT
            )
            return model
            
        except Exception as e:
            self.logger.warning(f"Failed to train model {model_index+1}: {e}")
            return None
    
    def _train_ensemble_parallel(
        self, 
        X_balanced: pd.DataFrame, 
        y_balanced: pd.Series, 
        parameters: Dict[str, Any]
    ) -> List[Any]:
        """Train ensemble models in parallel using joblib"""
        if not JOBLIB_AVAILABLE:
            self.logger.warning("joblib not available, falling back to sequential training")
            return self._train_ensemble_sequential(X_balanced, y_balanced, parameters)
        
        try:
            self.logger.info(f"Training ensemble of {self.config.N_ENSEMBLE_GROUP_NUMBER} models ({self.config.MODEL_TYPE}) in parallel (n_jobs={self.config.N_JOBS})")
            
            # Train models in parallel
            trained_models = Parallel(n_jobs=self.config.N_JOBS)(
                delayed(self._train_single_model)(i, X_balanced, y_balanced, parameters)
                for i in range(self.config.N_ENSEMBLE_GROUP_NUMBER)
            )
            
            # Filter out None results (failed models)
            models = [model for model in trained_models if model is not None]
            
            self.logger.info(f"Successfully trained {len(models)}/{self.config.N_ENSEMBLE_GROUP_NUMBER} models in parallel")
            return models
            
        except Exception as e:
            self.logger.error(f"Error in parallel training: {e}")
            self.logger.info("Falling back to sequential training")
            return self._train_ensemble_sequential(X_balanced, y_balanced, parameters)
    
    def _train_ensemble_sequential(
        self, 
        X_balanced: pd.DataFrame, 
        y_balanced: pd.Series, 
        parameters: Dict[str, Any]
    ) -> List[Any]:
        """Train ensemble models sequentially"""
        models = []
        successful_models = 0
        
        self.logger.info(f"Training ensemble of {self.config.N_ENSEMBLE_GROUP_NUMBER} models ({self.config.MODEL_TYPE}) sequentially")
        
        for i in range(self.config.N_ENSEMBLE_GROUP_NUMBER):
            model = self._train_single_model(i, X_balanced, y_balanced, parameters)
            if model is not None:
                models.append(model)
                successful_models += 1
        
        self.logger.info(f"Successfully trained {successful_models}/{self.config.N_ENSEMBLE_GROUP_NUMBER} models sequentially")
        return models
    
    def train_ensemble(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series, 
        parameters: Dict[str, Any]
    ) -> List[Any]:
        """Train ensemble of models (parallel or sequential based on config)"""
        # Create balanced sample
        X_balanced, y_balanced = self.create_balanced_sample(X_train, y_train)
        
        # Choose training mode based on configuration
        if self.config.PARALLEL_TRAINING:
            models = self._train_ensemble_parallel(X_balanced, y_balanced, parameters)
        else:
            models = self._train_ensemble_sequential(X_balanced, y_balanced, parameters)
        
        self.models = models
        return models
    
    def predict_soft_voting(self, models: List[Any], X: pd.DataFrame) -> np.ndarray:
        """Make predictions using soft voting (probability averaging)"""
        if not models:
            self.logger.warning("No models available for prediction")
            return np.zeros(len(X))
        
        try:
            probas = np.array([self.output_wrapper.predict_proba(model, X) for model in models])
            return np.mean(probas, axis=0)
        except Exception as e:
            self.logger.error(f"Error in soft voting prediction: {e}")
            return np.zeros(len(X))
    
    def predict_hard_voting(self, models: List[Any], X: pd.DataFrame) -> np.ndarray:
        """Make predictions using hard voting (prediction averaging)"""
        if not models:
            self.logger.warning("No models available for prediction")
            return np.zeros(len(X))
        
        try:
            preds = np.array([self.output_wrapper.predict(model, X) for model in models])
            return np.mean(preds, axis=0)
        except Exception as e:
            self.logger.error(f"Error in hard voting prediction: {e}")
            return np.zeros(len(X))
    
    def calculate_feature_importance(
        self, 
        models: List[Any], 
        X_test: pd.DataFrame, 
        y_test: pd.Series,
        feature_names: List[str],
        n_repeats: int = 10
    ) -> Dict[str, Any]:
        """
        Calculate feature importance using both built-in and permutation importance
        
        Args:
            models: List of trained models
            X_test: Test features
            y_test: Test targets  
            feature_names: List of feature names
            n_repeats: Number of permutation repeats for stability
            
        Returns:
            Dictionary containing both importance types and analysis
        """
        try:
            if not models:
                self.logger.warning("No models available for feature importance calculation")
                return {}
            
            # 1. Built-in Feature Importance (averaged across ensemble)
            model_importances = []
            for model in models:
                # Get feature importance from Model strategy
                importance = self.output_wrapper.get_feature_importance(model)
                model_importances.append(importance)
            
            # Average importance across all models in ensemble
            avg_importance = np.mean(model_importances, axis=0)
            
            # 2. Permutation Importance (model-agnostic)
            # Create a wrapper class for permutation importance
            class EnsembleWrapper(ClassifierMixin, BaseEstimator):
                def __init__(self, ensemble_model, models, feature_names, config, dtypes):
                    self.ensemble_model = ensemble_model
                    self.models = models
                    self.feature_names = feature_names
                    self.config = config
                    self.dtypes = dtypes
                    self.classes_ = np.array([0, 1])  # Required by ClassifierMixin/check_is_fitted
                
                def fit(self, X, y):
                    return self
                
                def predict(self, X):
                    # Convert to DataFrame if needed
                    if isinstance(X, np.ndarray):
                        X = pd.DataFrame(X, columns=self.feature_names)
                        
                        # Restore original dtypes (crucial for LightGBM categorical features)
                        for col, dtype in self.dtypes.items():
                            if col in X.columns:
                                try:
                                    X[col] = X[col].astype(dtype)
                                except Exception:
                                    pass

                    # Get soft voting predictions and convert to binary
                    soft_predictions = self.ensemble_model.predict_soft_voting(self.models, X)
                    return (soft_predictions > self.config.SOFT_PREDICTION_THRESHOLD).astype(int)
            
            # Create wrapper and calculate permutation importance
            ensemble_wrapper = EnsembleWrapper(self, models, feature_names, self.config, X_test.dtypes)
            perm_importance = permutation_importance(
                estimator=ensemble_wrapper,
                X=X_test.values,
                y=y_test.values,
                scoring='f1',  # Use F1 score as it's one of our optimization targets
                n_repeats=n_repeats,
                random_state=42,
                n_jobs=1  # Use single job to avoid pickling issues
            )
            
            # 3. Create comprehensive results
            feature_importance_results = {
                'feature_names': feature_names,
                'lgb_importance': avg_importance,  # Kept key as 'lgb_importance' for compatibility with existing outputs
                'model_importance': avg_importance, # New generic key
                'lgb_importance_std': np.std(model_importances, axis=0),
                'permutation_importance': perm_importance.importances_mean,
                'permutation_importance_std': perm_importance.importances_std,
                'n_models': len(models),
                'n_repeats': n_repeats
            }
            
            # 4. Create sorted importance rankings
            model_ranking = sorted(
                zip(feature_names, avg_importance), 
                key=lambda x: x[1], reverse=True
            )
            perm_ranking = sorted(
                zip(feature_names, perm_importance.importances_mean), 
                key=lambda x: x[1], reverse=True
            )
            
            feature_importance_results['lgb_ranking'] = model_ranking
            feature_importance_results['perm_ranking'] = perm_ranking
            
            # 5. Identify top features from both methods
            top_model_features = [name for name, _ in model_ranking[:5]]
            top_perm_features = [name for name, _ in perm_ranking[:5]]
            consensus_features = list(set(top_model_features) & set(top_perm_features))
            
            feature_importance_results['top_lgb_features'] = top_model_features
            feature_importance_results['top_perm_features'] = top_perm_features
            feature_importance_results['consensus_features'] = consensus_features
            
            self.logger.info(f"Feature importance calculated successfully")
            self.logger.info(f"Top Model features: {top_model_features}")
            self.logger.info(f"Top Permutation features: {top_perm_features}")
            self.logger.info(f"Consensus features: {consensus_features}")
            
            return feature_importance_results
            
        except Exception as e:
            self.logger.error(f"Error calculating feature importance: {e}")
            return {}


class ModelEvaluator:
    """Handles model evaluation and metrics calculation"""
    
    def __init__(self, config: AEConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def evaluate_model(
        self, 
        models: List[Any], 
        X_test: pd.DataFrame, 
        y_test: pd.Series,
        ensemble_model: EnsembleModel
    ) -> Dict[str, float]:
        """Evaluate ensemble model performance"""
        try:
            from sklearn.metrics import confusion_matrix, accuracy_score, roc_auc_score, log_loss
            
            # Soft voting predictions
            soft_predictions = ensemble_model.predict_soft_voting(models, X_test)
            soft_binary_predictions = (soft_predictions > self.config.SOFT_PREDICTION_THRESHOLD).astype(int)
            
            # Hard voting predictions  
            hard_predictions = ensemble_model.predict_hard_voting(models, X_test)
            hard_binary_predictions = (hard_predictions > self.config.SOFT_PREDICTION_THRESHOLD).astype(int)
            
            # Calculate metrics
            soft_recall = recall_score(y_test, soft_binary_predictions, zero_division=0.0)
            hard_recall = recall_score(y_test, hard_binary_predictions, zero_division=0.0)
            
            soft_f1 = f1_score(y_test, soft_binary_predictions, zero_division=0.0)
            hard_f1 = f1_score(y_test, hard_binary_predictions, zero_division=0.0)
            
            soft_precision = precision_score(y_test, soft_binary_predictions, zero_division=0.0)
            hard_precision = precision_score(y_test, hard_binary_predictions, zero_division=0.0)
            
            # Additional Context (Confusion Matrix, Accuracy, AUC)
            tn, fp, fn, tp = confusion_matrix(y_test, soft_binary_predictions).ravel()
            soft_accuracy = accuracy_score(y_test, soft_binary_predictions)
            hard_accuracy = accuracy_score(y_test, hard_binary_predictions)
            
            # AUC calculation (requires at least 2 classes in y_test)
            try:
                soft_roc_auc = roc_auc_score(y_test, soft_predictions)
            except ValueError:
                # Handle edge case where y_test has only one class
                soft_roc_auc = 0.5

            # Cross Entropy / Log Loss (Negative for maximization)
            try:
                # Add small epsilon to avoid log(0) if not handled by sklearn
                # We use negative log loss because the optimizer maximizes the metric
                cross_entropy = -log_loss(y_test, soft_predictions, labels=[0, 1])
            except Exception:
                cross_entropy = -100.0 # Heavy penalty if calculation fails

            results = {
                "soft_recall": soft_recall,
                "hard_recall": hard_recall,
                "soft_f1_score": soft_f1,
                "hard_f1_score": hard_f1,
                "soft_precision": soft_precision,
                "hard_precision": hard_precision,
                "soft_accuracy": soft_accuracy,
                "hard_accuracy": hard_accuracy,
                "soft_roc_auc": soft_roc_auc,
                "neg_log_loss": cross_entropy,
                "cross_entropy": cross_entropy,
                "confusion_matrix_tp": int(tp),
                "confusion_matrix_fp": int(fp),
                "confusion_matrix_tn": int(tn),
                "confusion_matrix_fn": int(fn)
            }
            
            self.logger.info(
                f"Evaluation: Recall={soft_recall:.4f}, F1={soft_f1:.4f}, AUC={soft_roc_auc:.4f}, NegLogLoss={cross_entropy:.4f} | "
                f"TP={tp}, FP={fp} (Precision={soft_precision:.4f})"
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {e}")
            return {
                "soft_recall": 0.0,
                "hard_recall": 0.0,
                "soft_f1_score": 0.0,
                "hard_f1_score": 0.0,
                "soft_precision": 0.0,
                "hard_precision": 0.0,
                "soft_accuracy": 0.0,
                "hard_accuracy": 0.0,
                "soft_roc_auc": 0.5,
                "neg_log_loss": -100.0,
                "cross_entropy": -100.0,
                "confusion_matrix_tp": 0,
                "confusion_matrix_fp": 0,
                "confusion_matrix_tn": 0,
                "confusion_matrix_fn": 0
            }