import math
from pickletools import optimize
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from .layers import IsoEncoder, IsoDecoder
from pytorch_lightning import LightningModule
from torch.optim.lr_scheduler import LambdaLR
import wandb
from transformers import get_linear_schedule_with_warmup

import torch
import logging
from typing import Optional, Dict, Any, List

from .config import ClassificationConfig, LMConfig, TrainingConfig
from .trainer import TransJectTrainer
from .callbacks import MetricCallback

logger = logging.getLogger(__name__)

class IsoFormerForClassificationPL(LightningModule):
    def __init__(self, args, vocab_size, hidden_size, max_seq_length, num_layers, n_experts, n_out, use_eigen=False, pooling='mean', classification_type='binary', random_features=True):

        super().__init__()

        self.save_hyperparameters(ignore=['args'])
        self.args = args
        
        self.n_out = n_out
        self.pooling = pooling
        self.encoder = IsoEncoder(vocab_size, hidden_size, max_seq_length, num_layers, n_experts, use_eigen, random_features=random_features)
        self.out = nn.Linear(hidden_size, n_out)
        self.classification_type = classification_type

        self.best_acc = 0

        # For binary classification:
        # - If n_out=1: Use BCEWithLogitsLoss (single sigmoid output)
        # - If n_out=2: Use CrossEntropyLoss (two class logits)
        if self.args.classification_type == 'binary' and n_out == 1:
            self.loss_fn = nn.BCEWithLogitsLoss()
        else:
            # Use CrossEntropyLoss for multiclass or binary with 2 outputs
            self.loss_fn = nn.CrossEntropyLoss()

    def forward(self, src, debug=False):
        if debug == True:
            hidden_state, recon_loss, all_expert_weights, all_hidden_states,all_expert_hidden_states,  eigs = self.encoder(src, True, True)
        else:
            hidden_state, recon_loss = self.encoder(src)

        if self.n_out > 1:
            if self.pooling == 'mean':
                out = nn.Softmax(-1)(self.out(hidden_state.mean(1)))
            elif self.pooling == 'max':
                out = nn.Softmax(-1)(self.out(hidden_state.max(1).values))
            elif self.pooling == 'min':
                out = nn.Softmax(-1)(self.out(hidden_state.min(1).values))
            elif self.pooling == 'first':
                out = nn.Softmax(-1)(self.out(hidden_state[:,0,:]))
        else:
            if self.pooling == 'mean':
                out = self.out(hidden_state.mean(1))
            elif self.pooling == 'max':
                out = self.out(hidden_state.max(1).values)
            elif self.pooling == 'min':
                out = self.out(hidden_state.min(1).values)
            elif self.pooling == 'first':
                out = self.out(hidden_state[:,0,:])
        
        #print (cosine_similarity(hidden_state.mean(1).detach().cpu().numpy()))
        if self.classification_type == 'regression':
            out = F.relu(out)
        
        if debug == True:
            return out, recon_loss, all_expert_weights, all_hidden_states, all_expert_hidden_states, eigs
        else:
            return out, recon_loss

    def training_step(self, batch, batch_idx):
        lambda_ = self.args.lambda_

        src = batch['input_ids']
        trg = batch['out']

        #self.sched.zero_grad()
        outputs, recon_loss = self(src)

        l2_reg = 0

        # Prepare targets based on classification type and output dimension
        if len(trg.size()) == 2:
            trg = trg.squeeze(-1)  # [batch, 1] -> [batch]
        
        if self.n_out == 1:
            # BCEWithLogitsLoss: expects float targets
            trg = trg.float()
        else:
            # CrossEntropyLoss: expects long targets
            trg = trg.long()

        total_loss = self.loss_fn(outputs, trg) + lambda_ * l2_reg + lambda_ * recon_loss

        self.log("train_loss", total_loss, on_step=True, on_epoch=True, prog_bar=True, logger=True)

        return {'loss': total_loss}

    def validation_step(self, batch, batch_idx):
        src = batch['input_ids']
        trg = batch['out']

        outputs, recon_loss = self(src)

        # Prepare targets based on classification type and output dimension
        if len(trg.size()) == 2:
            trg = trg.squeeze(-1)  # [batch, 1] -> [batch]
        
        if self.n_out == 1:
            # BCEWithLogitsLoss: expects float targets
            trg = trg.float()
        else:
            # CrossEntropyLoss: expects long targets
            trg = trg.long()

        total_loss = self.loss_fn(outputs, trg)

        # Get predictions
        if self.n_out == 1:
            # Binary with single output: apply sigmoid
            outputs = torch.sigmoid(outputs)
        else:
            # Multi-output: use argmax
            outputs = outputs.argmax(-1)

        self.log("val_loss", total_loss, on_step=True, on_epoch=True, prog_bar=True, logger=True)    
        
        return {"val_loss": total_loss, "pred": outputs, "target": trg}

    def on_train_epoch_end(self):
        # Access outputs saved during training_step if needed
        # In PyTorch Lightning v2.0+, we use on_train_epoch_end instead of training_epoch_end
        pass

    def on_validation_epoch_end(self):
        # Access outputs saved during validation_step if needed
        # In PyTorch Lightning v2.0+, we use on_validation_epoch_end instead of validation_epoch_end
        pass

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.args.lr, betas=(0.9, 0.98), eps=1e-09)
        
        #scheduler = get_linear_schedule_with_warmup(
        #    optimizer,
        #    num_warmup_steps=self.args.n_warmup,
        #    num_training_steps=self.trainer.estimated_stepping_batches,
        #)
        #scheduler = {"scheduler": scheduler, "interval": "step", "frequency": 1}
        #return [optimizer], [scheduler]
        return optimizer


class IsoFormerForLanguageModelingPL(LightningModule):
    """
    IsoFormer for causal language modeling tasks.
    Supports GPT-2, Llama-3, and other decoder-only models.
    """
    def __init__(self, args, vocab_size, hidden_size, max_seq_length, num_layers, n_experts, use_eigen=False, random_features=True):
        super().__init__()

        self.save_hyperparameters(ignore=['args'])
        self.args = args
        
        self.decoder = IsoDecoder(vocab_size, hidden_size, max_seq_length, num_layers, n_experts, use_eigen, random_features=random_features)
        self.lm_head = nn.Linear(hidden_size, vocab_size)
        
        self.best_perplexity = float('inf')

    def forward(self, src, debug=False):
        """
        Forward pass for language modeling.
        
        Args:
            src: Input token IDs [batch_size, seq_len]
            debug: Return additional debug information
        
        Returns:
            logits: [batch_size, seq_len, vocab_size]
            recon_loss: Reconstruction loss from manifold preservation
        """
        if debug:
            hidden_state, recon_loss, all_expert_weights = self.decoder(src, encoder_out=None, output_expert_weights=True)
        else:
            hidden_state, recon_loss = self.decoder(src, encoder_out=None)

        # Project to vocabulary
        logits = self.lm_head(hidden_state)
        
        if debug:
            return logits, recon_loss, all_expert_weights
        else:
            return logits, recon_loss

    def training_step(self, batch, batch_idx):
        lambda_ = self.args.lambda_

        # For language modeling, input_ids and labels are typically the same
        # But shifted - input is tokens[:-1], target is tokens[1:]
        input_ids = batch['input_ids']
        
        # Get labels (next token prediction)
        if 'labels' in batch:
            labels = batch['labels']
        else:
            # Shift input for next-token prediction
            labels = input_ids.clone()
        
        # Forward pass
        logits, recon_loss = self(input_ids)
        
        # Calculate language modeling loss (cross-entropy)
        # Shift logits and labels for next-token prediction
        shift_logits = logits[..., :-1, :].contiguous()
        shift_labels = labels[..., 1:].contiguous()
        
        # Flatten for loss calculation
        loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
        lm_loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
        
        # Total loss includes reconstruction loss
        total_loss = lm_loss + lambda_ * recon_loss
        
        self.log("train_loss", total_loss, on_step=True, on_epoch=True, prog_bar=True, logger=True)
        self.log("train_lm_loss", lm_loss, on_step=True, on_epoch=True, prog_bar=False, logger=True)
        self.log("train_recon_loss", recon_loss, on_step=True, on_epoch=True, prog_bar=False, logger=True)

        return {'loss': total_loss}

    def validation_step(self, batch, batch_idx):
        input_ids = batch['input_ids']
        
        if 'labels' in batch:
            labels = batch['labels']
        else:
            labels = input_ids.clone()
        
        # Forward pass
        logits, recon_loss = self(input_ids)
        
        # Calculate language modeling loss
        shift_logits = logits[..., :-1, :].contiguous()
        shift_labels = labels[..., 1:].contiguous()
        
        loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
        lm_loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
        
        total_loss = lm_loss + self.args.lambda_ * recon_loss
        
        # Calculate perplexity
        perplexity = torch.exp(lm_loss)
        
        self.log("val_loss", total_loss, on_step=True, on_epoch=True, prog_bar=True, logger=True)
        self.log("val_lm_loss", lm_loss, on_step=True, on_epoch=True, prog_bar=False, logger=True)
        self.log("val_perplexity", perplexity, on_step=True, on_epoch=True, prog_bar=True, logger=True)
        
        return {"val_loss": total_loss, "perplexity": perplexity}

    def on_train_epoch_end(self):
        pass

    def on_validation_epoch_end(self):
        pass

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.args.lr, betas=(0.9, 0.98), eps=1e-09)
        return optimizer
    
    def generate(self, input_ids, max_length=50, temperature=1.0, top_k=50, top_p=0.95, do_sample=True):
        """
        Generate text autoregressively.
        
        Args:
            input_ids: Starting tokens [batch_size, seq_len]
            max_length: Maximum length to generate
            temperature: Sampling temperature (only used if do_sample=True)
            top_k: Top-k sampling parameter (only used if do_sample=True)
            top_p: Nucleus sampling parameter (only used if do_sample=True)
            do_sample: If True, use sampling; if False, use greedy decoding
        
        Returns:
            generated_ids: [batch_size, max_length]
        """
        self.eval()
        with torch.no_grad():
            for _ in range(max_length - input_ids.size(1)):
                logits, _ = self(input_ids)
                next_token_logits = logits[:, -1, :]
                
                if do_sample:
                    # Sampling mode with temperature, top-k, top-p
                    next_token_logits = next_token_logits / temperature
                    
                    # Apply top-k filtering
                    if top_k > 0:
                        indices_to_remove = next_token_logits < torch.topk(next_token_logits, top_k)[0][..., -1, None]
                        next_token_logits[indices_to_remove] = -float('Inf')
                    
                    # Apply top-p (nucleus) filtering
                    if top_p < 1.0:
                        sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                        sorted_indices_to_remove = cumulative_probs > top_p
                        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                        sorted_indices_to_remove[..., 0] = 0
                        indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                        next_token_logits[indices_to_remove] = -float('Inf')
                    
                    # Sample
                    probs = F.softmax(next_token_logits, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)
                else:
                    # Greedy decoding: select the token with highest probability
                    next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)
                
                # Append to sequence
                input_ids = torch.cat([input_ids, next_token], dim=-1)
        
        return input_ids
    
class TransJectForClassification:
    """
    TransJect model for classification tasks.
    
    Supports binary and multi-class classification with manifold-preserving transformers.
    Uses standard parameter naming conventions aligned with HuggingFace/PyTorch.
    
    Example:
        ```python
        from transject import TransJectForClassification, ClassificationConfig
        
        config = ClassificationConfig(
            num_labels=2,
            vocab_size=30522,
            num_layers=6,
            hidden_size=512,
            max_seq_length=128
        )
        
        model = TransJectForClassification(config)
        history = model.train(train_loader, val_loader, epochs=10)
        ```
    
    Args:
        config: ClassificationConfig with model architecture parameters
    """
    
    def __init__(self, config: ClassificationConfig):
        self.config = config
        self.model = None
        self.trainer = None
        
        # Detect classification type from num_labels
        if config.num_labels == 1:
            self.classification_type = 'regression'
        elif config.num_labels == 2:
            self.classification_type = 'binary'
        else:
            self.classification_type = 'multiclass'
        
        logger.info(f"Initialized TransJectForClassification ({self.classification_type})")
        logger.info(f"  num_labels: {config.num_labels}")
        logger.info(f"  vocab_size: {config.vocab_size}")
        logger.info(f"  num_layers: {config.num_layers}")
        logger.info(f"  hidden_size: {config.hidden_size}")
    
    def _create_model(self):
        """Create the internal PyTorch Lightning model."""
        # Create Args namespace for model compatibility
        class Args:
            def __init__(self, config, classification_type):
                self.lambda_ = config.lambda_
                self.lr = 2e-5  # Will be overridden by training config
                self.classification_type = classification_type
                self.metric = 'accuracy'  # Default metric
        
        args = Args(self.config, self.classification_type)
        
        # Create model
        self.model = IsoFormerForClassificationPL(
            args=args,
            vocab_size=self.config.vocab_size,
            hidden_size=self.config.hidden_size,
            max_seq_length=self.config.max_seq_length,
            num_layers=self.config.num_layers,
            n_experts=self.config.n_experts,
            n_out=self.config.num_labels,
            use_eigen=self.config.use_eigen,
            pooling=self.config.pooling,
            classification_type=self.classification_type,
            random_features=self.config.random_features
        )
        
        return self.model
    
    def train(
        self,
        train_loader,
        val_loader,
        epochs: int = 10,
        learning_rate: float = 2e-5,
        metric: str = 'accuracy',
        use_meta_learning: bool = False,
        auxiliary_loaders: Optional[List] = None,
        output_dir: str = './transject_outputs',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Train the classification model.
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Number of training epochs
            learning_rate: Learning rate
            metric: Evaluation metric ('accuracy', 'f1', 'matthews_correlation')
            use_meta_learning: Enable curriculum learning with auxiliary tasks
            auxiliary_loaders: List of (train_loader, val_loader) for auxiliary tasks
            output_dir: Directory for checkpoints and logs
            **kwargs: Additional training configuration parameters
        
        Returns:
            Training history dictionary
        """
        # Create training config
        training_config = TrainingConfig(
            epochs=epochs,
            learning_rate=learning_rate,
            output_dir=output_dir,
            **kwargs
        )
        
        # Create model if not exists
        if self.model is None:
            self._create_model()
        
        # Update Args with metric
        self.model.args.metric = metric
        
        # Create trainer
        self.trainer = TransJectTrainer(
            model=self.model,
            config=training_config,
            task_config=None  # Not needed anymore
        )
        
        # Add metric callback if specified
        if metric and metric != 'accuracy':
            metric_callback = MetricCallback(metric_names=[metric])
            if self.trainer.trainer.callbacks is None:
                self.trainer.trainer.callbacks = []
            self.trainer.trainer.callbacks.append(metric_callback)
        
        # Train
        if use_meta_learning and auxiliary_loaders:
            history = self.trainer.train_with_meta_learning(
                main_train_loader=train_loader,
                main_val_loader=val_loader,
                auxiliary_loaders=auxiliary_loaders
            )
        else:
            history = self.trainer.train(train_loader, val_loader)
        
        return history
    
    def evaluate(self, data_loader) -> Dict[str, float]:
        """
        Evaluate the model on a dataset.
        
        Args:
            data_loader: Data loader for evaluation
        
        Returns:
            Dictionary of evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        if self.trainer is None:
            raise ValueError("Trainer not initialized. Call train() first.")
        
        results = self.trainer.trainer.validate(self.model, data_loader)
        return results[0] if results else {}
    
    def predict(self, data_loader):
        """
        Generate predictions on a dataset.
        
        Args:
            data_loader: Data loader for prediction
        
        Returns:
            Predictions tensor
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        self.model.eval()
        predictions = []
        
        with torch.no_grad():
            for batch in data_loader:
                src = batch['input_ids']
                logits = self.model(src)
                
                if self.classification_type == 'binary':
                    preds = torch.sigmoid(logits)
                else:
                    preds = torch.softmax(logits, dim=-1)
                
                predictions.append(preds)
        
        return torch.cat(predictions, dim=0)
    
    def save(self, path: str):
        """Save model checkpoint."""
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'config': self.config.to_dict(),
            'classification_type': self.classification_type
        }, path)
        logger.info(f"Model saved to {path}")
    
    @classmethod
    def load(cls, path: str) -> 'TransJectForClassification':
        """Load model from checkpoint."""
        checkpoint = torch.load(path)
        config = ClassificationConfig.from_dict(checkpoint['config'])
        model = cls(config)
        model._create_model()
        model.model.load_state_dict(checkpoint['model_state_dict'])
        model.classification_type = checkpoint['classification_type']
        logger.info(f"Model loaded from {path}")
        return model


class TransJectDecoder:
    """
    TransJect decoder model for language modeling tasks.
    
    Supports causal language modeling with manifold-preserving transformers.
    Uses standard parameter naming conventions aligned with HuggingFace/PyTorch.
    
    Example:
        ```python
        from transject import TransJectDecoder, LMConfig
        
        config = LMConfig(
            vocab_size=50257,
            num_layers=6,
            hidden_size=512,
            max_seq_length=512
        )
        
        model = TransJectDecoder(config)
        history = model.train(train_loader, val_loader, epochs=10)
        ```
    
    Args:
        config: LMConfig with model architecture parameters
    """
    
    def __init__(self, config: LMConfig):
        self.config = config
        self.model = None
        self.trainer = None
        
        logger.info(f"Initialized TransJectDecoder")
        logger.info(f"  vocab_size: {config.vocab_size}")
        logger.info(f"  num_layers: {config.num_layers}")
        logger.info(f"  hidden_size: {config.hidden_size}")
        logger.info(f"  max_seq_length: {config.max_seq_length}")
    
    def _create_model(self):
        """Create the internal PyTorch Lightning model."""
        # Create Args namespace for model compatibility
        class Args:
            def __init__(self, config):
                self.lambda_ = config.lambda_
                self.lr = 5e-5  # Will be overridden by training config
                self.metric = 'perplexity'
        
        args = Args(self.config)
        
        # Create model
        self.model = IsoFormerForLanguageModelingPL(
            args=args,
            vocab_size=self.config.vocab_size,
            hidden_size=self.config.hidden_size,
            max_seq_length=self.config.max_seq_length,
            num_layers=self.config.num_layers,
            n_experts=self.config.n_experts,
            use_eigen=self.config.use_eigen,
            random_features=self.config.random_features
        )
        
        return self.model
    
    def train(
        self,
        train_loader,
        val_loader,
        epochs: int = 10,
        learning_rate: float = 5e-5,
        use_meta_learning: bool = False,
        auxiliary_loaders: Optional[List] = None,
        output_dir: str = './transject_outputs',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Train the language modeling model.
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Number of training epochs
            learning_rate: Learning rate
            use_meta_learning: Enable curriculum learning with auxiliary tasks
            auxiliary_loaders: List of (train_loader, val_loader) for auxiliary tasks
            output_dir: Directory for checkpoints and logs
            **kwargs: Additional training configuration parameters
        
        Returns:
            Training history dictionary
        """
        # Create training config
        training_config = TrainingConfig(
            epochs=epochs,
            learning_rate=learning_rate,
            output_dir=output_dir,
            **kwargs
        )
        
        # Create model if not exists
        if self.model is None:
            self._create_model()
        
        # Create trainer
        self.trainer = TransJectTrainer(
            model=self.model,
            config=training_config,
            task_config=None  # Not needed anymore
        )
        
        # Train
        if use_meta_learning and auxiliary_loaders:
            history = self.trainer.train_with_meta_learning(
                main_train_loader=train_loader,
                main_val_loader=val_loader,
                auxiliary_loaders=auxiliary_loaders
            )
        else:
            history = self.trainer.train(train_loader, val_loader)
        
        return history
    
    def evaluate(self, data_loader) -> Dict[str, float]:
        """
        Evaluate the model on a dataset.
        
        Args:
            data_loader: Data loader for evaluation
        
        Returns:
            Dictionary of evaluation metrics (perplexity, loss)
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        if self.trainer is None:
            raise ValueError("Trainer not initialized. Call train() first.")
        
        results = self.trainer.trainer.validate(self.model, data_loader)
        return results[0] if results else {}
    
    def generate(
        self,
        input_ids: torch.Tensor,
        max_length: int = 50,
        temperature: float = 1.0,
        top_k: int = 50,
        top_p: float = 0.95,
        do_sample: bool = True,
        num_return_sequences: int = 1
    ) -> torch.Tensor:
        """
        Generate text using the language model.
        
        Args:
            input_ids: Input token IDs [batch_size, seq_len]
            max_length: Maximum generation length
            temperature: Sampling temperature (only used if do_sample=True)
            top_k: Top-k sampling parameter (only used if do_sample=True)
            top_p: Nucleus sampling parameter (only used if do_sample=True)
            do_sample: If True, use sampling; if False, use greedy decoding
            num_return_sequences: Number of sequences to generate per input (currently only supports 1)
        
        Returns:
            Generated token IDs [batch_size, generated_len]
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        if num_return_sequences != 1:
            raise NotImplementedError("num_return_sequences > 1 is not yet supported")
        
        return self.model.generate(
            input_ids=input_ids,
            max_length=max_length,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            do_sample=do_sample
        )
    
    def decode(
        self,
        input_text: str,
        tokenizer,
        max_length: int = 50,
        do_sample: bool = False,
        **kwargs
    ) -> str:
        """
        Generate text from a text prompt (convenience method).
        
        Args:
            input_text: Input text prompt
            tokenizer: HuggingFace tokenizer
            max_length: Maximum generation length
            do_sample: If True, use sampling; if False, use greedy decoding (default)
            **kwargs: Additional generation parameters (temperature, top_k, top_p)
        
        Returns:
            Generated text string
        
        Example:
            >>> from transformers import AutoTokenizer
            >>> tokenizer = AutoTokenizer.from_pretrained('gpt2')
            >>> text = model.decode("Once upon a time", tokenizer, max_length=50)
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        # Tokenize input
        input_ids = tokenizer(input_text, return_tensors='pt')['input_ids']
        
        # Move to same device as model
        device = next(self.model.parameters()).device
        input_ids = input_ids.to(device)
        
        # Generate
        output_ids = self.generate(
            input_ids=input_ids,
            max_length=max_length,
            do_sample=do_sample,
            **kwargs
        )
        
        # Decode to text
        generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return generated_text
    
    def save(self, path: str):
        """Save model checkpoint."""
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'config': self.config.to_dict()
        }, path)
        logger.info(f"Model saved to {path}")
    
    @classmethod
    def load(cls, path: str) -> 'TransJectDecoder':
        """Load model from checkpoint."""
        checkpoint = torch.load(path)
        config = LMConfig.from_dict(checkpoint['config'])
        model = cls(config)
        model._create_model()
        model.model.load_state_dict(checkpoint['model_state_dict'])
        logger.info(f"Model loaded from {path}")
        return model
