"""
Trainer module for TransJect.

Wraps PyTorch Lightning trainer with simplified interface.
"""
import torch
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
from pytorch_lightning.loggers import WandbLogger, TensorBoardLogger
from typing import Optional, Dict, Any
import logging
import os

from .config import TrainingConfig, TaskConfig
from .callbacks import MetricCallback

logger = logging.getLogger(__name__)


class TransJectTrainer:
    """
    Trainer class for TransJect models.
    
    Wraps PyTorch Lightning Trainer with simplified interface
    matching MPDistil API.
    """
    
    def __init__(
        self,
        model: pl.LightningModule,
        config: TrainingConfig,
        task_config: TaskConfig
    ):
        """
        Initialize trainer.
        
        Args:
            model: PyTorch Lightning model
            config: Training configuration
            task_config: Task configuration
        """
        self.model = model
        self.config = config
        self.task_config = task_config
        self.trainer = None
        
    def train(
        self,
        train_loader,
        val_loader,
        test_loader: Optional[Any] = None,
        report_to: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Train the model.
        
        Args:
            train_loader: Training DataLoader
            val_loader: Validation DataLoader
            test_loader: Test DataLoader (optional)
            report_to: Logging backend ('wandb', 'tensorboard', None)
            **kwargs: Additional config overrides
        
        Returns:
            Training history dictionary
        """
        
        # Update config with kwargs
        if kwargs:
            self.config.update(**kwargs)
        
        # Override report_to if provided
        if report_to is not None:
            self.config.report_to = report_to
        
        # Setup callbacks
        callbacks = self._setup_callbacks()
        
        # Setup logger
        pl_logger = self._setup_logger()
        
        # Create PyTorch Lightning trainer
        self.trainer = pl.Trainer(
            max_epochs=self.config.epochs,
            accelerator=self.config.accelerator,
            devices=self.config.devices,
            precision=self.config.precision,
            callbacks=callbacks,
            logger=pl_logger,
            log_every_n_steps=self.config.log_every_n_steps,
            enable_progress_bar=self.config.verbose,
            enable_model_summary=self.config.verbose,
            deterministic=True,
            default_root_dir=self.config.output_dir,
        )
        
        # Train
        logger.info(f"Starting training for {self.config.epochs} epochs")
        
        self.trainer.fit(
            self.model,
            train_dataloaders=train_loader,
            val_dataloaders=val_loader
        )
        history = self._collect_history()
        
        # Test if test_loader provided
        if test_loader:
            logger.info("Running test evaluation")
            test_results = self.trainer.test(self.model, dataloaders=test_loader)
            history['test'] = test_results
        
        return history
    
    def _setup_callbacks(self):
        """Setup training callbacks."""
        callbacks = []
        
        # Add metric callback for classification tasks (only if task_config exists)
        if self.task_config is not None and self.task_config.task_type == 'classification':
            metric_callback = MetricCallback(
                metric_name=self.task_config.metric,
                task_type=self.task_config.task_type
            )
            callbacks.append(metric_callback)
            logger.info(f"Added metric callback for {self.task_config.metric}")
        
        # Checkpoint callback
        if self.config.save_checkpoints:
            checkpoint_callback = ModelCheckpoint(
                dirpath=os.path.join(self.config.output_dir, 'checkpoints'),
                filename='{epoch}-{val_loss:.4f}',
                monitor=self.config.monitor,
                mode=self.config.mode,
                save_top_k=3,
                verbose=self.config.verbose
            )
            callbacks.append(checkpoint_callback)
        
        # Early stopping
        if self.config.early_stopping:
            early_stop_callback = EarlyStopping(
                monitor=self.config.monitor,
                patience=self.config.patience,
                mode=self.config.mode,
                verbose=self.config.verbose
            )
            callbacks.append(early_stop_callback)
        
        return callbacks
    
    def _setup_logger(self):
        """Setup experiment logger."""
        if self.config.report_to == 'wandb':
            # Use task_name from task_config if available, otherwise use generic name
            task_name = self.task_config.task_name if self.task_config is not None else 'transject_experiment'
            return WandbLogger(
                project='transject',
                name=f"{task_name}_{self.config.epochs}ep",
                save_dir=self.config.output_dir
            )
        elif self.config.report_to == 'tensorboard':
            return TensorBoardLogger(
                save_dir=self.config.output_dir,
                name='tensorboard_logs'
            )
        else:
            return None
    
    def _collect_history(self) -> Dict[str, Any]:
        """Collect training history from trainer."""
        history = {
            'train': [],
            'val': []
        }
        
        # Extract metrics from trainer
        if self.trainer and self.trainer.logged_metrics:
            history['final_metrics'] = dict(self.trainer.logged_metrics)
        
        # Add callback metrics if available
        if self.trainer and self.trainer.callback_metrics:
            history['callback_metrics'] = dict(self.trainer.callback_metrics)
        
        return history
    
    def evaluate(self, data_loader) -> Dict[str, Any]:
        """
        Evaluate model on a dataset.
        
        Args:
            data_loader: DataLoader for evaluation
        
        Returns:
            Evaluation metrics
        """
        if self.trainer is None:
            raise ValueError("Trainer not initialized. Call train() first.")
        
        results = self.trainer.test(self.model, dataloaders=data_loader)
        return results[0] if results else {}
