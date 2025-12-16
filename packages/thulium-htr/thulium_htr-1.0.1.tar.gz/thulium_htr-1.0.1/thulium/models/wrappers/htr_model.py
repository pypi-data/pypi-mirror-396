import torch.nn as nn
from thulium.models.backbones.cnn_backbones import ResNetBackbone
from thulium.models.sequence.lstm_heads import BiLSTMHead
from thulium.models.decoders.ctc_decoder import CTCDecoder

class HTRModel(nn.Module):
    """
    End-to-End Handwritten Text Recognition Model.
    Composes Backbone -> Sequence Head -> Decoder.
    """
    def __init__(self, num_classes: int, backbone="resnet", head="bilstm", decoder="ctc"):
        super().__init__()
        # In a real impl, these would be factories based on string configs
        self.backbone = ResNetBackbone(output_channels=256)
        self.head = BiLSTMHead(input_size=256, hidden_size=256)
        self.decoder = CTCDecoder(input_size=256, num_classes=num_classes)

    def forward(self, x):
        features = self.backbone(x)
        sequence = self.head(features)
        log_probs = self.decoder(sequence)
        return log_probs

    @classmethod
    def from_config(cls, config_path: str):
        """
        Instantiate model from a YAML config.
        """
        logger = logging.getLogger(__name__)
        # Stub implementation
        # logger.info(f"Loading HTR model from {config_path}")
        return cls(num_classes=100) # Placeholder
