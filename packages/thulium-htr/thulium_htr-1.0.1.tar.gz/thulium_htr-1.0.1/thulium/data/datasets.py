"""
Dataset abstractions for HTR training and evaluation.
"""

import os
from pathlib import Path
from typing import List, Tuple, Callable, Optional
from torch.utils.data import Dataset
from PIL import Image
from thulium.data.loaders import load_image

class OCRDataset(Dataset):
    """
    Standard dataset for Image -> Text mapping.
    Expected format: list of (image_path, text_label).
    """
    def __init__(self, samples: List[Tuple[str, str]], transform: Optional[Callable] = None):
        self.samples = samples
        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        img_path, text = self.samples[idx]
        image = load_image(img_path)
        
        if self.transform:
            image = self.transform(image)
            
        return {"image": image, "text": text}

class FolderDataset(OCRDataset):
    """
    Loads samples from a directory structure or a label file (labels.txt).
    Format:
    filename.jpg  Ground Truth Text
    """
    def __init__(self, root: str, label_file: str, transform: Optional[Callable] = None):
        samples = []
        root_path = Path(root)
        with open(label_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    fname, label = parts
                    samples.append((str(root_path / fname), label))
        super().__init__(samples, transform)
