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

"""Benchmark CLI Command.

This module exposes benchmarking capabilities via the CLI. It allows running
evaluation suites defined in YAML configuration files and exporting the results
in various formats (Markdown, CSV, JSON).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import typer

from thulium.evaluation.benchmarking import run_benchmark
from thulium.evaluation.reporting import (
    generate_csv_report,
    generate_json_report,
    generate_markdown_report,
    save_report,
)

logger = logging.getLogger(__name__)

app = typer.Typer(help="Run HTR benchmarks.")


@app.command(name="run")
def run_benchmark_command(
    config: Path = typer.Argument(
        ...,
        exists=True,
        help="Path to the benchmark configuration YAML file.",
        resolve_path=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to save the benchmark report.",
        writable=True,
    ),
    report_format: str = typer.Option(
        "markdown",
        "--format",
        "-f",
        help="Output report format: 'markdown', 'csv', or 'json'.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output during benchmarking.",
    ),
    include_samples: bool = typer.Option(
        False,
        "--include-samples",
        help="Include individual sample predictions in the report.",
    ),
) -> None:
    """
    Execute a benchmark suite.

    Runs the evaluation pipeline as defined in the provided configuration file.
    Calculates metrics such as CER, WER, and SER.
    """
    logger.info("Starting benchmark using config: %s", config)

    try:
        # Run Benchmark
        result = run_benchmark(str(config), verbose=verbose)

        # Generate Report Content
        if report_format == "markdown":
            report_content = generate_markdown_report(result, include_samples=include_samples)
        elif report_format == "csv":
            report_content = generate_csv_report(result, include_samples=include_samples)
        elif report_format == "json":
            report_content = generate_json_report(result, include_samples=include_samples)
        else:
            logger.error("Unknown format: %s. Supported: markdown, csv, json", report_format)
            raise typer.Exit(1)

        # Output Handling
        if output:
            save_report(result, str(output), format=report_format, include_samples=include_samples)
            logger.info("Benchmark results saved to %s", output)
        else:
            # Print to stdout
            typer.echo(report_content)

        # Summary Log
        logger.info(
            "Benchmark Complete. Aggregate CER: %.2f%%, WER: %.2f%%",
            result.aggregate_cer * 100,
            result.aggregate_wer * 100,
        )

    except Exception as e:
        logger.error("Benchmarking failed: %s", e)
        if verbose:
            logger.exception("Traceback:")
        raise typer.Exit(1)


@app.command(name="list")
def list_configs() -> None:
    """List available benchmark configurations."""
    config_dir = Path("config/eval")
    
    if not config_dir.exists():
        logger.warning("Config directory not found: config/eval")
        return

    configs = sorted(config_dir.glob("*.yaml"))
    
    if not configs:
        typer.echo("No benchmark configurations found in config/eval/")
        return

    typer.echo("Available Benchmark Configurations:")
    for config_file in configs:
        typer.echo(f"  - {config_file}")
