"""
Text Generation Example with TransJect
=======================================

This example demonstrates how to use TransJect for text generation tasks:
1. Training a decoder model on text data
2. Generating text with greedy decoding (deterministic)
3. Generating text with sampling (stochastic)
4. Using the decode() convenience method
"""

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
from transject import TransJectDecoder, LMConfig
from transject.utils import get_vocab_size


class TextDataset(Dataset):
    """Simple text dataset for language modeling."""
    
    def __init__(self, texts, tokenizer, max_length=128):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.encodings = []
        
        for text in texts:
            encoding = tokenizer(
                text,
                max_length=max_length,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )
            self.encodings.append(encoding['input_ids'].squeeze(0))
    
    def __len__(self):
        return len(self.encodings)
    
    def __getitem__(self, idx):
        input_ids = self.encodings[idx]
        # For language modeling, labels are shifted input_ids
        return {
            'input_ids': input_ids,
            'labels': input_ids.clone()
        }


def main():
    # ============================================================
    # 1. Setup: Tokenizer and Data
    # ============================================================
    print("=" * 60)
    print("TransJect Text Generation Example")
    print("=" * 60)
    
    tokenizer = AutoTokenizer.from_pretrained('gpt2')
    tokenizer.pad_token = tokenizer.eos_token
    
    # Sample training texts
    train_texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning is transforming the world of technology.",
        "Natural language processing enables computers to understand human language.",
        "Deep learning models can generate realistic text.",
        "Transformers have revolutionized NLP research.",
    ] * 20  # Repeat for more training data
    
    val_texts = [
        "Artificial intelligence is the future.",
        "Language models can write creative stories.",
    ] * 10
    
    # Create datasets
    train_dataset = TextDataset(train_texts, tokenizer, max_length=64)
    val_dataset = TextDataset(val_texts, tokenizer, max_length=64)
    
    train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=4)
    
    # ============================================================
    # 2. Model Configuration and Training
    # ============================================================
    print("\n📋 Creating model configuration...")
    
    config = LMConfig(
        vocab_size=get_vocab_size('gpt2'),
        num_layers=4,        # Small model for quick training
        hidden_size=256,
        max_seq_length=64,
        n_experts=4,
        use_eigen=False,
        random_features=True
    )
    
    print(f"   Vocabulary size: {config.vocab_size}")
    print(f"   Number of layers: {config.num_layers}")
    print(f"   Hidden size: {config.hidden_size}")
    
    # Initialize model
    model = TransJectDecoder(config)
    
    print("\n🚀 Training model...")
    print("   (This may take a few minutes for demo purposes)")
    
    history = model.train(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=3,  # Small number for demo
        learning_rate=2e-4,
        accelerator='gpu' if torch.cuda.is_available() else 'cpu'
    )
    
    print("\n✅ Training complete!")
    if 'final_metrics' in history:
        print(f"   Final metrics: {history['final_metrics']}")
    elif 'callback_metrics' in history:
        print(f"   Callback metrics: {history['callback_metrics']}")
    
    # ============================================================
    # 3. Text Generation with decode() Method
    # ============================================================
    print("\n" + "=" * 60)
    print("Text Generation Examples")
    print("=" * 60)
    
    prompts = [
        "The quick brown",
        "Machine learning",
        "Natural language",
    ]
    
    # Example 1: Greedy Decoding (Deterministic)
    print("\n📝 Example 1: Greedy Decoding (do_sample=False)")
    print("-" * 60)
    
    for prompt in prompts:
        generated = model.decode(
            prompt,
            tokenizer,
            max_length=30,
            do_sample=False  # Greedy: always picks most likely token
        )
        print(f"Prompt: '{prompt}'")
        print(f"Generated: '{generated}'")
        print()
    
    # Example 2: Sampling with Temperature
    print("\n📝 Example 2: Sampling with Temperature (do_sample=True)")
    print("-" * 60)
    
    prompt = "The quick brown"
    
    for temp in [0.5, 1.0, 1.5]:
        generated = model.decode(
            prompt,
            tokenizer,
            max_length=30,
            do_sample=True,
            temperature=temp,
            top_k=50,
            top_p=0.95
        )
        print(f"Temperature {temp}: '{generated}'")
    
    # Example 3: Top-k and Top-p Sampling
    print("\n📝 Example 3: Nucleus Sampling (Top-p)")
    print("-" * 60)
    
    for top_p in [0.5, 0.9, 0.95]:
        generated = model.decode(
            prompt,
            tokenizer,
            max_length=30,
            do_sample=True,
            temperature=1.0,
            top_k=0,  # Disable top-k
            top_p=top_p
        )
        print(f"Top-p {top_p}: '{generated}'")
    
    # ============================================================
    # 4. Low-level Generation with Token IDs
    # ============================================================
    print("\n📝 Example 4: Low-level Generation with generate()")
    print("-" * 60)
    
    # Tokenize prompt
    prompt_text = "Machine learning is"
    input_ids = tokenizer(prompt_text, return_tensors='pt')['input_ids']
    
    # Move to same device as model
    device = next(model.model.parameters()).device
    input_ids = input_ids.to(device)
    
    # Generate with greedy decoding
    output_ids = model.generate(
        input_ids=input_ids,
        max_length=25,
        do_sample=False
    )
    
    # Decode output
    generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    print(f"Prompt: '{prompt_text}'")
    print(f"Generated: '{generated_text}'")
    
    # ============================================================
    # 5. Save and Load Model
    # ============================================================
    print("\n" + "=" * 60)
    print("Saving Model")
    print("=" * 60)
    
    model_path = './transject_lm_demo'
    model.save(model_path)
    print(f"✅ Model saved to: {model_path}")
    
    # Load model
    loaded_model = TransJectDecoder.load(model_path)
    print(f"✅ Model loaded from: {model_path}")
    
    # Test loaded model
    test_prompt = "The future of"
    generated = loaded_model.decode(
        test_prompt,
        tokenizer,
        max_length=20,
        do_sample=False
    )
    print(f"\nTest with loaded model:")
    print(f"Prompt: '{test_prompt}'")
    print(f"Generated: '{generated}'")
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("  ✅ Use decode() for text-to-text generation (convenience)")
    print("  ✅ Use generate() for low-level token generation")
    print("  ✅ Set do_sample=False for greedy (deterministic) decoding")
    print("  ✅ Set do_sample=True for stochastic sampling")
    print("  ✅ Control randomness with temperature, top_k, top_p")


if __name__ == "__main__":
    main()
