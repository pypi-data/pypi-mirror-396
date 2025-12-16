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

"""Error Analysis CLI Command.

This module provides tools for analyzing recognition errors in depth.
It generates confusion matrices, top-k error lists, and detailed metric breakdowns
to help researchers diagnose model weaknesses.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Optional

import typer

from thulium.evaluation.metrics import cer, ser, wer
from thulium.xai.error_analysis import ErrorAnalyzer

logger = logging.getLogger(__name__)

app = typer.Typer(help="Analyze recognition errors.")


@app.command(name="analyze")
def analyze_errors(
    predictions_file: Optional[Path] = typer.Option(
        None,
        "--predictions",
        "-p",
        help="Path to file containing model predictions (one per line).",
        exists=True,
    ),
    ground_truth_file: Optional[Path] = typer.Option(
        None,
        "--ground-truth",
        "-g",
        help="Path to file containing ground truth text (one per line).",
        exists=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to save the analysis report.",
        writable=True,
    ),
    top_k: int = typer.Option(
        20,
        "--top-k",
        "-k",
        help="Number of most frequent errors to display.",
    ),
    report_format: str = typer.Option(
        "markdown",
        "--format",
        "-f",
        help="Output format: 'markdown', 'json', or 'csv'.",
    ),
) -> None:
    """
    Analyze errors between predictions and ground truth.

    Inputs must be line-aligned text files.
    """
    if not predictions_file or not ground_truth_file:
        logger.error("Both --predictions and --ground-truth are required.")
        raise typer.Exit(1)

    logger.info("Loading data for analysis...")
    try:
        with open(predictions_file, "r", encoding="utf-8") as f:
            preds = [line.strip() for line in f]
        with open(ground_truth_file, "r", encoding="utf-8") as f:
            gts = [line.strip() for line in f]
    except Exception as e:
        logger.error("Failed to read input files: %s", e)
        raise typer.Exit(1)

    if len(preds) != len(gts):
        logger.error(
            "Line count mismatch: predictions (%d) vs ground truth (%d)",
            len(preds),
            len(gts),
        )
        raise typer.Exit(1)

    logger.info("Analyzing %d samples...", len(preds))

    analyzer = ErrorAnalyzer()
    
    # 1. Compute Top-K Errors
    top_errors = analyzer.analyze_top_k_errors(preds, gts, k=top_k)

    # 2. Compute Summary Metrics
    metrics = analyzer.summarize_metrics(preds, gts)

    # 3. Format Report
    if report_format == "json":
        report_data = {
            "metrics": metrics,
            "top_errors": top_errors,
            "sample_count": len(preds),
        }
        report_str = json.dumps(report_data, indent=2, ensure_ascii=False)
    
    elif report_format == "csv":
        lines = ["ground_truth,prediction,count,cer"]
        for err in top_errors:
            # Escape quotes for CSV
            gt = err['ground_truth'].replace('"', '""')
            pred = err['prediction'].replace('"', '""')
            lines.append(f'"{gt}","{pred}",{err["count"]},{err["cer"]:.4f}')
        report_str = "\n".join(lines)
        
    else:  # Markdown
        lines = [
            "# Error Analysis Report",
            "",
            "## Summary Metrics",
            "",
            "| Metric | Value |",
            "| :--- | :--- |",
            f"| CER | {metrics['CER']:.4f} ({metrics['CER']*100:.2f}%) |",
            f"| WER | {metrics['WER']:.4f} ({metrics['WER']*100:.2f}%) |",
            f"| SER | {metrics['SER']:.4f} ({metrics['SER']*100:.2f}%) |",
            f"| Samples | {len(preds)} |",
            "",
            f"## Top {top_k} Most Frequent Errors",
            "",
            "| Ground Truth | Prediction | Count | CER |",
            "| :--- | :--- | :--- | :--- |",
        ]
        for err in top_errors:
            # Truncate long strings for table display
            gt_disp = (err['ground_truth'][:40] + '...') if len(err['ground_truth']) > 40 else err['ground_truth']
            pred_disp = (err['prediction'][:40] + '...') if len(err['prediction']) > 40 else err['prediction']
            # Escape pipes for markdown table
            gt_disp = gt_disp.replace("|", "\\|")
            pred_disp = pred_disp.replace("|", "\\|")
            
            lines.append(f"| {gt_disp} | {pred_disp} | {err['count']} | {err['cer']:.4f} |")
        
        report_str = "\n".join(lines)

    # 4. Output
    if output:
        try:
            with open(output, "w", encoding="utf-8") as f:
                f.write(report_str)
            logger.info("Report saved to %s", output)
        except Exception as e:
            logger.error("Failed to write report to %s: %s", output, e)
            raise typer.Exit(1)
    else:
        typer.echo(report_str)
    
    logger.info("Analysis Complete.")
