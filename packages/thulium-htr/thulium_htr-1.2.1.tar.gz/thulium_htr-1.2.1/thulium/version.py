# Copyright 2025 Thulium Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Version information for the Thulium package.

This module contains the single source of truth for the package version,
following semantic versioning (https://semver.org/).

Attributes:
    __version__: The current version string in MAJOR.MINOR.PATCH format.

Example:
    >>> from thulium.version import __version__
    >>> print(__version__)
    '1.2.1'
"""

from __future__ import annotations

__version__: str = "1.2.1"
"""Current version of the Thulium package following semantic versioning."""

__all__ = ["__version__"]
