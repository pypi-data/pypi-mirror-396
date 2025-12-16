from typing import List
import numpy as np

def analyze_confidence(log_probs: np.ndarray, threshold: float = 0.8) -> List[int]:
    """
    Return indices of tokens with confidence below threshold.
    """
    probs = np.exp(log_probs)
    max_probs = np.max(probs, axis=-1)
    low_conf_indices = np.where(max_probs < threshold)[0]
    return low_conf_indices.tolist()
