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

"""Thulium Command Line Interface Entry Point.

This module serves as the main entry point for the Thulium HTR system CLI.
It sets up the Typer application, configures logging, and registers all
sub-commands for training, recognition, benchmarking, and analysis.

Usage:
    thulium [COMMAND] [ARGS]...
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

import typer

from thulium import __version__
from thulium.api.recognize import recognize_image
from thulium.cli.commands import (
    analyze_errors_cmd,
    benchmark_cmd,
    pipelines_cmd,
    profiles_cmd,
    train_cmd,
)

# Configure logging with a professional format
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger("thulium.cli")

app = typer.Typer(
    help="Thulium: State-of-the-Art Multilingual Handwriting Recognition System.",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="markdown",
)


def version_callback(value: bool):
    """Callback to display version information."""
    if value:
        typer.echo(f"Thulium v{__version__}")
        raise typer.Exit()


@app.callback()
def common(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        help="Show the application version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
    debug: bool = typer.Option(
        False, "--debug", help="Enable debug logging for verbose output."
    ),
):
    """
    Thulium HTR - High-performance Handwritten Text Recognition.
    """
    if debug:
        logging.getLogger("thulium").setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled.")


@app.command(name="recognize")
def recognize_command(
    path: Path = typer.Argument(
        ...,
        exists=True,
        help="Path to the input image or PDF file.",
        resolve_path=True,
    ),
    language: str = typer.Option(
        "en",
        "--language",
        "-l",
        help="ISO language code (e.g., 'en', 'fr', 'az').",
    ),
    pipeline: str = typer.Option(
        "default",
        "--pipeline",
        "-p",
        help="Name of the pipeline configuration to use.",
    ),
    device: str = typer.Option(
        "auto",
        "--device",
        "-d",
        help="Computation device ('cpu', 'cuda', 'auto').",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to save results as JSON.",
        writable=True,
    ),
) -> None:
    """
    Recognize text from a document image or PDF.

    This command runs the full HTR pipeline on the specified input file.
    It supports multiple languages and output formats.
    """
    logger.info("Starting recognition for %s (lang=%s)", path.name, language)

    try:
        result = recognize_image(
            image_path=path,
            language=language,
            pipeline_name=pipeline,
            device=device,
        )

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(result.to_json(indent=2))
            logger.info("Results successfully saved to %s", output)
        else:
            typer.secho("\n--- Recognition Result ---", fg=typer.colors.GREEN, bold=True)
            typer.echo(result.full_text)
            typer.secho("--------------------------\n", fg=typer.colors.GREEN, bold=True)

    except Exception as e:
        logger.error("Recognition failed: %s", e)
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logger.exception("Traceback:")
        sys.exit(1)


# Register sub-commands
app.add_typer(train_cmd.app, name="train")
app.add_typer(benchmark_cmd.app, name="benchmark")
app.add_typer(analyze_errors_cmd.app, name="analyze")
app.add_typer(pipelines_cmd.app, name="pipelines")
app.add_typer(profiles_cmd.app, name="profiles")


if __name__ == "__main__":
    app()
