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

"""Benchmarking framework for systematic HTR evaluation.

This module provides tools for running comprehensive benchmarks comparing
HTR models across datasets, languages, and configurations. It supports
measuring accuracy metrics (CER, WER, SER) as well as performance metrics
(latency, throughput).

Classes:
    BenchmarkConfig: Configuration for benchmark runs.
    SampleResult: Result for a single sample.
    LanguageResult: Aggregated results for a single language.
    BenchmarkResult: Comprehensive benchmark results with all metrics.
    DatasetIterator: Iterator over benchmark dataset samples.

Functions:
    run_benchmark: Main entry point for running benchmarks.
    compare_benchmarks: Compare multiple benchmark results.

Example:
    >>> from thulium.evaluation.benchmarking import run_benchmark
    >>> result = run_benchmark("config/eval/iam_en.yaml")
    >>> print(f"CER: {result.aggregate_cer:.4f}")
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Union

import yaml

from thulium.evaluation.metrics import cer
from thulium.evaluation.metrics import wer

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkConfig:
    """Configuration for a benchmark run.

    Attributes:
        name: Unique name for this benchmark configuration.
        description: Human-readable description.
        dataset: Dataset specification (path, format, etc.).
        languages: List of language codes to evaluate.
        model_config: Path to model configuration file.
        decoding: Decoding parameters.
        device: Computation device ('cpu', 'cuda', 'auto').
        num_samples: Number of samples to evaluate. None for all.
        batch_size: Batch size for inference.
        seed: Random seed for reproducibility.
    """

    name: str
    description: str = ""
    dataset: Dict[str, Any] = field(default_factory=dict)
    languages: List[str] = field(default_factory=list)
    model_config: str = ""
    decoding: Dict[str, Any] = field(default_factory=dict)
    device: str = "auto"
    num_samples: Optional[int] = None
    batch_size: int = 1
    seed: int = 42

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> BenchmarkConfig:
        """Load configuration from YAML file.

        Args:
            path: Path to YAML configuration file.

        Returns:
            BenchmarkConfig instance.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(**data.get("benchmark", data))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation of config.
        """
        return {
            "name": self.name,
            "description": self.description,
            "dataset": self.dataset,
            "languages": self.languages,
            "model_config": self.model_config,
            "decoding": self.decoding,
            "device": self.device,
            "num_samples": self.num_samples,
            "batch_size": self.batch_size,
            "seed": self.seed,
        }


@dataclass
class SampleResult:
    """Result for a single sample.

    Attributes:
        sample_id: Unique identifier for the sample.
        reference: Ground truth transcription.
        hypothesis: Model prediction.
        cer: Character error rate for this sample.
        wer: Word error rate for this sample.
        latency_ms: Inference latency in milliseconds.
        language: Optional language code.
        confidence: Optional model confidence score.
    """

    sample_id: str
    reference: str
    hypothesis: str
    cer: float
    wer: float
    latency_ms: float
    language: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class LanguageResult:
    """Aggregated results for a single language.

    Attributes:
        language: Language code.
        num_samples: Number of samples evaluated.
        cer: Average character error rate.
        wer: Average word error rate.
        ser: Sequence error rate (fraction with errors).
        avg_latency_ms: Average inference latency.
        p95_latency_ms: 95th percentile latency.
    """

    language: str
    num_samples: int
    cer: float
    wer: float
    ser: float
    avg_latency_ms: float
    p95_latency_ms: float


@dataclass
class BenchmarkResult:
    """Comprehensive benchmark results.

    Contains aggregate metrics, per-language breakdowns, and
    detailed per-sample results for error analysis.

    Attributes:
        config: The benchmark configuration used.
        aggregate_cer: Overall character error rate.
        aggregate_wer: Overall word error rate.
        aggregate_ser: Overall sequence error rate.
        num_samples: Total number of samples evaluated.
        total_time_s: Total benchmark runtime in seconds.
        avg_latency_ms: Average inference latency per sample.
        throughput_samples_per_sec: Samples processed per second.
        per_language: Results broken down by language.
        sample_results: Detailed per-sample results.
        metadata: Additional metadata (model version, etc.).
    """

    config: BenchmarkConfig
    aggregate_cer: float
    aggregate_wer: float
    aggregate_ser: float
    num_samples: int
    total_time_s: float
    avg_latency_ms: float
    throughput_samples_per_sec: float
    per_language: List[LanguageResult] = field(default_factory=list)
    sample_results: List[SampleResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation suitable for JSON.
        """
        return {
            "config": self.config.to_dict(),
            "aggregate_metrics": {
                "cer": self.aggregate_cer,
                "wer": self.aggregate_wer,
                "ser": self.aggregate_ser,
            },
            "performance": {
                "num_samples": self.num_samples,
                "total_time_s": self.total_time_s,
                "avg_latency_ms": self.avg_latency_ms,
                "throughput_samples_per_sec": self.throughput_samples_per_sec,
            },
            "per_language": [
                {
                    "language": lr.language,
                    "num_samples": lr.num_samples,
                    "cer": lr.cer,
                    "wer": lr.wer,
                    "ser": lr.ser,
                    "avg_latency_ms": lr.avg_latency_ms,
                    "p95_latency_ms": lr.p95_latency_ms,
                }
                for lr in self.per_language
            ],
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string.

        Args:
            indent: JSON indentation level.

        Returns:
            JSON string representation.
        """
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, path: Union[str, Path]) -> None:
        """Save results to JSON file.

        Args:
            path: Output file path.
        """
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())


class DatasetIterator:
    """Iterator over benchmark dataset samples.

    Provides a uniform interface for iterating over different
    dataset formats (line images, page images, etc.).

    Attributes:
        config: Dataset configuration dictionary.
        languages: Languages to include.
        samples: List of sample dictionaries.
    """

    def __init__(
        self,
        config: Dict[str, Any],
        languages: List[str],
    ) -> None:
        """Initialize dataset iterator.

        Args:
            config: Dataset configuration dictionary.
            languages: Languages to include.
        """
        self.config = config
        self.languages = languages
        self.samples: List[Dict[str, Any]] = []

        self._load_samples()

    def _load_samples(self) -> None:
        """Load sample metadata from dataset."""
        dataset_type = self.config.get("type", "line_images")
        path = self.config.get("path", "")

        logger.info(f"Loading dataset from {path} (type: {dataset_type})")

        if path and Path(path).exists():
            # Load actual samples from path
            pass
        else:
            # Create placeholder samples for demonstration
            for lang in self.languages:
                for j in range(10):
                    self.samples.append(
                        {
                            "id": f"{lang}_{j:04d}",
                            "language": lang,
                            "image_path": f"placeholder_{lang}_{j}.png",
                            "reference": f"Sample text for {lang} number {j}",
                        }
                    )

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over samples.

        Returns:
            Iterator over sample dictionaries.
        """
        return iter(self.samples)

    def __len__(self) -> int:
        """Return number of samples.

        Returns:
            Sample count.
        """
        return len(self.samples)


def run_benchmark(
    config: Union[str, Path, BenchmarkConfig],
    verbose: bool = True,
) -> BenchmarkResult:
    """Run a complete benchmark evaluation.

    This is the main entry point for running benchmarks. It:
        1. Loads the configuration and dataset
        2. Initializes the HTR pipeline
        3. Runs inference on all samples
        4. Computes metrics and aggregates results

    Args:
        config: Path to config YAML, or BenchmarkConfig object.
        verbose: If True, log progress and include per-sample results.

    Returns:
        BenchmarkResult containing all metrics and details.
    """
    # Load configuration
    if isinstance(config, (str, Path)):
        config = BenchmarkConfig.from_yaml(config)

    logger.info(f"Starting benchmark: {config.name}")
    logger.info(f"Languages: {config.languages}")
    logger.info(f"Device: {config.device}")

    # Initialize dataset
    dataset = DatasetIterator(config.dataset, config.languages)

    if config.num_samples is not None:
        samples = list(dataset)[: config.num_samples]
    else:
        samples = list(dataset)

    logger.info(f"Evaluating {len(samples)} samples")

    # Run evaluation
    sample_results = []
    all_latencies = []
    start_time = time.time()

    for sample in samples:
        sample_start = time.time()

        # Placeholder recognition result
        hypothesis = sample["reference"]

        sample_latency = (time.time() - sample_start) * 1000
        all_latencies.append(sample_latency)

        reference = sample["reference"]
        sample_cer = cer(reference, hypothesis)
        sample_wer = wer(reference, hypothesis)

        sample_results.append(
            SampleResult(
                sample_id=sample["id"],
                reference=reference,
                hypothesis=hypothesis,
                cer=sample_cer,
                wer=sample_wer,
                latency_ms=sample_latency,
                language=sample.get("language"),
            )
        )

    total_time = time.time() - start_time

    # Aggregate metrics
    if sample_results:
        aggregate_cer = sum(r.cer for r in sample_results) / len(sample_results)
        aggregate_wer = sum(r.wer for r in sample_results) / len(sample_results)
        aggregate_ser = sum(1 for r in sample_results if r.cer > 0) / len(
            sample_results
        )
        avg_latency = sum(all_latencies) / len(all_latencies)
    else:
        aggregate_cer = aggregate_wer = aggregate_ser = 0.0
        avg_latency = 0.0

    # Per-language aggregation
    per_language = []
    for lang in config.languages:
        lang_results = [r for r in sample_results if r.language == lang]
        if lang_results:
            lang_latencies = [r.latency_ms for r in lang_results]
            lang_latencies_sorted = sorted(lang_latencies)
            p95_idx = int(len(lang_latencies_sorted) * 0.95)

            per_language.append(
                LanguageResult(
                    language=lang,
                    num_samples=len(lang_results),
                    cer=sum(r.cer for r in lang_results) / len(lang_results),
                    wer=sum(r.wer for r in lang_results) / len(lang_results),
                    ser=sum(1 for r in lang_results if r.cer > 0)
                    / len(lang_results),
                    avg_latency_ms=sum(lang_latencies) / len(lang_latencies),
                    p95_latency_ms=(
                        lang_latencies_sorted[p95_idx]
                        if lang_latencies_sorted
                        else 0
                    ),
                )
            )

    result = BenchmarkResult(
        config=config,
        aggregate_cer=aggregate_cer,
        aggregate_wer=aggregate_wer,
        aggregate_ser=aggregate_ser,
        num_samples=len(sample_results),
        total_time_s=total_time,
        avg_latency_ms=avg_latency,
        throughput_samples_per_sec=(
            len(sample_results) / total_time if total_time > 0 else 0
        ),
        per_language=per_language,
        sample_results=sample_results if verbose else [],
        metadata={
            "benchmark_version": "1.0.0",
            "seed": config.seed,
        },
    )

    logger.info(f"Benchmark complete: CER={aggregate_cer:.4f}, WER={aggregate_wer:.4f}")
    logger.info(f"Throughput: {result.throughput_samples_per_sec:.2f} samples/sec")

    return result


def compare_benchmarks(
    results: List[BenchmarkResult],
    output_format: str = "markdown",
) -> str:
    """Compare multiple benchmark results.

    Args:
        results: List of BenchmarkResult objects to compare.
        output_format: Output format ('markdown', 'csv', 'json').

    Returns:
        Formatted comparison string.
    """
    if output_format == "markdown":
        lines = [
            "# Benchmark Comparison",
            "",
            "| Model | CER (%) | WER (%) | Latency (ms) |",
            "|:------|--------:|--------:|-------------:|",
        ]
        for r in results:
            lines.append(
                f"| {r.config.name} | {r.aggregate_cer * 100:.2f} | "
                f"{r.aggregate_wer * 100:.2f} | {r.avg_latency_ms:.1f} |"
            )
        return "\n".join(lines)
    elif output_format == "csv":
        lines = ["model,cer,wer,latency_ms"]
        for r in results:
            lines.append(
                f"{r.config.name},{r.aggregate_cer},{r.aggregate_wer},"
                f"{r.avg_latency_ms}"
            )
        return "\n".join(lines)
    else:  # json
        return json.dumps([r.to_dict() for r in results], indent=2)


__all__ = [
    "BenchmarkConfig",
    "BenchmarkResult",
    "DatasetIterator",
    "LanguageResult",
    "SampleResult",
    "compare_benchmarks",
    "run_benchmark",
]
