"""
Utility functions for TransJect.

Helper functions that don't belong in the core library but are useful for users.
"""
from transformers import AutoTokenizer
from typing import Union
import logging

logger = logging.getLogger(__name__)


def get_vocab_size(tokenizer_name: str) -> int:
    """
    Get vocabulary size from a HuggingFace tokenizer.
    
    This is a convenience function to help users who want to automatically
    detect vocab_size from a tokenizer name instead of providing it manually.
    
    Args:
        tokenizer_name: HuggingFace tokenizer name (e.g., 'bert-base-uncased', 'gpt2')
    
    Returns:
        Vocabulary size as integer
    
    Example:
        ```python
        from transject.utils import get_vocab_size
        from transject import TransJectForClassification, ClassificationConfig
        
        vocab_size = get_vocab_size('bert-base-uncased')
        
        config = ClassificationConfig(
            num_labels=2,
            vocab_size=vocab_size,
            num_layers=6,
            hidden_size=512
        )
        
        model = TransJectForClassification(config)
        ```
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        vocab_size = tokenizer.vocab_size
        logger.info(f"Vocabulary size for '{tokenizer_name}': {vocab_size}")
        return vocab_size
    except Exception as e:
        logger.error(f"Failed to load tokenizer '{tokenizer_name}': {e}")
        raise


def get_tokenizer(tokenizer_name: str, **kwargs) -> AutoTokenizer:
    """
    Load a HuggingFace tokenizer with common defaults.
    
    Args:
        tokenizer_name: HuggingFace tokenizer name
        **kwargs: Additional arguments passed to AutoTokenizer.from_pretrained
    
    Returns:
        Loaded tokenizer
    
    Example:
        ```python
        from transject.utils import get_tokenizer, get_vocab_size
        
        tokenizer = get_tokenizer('gpt2')
        tokenizer.pad_token = tokenizer.eos_token  # GPT-2 doesn't have pad token
        
        vocab_size = get_vocab_size('gpt2')
        ```
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, **kwargs)
        logger.info(f"Loaded tokenizer: {tokenizer_name}")
        return tokenizer
    except Exception as e:
        logger.error(f"Failed to load tokenizer '{tokenizer_name}': {e}")
        raise
