"""
SCLM: Stateful Coherent Language Models
========================================

A PyTorch library for building language models with persistent latent state
and multi-expert coherence mechanisms.

Author: Mike Amega
License: Proprietary (See LICENSE)
Repository: https://github.com/Volgat/sclm

Installation:
    pip install saclm

Quick Start:
    from sclm import SCLM, SCLMConfig
    
    config = SCLMConfig(vocab_size=50257)
    model = SCLM(config)
    
    # Forward pass
    output = model(input_ids)
    
    # Generation with persistent state
    generated = model.generate(prompt_ids, max_new_tokens=100)
    
    # Edit mode
    model.freeze_state()
    output = model(edited_ids, edit_mode=True)
    model.unfreeze_state()
"""

__version__ = "1.0.0"
__author__ = "Mike Amega"
__license__ = "MIT"

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class SCLMConfig:
    """
    Configuration class for SCLM (Stateful Coherent Language Model).
    
    Args:
        vocab_size: Size of the vocabulary
        max_seq_length: Maximum sequence length
        n_layers: Number of transformer layers
        n_heads: Number of attention heads
        d_model: Model dimension
        d_ff: Feed-forward dimension
        dropout: Dropout probability
        latent_state_dim: Dimension of the persistent latent state
        n_coherence_heads: Number of heads for coherence attention
        n_experts: Number of experts in coherence module
        propagation_depth: Number of propagation adapters
        alpha_P: Performance EMA coefficient (EARCP)
        alpha_C: Coherence EMA coefficient (EARCP)
        beta: Performance-coherence balance (EARCP)
        eta_s: Coherence sensitivity parameter
        w_min: Minimum expert weight floor
        
    Example:
        >>> config = SCLMConfig(vocab_size=50257, d_model=768, n_layers=12)
        >>> print(config)
    """
    # Model architecture
    vocab_size: int = 50257
    max_seq_length: int = 512
    n_layers: int = 6
    n_heads: int = 8
    d_model: int = 512
    d_ff: int = 2048
    dropout: float = 0.1
    
    # SCLM-specific parameters
    latent_state_dim: int = 256
    n_coherence_heads: int = 4
    n_experts: int = 4
    propagation_depth: int = 3
    
    # EARCP parameters
    alpha_P: float = 0.9
    alpha_C: float = 0.85
    beta: float = 0.7
    eta_s: float = 5.0
    w_min: float = 0.05
    
    # Which layers get EARCP
    earcp_every_n_layers: int = 2
    use_global_earcp: bool = True
    
    def __post_init__(self):
        assert self.d_model % self.n_heads == 0, "d_model must be divisible by n_heads"
        assert self.d_model % self.n_coherence_heads == 0, "d_model must be divisible by n_coherence_heads"


# =============================================================================
# EARCP MODULES
# =============================================================================

class EncapsulationModule(nn.Module):
    """
    E - Encapsulation: Creates and updates the persistent latent state.
    
    Uses GRU-style gating to maintain stable state across time steps.
    
    Mathematical formulation:
        z_t = σ(W_z[h̄; s_{t-1}] + b_z)           # update gate
        r_t = σ(W_r[h̄; s_{t-1}] + b_r)           # reset gate  
        s̃_t = tanh(W_s[h̄; r_t ⊙ s_{t-1}] + b_s)  # candidate
        s_t = (1 - z_t) ⊙ s_{t-1} + z_t ⊙ s̃_t    # new state
    """
    
    def __init__(self, config: SCLMConfig):
        super().__init__()
        self.config = config
        
        combined_dim = config.d_model + config.latent_state_dim
        
        self.state_encoder = nn.Sequential(
            nn.Linear(combined_dim, config.d_model),
            nn.LayerNorm(config.d_model),
            nn.GELU(),
            nn.Linear(config.d_model, config.latent_state_dim),
        )
        
        self.update_gate = nn.Linear(combined_dim, config.latent_state_dim)
        self.reset_gate = nn.Linear(combined_dim, config.latent_state_dim)
        self.state_norm = nn.LayerNorm(config.latent_state_dim)
        
    def forward(
        self, 
        hidden: torch.Tensor, 
        prev_state: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Args:
            hidden: Hidden states [batch, seq_len, d_model]
            prev_state: Previous latent state [batch, latent_state_dim]
            
        Returns:
            new_state: Updated latent state [batch, latent_state_dim]
        """
        batch_size = hidden.size(0)
        
        if prev_state is None:
            prev_state = torch.zeros(
                batch_size, self.config.latent_state_dim, 
                device=hidden.device, dtype=hidden.dtype
            )
        
        # Pool hidden states
        pooled = hidden.mean(dim=1)  # [batch, d_model]
        
        # Combine with previous state
        combined = torch.cat([pooled, prev_state], dim=-1)
        
        # Gating
        update = torch.sigmoid(self.update_gate(combined))
        reset = torch.sigmoid(self.reset_gate(combined))
        
        # Candidate state
        reset_state = reset * prev_state
        combined_reset = torch.cat([pooled, reset_state], dim=-1)
        candidate = torch.tanh(self.state_encoder(combined_reset))
        
        # New state
        new_state = (1 - update) * prev_state + update * candidate
        
        return self.state_norm(new_state)


class AlignmentModule(nn.Module):
    """
    A - Alignment: Measures and enforces hidden-state consistency.
    
    Uses cross-attention between hidden states and latent state,
    producing an alignment score in [0, 1].
    """
    
    def __init__(self, config: SCLMConfig):
        super().__init__()
        self.n_heads = config.n_coherence_heads
        self.head_dim = config.d_model // self.n_heads
        
        self.query = nn.Linear(config.d_model, config.d_model)
        self.key = nn.Linear(config.latent_state_dim, config.d_model)
        self.value = nn.Linear(config.latent_state_dim, config.d_model)
        self.output = nn.Linear(config.d_model, config.d_model)
        
        self.alignment_scorer = nn.Sequential(
            nn.Linear(config.d_model * 2, config.d_model),
            nn.GELU(),
            nn.Linear(config.d_model, 1),
            nn.Sigmoid()
        )
        
        self.norm = nn.LayerNorm(config.d_model)
        self.dropout = nn.Dropout(config.dropout)
        
    def forward(
        self, 
        hidden: torch.Tensor, 
        state: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            hidden: Hidden states [batch, seq_len, d_model]
            state: Latent state [batch, latent_state_dim]
            
        Returns:
            aligned_hidden: State-aligned hidden [batch, seq_len, d_model]
            alignment_score: Alignment score [batch]
        """
        B, T, _ = hidden.size()
        state_expanded = state.unsqueeze(1)  # [batch, 1, latent_state_dim]
        
        # Multi-head cross-attention
        Q = self.query(hidden).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        K = self.key(state_expanded).view(B, 1, self.n_heads, self.head_dim).transpose(1, 2)
        V = self.value(state_expanded).view(B, 1, self.n_heads, self.head_dim).transpose(1, 2)
        
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.head_dim)
        attn = self.dropout(F.softmax(scores, dim=-1))
        
        aligned = torch.matmul(attn, V).transpose(1, 2).contiguous().view(B, T, -1)
        aligned = self.output(aligned)
        
        # Residual connection
        aligned_hidden = self.norm(hidden + aligned)
        
        # Compute alignment score
        score_input = torch.cat([hidden.mean(1), aligned.mean(1)], dim=-1)
        alignment_score = self.alignment_scorer(score_input).squeeze(-1)
        
        return aligned_hidden, alignment_score


class RevisionModule(nn.Module):
    """
    R - Revision: Detects and corrects semantic drift.
    
    Applies state-guided corrections when drift is detected
    and alignment is low.
    """
    
    def __init__(self, config: SCLMConfig):
        super().__init__()
        
        self.drift_detector = nn.Sequential(
            nn.Linear(config.d_model + config.latent_state_dim, config.d_model),
            nn.GELU(),
            nn.Linear(config.d_model, 1),
            nn.Sigmoid()
        )
        
        self.correction = nn.Sequential(
            nn.Linear(config.latent_state_dim, config.d_model),
            nn.LayerNorm(config.d_model),
            nn.GELU(),
            nn.Linear(config.d_model, config.d_model),
        )
        
        self.gate = nn.Sequential(
            nn.Linear(config.d_model * 2, config.d_model),
            nn.Sigmoid()
        )
        
        self.norm = nn.LayerNorm(config.d_model)
        
    def forward(
        self, 
        hidden: torch.Tensor, 
        state: torch.Tensor, 
        alignment_score: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            hidden: Hidden states [batch, seq_len, d_model]
            state: Latent state [batch, latent_state_dim]
            alignment_score: Alignment score [batch]
            
        Returns:
            revised_hidden: Drift-corrected hidden [batch, seq_len, d_model]
            drift_score: Detected drift [batch]
        """
        B, T, D = hidden.size()
        
        # Detect drift
        pooled = hidden.mean(dim=1)
        drift_input = torch.cat([pooled, state], dim=-1)
        drift = self.drift_detector(drift_input).squeeze(-1)
        
        # Compute correction
        correction = self.correction(state).unsqueeze(1).expand(-1, T, -1)
        gate = self.gate(torch.cat([hidden, correction], dim=-1))
        
        # Apply correction proportional to drift and misalignment
        strength = (drift * (1 - alignment_score)).view(B, 1, 1).expand(-1, T, D)
        revised = hidden + strength * gate * correction
        
        return self.norm(revised), drift


class CoherenceModule(nn.Module):
    """
    C - Coherence: Multi-expert processing with coherence-based weighting.
    
    Experts that produce outputs similar to other experts receive
    higher weights, promoting coherent representations.
    """
    
    def __init__(self, config: SCLMConfig):
        super().__init__()
        self.config = config
        self.n_experts = config.n_experts
        
        # Expert networks
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(config.d_model, config.d_model),
                nn.GELU(),
                nn.Linear(config.d_model, config.d_model)
            ) for _ in range(self.n_experts)
        ])
        
        # Coherence attention
        self.coherence_attn = nn.MultiheadAttention(
            config.d_model, config.n_coherence_heads,
            dropout=config.dropout, batch_first=True
        )
        
        self.eta_s = config.eta_s
        self.w_min = config.w_min
        
        self.output = nn.Linear(config.d_model, config.d_model)
        self.norm = nn.LayerNorm(config.d_model)
        
        # Store weights for inspection
        self.last_weights = None
    
    def compute_coherence(
        self, 
        expert_outputs: List[torch.Tensor]
    ) -> torch.Tensor:
        """Compute pairwise coherence between experts."""
        scores = []
        for i in range(self.n_experts):
            sims = []
            for j in range(self.n_experts):
                if i != j:
                    sim = F.cosine_similarity(
                        expert_outputs[i].mean(1).detach(),
                        expert_outputs[j].mean(1).detach(),
                        dim=-1
                    )
                    sims.append(sim)
            scores.append(torch.stack(sims, -1).mean(-1))
        return torch.stack(scores, -1)
    
    def compute_weights(
        self, 
        coherence: torch.Tensor, 
        device: torch.device
    ) -> torch.Tensor:
        """Compute expert weights from coherence scores."""
        with torch.no_grad():
            batch_coh = coherence.mean(0)
            c_min, c_max = batch_coh.min(), batch_coh.max()
            
            if c_max - c_min > 1e-8:
                c_norm = (batch_coh - c_min) / (c_max - c_min)
            else:
                c_norm = torch.ones_like(batch_coh) * 0.5
            
            # Softmax with sensitivity
            weights = torch.exp(self.eta_s * torch.clamp(c_norm, -10, 10))
            weights = weights / weights.sum()
            
            # Apply floor
            weights = torch.maximum(weights, torch.tensor(self.w_min, device=device))
            weights = weights / weights.sum()
            
        return weights
        
    def forward(
        self, 
        hidden: torch.Tensor, 
        state: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Args:
            hidden: Hidden states [batch, seq_len, d_model]
            state: Latent state [batch, latent_state_dim]
            
        Returns:
            coherent_hidden: Coherence-processed hidden [batch, seq_len, d_model]
            coherence_score: Mean coherence [scalar]
            expert_weights: Expert weights [n_experts]
        """
        device = hidden.device
        
        # Expert outputs
        expert_outputs = [expert(hidden) for expert in self.experts]
        
        # Compute coherence and weights
        coherence = self.compute_coherence(expert_outputs)
        weights = self.compute_weights(coherence, device)
        self.last_weights = weights.detach()
        
        # Weighted combination
        w = weights.view(1, 1, 1, -1)
        stacked = torch.stack(expert_outputs, -1)
        weighted = (stacked * w).sum(-1)
        
        # Self-attention for coherence
        coherent, _ = self.coherence_attn(weighted, weighted, weighted)
        coherent = self.output(coherent)
        
        return self.norm(hidden + coherent), coherence.mean().detach(), weights.detach()


class PropagationModule(nn.Module):
    """
    P - Propagation: Injects state information into deeper layers.
    
    Uses cross-attention and layer-specific adapters to propagate
    state influence throughout the network.
    """
    
    def __init__(self, config: SCLMConfig):
        super().__init__()
        
        self.state_proj = nn.Linear(config.latent_state_dim, config.d_model)
        
        self.cross_attn = nn.MultiheadAttention(
            config.d_model, config.n_coherence_heads,
            dropout=config.dropout, batch_first=True
        )
        
        self.gate = nn.Sequential(
            nn.Linear(config.d_model * 2, config.d_model),
            nn.Sigmoid()
        )
        
        self.adapters = nn.ModuleList([
            nn.Linear(config.d_model, config.d_model)
            for _ in range(config.propagation_depth)
        ])
        
        self.norm = nn.LayerNorm(config.d_model)
        
    def forward(
        self, 
        hidden: torch.Tensor, 
        state: torch.Tensor, 
        layer_idx: int = 0
    ) -> torch.Tensor:
        """
        Args:
            hidden: Hidden states [batch, seq_len, d_model]
            state: Latent state [batch, latent_state_dim]
            layer_idx: Current layer index
            
        Returns:
            propagated_hidden: State-propagated hidden [batch, seq_len, d_model]
        """
        state_proj = self.state_proj(state).unsqueeze(1)
        
        attended, _ = self.cross_attn(hidden, state_proj, state_proj)
        gate = self.gate(torch.cat([hidden, attended], -1))
        
        adapter_idx = min(layer_idx, len(self.adapters) - 1)
        adapted = self.adapters[adapter_idx](attended)
        
        return self.norm(hidden + gate * adapted)


# =============================================================================
# EARCP LAYER
# =============================================================================

class EARCPLayer(nn.Module):
    """
    Complete EARCP Pipeline: Encapsulation → Alignment → Revision → Coherence → Propagation
    
    This is the core innovation of SCLM, providing:
    - Persistent latent state via Encapsulation
    - State-hidden consistency via Alignment
    - Drift correction via Revision
    - Multi-expert coherence via Coherence
    - Cross-layer state influence via Propagation
    
    Example:
        >>> layer = EARCPLayer(config)
        >>> output, metrics = layer(hidden_states, layer_idx=0)
        >>> print(metrics['coherence'], metrics['state_norm'])
    """
    
    def __init__(self, config: SCLMConfig):
        super().__init__()
        
        self.encapsulation = EncapsulationModule(config)
        self.alignment = AlignmentModule(config)
        self.revision = RevisionModule(config)
        self.coherence = CoherenceModule(config)
        self.propagation = PropagationModule(config)
        
        self._state: Optional[torch.Tensor] = None
        self._frozen_state: Optional[torch.Tensor] = None
        
    def reset_state(self) -> None:
        """Reset the persistent state to None."""
        self._state = None
        self._frozen_state = None
    
    def freeze_state(self) -> bool:
        """Freeze current state for edit mode. Returns True if successful."""
        if self._state is not None:
            self._frozen_state = self._state.detach().clone()
            return True
        return False
    
    def unfreeze_state(self) -> None:
        """Unfreeze state, returning to normal mode."""
        self._frozen_state = None
    
    def get_state(self) -> Optional[torch.Tensor]:
        """Get the current latent state."""
        return self._state
    
    def set_state(self, state: torch.Tensor) -> None:
        """Manually set the latent state."""
        self._state = state.detach().clone()
        
    def forward(
        self, 
        hidden: torch.Tensor, 
        layer_idx: int = 0, 
        edit_mode: bool = False
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Forward pass through the EARCP pipeline.
        
        Args:
            hidden: Hidden states [batch, seq_len, d_model]
            layer_idx: Current transformer layer index
            edit_mode: If True, use frozen state instead of updating
            
        Returns:
            output: Processed hidden states [batch, seq_len, d_model]
            metrics: Dictionary containing:
                - alignment: Alignment score [batch]
                - drift: Drift score [batch]
                - coherence: Mean coherence score [scalar]
                - weights: Expert weights [n_experts]
                - state_norm: State norm [scalar]
        """
        batch_size = hidden.size(0)
        
        # Determine previous state
        if edit_mode and self._frozen_state is not None:
            prev_state = self._frozen_state
            if prev_state.size(0) != batch_size:
                prev_state = prev_state.expand(batch_size, -1)
        elif self._state is not None and self._state.size(0) == batch_size:
            prev_state = self._state.detach()
        else:
            prev_state = None
        
        # E - Encapsulation
        state = self.encapsulation(hidden, prev_state)
        
        # Store state (unless in edit mode)
        if not edit_mode:
            self._state = state.detach().clone()
        
        # A - Alignment
        aligned, alignment_score = self.alignment(hidden, state)
        
        # R - Revision
        revised, drift_score = self.revision(aligned, state, alignment_score)
        
        # C - Coherence
        coherent, coherence_score, weights = self.coherence(revised, state)
        
        # P - Propagation
        output = self.propagation(coherent, state, layer_idx)
        
        metrics = {
            'alignment': alignment_score.detach(),
            'drift': drift_score.detach(),
            'coherence': coherence_score,
            'weights': weights,
            'state_norm': state.norm(dim=-1).mean().detach()
        }
        
        return output, metrics


# =============================================================================
# TRANSFORMER COMPONENTS
# =============================================================================

class MultiHeadAttention(nn.Module):
    """Standard multi-head self-attention."""
    
    def __init__(self, config: SCLMConfig):
        super().__init__()
        self.n_heads = config.n_heads
        self.head_dim = config.d_model // config.n_heads
        
        self.qkv = nn.Linear(config.d_model, 3 * config.d_model)
        self.out = nn.Linear(config.d_model, config.d_model)
        self.dropout = nn.Dropout(config.dropout)
        
    def forward(
        self, 
        x: torch.Tensor, 
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        B, T, _ = x.size()
        
        qkv = self.qkv(x).reshape(B, T, 3, self.n_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)
        Q, K, V = qkv[0], qkv[1], qkv[2]
        
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.head_dim)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        
        attn = self.dropout(F.softmax(scores, dim=-1))
        out = torch.matmul(attn, V).transpose(1, 2).reshape(B, T, -1)
        
        return self.out(out)


class TransformerBlock(nn.Module):
    """Transformer block with optional EARCP layer."""
    
    def __init__(self, config: SCLMConfig, layer_idx: int, use_earcp: bool = True):
        super().__init__()
        self.layer_idx = layer_idx
        
        self.attn = MultiHeadAttention(config)
        self.attn_norm = nn.LayerNorm(config.d_model)
        
        self.ff = nn.Sequential(
            nn.Linear(config.d_model, config.d_ff),
            nn.GELU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.d_ff, config.d_model),
            nn.Dropout(config.dropout)
        )
        self.ff_norm = nn.LayerNorm(config.d_model)
        
        # Add EARCP layer based on config
        self.earcp = EARCPLayer(config) if use_earcp else None
        
    def forward(
        self, 
        x: torch.Tensor, 
        mask: Optional[torch.Tensor] = None, 
        edit_mode: bool = False
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        # Self-attention
        x = x + self.attn(self.attn_norm(x), mask)
        
        # EARCP (if present)
        metrics = {}
        if self.earcp is not None:
            x, metrics = self.earcp(x, self.layer_idx, edit_mode)
        
        # Feed-forward
        x = x + self.ff(self.ff_norm(x))
        
        return x, metrics


# =============================================================================
# MAIN MODEL
# =============================================================================

class SCLM(nn.Module):
    """
    Stateful Coherent Language Model (SCLM)
    
    A transformer language model with persistent latent state and
    multi-expert coherence mechanisms.
    
    Key Features:
    - Persistent state that maintains semantic context across generations
    - Multi-expert coherence that promotes consistent representations
    - Edit mode for local modifications without global drift
    
    Example:
        >>> from sclm import SCLM, SCLMConfig
        >>> 
        >>> # Create model
        >>> config = SCLMConfig(vocab_size=50257, d_model=512, n_layers=6)
        >>> model = SCLM(config)
        >>> 
        >>> # Forward pass
        >>> input_ids = torch.randint(0, 50257, (1, 64))
        >>> output = model(input_ids)
        >>> logits = output['logits']
        >>> 
        >>> # Generate text
        >>> prompt = torch.tensor([[1, 2, 3]])  # tokenized prompt
        >>> generated = model.generate(prompt, max_new_tokens=50)
        >>> 
        >>> # Edit mode
        >>> model.reset_state()
        >>> _ = model(original_ids)  # Build state
        >>> model.freeze_state()
        >>> output = model(edited_ids, edit_mode=True)  # Use frozen state
        >>> model.unfreeze_state()
    """
    
    def __init__(self, config: SCLMConfig, use_earcp: bool = True):
        super().__init__()
        self.config = config
        self.use_earcp = use_earcp
        
        # Embeddings
        self.tok_emb = nn.Embedding(config.vocab_size, config.d_model)
        self.pos_emb = nn.Embedding(config.max_seq_length, config.d_model)
        self.drop = nn.Dropout(config.dropout)
        
        # Transformer blocks
        self.blocks = nn.ModuleList([
            TransformerBlock(
                config, 
                layer_idx=i, 
                use_earcp=use_earcp and (i % config.earcp_every_n_layers == 0)
            )
            for i in range(config.n_layers)
        ])
        
        # Output
        self.out_norm = nn.LayerNorm(config.d_model)
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)
        
        # Weight tying
        self.lm_head.weight = self.tok_emb.weight
        
        # Global EARCP layer
        self.global_earcp = EARCPLayer(config) if use_earcp and config.use_global_earcp else None
        
        # Initialize weights
        self.apply(self._init_weights)
        
    def _init_weights(self, module: nn.Module) -> None:
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, std=0.02)
            
    def reset_state(self) -> None:
        """Reset all EARCP states."""
        if self.global_earcp:
            self.global_earcp.reset_state()
        for block in self.blocks:
            if block.earcp:
                block.earcp.reset_state()
    
    def freeze_state(self) -> None:
        """Freeze all EARCP states for edit mode."""
        if self.global_earcp:
            self.global_earcp.freeze_state()
        for block in self.blocks:
            if block.earcp:
                block.earcp.freeze_state()
    
    def unfreeze_state(self) -> None:
        """Unfreeze all EARCP states."""
        if self.global_earcp:
            self.global_earcp.unfreeze_state()
        for block in self.blocks:
            if block.earcp:
                block.earcp.unfreeze_state()
    
    def get_num_params(self) -> int:
        """Get total number of parameters."""
        return sum(p.numel() for p in self.parameters())
                
    def forward(
        self, 
        input_ids: torch.Tensor, 
        labels: Optional[torch.Tensor] = None,
        edit_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Forward pass.
        
        Args:
            input_ids: Input token IDs [batch, seq_len]
            labels: Target labels for loss computation [batch, seq_len]
            edit_mode: If True, use frozen state
            
        Returns:
            Dictionary containing:
                - logits: Output logits [batch, seq_len, vocab_size]
                - loss: Cross-entropy loss (if labels provided)
                - block_metrics: List of metrics from each EARCP block
                - global_metrics: Metrics from global EARCP layer
        """
        B, T = input_ids.size()
        device = input_ids.device
        
        # Embeddings
        pos = torch.arange(T, device=device).unsqueeze(0)
        x = self.drop(self.tok_emb(input_ids) + self.pos_emb(pos))
        
        # Causal mask
        mask = torch.tril(torch.ones(T, T, device=device)).view(1, 1, T, T)
        
        # Transformer blocks
        all_metrics = []
        for block in self.blocks:
            x, metrics = block(x, mask, edit_mode)
            if metrics:
                all_metrics.append(metrics)
        
        # Global EARCP
        global_metrics = {}
        if self.global_earcp:
            x, global_metrics = self.global_earcp(x, edit_mode=edit_mode)
        
        # Output
        logits = self.lm_head(self.out_norm(x))
        
        # Loss
        loss = None
        if labels is not None:
            loss = F.cross_entropy(
                logits[:, :-1].contiguous().view(-1, self.config.vocab_size),
                labels[:, 1:].contiguous().view(-1)
            )
        
        return {
            'logits': logits,
            'loss': loss,
            'block_metrics': all_metrics,
            'global_metrics': global_metrics
        }
    
    @torch.no_grad()
    def generate(
        self, 
        input_ids: torch.Tensor,
        max_new_tokens: int = 50,
        temperature: float = 0.8,
        top_k: int = 50,
        top_p: float = 0.9,
        repetition_penalty: float = 1.2,
        do_sample: bool = True
    ) -> torch.Tensor:
        """
        Generate text autoregressively.
        
        Args:
            input_ids: Prompt token IDs [batch, seq_len]
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_k: Top-k filtering
            top_p: Nucleus sampling threshold
            repetition_penalty: Penalty for repeated tokens
            do_sample: Whether to sample or use greedy decoding
            
        Returns:
            generated: Full sequence including prompt [batch, seq_len + max_new_tokens]
        """
        self.eval()
        generated = input_ids.clone()
        
        for _ in range(max_new_tokens):
            # Truncate to max length
            context = generated[:, -self.config.max_seq_length:]
            
            # Forward pass
            logits = self(context)['logits'][:, -1] / temperature
            
            # Repetition penalty
            if repetition_penalty != 1.0:
                for i in range(generated.size(0)):
                    for token_id in set(generated[i].tolist()):
                        logits[i, token_id] /= repetition_penalty
            
            # Top-k filtering
            if top_k > 0:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = float('-inf')
            
            # Top-p (nucleus) filtering
            if top_p < 1.0:
                sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                sorted_indices_to_remove = cumulative_probs > top_p
                sorted_indices_to_remove[:, 1:] = sorted_indices_to_remove[:, :-1].clone()
                sorted_indices_to_remove[:, 0] = 0
                for i in range(logits.size(0)):
                    indices_to_remove = sorted_indices[i, sorted_indices_to_remove[i]]
                    logits[i, indices_to_remove] = float('-inf')
            
            # Sample or greedy
            if do_sample:
                probs = F.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, 1)
            else:
                next_token = logits.argmax(dim=-1, keepdim=True)
            
            generated = torch.cat([generated, next_token], dim=1)
        
        return generated


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_sclm_small(vocab_size: int = 50257) -> SCLM:
    """Create a small SCLM model (~45M params)."""
    config = SCLMConfig(
        vocab_size=vocab_size,
        n_layers=6,
        n_heads=8,
        d_model=512,
        d_ff=2048,
        latent_state_dim=256
    )
    return SCLM(config)


def create_sclm_medium(vocab_size: int = 50257) -> SCLM:
    """Create a medium SCLM model (~125M params)."""
    config = SCLMConfig(
        vocab_size=vocab_size,
        n_layers=12,
        n_heads=12,
        d_model=768,
        d_ff=3072,
        latent_state_dim=384
    )
    return SCLM(config)


def create_sclm_large(vocab_size: int = 50257) -> SCLM:
    """Create a large SCLM model (~350M params)."""
    config = SCLMConfig(
        vocab_size=vocab_size,
        n_layers=24,
        n_heads=16,
        d_model=1024,
        d_ff=4096,
        latent_state_dim=512
    )
    return SCLM(config)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Config
    'SCLMConfig',
    
    # Main model
    'SCLM',
    
    # EARCP components
    'EARCPLayer',
    'EncapsulationModule',
    'AlignmentModule',
    'RevisionModule',
    'CoherenceModule',
    'PropagationModule',
    
    # Convenience functions
    'create_sclm_small',
    'create_sclm_medium',
    'create_sclm_large',
]
