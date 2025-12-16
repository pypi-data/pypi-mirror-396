import yaml
from pathlib import Path
from typing import Dict, Any

def load_pipeline_config(pipeline_name: str = "default") -> Dict[str, Any]:
    """
    Load pipeline configuration from yaml.
    Searches in thulium/config/pipelines first.
    """
    # Stub implementation - just return a dict for now
    return {"model": "htr_resnet_bilstm_ctc", "steps": ["segmentation", "recognition"]}

def load_language_config(lang_code: str) -> Dict[str, Any]:
    """
    Load language specific configuration.
    """
    return {"alphabet": "latin"}
