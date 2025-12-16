"""
IMDB Sentiment Classification with TransJect
=============================================

This example demonstrates how to use TransJect for binary sentiment classification
on the IMDB movie review dataset.

Dataset: IMDB (25,000 training + 25,000 test movie reviews)
Task: Binary classification (positive/negative sentiment)
"""

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
from datasets import load_dataset
from transject import TransJectForClassification, ClassificationConfig
from transject.utils import get_vocab_size


class IMDBDataset(Dataset):
    """Dataset wrapper for IMDB reviews."""
    
    def __init__(self, hf_dataset, tokenizer, max_length=256):
        self.data = hf_dataset
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # Tokenize text
        encoding = self.tokenizer(
            item['text'],
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'out': torch.tensor(item['label'], dtype=torch.long)
        }


def main():
    # ============================================================
    # 1. Setup: Load Dataset and Tokenizer
    # ============================================================
    print("=" * 60)
    print("IMDB Sentiment Classification with TransJect")
    print("=" * 60)
    
    print("\n Loading IMDB dataset...")
    
    # Load IMDB dataset from HuggingFace
    dataset = load_dataset('imdb')
    
    # Use subset for faster demo (remove these lines for full training)
    train_data = dataset['train'].shuffle(seed=42).select(range(1000))
    test_data = dataset['test'].shuffle(seed=42).select(range(500))
    
    print(f"   Training samples: {len(train_data)}")
    print(f"   Test samples: {len(test_data)}")
    
    # Initialize tokenizer
    print("\n Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
    
    # Create datasets
    train_dataset = IMDBDataset(train_data, tokenizer, max_length=256)
    test_dataset = IMDBDataset(test_data, tokenizer, max_length=256)
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True, num_workers=0)
    val_loader = DataLoader(test_dataset, batch_size=8, num_workers=0)
    
    print(" Data prepared!")
    
    # ============================================================
    # 2. Model Configuration
    # ============================================================
    print("\n Creating model configuration...")
    
    config = ClassificationConfig(
        num_labels=2,  # Binary classification (positive/negative)
        vocab_size=get_vocab_size('bert-base-uncased'),
        num_layers=6,
        hidden_size=512,
        max_seq_length=256,
        n_experts=4,
        pooling='mean',  # Mean pooling over sequence
        use_eigen=False,
        random_features=True
    )
    
    print(f"   Task: Sentiment Classification")
    print(f"   Number of labels: {config.num_labels}")
    print(f"   Vocabulary size: {config.vocab_size}")
    print(f"   Number of layers: {config.num_layers}")
    print(f"   Hidden size: {config.hidden_size}")
    print(f"   Pooling strategy: {config.pooling}")
    
    # ============================================================
    # 3. Initialize and Train Model
    # ============================================================
    print("\n Initializing model...")
    model = TransJectForClassification(config)
    
    print("\n Training model...")
    print("   (This may take several minutes)")
    
    history = model.train(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=5,
        learning_rate=2e-5,
        metric='accuracy',  # Use accuracy as evaluation metric
        accelerator='gpu' if torch.cuda.is_available() else 'cpu'
    )
    
    print("\n Training complete!")
    if 'final_metrics' in history:
        print(f"   Final metrics: {history['final_metrics']}")
    elif 'callback_metrics' in history:
        print(f"   Callback metrics: {history['callback_metrics']}")
    
    # ============================================================
    # 4. Evaluate Model
    # ============================================================
    print("\n" + "=" * 60)
    print("Model Evaluation")
    print("=" * 60)
    
    print("\n Evaluating on test set...")
    results = model.evaluate(val_loader)
    
    print("\nTest Results:")
    for metric, value in results.items():
        print(f"   {metric}: {value}")
    
    # ============================================================
    # 5. Test Predictions on Sample Reviews
    # ============================================================
    print("\n" + "=" * 60)
    print("Sample Predictions")
    print("=" * 60)
    
    sample_reviews = [
        "This movie was absolutely fantastic! I loved every minute of it.",
        "Terrible film. Complete waste of time and money.",
        "An okay movie, nothing special but not terrible either.",
        "One of the best movies I've ever seen! Highly recommended!",
        "I fell asleep halfway through. Boring and predictable.",
    ]
    
    # Ensure model is in eval mode
    if model.model is not None:
        model.model.eval()
        device = next(model.model.parameters()).device
        
        print("\nPredictions:")
        with torch.no_grad():
            for review in sample_reviews:
                # Tokenize
                encoding = tokenizer(
                    review,
                    max_length=256,
                    padding='max_length',
                    truncation=True,
                    return_tensors='pt'
                )
                input_ids = encoding['input_ids'].to(device)
                
                # Predict
                logits = model.model(input_ids)
                # Extract the tensor from the tuple
                if isinstance(logits, tuple):
                    logits = logits[0]
                prediction = torch.argmax(logits, dim=-1).item()
                
                sentiment = "Positive " if prediction == 1 else "Negative "
                print(f"\nReview: \"{review[:70]}...\"")
                print(f"Prediction: {sentiment}")
    else:
        print(" Model not trained, skipping predictions")
    
    # ============================================================
    # 6. Save Model
    # ============================================================
    print("\n" + "=" * 60)
    print("Saving Model")
    print("=" * 60)
    
    model_path = './transject_imdb_classifier.pt'
    model.save(model_path)
    print(f" Model saved to: {model_path}")
    
    # Load and test
    loaded_model = TransJectForClassification.load(model_path)
    print(f" Model loaded from: {model_path}")
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("   TransJectForClassification for classification tasks")
    print("   Use any HuggingFace dataset with proper data loader")
    print("   Configure num_labels, vocab_size, num_layers")
    print("   Choose metric: 'accuracy', 'f1', 'precision', 'recall'")
    print("   Save and load models easily")


if __name__ == "__main__":
    main()
