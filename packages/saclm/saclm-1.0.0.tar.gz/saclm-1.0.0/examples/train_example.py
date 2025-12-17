#!/usr/bin/env python3
"""
SCLM Training Example with Knowledge Distillation
==================================================

This script demonstrates how to train an SCLM model using:
1. Knowledge distillation from GPT-2-Large
2. Custom text dataset
3. Comprehensive evaluation

Requirements:
    pip install sclm transformers datasets

Run with: python train_example.py
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sclm import SCLM, SCLMConfig


# =============================================================================
# CONFIGURATION
# =============================================================================

class TrainingConfig:
    # Model
    vocab_size = 50257
    max_seq_length = 64
    n_layers = 6
    n_heads = 8
    d_model = 512
    
    # Training
    batch_size = 8
    learning_rate = 1e-4
    weight_decay = 0.01
    epochs = 3
    grad_clip = 1.0
    
    # Distillation
    temperature = 2.0
    distill_weight = 0.5
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# =============================================================================
# DATASET
# =============================================================================

class TextDataset(Dataset):
    """Simple text dataset for demonstration."""
    
    def __init__(self, tokenizer, max_length: int, n_samples: int = 1000):
        self.examples = []
        
        # Sample texts (in real use, load from file)
        texts = [
            "The wizard Elara lived in Silverwood with her cat Nimbus.",
            "Captain Chen commanded the starship Horizon through unknown space.",
            "The blacksmith Arthur forged a sword of blue steel.",
            "Machine learning models process data through neural networks.",
            "The old mansion stood at the end of the winding path.",
        ]
        
        # Tokenize and create chunks
        all_tokens = []
        for text in texts * (n_samples // len(texts)):
            all_tokens.extend(tokenizer.encode(text))
        
        # Create chunks
        for i in range(0, len(all_tokens) - max_length, max_length // 2):
            chunk = all_tokens[i:i + max_length + 1]
            if len(chunk) == max_length + 1:
                self.examples.append(torch.tensor(chunk))
        
        print(f"Created {len(self.examples)} training examples")
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        chunk = self.examples[idx]
        return chunk[:-1], chunk[1:]


# =============================================================================
# TRAINING FUNCTIONS
# =============================================================================

def train_epoch(
    student: SCLM,
    teacher: nn.Module,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler._LRScheduler,
    config: TrainingConfig
) -> dict:
    """Train for one epoch with knowledge distillation."""
    
    student.train()
    total_loss = 0
    total_lm_loss = 0
    total_distill_loss = 0
    n_batches = 0
    
    T = config.temperature
    alpha = config.distill_weight
    
    for batch_idx, (input_ids, labels) in enumerate(dataloader):
        input_ids = input_ids.to(config.device)
        labels = labels.to(config.device)
        
        # Reset state for each batch
        student.reset_state()
        optimizer.zero_grad()
        
        # Student forward
        student_out = student(input_ids, labels)
        lm_loss = student_out['loss']
        student_logits = student_out['logits']
        
        # Teacher forward (no grad)
        with torch.no_grad():
            teacher_out = teacher(input_ids)
            teacher_logits = teacher_out.logits
        
        # Distillation loss
        student_soft = F.log_softmax(student_logits / T, dim=-1)
        teacher_soft = F.softmax(teacher_logits / T, dim=-1)
        
        distill_loss = F.kl_div(
            student_soft[:, :-1].reshape(-1, student_logits.size(-1)),
            teacher_soft[:, :-1].reshape(-1, teacher_logits.size(-1)),
            reduction='batchmean'
        ) * (T ** 2)
        
        # Combined loss
        loss = (1 - alpha) * lm_loss + alpha * distill_loss
        
        # Backward
        loss.backward()
        nn.utils.clip_grad_norm_(student.parameters(), config.grad_clip)
        optimizer.step()
        scheduler.step()
        
        total_loss += loss.item()
        total_lm_loss += lm_loss.item()
        total_distill_loss += distill_loss.item()
        n_batches += 1
        
        if batch_idx % 10 == 0:
            coh = student_out['global_metrics']['coherence']
            print(f"  Batch {batch_idx}: loss={loss.item():.4f}, coh={coh:.4f}")
    
    return {
        'loss': total_loss / n_batches,
        'lm_loss': total_lm_loss / n_batches,
        'distill_loss': total_distill_loss / n_batches,
    }


def evaluate(
    model: SCLM,
    dataloader: DataLoader,
    config: TrainingConfig
) -> dict:
    """Evaluate model."""
    
    model.eval()
    total_loss = 0
    total_coherence = 0
    n_batches = 0
    
    with torch.no_grad():
        for input_ids, labels in dataloader:
            input_ids = input_ids.to(config.device)
            labels = labels.to(config.device)
            
            model.reset_state()
            out = model(input_ids, labels)
            
            total_loss += out['loss'].item()
            total_coherence += out['global_metrics']['coherence'].item()
            n_batches += 1
    
    avg_loss = total_loss / n_batches
    return {
        'loss': avg_loss,
        'perplexity': math.exp(avg_loss),
        'coherence': total_coherence / n_batches,
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("  SCLM Training with Knowledge Distillation")
    print("=" * 60)
    
    config = TrainingConfig()
    print(f"\n🔧 Device: {config.device}")
    
    # Load tokenizer
    print("\n📚 Loading tokenizer...")
    try:
        from transformers import GPT2Tokenizer, GPT2LMHeadModel
        tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        tokenizer.pad_token = tokenizer.eos_token
    except ImportError:
        print("❌ transformers not installed. Run: pip install transformers")
        return
    
    # Create dataset
    print("\n📊 Creating dataset...")
    dataset = TextDataset(tokenizer, config.max_seq_length, n_samples=500)
    
    train_size = int(0.9 * len(dataset))
    eval_size = len(dataset) - train_size
    train_data, eval_data = torch.utils.data.random_split(dataset, [train_size, eval_size])
    
    train_loader = DataLoader(train_data, batch_size=config.batch_size, shuffle=True)
    eval_loader = DataLoader(eval_data, batch_size=config.batch_size)
    
    print(f"   Train: {len(train_data)}, Eval: {len(eval_data)}")
    
    # Create student model
    print("\n🏗️ Creating SCLM student...")
    sclm_config = SCLMConfig(
        vocab_size=config.vocab_size,
        max_seq_length=config.max_seq_length,
        n_layers=config.n_layers,
        n_heads=config.n_heads,
        d_model=config.d_model,
    )
    student = SCLM(sclm_config).to(config.device)
    print(f"   Parameters: {student.get_num_params():,}")
    
    # Load teacher
    print("\n👨‍🏫 Loading GPT-2 teacher...")
    teacher = GPT2LMHeadModel.from_pretrained('gpt2').to(config.device)
    teacher.eval()
    for p in teacher.parameters():
        p.requires_grad = False
    print(f"   Parameters: {sum(p.numel() for p in teacher.parameters()):,}")
    
    # Optimizer
    optimizer = torch.optim.AdamW(
        student.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=len(train_loader) * config.epochs
    )
    
    # Training loop
    print("\n🏋️ Training...")
    print(f"   Epochs: {config.epochs}")
    print(f"   Batch size: {config.batch_size}")
    print(f"   Temperature: {config.temperature}")
    print(f"   Distillation weight: {config.distill_weight}")
    
    for epoch in range(config.epochs):
        print(f"\n📌 Epoch {epoch + 1}/{config.epochs}")
        
        # Train
        train_metrics = train_epoch(
            student, teacher, train_loader, optimizer, scheduler, config
        )
        
        # Evaluate
        eval_metrics = evaluate(student, eval_loader, config)
        
        print(f"   Train loss: {train_metrics['loss']:.4f}")
        print(f"   Eval loss: {eval_metrics['loss']:.4f}")
        print(f"   Perplexity: {eval_metrics['perplexity']:.2f}")
        print(f"   Coherence: {eval_metrics['coherence']:.4f}")
    
    # Final evaluation
    print("\n" + "=" * 60)
    print("  Final Results")
    print("=" * 60)
    
    final_metrics = evaluate(student, eval_loader, config)
    print(f"\n📊 Final Metrics:")
    print(f"   Loss: {final_metrics['loss']:.4f}")
    print(f"   Perplexity: {final_metrics['perplexity']:.2f}")
    print(f"   Coherence: {final_metrics['coherence']:.4f}")
    
    # Save model
    print("\n💾 Saving model...")
    torch.save({
        'model_state_dict': student.state_dict(),
        'config': sclm_config,
        'metrics': final_metrics,
    }, 'sclm_trained.pt')
    print("   Saved to: sclm_trained.pt")
    
    print("\n✅ Training complete!")


if __name__ == "__main__":
    main()
