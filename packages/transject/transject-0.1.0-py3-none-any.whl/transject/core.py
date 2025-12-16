"""
Core TransJect class - Main API for transformer training.
"""
import torch
import sys
import os
from typing import Optional, Dict, Any
import logging

from .models import IsoFormerForClassificationPL, IsoFormerForLanguageModelingPL
from .config import TrainingConfig, TaskConfig
from .trainer import TransJectTrainer
from .metrics import get_metric
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)


class TransJect:
    """
    Main TransJect class for training manifold-preserving transformers.
    
    Provides a unified API for training transformer models with orthogonal
    and manifold-preserving properties.
    
    Supports:
    - Classification tasks (SuperGLUE, GLUE, custom)
    - Language modeling tasks (Alpaca, custom)
    - Multiple architectures (BERT-like encoders, GPT-2, Llama-3)
    - User-controlled evaluation metrics
    
    Args:
        task_name: Name of the task (e.g., 'COPA', 'RTE', 'alpaca')
        task_type: Type of task ('classification', 'language_modeling', 'regression')
        num_labels: Number of output labels (for classification/regression)
        num_layers: Number of transformer layers (-1 = use default of 6)
        device: Device to use ('auto', 'cuda', 'cpu')
        metric: Evaluation metric name ('accuracy', 'f1', 'mcc', 'auto')
        tokenizer_name: Tokenizer name (default: 'bert-base-uncased')
        vocab_size: Vocabulary size (auto-detected from tokenizer if not provided)
        max_length: Maximum sequence length
        output_dir: Output directory for checkpoints and logs
    """
    
    def __init__(
        self,
        task_name: str,
        task_type: str = 'classification',
        num_labels: Optional[int] = None,
        num_layers: int = -1,
        device: str = "auto",
        metric: str = "accuracy",
        tokenizer_name: str = "bert-base-uncased",
        vocab_size: Optional[int] = None,
        max_length: int = 128,
        output_dir: str = './transject_outputs'
    ):
        self.task_name = task_name
        self.task_type = task_type
        self.num_labels = num_labels
        self.num_layers = num_layers
        self.tokenizer_name = tokenizer_name
        self.max_length = max_length
        self.output_dir = output_dir
        
        # Set device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        logger.info(f"Initializing TransJect for {task_type} task: {task_name}")
        logger.info(f"Using device: {self.device}")
        
        # Load tokenizer to get vocab size
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        if vocab_size is None:
            vocab_size = self.tokenizer.vocab_size
        
        # Create task config
        self.task_config = TaskConfig(
            task_name=task_name,
            task_type=task_type,
            num_labels=num_labels,
            vocab_size=vocab_size,
            metric=metric,
            max_length=max_length
        )
        
        # Initialize model (will be created in train() with config)
        self.model = None
        self.trainer_instance = None
        
        logger.info(f"TransJect initialized successfully")
        logger.info(f"  Task: {task_name} ({task_type})")
        logger.info(f"  Vocabulary size: {vocab_size}")
        if num_labels:
            logger.info(f"  Number of labels: {num_labels}")
    
    def _create_model(self, config: TrainingConfig):
        """
        Create TransJect model based on task type.
        
        Args:
            config: Training configuration
        
        Returns:
            PyTorch Lightning model
        """
        
        if self.task_type == 'classification':
            return self._create_classification_model(config)
        elif self.task_type == 'language_modeling':
            return self._create_language_modeling_model(config)
        elif self.task_type == 'regression':
            return self._create_regression_model(config)
        else:
            raise ValueError(f"Unsupported task type: {self.task_type}")
    
    def _create_classification_model(self, config: TrainingConfig):
        """Create model for classification tasks."""
        
        # Determine number of layers
        if self.num_layers == -1:
            # Use default: 6 layers
            N = 6
            logger.info(f"Using default architecture: {N} layers")
        else:
            N = self.num_layers
            logger.info(f"Using {N} layers")
        
        # Determine classification type
        if self.num_labels == 2:
            classification_type = 'binary'
            n_out = 1
        else:
            classification_type = 'multiclass'
            n_out = self.num_labels
        
        # Create args namespace for compatibility with existing model
        class Args:
            def __init__(self, config, task_config):
                self.lambda_ = config.lambda_
                self.use_ortho = config.use_ortho
                self.use_rezero = config.use_rezero
                self.use_eigen = config.use_eigen
                self.classification_type = classification_type
                self.lr = config.learning_rate  # Model expects 'lr' not 'learning_rate'
                self.weight_decay = config.weight_decay
                self.warmup_steps = config.warmup_steps
                self.epochs = config.epochs
                self.metric = task_config.metric
        
        args = Args(config, self.task_config)
        
        model = IsoFormerForClassificationPL(
            args=args,
            src_vocab=self.task_config.vocab_size,
            d_model=config.d_model,
            MAX_LEN=self.max_length,
            N=N,
            n_experts=config.n_experts,
            n_out=n_out,
            use_eigen=config.use_eigen,
            pooling=config.pooling,
            classification_type=classification_type,
            random_features=config.random_features
        )
        
        logger.info(f"Created IsoFormer classification model")
        logger.info(f"  Architecture: {N} layers, {config.d_model} hidden size")
        logger.info(f"  Classification type: {classification_type}")
        logger.info(f"  Output labels: {n_out}")
        
        return model
    
    def _create_language_modeling_model(self, config: TrainingConfig):
        """Create model for language modeling tasks."""
        
        # Determine number of layers
        if self.num_layers == -1:
            N = 6
            logger.info(f"Using default architecture: {N} layers")
        else:
            N = self.num_layers
            logger.info(f"Using {N} layers")
        
        # Create args namespace for compatibility with existing model
        class Args:
            def __init__(self, config, task_config):
                self.lambda_ = config.lambda_
                self.use_ortho = config.use_ortho
                self.use_rezero = config.use_rezero
                self.use_eigen = config.use_eigen
                self.lr = config.learning_rate
                self.weight_decay = config.weight_decay
                self.warmup_steps = config.warmup_steps
                self.epochs = config.epochs
                self.metric = task_config.metric
        
        args = Args(config, self.task_config)
        
        model = IsoFormerForLanguageModelingPL(
            args=args,
            src_vocab=self.task_config.vocab_size,
            d_model=config.d_model,
            MAX_LEN=self.max_length,
            N=N,
            n_experts=config.n_experts,
            use_eigen=config.use_eigen,
            random_features=config.random_features
        )
        
        logger.info(f"Created IsoFormer language modeling model")
        logger.info(f"  Architecture: {N} layers, {config.d_model} hidden size")
        logger.info(f"  Vocabulary size: {self.task_config.vocab_size}")
        
        return model
    
    def _create_regression_model(self, config: TrainingConfig):
        """Create model for regression tasks."""
        
        # Similar to classification but with regression output
        if self.num_layers == -1:
            N = 6
        else:
            N = self.num_layers
        
        class Args:
            def __init__(self, config, task_config):
                self.lambda_ = config.lambda_
                self.use_ortho = config.use_ortho
                self.use_rezero = config.use_rezero
                self.use_eigen = config.use_eigen
                self.classification_type = 'regression'
                self.lr = config.learning_rate  # Model expects 'lr' not 'learning_rate'
                self.weight_decay = config.weight_decay
                self.warmup_steps = config.warmup_steps
                self.epochs = config.epochs
                self.metric = task_config.metric
        
        args = Args(config, self.task_config)
        
        model = IsoFormerForClassificationPL(
            args=args,
            src_vocab=self.task_config.vocab_size,
            d_model=config.d_model,
            MAX_LEN=self.max_length,
            N=N,
            n_experts=config.n_experts,
            n_out=1,
            use_eigen=config.use_eigen,
            pooling=config.pooling,
            classification_type='regression',
            random_features=config.random_features
        )
        
        return model
    
    def train(
        self,
        train_loader,
        val_loader,
        test_loader: Optional[Any] = None,
        meta_loaders: Optional[Dict[str, Any]] = None,
        config: Optional[TrainingConfig] = None,
        report_to: Optional[str] = None,
        **config_kwargs
    ) -> Dict[str, Any]:
        """
        Train the TransJect model.
        
        Args:
            train_loader: Training DataLoader
            val_loader: Validation DataLoader
            test_loader: Test DataLoader (optional)
            meta_loaders: Dict of auxiliary task loaders (optional)
                Format: {'task_name': val_loader}
            config: TrainingConfig object (creates default if None)
            report_to: Logging backend ('wandb', 'tensorboard', None)
            **config_kwargs: Override specific config parameters
                Examples: epochs=10, learning_rate=2e-5, lambda_=0.1
        
        Returns:
            Dictionary containing training history
        """
        
        # Create or update config
        if config is None:
            config = TrainingConfig(output_dir=self.output_dir)
        
        # Update config with kwargs
        if config_kwargs:
            config.update(**config_kwargs)
        
        # Create model
        self.model = self._create_model(config)
        
        # Create trainer
        self.trainer_instance = TransJectTrainer(
            model=self.model,
            config=config,
            task_config=self.task_config
        )
        
        # Train
        history = self.trainer_instance.train(
            train_loader=train_loader,
            val_loader=val_loader,
            test_loader=test_loader,
            meta_loaders=meta_loaders,
            report_to=report_to
        )
        
        return history
    
    def evaluate(self, data_loader):
        """
        Evaluate the model on a dataset.
        
        Args:
            data_loader: DataLoader for evaluation
        
        Returns:
            Evaluation metrics
        """
        if self.trainer_instance is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        return self.trainer_instance.evaluate(data_loader)
    
    def predict(self, data_loader):
        """
        Generate predictions on a dataset.
        
        Args:
            data_loader: DataLoader for prediction
        
        Returns:
            Predictions
        """
        if self.model is None:
            raise ValueError("Model not initialized. Call train() first.")
        
        self.model.eval()
        predictions = []
        
        with torch.no_grad():
            for batch in data_loader:
                inputs = batch['input_ids'].to(self.device)
                outputs, _ = self.model(inputs)
                
                if self.task_type == 'classification':
                    if self.num_labels == 2:
                        preds = (outputs > 0.5).int()
                    else:
                        preds = torch.argmax(outputs, dim=-1)
                else:
                    preds = outputs
                
                predictions.extend(preds.cpu().numpy())
        
        return predictions
    
    def save_model(self, path: str):
        """
        Save the trained model.
        
        Args:
            path: Path to save directory
        """
        if self.model is None:
            raise ValueError("Model not initialized. Call train() first.")
        
        os.makedirs(path, exist_ok=True)
        
        # Save model checkpoint
        checkpoint_path = os.path.join(path, 'model.ckpt')
        self.trainer_instance.trainer.save_checkpoint(checkpoint_path)
        
        # Save config
        config_path = os.path.join(path, 'task_config.json')
        with open(config_path, 'w') as f:
            import json
            json.dump(self.task_config.to_dict(), f, indent=2)
        
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """
        Load a trained model.
        
        Args:
            path: Path to saved model directory
        """
        # Load config
        config_path = os.path.join(path, 'task_config.json')
        import json
        with open(config_path, 'r') as f:
            task_dict = json.load(f)
        
        self.task_config = TaskConfig.from_dict(task_dict)
        
        # Load model checkpoint
        checkpoint_path = os.path.join(path, 'model.ckpt')
        
        # Create model with loaded config
        config = TrainingConfig()
        self.model = self._create_model(config)
        
        # Load weights
        checkpoint = torch.load(checkpoint_path)
        self.model.load_state_dict(checkpoint['state_dict'])
        
        logger.info(f"Model loaded from {path}")
    
    # Deprecated aliases for backward compatibility
    def save_student(self, path: str):
        """Deprecated: Use save_model() instead."""
        logger.warning("save_student() is deprecated, use save_model() instead")
        return self.save_model(path)
    
    def load_student(self, path: str):
        """Deprecated: Use load_model() instead."""
        logger.warning("load_student() is deprecated, use load_model() instead")
        return self.load_model(path)

