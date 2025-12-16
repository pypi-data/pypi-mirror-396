import torch.nn as nn

class WordSegmenter(nn.Module):
    """
    Network for segmenting words within a line or page.
    Could be a Mask-RCNN style or a simpler heatmap regressor.
    """
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 1, 1) # Stub
    
    def forward(self, x):
        return self.conv(x)
