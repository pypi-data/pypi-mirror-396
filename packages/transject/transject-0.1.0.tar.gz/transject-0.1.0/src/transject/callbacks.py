"""
Custom callbacks for TransJect training.
"""
import torch
import pytorch_lightning as pl
from pytorch_lightning.callbacks import Callback
import numpy as np
from .metrics import get_metric
import logging

logger = logging.getLogger(__name__)


class MetricCallback(Callback):
    """
    Callback to compute custom metrics during validation.
    
    Uses HuggingFace evaluate library for flexible metric computation.
    """
    
    def __init__(self, metric_name: str = 'accuracy', task_type: str = 'classification'):
        super().__init__()
        self.metric_name = metric_name
        self.task_type = task_type
        self.metric = get_metric(metric_name)
        self.predictions = []
        self.targets = []
    
    def on_validation_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        """Collect predictions and targets from each validation batch."""
        if 'pred' in outputs and 'target' in outputs:
            self.predictions.extend(outputs['pred'].detach().cpu().numpy())
            self.targets.extend(outputs['target'].detach().cpu().numpy())
    
    def on_validation_epoch_end(self, trainer, pl_module):
        """Compute metrics at the end of validation epoch."""
        if len(self.predictions) > 0 and len(self.targets) > 0:
            predictions = np.array(self.predictions)
            targets = np.array(self.targets)
            
            # Compute metric
            try:
                if self.metric_name == 'accuracy':
                    # Round for binary/multiclass classification
                    if self.task_type == 'classification':
                        score = self.metric.compute(
                            predictions=predictions.round().astype(int),
                            references=targets.round().astype(int)
                        )
                    else:
                        score = self.metric.compute(predictions=predictions, references=targets)
                elif self.metric_name == 'f1':
                    score = self.metric.compute(
                        predictions=predictions.round().astype(int),
                        references=targets.round().astype(int),
                        average='weighted'
                    )
                elif self.metric_name == 'matthews_correlation':
                    score = self.metric.compute(
                        predictions=predictions.round().astype(int),
                        references=targets.round().astype(int)
                    )
                else:
                    score = self.metric.compute(predictions=predictions, references=targets)
                
                # Log the metric
                metric_value = score.get(self.metric_name, score.get('score', 0))
                pl_module.log(f'val_{self.metric_name}', metric_value, prog_bar=True, logger=True)
                logger.info(f"Validation {self.metric_name}: {metric_value:.4f}")
                
            except Exception as e:
                logger.warning(f"Failed to compute metric {self.metric_name}: {e}")
            
            # Clear for next epoch
            self.predictions = []
            self.targets = []
