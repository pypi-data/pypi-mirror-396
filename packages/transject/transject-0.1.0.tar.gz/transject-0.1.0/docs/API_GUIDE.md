# TransJect API Guide

This document describes the TransJect API for training manifold-preserving transformers.

## Overview

TransJect provides two APIs:
1. **New API** (Recommended): Clean, configuration-based API with separate classes for classification and language modeling
2. **Legacy API**: Backward-compatible unified API

## New API

### Classification

The new API uses separate model classes and configuration objects for cleaner code:

```python
from transject import TransJectForClassification, ClassificationConfig
from transject.utils import get_vocab_size

# Create configuration
config = ClassificationConfig(
    num_labels=2,
    vocab_size=get_vocab_size('bert-base-uncased'),
    num_layers=6,
    hidden_size=512,
    max_seq_length=128,
    n_experts=4,
    pooling='mean',
    use_eigen=False,
    random_features=True
)

# Initialize model
model = TransJectForClassification(config)

# Train
history = model.train(
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=10,
    learning_rate=2e-5,
    metric='accuracy',
    report_to='wandb'  # Optional: 'wandb', 'tensorboard', or None
)

# Evaluate
metrics = model.evaluate(test_loader, metric='accuracy')

# Predict
predictions = model.predict(data_loader)

# Save/Load
model.save('./my_model')
loaded_model = TransJectForClassification.load('./my_model')
```

### Language Modeling

```python
from transject import TransJectDecoder, LMConfig
from transject.utils import get_vocab_size

# Create configuration
config = LMConfig(
    vocab_size=get_vocab_size('gpt2'),
    num_layers=6,
    hidden_size=512,
    max_seq_length=512,
    n_experts=4
)

# Initialize model
model = TransJectDecoder(config)

# Train
history = model.train(
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=10,
    learning_rate=2e-5
)

# Generate text
generated_ids = model.generate(
    input_ids=prompt_tokens,
    max_length=100,
    temperature=0.8,
    top_k=50,
    top_p=0.95
)
```

## Configuration Classes

### ClassificationConfig

```python
@dataclass
class ClassificationConfig:
    num_labels: int              # Number of output classes
    vocab_size: int              # Vocabulary size
    num_layers: int = 6          # Number of transformer layers
    hidden_size: int = 512       # Hidden dimension
    max_seq_length: int = 128    # Maximum sequence length
    n_experts: int = 4           # Number of expert sublayers
    pooling: str = 'mean'        # Pooling: 'mean', 'max', 'min', 'first'
    use_eigen: bool = False      # Use eigenvalue-based attention
    random_features: bool = True  # Use random feature mixing
```

### LMConfig

```python
@dataclass
class LMConfig:
    vocab_size: int              # Vocabulary size
    num_layers: int = 6          # Number of transformer layers
    hidden_size: int = 512       # Hidden dimension
    max_seq_length: int = 512    # Maximum sequence length
    n_experts: int = 4           # Number of expert sublayers
    use_eigen: bool = False      # Use eigenvalue-based attention
    random_features: bool = True  # Use random feature mixing
```

## Utility Functions

### get_vocab_size()

Get vocabulary size from any HuggingFace tokenizer:

```python
from transject.utils import get_vocab_size

vocab_size = get_vocab_size('bert-base-uncased')  # 30522
vocab_size = get_vocab_size('gpt2')               # 50257
vocab_size = get_vocab_size('meta-llama/Llama-3.2-1B')
```

### get_tokenizer()

Get a tokenizer instance:

```python
from transject.utils import get_tokenizer

tokenizer = get_tokenizer('bert-base-uncased')
tokens = tokenizer("Hello world", return_tensors='pt')
```

## Data Format

### Classification DataLoader

Your DataLoader should return batches with:

```python
{
    'input_ids': torch.LongTensor,  # Shape: [batch_size, seq_len]
    'out': torch.LongTensor         # Shape: [batch_size] or [batch_size, 1]
}
```

Example:
```python
class MyDataset(torch.utils.data.Dataset):
    def __getitem__(self, idx):
        return {
            'input_ids': torch.tensor([101, 2023, 2003, ...]),  # Tokenized input
            'out': torch.tensor([1])  # Label
        }
```

### Language Modeling DataLoader

```python
{
    'input_ids': torch.LongTensor,  # Shape: [batch_size, seq_len]
    'labels': torch.LongTensor      # Shape: [batch_size, seq_len] (optional)
}
```

If `labels` are not provided, the model uses input_ids shifted by one position.

## Training Configuration

Use `TrainingConfig` for advanced control:

```python
from transject import TransJectForClassification, ClassificationConfig, TrainingConfig

# Model config
model_config = ClassificationConfig(
    num_labels=2,
    vocab_size=30522,
    num_layers=6
)

# Training config
train_config = TrainingConfig(
    epochs=10,
    learning_rate=2e-5,
    batch_size=16,
    lambda_=0.1,        # Reconstruction loss weight
    use_ortho=True,     # Use orthogonal constraints
    use_rezero=True,    # Use ReZero initialization
    early_stopping=True,
    patience=3,
    output_dir='./outputs',
    report_to='wandb'   # Logging backend
)

model = TransJectForClassification(model_config)
history = model.train(
    train_loader=train_loader,
    val_loader=val_loader,
    config=train_config
)
```

## Legacy API (Backward Compatible)

The unified `TransJect` class is still supported:

```python
from transject import TransJect

model = TransJect(
    task_name='my_task',
    task_type='classification',  # or 'language_modeling'
    num_labels=2,
    num_layers=6,     # Replaces old student_layers parameter
    metric='accuracy',
    tokenizer_name='bert-base-uncased',
    max_length=128
)

history = model.train(
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=10
)

# New method names (old names still work with deprecation warnings)
model.save_model('./my_model')  # Replaces save_student()
model.load_model('./my_model')  # Replaces load_student()
```

## Metrics

Supported metrics from HuggingFace `evaluate`:

- `'accuracy'` - Classification accuracy
- `'f1'` - F1 score (supports micro, macro, weighted)
- `'matthews_correlation'` - Matthews Correlation Coefficient
- `'precision'` - Precision
- `'recall'` - Recall
- `'pearsonr'` - Pearson correlation (for regression)
- `'spearmanr'` - Spearman correlation (for regression)

Example:
```python
# F1 with macro averaging
history = model.train(
    train_loader=train_loader,
    val_loader=val_loader,
    metric='f1',
    epochs=10
)

# Evaluate with different metric
test_metrics = model.evaluate(test_loader, metric='matthews_correlation')
```

## Key Differences Between APIs

| Feature | New API | Legacy API |
|---------|---------|------------|
| Model Classes | Separate (TransJectForClassification, TransJectDecoder) | Unified (TransJect) |
| Configuration | Config objects (ClassificationConfig, LMConfig) | Constructor parameters |
| Parameter Names | num_layers, hidden_size, vocab_size | num_layers (was student_layers), d_model, src_vocab |
| Save/Load | save(), load() | save_model(), load_model() |
| Type Safety | Strong (dataclasses) | Weak (kwargs) |

## Migration from Old API

If you have code using the old API:

```python
# Old code
model = TransJect(
    task_name='COPA',
    task_type='classification',
    num_labels=2,
    student_layers=6,  # OLD PARAMETER
    metric='accuracy'
)
model.save_student('./model')  # OLD METHOD
```

Migrate to new API:

```python
# New code
from transject import TransJectForClassification, ClassificationConfig
from transject.utils import get_vocab_size

config = ClassificationConfig(
    num_labels=2,
    vocab_size=get_vocab_size('bert-base-uncased'),
    num_layers=6,  # NEW PARAMETER NAME
    hidden_size=512,
    max_seq_length=128
)
model = TransJectForClassification(config)
model.save('./model')  # NEW METHOD
```

Or use the legacy API with updated parameter names:

```python
# Updated legacy code
model = TransJect(
    task_name='COPA',
    task_type='classification',
    num_labels=2,
    num_layers=6,  # UPDATED PARAMETER NAME
    metric='accuracy'
)
model.save_model('./model')  # UPDATED METHOD NAME
```
