from typing import List
from thulium.api.types import Line

class SegmentationPipeline:
    """
    Pipeline step for converting a page image into a list of line images/bboxes.
    """
    def __init__(self, model_name="unet_line_v1"):
        self.model_name = model_name

    def run(self, image_path) -> List[Line]:
        # Stub logic
        return []
