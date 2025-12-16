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

"""Language models for HTR decoding enhancement.

This module provides language models that can be integrated with CTC or
attention-based decoding to improve recognition accuracy by incorporating
linguistic knowledge.

Submodules:
    char_lm: Character-level LSTM and Transformer language models.
    word_lm: Word-level language models.
    ngram_lm: N-gram based language models.

Classes:
    CharacterLM: LSTM-based character language model.
    TransformerCharLM: Transformer-based character language model.
    LanguageModelScorer: Abstract interface for LM scoring.

Example:
    >>> from thulium.models.language_models import CharacterLM
    >>> lm = CharacterLM(vocab_size=100, hidden_size=256)
    >>> log_prob = lm.score([5, 10, 15, 20])
"""

from __future__ import annotations

__all__: list[str] = []
