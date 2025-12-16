import torch.nn as nn

class UNetLineSegmenter(nn.Module):
    """
    U-Net based architecture for line segmentation.
    Outputs a binary mask or probability map for text lines.
    """
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
             nn.Conv2d(3, 32, 3, padding=1),
             nn.ReLU()
        )
        self.decoder = nn.Sequential(
             nn.Conv2d(32, 1, 1),
             nn.Sigmoid()
        )

    def forward(self, x):
        feat = self.encoder(x)
        return self.decoder(feat)
