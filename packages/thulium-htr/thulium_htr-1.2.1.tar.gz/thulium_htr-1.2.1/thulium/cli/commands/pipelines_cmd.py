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

"""Pipelines CLI Command.

This module allows users to list and inspect pre-configured HTR pipelines.
It provides metadata about model capacity, architecture, and intended use cases.
"""

from __future__ import annotations

import json
from typing import Dict, List, Optional

import typer

app = typer.Typer(help="List available recognition pipelines.")


def _get_pipelines() -> List[Dict[str, str]]:
    """Return the registry of available pipelines."""
    return [
        {
            "name": "cnn_lstm_ctc_tiny",
            "architecture": "CNN-LSTM-CTC",
            "capacity": "tiny",
            "params": "~2M",
            "target": "Edge/Mobile",
        },
        {
            "name": "cnn_lstm_ctc_small",
            "architecture": "CNN-LSTM-CTC",
            "capacity": "small",
            "params": "~5M",
            "target": "CPU Inference",
        },
        {
            "name": "cnn_lstm_ctc_base",
            "architecture": "CNN-LSTM-CTC",
            "capacity": "base",
            "params": "~8M",
            "target": "General Purpose",
        },
        {
            "name": "cnn_lstm_ctc_large",
            "architecture": "CNN-LSTM-CTC",
            "capacity": "large",
            "params": "~15M",
            "target": "Maximum Accuracy",
        },
        {
            "name": "vit_transformer_seq2seq_base",
            "architecture": "ViT-Transformer-Seq2Seq",
            "capacity": "base",
            "params": "~25M",
            "target": "Production SoTA",
        },
        {
            "name": "vit_transformer_seq2seq_large",
            "architecture": "ViT-Transformer-Seq2Seq",
            "capacity": "large",
            "params": "~45M",
            "target": "Research SoTA",
        },
    ]


@app.command(name="list")
def list_pipelines(
    filter_keyword: Optional[str] = typer.Option(
        None,
        "--filter",
        "-f",
        help="Filter pipelines by name containing this keyword.",
    ),
    show_params: bool = typer.Option(
        False,
        "--params",
        "-p",
        help="Show parameter count column.",
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        help="Output format: 'table' or 'json'.",
    ),
) -> None:
    """
    List all available recognition pipelines.
    """
    pipelines = _get_pipelines()

    if filter_keyword:
        pipelines = [
            p for p in pipelines if filter_keyword.lower() in p["name"].lower()
        ]

    if not pipelines:
        typer.echo("No pipelines found matching the criteria.")
        return

    if output_format == "json":
        typer.echo(json.dumps(pipelines, indent=2))
        return

    # Table Output
    typer.secho("\nAvailable Recognition Pipelines:", bold=True)
    typer.echo("=" * 80)

    if show_params:
        header = f"{'Name':<35} {'Architecture':<25} {'Params':<8} {'Target'}"
        typer.echo(header)
        typer.echo("-" * 80)
        for p in pipelines:
            row = f"{p['name']:<35} {p['architecture']:<25} {p['params']:<8} {p['target']}"
            typer.echo(row)
    else:
        header = f"{'Name':<35} {'Capacity':<10} {'Target'}"
        typer.echo(header)
        typer.echo("-" * 60)
        for p in pipelines:
            row = f"{p['name']:<35} {p['capacity']:<10} {p['target']}"
            typer.echo(row)

    typer.echo("=" * 80)
    typer.echo(f"Total: {len(pipelines)} pipelines.\n")
    typer.echo("Use 'thulium recognize --pipeline <name>' to use one.")
