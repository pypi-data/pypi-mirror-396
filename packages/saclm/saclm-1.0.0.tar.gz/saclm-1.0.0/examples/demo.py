#!/usr/bin/env python3
"""
SCLM Demonstration Script
=========================

This script demonstrates the key features of the Stateful Coherent Language Model (SCLM):

1. Basic Model Creation
2. Forward Pass & Metrics
3. Text Generation
4. Edit Mode (Local Editing)
5. State Persistence Test
6. Knowledge Distillation Setup

Run with: python demo.py
"""

import torch
import torch.nn.functional as F
import numpy as np
import sys
import os

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sclm import SCLM, SCLMConfig, create_sclm_small


def print_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_1_model_creation():
    """Demo 1: Create an SCLM model."""
    print_header("DEMO 1: Model Creation")
    
    # Method 1: Full configuration
    config = SCLMConfig(
        vocab_size=50257,
        max_seq_length=256,
        n_layers=6,
        n_heads=8,
        d_model=512,
        d_ff=2048,
        latent_state_dim=256,
        n_experts=4,
    )
    model = SCLM(config)
    
    print(f"✅ Created SCLM model")
    print(f"   Layers: {config.n_layers}")
    print(f"   Heads: {config.n_heads}")
    print(f"   Model dim: {config.d_model}")
    print(f"   State dim: {config.latent_state_dim}")
    print(f"   Experts: {config.n_experts}")
    print(f"   Parameters: {model.get_num_params():,}")
    
    # Method 2: Pre-built model
    model_small = create_sclm_small()
    print(f"\n✅ Pre-built small model: {model_small.get_num_params():,} params")
    
    return model


def demo_2_forward_pass(model: SCLM):
    """Demo 2: Forward pass and metrics."""
    print_header("DEMO 2: Forward Pass & Metrics")
    
    device = next(model.parameters()).device
    
    # Create dummy input
    batch_size, seq_len = 2, 64
    input_ids = torch.randint(0, model.config.vocab_size, (batch_size, seq_len), device=device)
    labels = input_ids.clone()
    
    # Reset state before processing
    model.reset_state()
    
    # Forward pass
    output = model(input_ids, labels=labels)
    
    print(f"✅ Forward pass complete")
    print(f"   Input shape: {input_ids.shape}")
    print(f"   Logits shape: {output['logits'].shape}")
    print(f"   Loss: {output['loss'].item():.4f}")
    
    # Global metrics
    if output['global_metrics']:
        gm = output['global_metrics']
        print(f"\n📊 Global EARCP Metrics:")
        print(f"   Coherence: {gm['coherence']:.4f}")
        print(f"   Alignment: {gm['alignment'].mean().item():.4f}")
        print(f"   Drift: {gm['drift'].mean().item():.4f}")
        print(f"   State Norm: {gm['state_norm']:.4f}")
        print(f"   Expert Weights: {gm['weights'].tolist()}")
    
    # Block metrics
    print(f"\n📊 Block Metrics (EARCP blocks only):")
    for i, bm in enumerate(output['block_metrics']):
        print(f"   Block {i}: coherence={bm['coherence']:.4f}, alignment={bm['alignment'].mean().item():.4f}")
    
    return output


def demo_3_text_generation(model: SCLM):
    """Demo 3: Text generation."""
    print_header("DEMO 3: Text Generation")
    
    device = next(model.parameters()).device
    
    # Simple prompt (random tokens for demo)
    prompt = torch.randint(0, 1000, (1, 10), device=device)
    
    print(f"📝 Generating text...")
    print(f"   Prompt length: {prompt.size(1)} tokens")
    
    # Reset state
    model.reset_state()
    
    # Generate
    generated = model.generate(
        prompt,
        max_new_tokens=30,
        temperature=0.8,
        top_k=50,
        repetition_penalty=1.2
    )
    
    print(f"✅ Generation complete")
    print(f"   Generated length: {generated.size(1)} tokens")
    print(f"   New tokens: {generated.size(1) - prompt.size(1)}")
    print(f"   Token IDs: {generated[0, :20].tolist()}...")
    
    return generated


def demo_4_edit_mode(model: SCLM):
    """Demo 4: Edit mode for local modifications."""
    print_header("DEMO 4: Edit Mode (Local Editing)")
    
    device = next(model.parameters()).device
    
    # Original text (simulated as token IDs)
    original = torch.randint(0, 1000, (1, 32), device=device)
    
    # Edited text (change a few tokens)
    edited = original.clone()
    edited[0, 15:18] = torch.randint(1000, 2000, (3,), device=device)  # Change 3 tokens
    
    print(f"📝 Original tokens: {original[0, 10:25].tolist()}")
    print(f"📝 Edited tokens:   {edited[0, 10:25].tolist()}")
    print(f"   (Tokens 15-17 changed)")
    
    # Step 1: Process original to build state
    model.reset_state()
    out_original = model(original)
    orig_coherence = out_original['global_metrics']['coherence'].item()
    orig_state_norm = out_original['global_metrics']['state_norm'].item()
    
    print(f"\n🔷 Original:")
    print(f"   Coherence: {orig_coherence:.4f}")
    print(f"   State Norm: {orig_state_norm:.4f}")
    
    # Step 2: Freeze state
    model.freeze_state()
    print(f"\n❄️  State frozen")
    
    # Step 3: Process edited with edit_mode=True
    out_edited = model(edited, edit_mode=True)
    edit_coherence = out_edited['global_metrics']['coherence'].item()
    edit_state_norm = out_edited['global_metrics']['state_norm'].item()
    
    print(f"\n🔶 After Edit (with frozen state):")
    print(f"   Coherence: {edit_coherence:.4f}")
    print(f"   State Norm: {edit_state_norm:.4f}")
    
    # Calculate changes
    coh_change = abs(edit_coherence - orig_coherence) / max(orig_coherence, 0.001) * 100
    norm_change = abs(edit_state_norm - orig_state_norm) / max(orig_state_norm, 0.001) * 100
    
    print(f"\n📊 Changes:")
    print(f"   Coherence Δ: {coh_change:.2f}%")
    print(f"   State Norm Δ: {norm_change:.2f}%")
    
    # Step 4: Unfreeze
    model.unfreeze_state()
    print(f"\n🔓 State unfrozen")
    
    # Verdict
    if coh_change < 30:
        print(f"\n✅ Edit Mode SUCCESS - Coherence preserved!")
    else:
        print(f"\n⚠️  Coherence drift detected")
    
    return {'coh_change': coh_change, 'norm_change': norm_change}


def demo_5_state_persistence(model: SCLM):
    """Demo 5: Test state persistence across multiple steps."""
    print_header("DEMO 5: State Persistence Test")
    
    device = next(model.parameters()).device
    
    # Fixed input
    input_ids = torch.randint(0, 1000, (1, 32), device=device)
    
    # Reset and run multiple times
    model.reset_state()
    
    state_norms = []
    coherences = []
    
    print(f"📊 Running 5 forward passes with same input...")
    
    with torch.no_grad():
        for step in range(5):
            out = model(input_ids)
            
            sn = out['global_metrics']['state_norm'].item()
            coh = out['global_metrics']['coherence'].item()
            
            state_norms.append(sn)
            coherences.append(coh)
            
            print(f"   Step {step+1}: state_norm={sn:.6f}, coherence={coh:.4f}")
    
    # Calculate variance
    variance = np.var(state_norms[-3:])
    
    print(f"\n📈 Results:")
    print(f"   State norm variance (last 3): {variance:.10f}")
    print(f"   Threshold: 1e-5")
    
    if variance < 1e-5:
        print(f"\n✅ State Persistence VERIFIED - Variance < 10⁻⁵")
    else:
        print(f"\n⚠️  State variance above threshold")
    
    return {'variance': variance, 'state_norms': state_norms, 'coherences': coherences}


def demo_6_knowledge_distillation_setup():
    """Demo 6: Setup for knowledge distillation (no actual training)."""
    print_header("DEMO 6: Knowledge Distillation Setup")
    
    print("📚 Knowledge Distillation from GPT-2-Large")
    print("\nCode example:")
    print("-" * 50)
    
    code = '''
from transformers import GPT2LMHeadModel
from sclm import SCLM, SCLMConfig
import torch.nn.functional as F

# Teacher (pre-trained)
teacher = GPT2LMHeadModel.from_pretrained('gpt2-large')
teacher.eval()
for p in teacher.parameters():
    p.requires_grad = False

# Student (SCLM)
config = SCLMConfig(vocab_size=50257, n_layers=6, d_model=512)
student = SCLM(config)

# Distillation parameters
T = 2.0      # Temperature
alpha = 0.5  # Distillation weight

# Training step
def train_step(input_ids, labels):
    student.reset_state()
    
    # Student forward
    out = student(input_ids, labels)
    lm_loss = out['loss']
    
    # Teacher forward
    with torch.no_grad():
        teacher_logits = teacher(input_ids).logits
    
    # Soft targets
    student_soft = F.log_softmax(out['logits'] / T, dim=-1)
    teacher_soft = F.softmax(teacher_logits / T, dim=-1)
    
    # KL divergence
    distill_loss = F.kl_div(
        student_soft[:, :-1].reshape(-1, student_soft.size(-1)),
        teacher_soft[:, :-1].reshape(-1, teacher_soft.size(-1)),
        reduction='batchmean'
    ) * (T ** 2)
    
    # Combined loss
    loss = (1 - alpha) * lm_loss + alpha * distill_loss
    return loss
'''
    print(code)
    print("-" * 50)
    print("\n✅ Distillation setup ready")


def run_all_demos():
    """Run all demonstrations."""
    print("\n" + "🧠 " * 20)
    print("\n   SCLM: Stateful Coherent Language Models")
    print("   Demonstration Script")
    print("\n" + "🧠 " * 20)
    
    # Check device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n🔧 Device: {device}")
    
    # Demo 1: Create model
    model = demo_1_model_creation()
    model = model.to(device)
    
    # Demo 2: Forward pass
    demo_2_forward_pass(model)
    
    # Demo 3: Generation
    demo_3_text_generation(model)
    
    # Demo 4: Edit mode
    demo_4_edit_mode(model)
    
    # Demo 5: State persistence
    demo_5_state_persistence(model)
    
    # Demo 6: Distillation setup
    demo_6_knowledge_distillation_setup()
    
    # Summary
    print_header("SUMMARY")
    print("""
✅ SCLM Features Demonstrated:
   1. Model creation with full configuration
   2. Forward pass with EARCP metrics
   3. Text generation with persistent state
   4. Edit mode for local modifications
   5. State persistence verification
   6. Knowledge distillation setup

📖 Next Steps:
   - Train on your dataset with distillation
   - Experiment with different configurations
   - Use edit mode for document editing tasks

📚 Documentation: https://github.com/Volgat/sclm
📄 Paper: arXiv:2512.XXXXX
    """)


if __name__ == "__main__":
    run_all_demos()
