"""
Evaluation metrics using HuggingFace evaluate library.
"""
import evaluate
from typing import Union, Dict, Any, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)


def get_metric(metric_name: Union[str, list], task_name: Optional[str] = None):
    """
    Load evaluation metric from HuggingFace evaluate library.
    
    Args:
        metric_name: Name of metric or list of metrics or 'auto'
            Examples: 'accuracy', 'f1', 'bleu', 'rouge', ['accuracy', 'f1']
        task_name: Task name for auto-detection (optional)
    
    Returns:
        Metric object with add_batch() and compute() methods
    """
    
    # Auto-detect metric based on task
    if metric_name == 'auto' and task_name:
        metric_name = _auto_detect_metric(task_name)
        logger.info(f"Auto-detected metric for task '{task_name}': {metric_name}")
    
    if isinstance(metric_name, str):
        logger.info(f"Loading metric: {metric_name}")
        try:
            return evaluate.load(metric_name)
        except Exception as e:
            logger.warning(f"Failed to load metric '{metric_name}': {e}. Using accuracy as fallback.")
            return evaluate.load('accuracy')
    
    elif isinstance(metric_name, list):
        logger.info(f"Loading combined metrics: {metric_name}")
        return evaluate.combine(metric_name)
    
    else:
        raise ValueError(f"Invalid metric type: {type(metric_name)}")


def _auto_detect_metric(task_name: str) -> str:
    """
    Auto-detect appropriate metric based on task name.
    
    Args:
        task_name: Name of the task
    
    Returns:
        Metric name
    """
    task_lower = task_name.lower()
    
    # SuperGLUE tasks
    if task_lower in ['boolq', 'copa', 'rte', 'wic', 'wsc']:
        return 'accuracy'
    elif task_lower == 'cb':
        return 'f1'
    
    # GLUE tasks
    elif task_lower in ['sst2', 'mnli', 'qnli', 'wnli']:
        return 'accuracy'
    elif task_lower in ['mrpc', 'qqp']:
        return 'f1'
    elif task_lower == 'cola':
        return 'matthews_correlation'
    elif task_lower in ['sts-b', 'stsb']:
        return 'pearsonr'
    
    # Default
    else:
        logger.warning(f"Unknown task '{task_name}', using accuracy as default metric")
        return 'accuracy'


class MetricWrapper:
    """
    Wrapper for multiple metrics with simplified interface.
    """
    
    def __init__(self, metrics: Union[str, list], task_name: Optional[str] = None):
        """
        Initialize metric wrapper.
        
        Args:
            metrics: Single metric name or list of metric names
            task_name: Task name for auto-detection
        """
        if isinstance(metrics, str):
            self.metric = get_metric(metrics, task_name)
            self.is_combined = False
        else:
            self.metric = get_metric(metrics, task_name)
            self.is_combined = True
    
    def add_batch(self, predictions, references):
        """Add batch of predictions and references."""
        self.metric.add_batch(predictions=predictions, references=references)
    
    def compute(self) -> Dict[str, Any]:
        """Compute final metric values."""
        return self.metric.compute()
    
    def reset(self):
        """Reset metric state."""
        if hasattr(self.metric, 'reset'):
            self.metric.reset()
        else:
            # For metrics without reset, recreate
            pass


class SKLearnMetricWrapper:
    """
    Wrapper for sklearn metrics to match HuggingFace evaluate interface.
    Useful for custom metrics or when evaluate library is not available.
    """
    
    def __init__(self, metric_fn, metric_name: str = 'custom'):
        """
        Initialize sklearn metric wrapper.
        
        Args:
            metric_fn: Sklearn metric function (e.g., accuracy_score, f1_score)
            metric_name: Name of the metric
        """
        self.metric_fn = metric_fn
        self.metric_name = metric_name
        self.predictions = []
        self.references = []
    
    def add_batch(self, predictions, references):
        """Add batch of predictions and references."""
        if hasattr(predictions, 'cpu'):
            predictions = predictions.cpu().numpy()
        if hasattr(references, 'cpu'):
            references = references.cpu().numpy()
        
        self.predictions.extend(predictions)
        self.references.extend(references)
    
    def compute(self) -> Dict[str, float]:
        """Compute final metric value."""
        try:
            value = self.metric_fn(self.references, self.predictions)
            return {self.metric_name: value}
        except Exception as e:
            logger.error(f"Error computing metric: {e}")
            return {self.metric_name: 0.0}
    
    def reset(self):
        """Reset metric state."""
        self.predictions = []
        self.references = []
