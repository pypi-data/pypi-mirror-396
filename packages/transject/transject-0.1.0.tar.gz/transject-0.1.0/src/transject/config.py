"""
Configuration classes for TransJect training.
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, Literal
import json


@dataclass
class TrainingConfig:
    """
    Training configuration for TransJect model.
    
    Controls hyperparameters for training phases.
    """
    # Training epochs
    epochs: int = 10
    batch_size: int = 8
    
    # Learning rate
    learning_rate: float = 2e-5
    warmup_steps: int = 0
    weight_decay: float = 0.01
    max_grad_norm: float = 1.0
    
    # TransJect-specific parameters
    lambda_: float = 0.1  # Regularization weight for reconstruction loss
    use_ortho: bool = True  # Use orthogonal constraints
    use_rezero: bool = False  # Use ReZero initialization
    use_eigen: bool = False  # Use eigenvalue decomposition
    random_features: bool = True  # Use random feature mixing
    
    # Model architecture
    d_model: int = 512
    n_heads: int = 8
    n_experts: int = 1
    pooling: str = 'mean'  # 'mean', 'max', 'min', 'first'
    dropout: float = 0.1
    
    # System settings
    seed: int = 42
    num_workers: int = 0
    accelerator: str = 'auto'  # 'auto', 'gpu', 'cpu'
    devices: int = 1
    precision: str = '32'  # '16', '32', 'bf16'
    
    # Logging
    report_to: Optional[str] = None  # 'wandb', 'tensorboard', None
    output_dir: str = './transject_outputs'
    save_checkpoints: bool = True
    verbose: bool = True
    log_every_n_steps: int = 10
    
    # Early stopping
    early_stopping: bool = False
    patience: int = 3
    monitor: str = 'val_loss'
    mode: str = 'min'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'TrainingConfig':
        """Create config from dictionary."""
        return cls(**config_dict)
    
    def update(self, **kwargs) -> 'TrainingConfig':
        """Update config parameters."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self
    
    def save(self, path: str):
        """Save config to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'TrainingConfig':
        """Load config from JSON file."""
        with open(path, 'r') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)


@dataclass
class TaskConfig:
    """
    Task-specific configuration.
    
    Defines the task type, labels, and evaluation metrics.
    """
    task_name: str
    task_type: Literal['classification', 'language_modeling', 'regression'] = 'classification'
    num_labels: Optional[int] = None
    vocab_size: Optional[int] = None
    metric: str = 'accuracy'
    label_mapping: Optional[Dict[int, str]] = None
    max_length: int = 128
    
    @property
    def is_regression(self) -> bool:
        """Check if task is regression."""
        return self.task_type == 'regression'
    
    @property
    def is_language_modeling(self) -> bool:
        """Check if task is language modeling."""
        return self.task_type == 'language_modeling'
    
    @property
    def is_classification(self) -> bool:
        """Check if task is classification."""
        return self.task_type == 'classification'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'TaskConfig':
        """Create config from dictionary."""
        return cls(**config_dict)


@dataclass
class ClassificationConfig:
    """
    Configuration for classification tasks.
    
    Standard parameter names aligned with HuggingFace/PyTorch conventions.
    NO task_name or tokenizer_name - only model architecture parameters.
    """
    # Required parameters
    num_labels: int
    vocab_size: int
    
    # Model architecture
    num_layers: int = 6
    hidden_size: int = 512
    max_seq_length: int = 128
    n_experts: int = 1
    n_heads: int = 8
    
    # TransJect-specific
    use_eigen: bool = False
    random_features: bool = True
    use_ortho: bool = True
    pooling: str = 'mean'  # 'mean', 'max', 'min', 'first'
    dropout: float = 0.1
    
    # Training params
    lambda_: float = 0.1  # Regularization weight
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ClassificationConfig':
        """Create config from dictionary."""
        return cls(**config_dict)
    
    def save(self, path: str):
        """Save config to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'ClassificationConfig':
        """Load config from JSON file."""
        with open(path, 'r') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)


@dataclass
class LMConfig:
    """
    Configuration for language modeling tasks.
    
    Standard parameter names aligned with HuggingFace/PyTorch conventions.
    NO task_name or tokenizer_name - only model architecture parameters.
    """
    # Required parameters
    vocab_size: int
    
    # Model architecture
    num_layers: int = 6
    hidden_size: int = 512
    max_seq_length: int = 512
    n_experts: int = 1
    n_heads: int = 8
    
    # TransJect-specific
    use_eigen: bool = False
    random_features: bool = True
    use_ortho: bool = True
    dropout: float = 0.1
    
    # Training params
    lambda_: float = 0.1  # Regularization weight
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'LMConfig':
        """Create config from dictionary."""
        return cls(**config_dict)
    
    def save(self, path: str):
        """Save config to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'LMConfig':
        """Load config from JSON file."""
        with open(path, 'r') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)
