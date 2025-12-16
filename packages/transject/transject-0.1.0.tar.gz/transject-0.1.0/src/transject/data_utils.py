"""
Data loading utilities for TransJect.

Provides functions to load SuperGLUE, GLUE, and Alpaca datasets
in a format compatible with TransJect models.
"""
import torch
from torch.utils.data import DataLoader
from datasets import load_dataset
from transformers import AutoTokenizer
from typing import Dict, Tuple, Optional, Any
import logging
import sys
import os

from custom_datasets import ClassificationDataset, CustomDataset

logger = logging.getLogger(__name__)


def load_superglue_dataset(
    task_name: str,
    tokenizer_name: str = 'bert-base-uncased',
    max_length: int = 128,
    batch_size: int = 8,
    cache_dir: Optional[str] = None,
    max_samples: Optional[int] = None,
    num_workers: int = 0
) -> Tuple[Dict[str, DataLoader], int]:
    """
    Load SuperGLUE dataset.
    
    Supported tasks: CB, RTE, BoolQ, COPA, WiC, WSC
    
    Args:
        task_name: Name of SuperGLUE task
        tokenizer_name: HuggingFace tokenizer name
        max_length: Maximum sequence length
        batch_size: Batch size for DataLoaders
        cache_dir: Cache directory for datasets
        max_samples: Maximum number of samples (for debugging)
        num_workers: Number of workers for DataLoader
    
    Returns:
        Tuple of (loaders_dict, num_labels)
        - loaders_dict: Dict with keys 'train', 'val', 'test'
        - num_labels: Number of output labels
    """
    
    logger.info(f"Loading SuperGLUE task: {task_name}")
    
    # Load dataset from HuggingFace
    dataset = load_dataset("super_glue", task_name.lower(), cache_dir=cache_dir)
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    
    # Task-specific preprocessing
    task_upper = task_name.upper()
    
    if task_upper == "COPA":
        num_labels = 2
        texts_train, labels_train = _preprocess_copa(dataset['train'], tokenizer, max_length, max_samples)
        texts_val, labels_val = _preprocess_copa(dataset['validation'], tokenizer, max_length, max_samples)
        texts_test, labels_test = _preprocess_copa(dataset['test'], tokenizer, max_length, None)
    
    elif task_upper == "BOOLQ":
        num_labels = 2
        texts_train, labels_train = _preprocess_boolq(dataset['train'], tokenizer, max_length, max_samples)
        texts_val, labels_val = _preprocess_boolq(dataset['validation'], tokenizer, max_length, max_samples)
        texts_test, labels_test = _preprocess_boolq(dataset['test'], tokenizer, max_length, None)
    
    elif task_upper == "RTE":
        num_labels = 2
        texts_train, labels_train = _preprocess_rte(dataset['train'], tokenizer, max_length, max_samples)
        texts_val, labels_val = _preprocess_rte(dataset['validation'], tokenizer, max_length, max_samples)
        texts_test, labels_test = _preprocess_rte(dataset['test'], tokenizer, max_length, None)
    
    elif task_upper == "CB":
        num_labels = 3
        texts_train, labels_train = _preprocess_cb(dataset['train'], tokenizer, max_length, max_samples)
        texts_val, labels_val = _preprocess_cb(dataset['validation'], tokenizer, max_length, max_samples)
        texts_test, labels_test = _preprocess_cb(dataset['test'], tokenizer, max_length, None)
    
    elif task_upper == "WIC":
        num_labels = 2
        texts_train, labels_train = _preprocess_wic(dataset['train'], tokenizer, max_length, max_samples)
        texts_val, labels_val = _preprocess_wic(dataset['validation'], tokenizer, max_length, max_samples)
        texts_test, labels_test = _preprocess_wic(dataset['test'], tokenizer, max_length, None)
    
    elif task_upper == "WSC":
        num_labels = 2
        texts_train, labels_train = _preprocess_wsc(dataset['train'], tokenizer, max_length, max_samples)
        texts_val, labels_val = _preprocess_wsc(dataset['validation'], tokenizer, max_length, max_samples)
        texts_test, labels_test = _preprocess_wsc(dataset['test'], tokenizer, max_length, None)
    
    else:
        raise NotImplementedError(f"Task {task_name} not yet implemented")
    
    # Create datasets
    train_dataset = CustomDataset(texts_train, labels_train)
    val_dataset = CustomDataset(texts_val, labels_val)
    test_dataset = CustomDataset(texts_test, labels_test)
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers
    )
    
    loaders = {
        'train': train_loader,
        'val': val_loader,
        'test': test_loader
    }
    
    logger.info(f"Loaded {len(train_dataset)} train, {len(val_dataset)} val, {len(test_dataset)} test samples")
    
    return loaders, num_labels


def _preprocess_copa(dataset, tokenizer, max_length, max_samples):
    """Preprocess COPA dataset."""
    texts = []
    labels = []
    
    for i, example in enumerate(dataset):
        if max_samples and i >= max_samples:
            break
        
        premise = example['premise']
        choice1 = example['choice1']
        choice2 = example['choice2']
        
        # Concatenate premise with both choices
        text = f"{premise} {choice1} {choice2}"
        texts.append(tokenizer.encode(text, padding='max_length', max_length=max_length, truncation=True)[:max_length])
        labels.append(example['label'] if example['label'] != -1 else 0)
    
    return texts, labels


def _preprocess_boolq(dataset, tokenizer, max_length, max_samples):
    """Preprocess BoolQ dataset."""
    texts = []
    labels = []
    
    for i, example in enumerate(dataset):
        if max_samples and i >= max_samples:
            break
        
        question = example['question']
        passage = example['passage']
        
        text = f"{question} {passage}"
        texts.append(tokenizer.encode(text, padding='max_length', max_length=max_length, truncation=True)[:max_length])
        labels.append(example['label'] if example['label'] != -1 else 0)
    
    return texts, labels


def _preprocess_rte(dataset, tokenizer, max_length, max_samples):
    """Preprocess RTE dataset."""
    texts = []
    labels = []
    
    for i, example in enumerate(dataset):
        if max_samples and i >= max_samples:
            break
        
        premise = example['premise']
        hypothesis = example['hypothesis']
        
        text = f"{premise} {hypothesis}"
        texts.append(tokenizer.encode(text, padding='max_length', max_length=max_length, truncation=True)[:max_length])
        labels.append(example['label'] if example['label'] != -1 else 0)
    
    return texts, labels


def _preprocess_cb(dataset, tokenizer, max_length, max_samples):
    """Preprocess CB dataset."""
    texts = []
    labels = []
    
    for i, example in enumerate(dataset):
        if max_samples and i >= max_samples:
            break
        
        premise = example['premise']
        hypothesis = example['hypothesis']
        
        text = f"{premise} {hypothesis}"
        texts.append(tokenizer.encode(text, padding='max_length', max_length=max_length, truncation=True)[:max_length])
        labels.append(example['label'] if example['label'] != -1 else 0)
    
    return texts, labels


def _preprocess_wic(dataset, tokenizer, max_length, max_samples):
    """Preprocess WiC dataset."""
    texts = []
    labels = []
    
    for i, example in enumerate(dataset):
        if max_samples and i >= max_samples:
            break
        
        sentence1 = example['sentence1']
        sentence2 = example['sentence2']
        word = example['word']
        
        text = f"{word}: {sentence1} {sentence2}"
        texts.append(tokenizer.encode(text, padding='max_length', max_length=max_length, truncation=True)[:max_length])
        labels.append(example['label'] if example['label'] != -1 else 0)
    
    return texts, labels


def _preprocess_wsc(dataset, tokenizer, max_length, max_samples):
    """Preprocess WSC dataset."""
    texts = []
    labels = []
    
    for i, example in enumerate(dataset):
        if max_samples and i >= max_samples:
            break
        
        text_content = example['text']
        texts.append(tokenizer.encode(text_content, padding='max_length', max_length=max_length, truncation=True)[:max_length])
        labels.append(example['label'] if example['label'] != -1 else 0)
    
    return texts, labels


def load_glue_dataset(
    task_name: str,
    tokenizer_name: str = 'bert-base-uncased',
    max_length: int = 128,
    batch_size: int = 16,
    cache_dir: Optional[str] = None,
    max_samples: Optional[int] = None,
    num_workers: int = 0
) -> Tuple[Dict[str, DataLoader], int]:
    """
    Load GLUE dataset.
    
    Supported tasks: SST2, MRPC, QQP, MNLI, QNLI, RTE, WNLI, CoLA
    
    Args:
        task_name: Name of GLUE task
        tokenizer_name: HuggingFace tokenizer name
        max_length: Maximum sequence length
        batch_size: Batch size for DataLoaders
        cache_dir: Cache directory for datasets
        max_samples: Maximum number of samples (for debugging)
        num_workers: Number of workers for DataLoader
    
    Returns:
        Tuple of (loaders_dict, num_labels)
    """
    
    logger.info(f"Loading GLUE task: {task_name}")
    
    dataset = load_dataset("glue", task_name.lower(), cache_dir=cache_dir)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    
    # Get num_labels from dataset
    num_labels = dataset['train'].features['label'].num_classes
    
    # Task-specific keys
    task_to_keys = {
        'cola': ('sentence', None),
        'sst2': ('sentence', None),
        'mrpc': ('sentence1', 'sentence2'),
        'qqp': ('question1', 'question2'),
        'mnli': ('premise', 'hypothesis'),
        'qnli': ('question', 'sentence'),
        'rte': ('sentence1', 'sentence2'),
        'wnli': ('sentence1', 'sentence2'),
    }
    
    sentence1_key, sentence2_key = task_to_keys[task_name.lower()]
    
    # Preprocess datasets
    texts_train, labels_train = _preprocess_glue(
        dataset['train'], tokenizer, max_length, sentence1_key, sentence2_key, max_samples
    )
    
    val_key = 'validation_matched' if task_name.lower() == 'mnli' else 'validation'
    texts_val, labels_val = _preprocess_glue(
        dataset[val_key], tokenizer, max_length, sentence1_key, sentence2_key, max_samples
    )
    
    # GLUE test sets don't have labels
    if 'test' in dataset:
        texts_test, labels_test = _preprocess_glue(
            dataset['test'], tokenizer, max_length, sentence1_key, sentence2_key, None
        )
    else:
        texts_test, labels_test = [], []
    
    # Create datasets
    train_dataset = CustomDataset(texts_train, labels_train)
    val_dataset = CustomDataset(texts_val, labels_val)
    test_dataset = CustomDataset(texts_test, labels_test) if texts_test else None
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers) if test_dataset else None
    
    loaders = {
        'train': train_loader,
        'val': val_loader,
    }
    if test_loader:
        loaders['test'] = test_loader
    
    logger.info(f"Loaded {len(train_dataset)} train, {len(val_dataset)} val samples")
    
    return loaders, num_labels


def _preprocess_glue(dataset, tokenizer, max_length, sentence1_key, sentence2_key, max_samples):
    """Preprocess GLUE dataset."""
    texts = []
    labels = []
    
    for i, example in enumerate(dataset):
        if max_samples and i >= max_samples:
            break
        
        if sentence2_key is None:
            text = example[sentence1_key]
        else:
            text = f"{example[sentence1_key]} {example[sentence2_key]}"
        
        texts.append(tokenizer.encode(text, padding='max_length', max_length=max_length, truncation=True)[:max_length])
        labels.append(example['label'] if example['label'] != -1 else 0)
    
    return texts, labels


def load_alpaca_dataset(
    tokenizer,
    max_seq_length: int = 512,
    batch_size: int = 4,
    num_samples: Optional[int] = None,
    dataset_name: str = 'tatsu-lab/alpaca',
    cache_dir: Optional[str] = None,
    num_workers: int = 0
) -> Tuple[Dict[str, DataLoader], Dict[str, Any]]:
    """
    Load Alpaca instruction-following dataset for language modeling.
    
    Format: instruction + input + output
    
    Args:
        tokenizer: HuggingFace tokenizer instance
        max_seq_length: Maximum sequence length
        batch_size: Batch size for DataLoaders
        num_samples: Maximum number of samples (for debugging)
        dataset_name: HuggingFace dataset name
        cache_dir: Cache directory for datasets
        num_workers: Number of workers for DataLoader
    
    Returns:
        Tuple of (loaders_dict, info_dict)
        - loaders_dict: Dict with keys 'train', 'val'
        - info_dict: Dict with 'vocab_size', 'num_samples'
    """
    
    logger.info("Loading Alpaca dataset for language modeling")
    
    # Load dataset
    dataset = load_dataset(dataset_name, split="train", cache_dir=cache_dir)
    
    if num_samples:
        dataset = dataset.select(range(min(num_samples, len(dataset))))
    
    # Split into train/val
    split = dataset.train_test_split(test_size=0.1, seed=42)
    
    # Preprocess
    texts_train, labels_train = _preprocess_alpaca(split['train'], tokenizer, max_seq_length)
    texts_val, labels_val = _preprocess_alpaca(split['test'], tokenizer, max_seq_length)
    
    # Create datasets
    train_dataset = CustomDataset(texts_train, labels_train)
    val_dataset = CustomDataset(texts_val, labels_val)
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    
    logger.info(f"Loaded {len(train_dataset)} train, {len(val_dataset)} val samples")
    
    # Create info dict
    info = {
        'vocab_size': tokenizer.vocab_size,
        'num_samples': len(train_dataset) + len(val_dataset),
        'max_seq_length': max_seq_length
    }
    
    return {'train': train_loader, 'val': val_loader}, info


def _preprocess_alpaca(dataset, tokenizer, max_seq_length):
    """Preprocess Alpaca dataset."""
    texts = []
    labels = []
    
    for example in dataset:
        # Format: "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n{output}"
        inst = example['instruction']
        inp = example.get('input', '')
        out = example['output']
        
        if inp:
            prompt = f"### Instruction:\n{inst}\n\n### Input:\n{inp}\n\n### Response:\n{out}"
        else:
            prompt = f"### Instruction:\n{inst}\n\n### Response:\n{out}"
        
        encoded = tokenizer.encode(prompt, padding='max_length', max_length=max_seq_length, truncation=True)[:max_seq_length]
        texts.append(encoded)
        # For language modeling, labels = input_ids
        labels.append(encoded)
    
    return texts, labels


