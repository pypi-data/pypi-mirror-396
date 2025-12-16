import pytest
import os
import thulium
from thulium.api.recognize import recognize_image
from thulium.data.language_profiles import get_language_profile

def test_version():
    assert thulium.__version__ == "0.1.0"

def test_language_profile():
    prof = get_language_profile("az")
    assert prof.name == "Azerbaijani"
    assert "ə" in prof.alphabet
    
    with pytest.raises(ValueError):
        get_language_profile("xyz_nonexistent")

@pytest.mark.skip(reason="Requires real model weights or mocking")
def test_recognition_api_stub():
    # This test would require a dummy image or mocking the pipeline
    pass
