"""
WikiText-2 Language Modeling with TransJect
============================================

This example demonstrates how to use TransJect for language modeling
on the WikiText-2 dataset.

Dataset: WikiText-2 (2 million tokens from Wikipedia)
Task: Autoregressive language modeling
Evaluation: Perplexity
"""

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
from datasets import load_dataset
from transject import TransJectDecoder, LMConfig
from transject.utils import get_vocab_size


class WikiTextDataset(Dataset):
    """Dataset wrapper for WikiText-2."""
    
    def __init__(self, hf_dataset, tokenizer, max_length=512):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.encodings = []
        
        # Filter out empty texts and tokenize
        print(f"   Processing {len(hf_dataset)} examples...")
        for idx, item in enumerate(hf_dataset):
            text = item['text'].strip()
            if len(text) > 10:  # Skip very short or empty lines
                encoding = tokenizer(
                    text,
                    max_length=max_length,
                    padding='max_length',
                    truncation=True,
                    return_tensors='pt'
                )
                self.encodings.append(encoding['input_ids'].squeeze(0))
            
            if (idx + 1) % 1000 == 0:
                print(f"   Processed {idx + 1}/{len(hf_dataset)} examples...")
        
        print(f"   Kept {len(self.encodings)} non-empty examples")
    
    def __len__(self):
        return len(self.encodings)
    
    def __getitem__(self, idx):
        input_ids = self.encodings[idx]
        return {
            'input_ids': input_ids,
            'labels': input_ids.clone()  # For LM, labels = inputs (shifted internally)
        }


def main():
    # ============================================================
    # 1. Setup: Load Dataset and Tokenizer
    # ============================================================
    print("=" * 60)
    print("WikiText-2 Language Modeling with TransJect")
    print("=" * 60)
    
    print("\n Loading WikiText-2 dataset...")
    
    # Load WikiText-2 dataset from HuggingFace
    dataset = load_dataset('wikitext', 'wikitext-2-raw-v1')
    
    print(f"   Raw training samples: {len(dataset['train'])}")
    print(f"   Raw validation samples: {len(dataset['validation'])}")
    print(f"   Raw test samples: {len(dataset['test'])}")
    
    # Initialize tokenizer
    print("\n Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained('gpt2')
    tokenizer.pad_token = tokenizer.eos_token
    
    # Create datasets
    print("\n Preparing training dataset...")
    train_dataset = WikiTextDataset(dataset['train'], tokenizer, max_length=512)
    
    print("\n Preparing validation dataset...")
    val_dataset = WikiTextDataset(dataset['validation'], tokenizer, max_length=512)
    
    print("\n Preparing test dataset...")
    test_dataset = WikiTextDataset(dataset['test'], tokenizer, max_length=512)
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=4, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=4, num_workers=0)
    
    print("\n Data prepared!")
    
    # ============================================================
    # 2. Model Configuration
    # ============================================================
    print("\n Creating model configuration...")
    
    config = LMConfig(
        vocab_size=get_vocab_size('gpt2'),
        num_layers=6,
        hidden_size=512,
        max_seq_length=512,
        n_experts=4,
        use_eigen=False,
        random_features=True
    )
    
    print(f"   Task: Language Modeling")
    print(f"   Vocabulary size: {config.vocab_size}")
    print(f"   Number of layers: {config.num_layers}")
    print(f"   Hidden size: {config.hidden_size}")
    print(f"   Max sequence length: {config.max_seq_length}")
    
    # ============================================================
    # 3. Initialize and Train Model
    # ============================================================
    print("\n Initializing model...")
    model = TransJectDecoder(config)
    
    print("\n Training model...")
    print("   (This will take some time)")
    
    history = model.train(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=5,
        learning_rate=1e-4,
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
    test_results = model.evaluate(test_loader)
    
    print("\nTest Results:")
    for metric, value in test_results.items():
        print(f"   {metric}: {value}")
    
    # ============================================================
    # 5. Generate Sample Text
    # ============================================================
    print("\n" + "=" * 60)
    print("Text Generation Examples")
    print("=" * 60)
    
    prompts = [
        "The history of",
        "In the year",
        "Scientists have discovered",
        "The most important",
    ]
    
    print("\n Generating text with greedy decoding:")
    for prompt in prompts:
        generated = model.decode(
            prompt,
            tokenizer,
            max_length=50,
            do_sample=False
        )
        print(f"\nPrompt: '{prompt}'")
        print(f"Generated: '{generated}'")
    
    print("\n Generating text with sampling (temperature=0.8):")
    for prompt in prompts[:2]:  # Just first 2 for variety
        generated = model.decode(
            prompt,
            tokenizer,
            max_length=50,
            do_sample=True,
            temperature=0.8,
            top_k=50,
            top_p=0.95
        )
        print(f"\nPrompt: '{prompt}'")
        print(f"Generated: '{generated}'")
    
    # ============================================================
    # 6. Save Model
    # ============================================================
    print("\n" + "=" * 60)
    print("Saving Model")
    print("=" * 60)
    
    model_path = './transject_wikitext_lm.pt'
    model.save(model_path)
    print(f" Model saved to: {model_path}")
    
    # Load and test
    loaded_model = TransJectDecoder.load(model_path)
    print(f" Model loaded from: {model_path}")
    
    # Test loaded model
    test_prompt = "The meaning of life"
    generated = loaded_model.decode(test_prompt, tokenizer, max_length=30, do_sample=False)
    print(f"\n Test with loaded model:")
    print(f"   Prompt: '{test_prompt}'")
    print(f"   Generated: '{generated}'")
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("   TransJectDecoder for language modeling tasks")
    print("   WikiText-2 dataset from HuggingFace")
    print("   Perplexity evaluation handled automatically")
    print("   Text generation with greedy and sampling strategies")
    print("   Model save/load functionality")


if __name__ == "__main__":
    main()
