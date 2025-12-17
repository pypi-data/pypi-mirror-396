"""
Benchmark datasets for RNA structure analysis.

Includes curated gold-standard datasets for validation.
"""

from rnaview.datasets.benchmark import (
    load_benchmark,
    list_benchmarks,
    BenchmarkDataset,
)

__all__ = [
    "load_benchmark",
    "list_benchmarks",
    "BenchmarkDataset",
]
