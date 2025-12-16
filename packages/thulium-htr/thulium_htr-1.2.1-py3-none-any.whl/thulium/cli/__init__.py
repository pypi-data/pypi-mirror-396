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

"""Command-line interface for Thulium HTR.

This module provides the CLI entry points for Thulium, enabling recognition,
training, evaluation, and analysis from the command line.

Submodules:
    main: CLI entry point and command group.
    commands: Individual CLI command implementations.

Commands:
    recognize: Recognize text from handwriting images.
    train: Train models from configuration files.
    benchmark: Run evaluation benchmarks on trained models.
    analyze-errors: Analyze recognition errors.
    show-language-profiles: Display supported languages.
    list-pipelines: List available model pipelines.

Example:
    Command-line usage:

    $ thulium recognize --image document.png --language en
    $ thulium train --config config/training/train_cnn_lstm_base.yaml
    $ thulium benchmark --config config/eval/iam_en.yaml
    $ thulium show-language-profiles

    Python usage:

    >>> from thulium.cli.main import app
    >>> app(["recognize", "--image", "doc.png"])
"""

from __future__ import annotations

__all__: list[str] = []
