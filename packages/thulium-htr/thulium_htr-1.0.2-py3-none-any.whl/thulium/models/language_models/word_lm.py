import torch.nn as nn

class WordLM(nn.Module):
    """
    Word-level Language Model.
    Typically uses BPE or word embeddings.
    """
    def __init__(self, vocab_size=10000, hidden_size=512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=hidden_size, nhead=8), 
            num_layers=4
        )
        self.fc = nn.Linear(hidden_size, vocab_size)
