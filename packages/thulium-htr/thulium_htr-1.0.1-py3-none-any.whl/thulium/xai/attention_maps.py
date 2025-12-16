from typing import List, Tuple
import numpy as np

def generate_attention_map(decoder_output: np.ndarray, tokens: List[str]) -> np.ndarray:
    """
    Visualize attention weights for a prediction.
    Args:
        decoder_output: Attention weights (Steps, SourceLen)
        tokens: List of decoded tokens
    Returns:
        Plot or array representing the heatmap (Stub).
    """
    # Stub implementation
    return np.random.rand(len(tokens), 10) # Random heatmap

def compute_confidence_scores(log_probs: np.ndarray) -> List[float]:
    """
    Compute confidence scores from log probabilities.
    """
    probs = np.exp(log_probs)
    max_probs = np.max(probs, axis=-1)
    return max_probs.tolist()
