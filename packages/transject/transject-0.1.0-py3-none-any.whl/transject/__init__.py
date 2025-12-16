"""
TransJect: Manifold-Preserving Transformer Framework

A flexible transformer library supporting:
- Multiple architectures (BERT-like encoders, GPT-2, Llama-3, etc.)
- Multiple tasks (classification, language modeling, regression)
- Manifold-preserving orthogonal transformations
- Layer slicing and architecture flexibility
- Custom evaluation metrics from HuggingFace evaluate

NEW API (Recommended):
    ```python
    from transject import TransJectForClassification, ClassificationConfig
    from transject.utils import get_vocab_size
    from torch.utils.data import DataLoader
    
    # Get vocab size from tokenizer
    vocab_size = get_vocab_size('bert-base-uncased')
    
    # Create config
    config = ClassificationConfig(
        num_labels=2,
        vocab_size=vocab_size,
        num_layers=6,
        hidden_size=512,
        max_seq_length=128
    )
    
    # Initialize model
    model = TransJectForClassification(config)
    
    # Train with your own data loaders
    train_loader = DataLoader(your_train_dataset, batch_size=8)
    val_loader = DataLoader(your_val_dataset, batch_size=8)
    
    history = model.train(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=10,
        learning_rate=2e-5,
        metric='accuracy'
    )
    
    # Save
    model.save('./my_model.pth')
    ```

For dataset loading examples, see the examples/ directory.
"""

# New API (Recommended)
from .models import TransJectForClassification, TransJectDecoder
from .config import ClassificationConfig, LMConfig

# Legacy API (Deprecated - for backward compatibility)
from .core import TransJect
from .config import TrainingConfig, TaskConfig
from .trainer import TransJectTrainer

from .__version__ import __version__

__all__ = [
    # New API (Recommended)
    'TransJectForClassification',
    'TransJectDecoder',
    'ClassificationConfig',
    'LMConfig',
    
    # Legacy API (Deprecated)
    'TransJect',
    'TransJectTrainer',
    'TrainingConfig',
    'TaskConfig',
    
    # Version
    '__version__'
]

# Set up logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"TransJect v{__version__} initialized")
