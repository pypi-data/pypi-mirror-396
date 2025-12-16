# TransJect: Manifold-Preserving Transformer Framework

TransJect is a transformer framework that uses orthogonal transformations to preserve token distances across layers. It provides a clean API for training transformers on classification and language modeling tasks with manifold-preserving properties.

## Features

- ✅ **Manifold-Preserving Architecture**: Orthogonal transformations preserve token distances
- ✅ **Multiple Tasks**: Classification and Language Modeling
- ✅ **Generic DataLoader Support**: Works with ANY PyTorch DataLoader
- ✅ **Flexible Configuration**: Control layers, hidden size, and architectural parameters
- ✅ **User-Controlled Metrics**: Any HuggingFace evaluate metric (accuracy, F1, MCC, etc.)
- ✅ **Easy Installation**: `pip install git+https://github.com/parmanu-lcs2/TransJect.git`

## Installation

```bash
pip install git+https://github.com/parmanu-lcs2/TransJect.git
```

## Quick Start

### NEW API (Recommended)

```python
from transject import TransJectForClassification, ClassificationConfig
from transject.utils import get_vocab_size
from torch.utils.data import DataLoader

# Get vocabulary size from tokenizer
vocab_size = get_vocab_size('bert-base-uncased')

# Create configuration
config = ClassificationConfig(
    num_labels=2,
    vocab_size=vocab_size,
    num_layers=6,
    hidden_size=512,
    max_seq_length=128,
    pooling='mean'
)

# Initialize model
model = TransJectForClassification(config)

# Your custom dataloaders
train_loader = DataLoader(your_train_dataset, batch_size=8)
val_loader = DataLoader(your_val_dataset, batch_size=8)

# Train
history = model.train(
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=10,
    learning_rate=2e-5,
    metric='accuracy'
)

# Save model
model.save('./my_model')
```

### Language Modeling

```python
from transject import TransJectDecoder, LMConfig
from transject.utils import get_vocab_size

# Configuration for language modeling
config = LMConfig(
    vocab_size=get_vocab_size('gpt2'),
    num_layers=6,
    hidden_size=512,
    max_seq_length=512
)

# Initialize decoder model
model = TransJectDecoder(config)

# Train
history = model.train(
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=10,
    learning_rate=2e-5
)

# Generate text with greedy decoding (deterministic)
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained('gpt2')
generated_text = model.decode(
    "Once upon a time",
    tokenizer,
    max_length=50,
    do_sample=False  # Greedy decoding
)

# Or generate with sampling (stochastic)
generated_text = model.decode(
    "Once upon a time",
    tokenizer,
    max_length=50,
    do_sample=True,
    temperature=0.8,
    top_k=50,
    top_p=0.95
)

# Low-level generation with token IDs
generated_ids = model.generate(
    input_ids=prompt_tokens,
    max_length=100,
    do_sample=False  # Use greedy decoding
)
```

### Legacy API (Backward Compatible)

```python
from transject import TransJect
from torch.utils.data import DataLoader

# Initialize TransJect (old API)
model = TransJect(
    task_name='my_task',
    task_type='classification',
    num_labels=2,
    num_layers=6,  # Replaces student_layers
    metric='accuracy'
)

# Train
history = model.train(
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=10,
    learning_rate=2e-5
)

# Save model (new method names)
model.save_model('./my_model')  # Replaces save_student()
```

## Configuration Classes

### ClassificationConfig

```python
ClassificationConfig(
    num_labels: int,           # Number of output classes
    vocab_size: int,          # Vocabulary size
    num_layers: int = 6,      # Number of transformer layers
    hidden_size: int = 512,   # Hidden dimension
    max_seq_length: int = 128, # Maximum sequence length
    n_experts: int = 4,       # Number of expert sublayers
    pooling: str = 'mean',    # Pooling strategy: 'mean', 'max', 'first'
    use_eigen: bool = False,  # Use eigenvalue-based attention
    random_features: bool = True  # Use random feature mixing
)
```

### LMConfig

```python
LMConfig(
    vocab_size: int,          # Vocabulary size
    num_layers: int = 6,      # Number of transformer layers
    hidden_size: int = 512,   # Hidden dimension
    max_seq_length: int = 512, # Maximum sequence length
    n_experts: int = 4,       # Number of expert sublayers
    use_eigen: bool = False,  # Use eigenvalue-based attention
    random_features: bool = True  # Use random feature mixing
)
```

## Utility Functions

```python
from transject.utils import get_vocab_size, get_tokenizer

# Get vocabulary size from any HuggingFace tokenizer
vocab_size = get_vocab_size('bert-base-uncased')
vocab_size = get_vocab_size('gpt2')
vocab_size = get_vocab_size('meta-llama/Llama-3.2-1B')

# Get tokenizer instance
tokenizer = get_tokenizer('bert-base-uncased')
```

## Data Format

Your PyTorch DataLoader should return batches with:

**For Classification:**
```python
{
    'input_ids': torch.LongTensor,  # Shape: [batch_size, seq_len]
    'out': torch.LongTensor         # Shape: [batch_size] or [batch_size, 1]
}
```

**For Language Modeling:**
```python
{
    'input_ids': torch.LongTensor,  # Shape: [batch_size, seq_len]
    'labels': torch.LongTensor      # Shape: [batch_size, seq_len] (optional)
}
```

## Examples

See the `examples/` directory for Python scripts and `notebooks/` for interactive notebooks:

**Python Scripts (`examples/`):**
- `01_imdb_classification.py` - IMDB sentiment classification example
- `02_wikitext_language_modeling.py` - WikiText-2 language modeling with perplexity
- `03_text_generation.py` - Text generation with greedy decoding and sampling
- `utils.py` - Dataset loading utilities (SuperGLUE, GLUE, Alpaca)

## Architecture Details

TransJect uses:
- **IsoAttention**: Orthogonal attention mechanism for distance preservation
- **OrthogonalFeedForward**: Lipschitz-continuous feedforward layers
- **Random Feature Mixing**: Stochastic feature combination for regularization
- **Reconstruction Loss**: Additional loss term for manifold preservation

## Requirements

- Python >= 3.8
- PyTorch >= 1.12.0
- Transformers >= 4.30.0
- PyTorch Lightning >= 2.0.0
- Datasets >= 2.10.0
- Evaluate >= 0.4.0

## Contributing

We welcome contributions to TransJect! Here's how you can help:

### Ways to Contribute

- **Report bugs**: Open an issue describing the bug and how to reproduce it
- **Suggest features**: Share ideas for new features or improvements
- **Submit pull requests**: Fix bugs, add features, or improve documentation
- **Improve documentation**: Help us make the docs clearer and more comprehensive

### Contribution Process

1. **Fork the repository** on GitHub
2. **Create a new branch** for your feature or bugfix
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and commit with clear messages
4. **Add tests** if applicable
5. **Submit a pull request** with a description of your changes

## Citation

If you find this repo useful, please cite our paper:
```BibTex
@inproceedings{sengupta-etal-2023-manifold,
    title = "Manifold-Preserving Transformers are Effective for Short-Long Range Encoding",
    author = "Sengupta, Ayan  and
      Akhtar, Md. Shad  and
      Chakraborty, Tanmoy",
    editor = "Bouamor, Houda  and
      Pino, Juan  and
      Bali, Kalika",
    booktitle = "Findings of the Association for Computational Linguistics: EMNLP 2023",
    month = dec,
    year = "2023",
    address = "Singapore",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2023.findings-emnlp.228/",
    doi = "10.18653/v1/2023.findings-emnlp.228",
    pages = "3533--3549",
    abstract = "Multi-head self-attention-based Transformers have shown promise in different learning tasks. Albeit these models exhibit significant improvement in understanding short-term and long-term contexts from sequences, encoders of Transformers and their variants fail to preserve layer-wise contextual information. Transformers usually project tokens onto sparse manifolds and fail to preserve mathematical equivalence among the token representations. In this work, we propose TransJect, an encoder model that guarantees a theoretical bound for layer-wise distance preservation between a pair of tokens. We propose a simple alternative to dot-product attention to ensure Lipschitz continuity. This allows TransJect to learn injective mappings to transform token representations to different manifolds with similar topology and preserve Euclidean distance between every pair of tokens in subsequent layers. Evaluations across multiple benchmark short- and long-sequence classification tasks show maximum improvements of 6.8{\%} and 5.9{\%}, respectively, over the variants of Transformers. Additionally, TransJect displays 79{\%} better performance than Transformer on the language modeling task. We further highlight the shortcomings of multi-head self-attention from the statistical physics viewpoint. Although multi-head self-attention was incepted to learn different abstraction levels within the networks, our empirical analyses suggest that different attention heads learn randomly and unorderly. In contrast, TransJect adapts a mixture of experts for regularization; these experts are more orderly and balanced and learn different sparse representations from the input sequences. TransJect exhibits very low entropy and can be efficiently scaled to larger depths."
}
```

## License

MIT License - see LICENSE file for details
