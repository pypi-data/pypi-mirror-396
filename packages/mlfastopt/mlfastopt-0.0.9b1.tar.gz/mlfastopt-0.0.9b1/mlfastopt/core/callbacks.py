
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

class OptimizationCallback(ABC):
    """Abstract base class for optimization callbacks"""
    
    @abstractmethod
    def on_optimization_start(self, config: Any) -> None:
        """Called when optimization starts"""
        pass
        
    @abstractmethod
    def on_trial_start(self, trial_index: int, parameters: Dict[str, Any]) -> None:
        """Called before a trial starts"""
        pass
        
    @abstractmethod
    def on_trial_complete(self, trial_index: int, result: Dict[str, float], duration: float) -> None:
        """Called after a trial completes successfully"""
        pass
        
    @abstractmethod
    def on_trial_error(self, trial_index: int, error: Exception) -> None:
        """Called when a trial fails"""
        pass
        
    @abstractmethod
    def on_optimization_end(self, best_params: Dict[str, Any], total_duration: float) -> None:
        """Called when optimization finishes"""
        pass

class LoggingCallback(OptimizationCallback):
    """Default callback for logging optimization progress"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def on_optimization_start(self, config: Any) -> None:
        self.logger.info(f"🚀 Starting optimization with {config.AE_NUM_TRIALS} trials")
        
    def on_trial_start(self, trial_index: int, parameters: Dict[str, Any]) -> None:
        self.logger.debug(f"Starting trial {trial_index+1}")
        
    def on_trial_complete(self, trial_index: int, result: Dict[str, float], duration: float) -> None:
        recall = result.get('soft_recall', 0.0)
        f1 = result.get('soft_f1_score', 0.0)
        
        # Handle tuple return types from Ax (mean, sem)
        if isinstance(recall, tuple):
            recall = recall[0]
        if isinstance(f1, tuple):
            f1 = f1[0]
            
        self.logger.info(
            f"Trial {trial_index+1} completed in {duration:.1f}s: "
            f"Recall={recall:.4f}, F1={f1:.4f}"
        )
        
    def on_trial_error(self, trial_index: int, error: Exception) -> None:
        self.logger.error(f"Trial {trial_index+1} failed: {error}")
        
    def on_optimization_end(self, best_params: Dict[str, Any], total_duration: float) -> None:
        self.logger.info(f"🎉 Optimization finished in {total_duration:.1f}s")
