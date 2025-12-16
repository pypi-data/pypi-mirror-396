# Copyright 2025 Thulium Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Word-level Language Model (Transformer).

This module provides a Transformer-based word-level language model for
scoring word sequences or for use in higher-level post-processing.
Unlike N-gram models, this neural LM can capture long-range dependencies
and semantic context.
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from thulium.models.language_models.char_lm import LanguageModelScorer


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding."""

    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer("pe", pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding."""
        x = x + self.pe[:, : x.size(1), :]
        return self.dropout(x)


class TransformerWordLM(nn.Module, LanguageModelScorer):
    """Transformer-based Word Language Model.

    Predicts the next word probability distribution given a history of words.

    Architecture:
        Embedding -> PositionalEncoding -> TransformerEncoder -> Linear -> Softmax

    Attributes:
        vocab_size: Size of word vocabulary.
        d_model: Model dimension.
        nhead: Number of attention heads.
        num_layers: Number of transformer layers.
    """

    def __init__(
        self,
        vocab_size: int = 10000,
        d_model: int = 512,
        nhead: int = 8,
        num_layers: int = 6,
        dim_feedforward: int = 2048,
        dropout: float = 0.1,
        max_seq_len: int = 512,
        pad_token_id: int = 0,
    ) -> None:
        """Initialize the Word LM.

        Args:
            vocab_size: Vocabulary size.
            d_model: Embedding dimension.
            nhead: Number of attention heads.
            num_layers: Number of encoder layers.
            dim_feedforward: FFN dimension.
            dropout: Dropout probability.
            max_seq_len: Maximum sequence length.
            pad_token_id: Padding token index.
        """
        super().__init__()

        self.d_model = d_model
        self.pad_token_id = pad_token_id

        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=pad_token_id)
        self.pos_encoder = PositionalEncoding(d_model, max_seq_len, dropout)

        encoder_layers = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True,
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layers, num_layers=num_layers
        )

        self.decoder = nn.Linear(d_model, vocab_size)

        self.init_weights()

        # Causal mask cache
        self.register_buffer(
            "causal_mask", torch.triu(torch.ones(max_seq_len, max_seq_len) * float('-inf'), diagonal=1)
        )

    def init_weights(self) -> None:
        """Initialize weights uniformly."""
        initrange = 0.1
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.decoder.bias.data.zero_()
        self.decoder.weight.data.uniform_(-initrange, initrange)

    def _generate_square_subsequent_mask(self, sz: int) -> torch.Tensor:
        """Generate causal mask."""
        return torch.triu(torch.ones(sz, sz) * float('-inf'), diagonal=1)

    def forward(self, src: torch.Tensor, src_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass.

        Args:
            src: Input token tensor (B, T).
            src_mask: Optional mask.

        Returns:
            Logits (B, T, vocab_size).
        """
        if src_mask is None:
            device = src.device
            seq_len = src.size(1)
            # Use cached mask if possible, else generate
            if seq_len <= self.causal_mask.size(0):
                 src_mask = self.causal_mask[:seq_len, :seq_len]
            else:
                 src_mask = self._generate_square_subsequent_mask(seq_len).to(device)

        src = self.embedding(src) * math.sqrt(self.d_model)
        src = self.pos_encoder(src)
        output = self.transformer_encoder(src, mask=src_mask)
        output = self.decoder(output)
        return output

    @torch.no_grad()
    def score(self, token_sequence: List[int], language: str = "en") -> float:
        """Compute log probability of a sequence.

        Args:
            token_sequence: List of word indices.
            language: Unused.

        Returns:
            Log probability sum.
        """
        if len(token_sequence) < 2:
             return 0.0

        input_tokens = torch.tensor([token_sequence[:-1]], dtype=torch.long)
        target_tokens = torch.tensor(token_sequence[1:], dtype=torch.long)
        
        logits = self.forward(input_tokens)
        log_probs = F.log_softmax(logits[0], dim=-1)
        
        score = 0.0
        for i, target in enumerate(target_tokens):
             score += log_probs[i, target].item()
        return score

    @torch.no_grad()
    def score_partial(
        self,
        prefix: List[int],
        next_token: int,
        state: Optional[object] = None,
        language: str = "en"
    ) -> Tuple[float, object]:
        """Score incrementally (recomputes full sequence for Transformer)."""
        # Transformers aren't naturally incremental without KV caching
        # This is a naive implementation recomputing the whole prefix
        if not prefix:
             return -10.0, None # Rough prior
        
        input_tokens = torch.tensor([prefix], dtype=torch.long)
        logits = self.forward(input_tokens)
        log_probs = F.log_softmax(logits[0, -1], dim=-1) # Last step
        
        return log_probs[next_token].item(), None
