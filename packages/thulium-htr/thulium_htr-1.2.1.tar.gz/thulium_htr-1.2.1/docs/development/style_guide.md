# Style Guide

Code style standards for Thulium development.

## Python Style

All code follows the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

### Key Requirements

#### Imports

```python
# Standard library imports
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

# Third-party imports
import numpy as np
import torch
import torch.nn as nn

# Local imports
from thulium.evaluation.metrics import cer
from thulium.models.backbones import ResNetBackbone
```

**Rules:**
- `from __future__ import annotations` first
- One import per line for `typing`
- Blank line between groups
- Alphabetical within groups

#### Type Annotations

```python
def recognize_image(
    image_path: str | Path,
    language: str = "en",
    *,
    device: str = "auto",
) -> RecognitionResult:
    ...
```

**Rules:**
- All public functions must have type annotations
- Use `|` instead of `Union` (Python 3.10+)
- Use `list[str]` instead of `List[str]` (Python 3.9+)

#### Docstrings

```python
def cer(reference: str, hypothesis: str) -> float:
    """Compute Character Error Rate.
    
    Args:
        reference: Ground truth text.
        hypothesis: Predicted text.
        
    Returns:
        CER value between 0.0 and 1.0+.
        
    Raises:
        ValueError: If reference is empty.
        
    Example:
        >>> cer("hello", "hallo")
        0.2
    """
```

**Rules:**
- One-line summary
- Blank line before Args
- Args, Returns, Raises, Example sections
- Use imperative mood ("Compute", not "Computes")

#### Naming

| Type | Convention | Example |
|------|------------|---------|
| Module | `snake_case` | `language_profiles.py` |
| Class | `PascalCase` | `HTRPipeline` |
| Function | `snake_case` | `recognize_image` |
| Constant | `UPPER_SNAKE_CASE` | `DEFAULT_DEVICE` |
| Private | `_leading_underscore` | `_levenshtein_distance` |

#### Line Length

- Maximum 88 characters
- Break long lines at logical points

## Markdown Style

### Headers

```markdown
# Document Title

## Main Section

### Subsection
```

### Tables

```markdown
| Column 1 | Column 2 |
|----------|----------|
| Value | Value |
```

### Code Blocks

````markdown
```python
from thulium import recognize_image
```
````

## Tools

### Linting

```bash
# Type checking
mypy thulium/

# Style checking
ruff check thulium/

# Fixing
ruff check --fix thulium/
```

### Formatting

```bash
# Auto-format
ruff format thulium/

# Import sorting
isort thulium/
```

## See Also

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Development Guide](dev_guide.md) — Setup
