"""CAT Cafe SDK for Continuous Alignment Testing."""

from .client import (
    CATCafeClient,
    Experiment,
    ExperimentResult,
    EvaluationMetric,
    EvaluatorResult,  # Backwards compatibility
    DatasetConfig,
    DatasetExample,
    DatasetImport,
    Example,
    Dataset,
)

# Experiment runner functionality now lives in the cat-experiments package.


__version__ = "0.0.1"

__all__ = [
    # Client
    "CATCafeClient",
    "Experiment",
    "ExperimentResult",
    "EvaluationMetric",
    "EvaluatorResult",  # Backwards compatibility
    "DatasetConfig",
    "DatasetExample",
    "DatasetImport",
    "Example",
    "Dataset",
]
