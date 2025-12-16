from typing import Union, List, Optional
from pathlib import Path
from thulium.pipeline.htr_pipeline import HTRPipeline
from thulium.pipeline.config import load_pipeline_config
from thulium.api.types import PageResult

# Cache pipelines to avoid reloading models
_PIPELINE_CACHE = {}

def recognize_image(
    path: Union[str, Path],
    language: str = "en",
    pipeline: str = "default",
    device: str = "auto"
) -> PageResult:
    """
    Recognize handwriting in an image file.

    Args:
        path: Path to image file.
        language: Language code (e.g., 'en', 'az', 'tr').
        pipeline: Name of the pipeline configuration.
        device: 'cpu', 'cuda', or 'auto'.

    Returns:
        PageResult object containing text and metadata.
    """
    key = (pipeline, device)
    if key not in _PIPELINE_CACHE:
        config = load_pipeline_config(pipeline)
        _PIPELINE_CACHE[key] = HTRPipeline(config, device=device)
    
    runner = _PIPELINE_CACHE[key]
    return runner.process(path, language)

def recognize_pdf(
    path: Union[str, Path],
    language: str = "en",
    pipeline: str = "default",
    device: str = "auto"
) -> List[PageResult]:
    """
    Recognize text in a PDF document (all pages).
    """
    # Logic to split PDF and call pipeline per page
    # Stub:
    return [recognize_image(path, language, pipeline, device)]

def recognize_batch(
    paths: List[Union[str, Path]],
    language: str = "en",
    pipeline: str = "default",
    device: str = "auto"
) -> List[PageResult]:
    """
    Process a batch of images.
    """
    return [recognize_image(p, language, pipeline, device) for p in paths]
