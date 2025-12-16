"""CAT Cafe SDK client for external experiment integration."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from urllib.parse import quote
import httpx


@dataclass
class Experiment:
    """Experiment configuration."""

    __test__ = False  # Tell pytest this is not a test class

    name: str
    description: str
    dataset_id: str
    dataset_version: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentResult:
    """A single experiment result."""

    __test__ = False  # Tell pytest this is not a test class

    example_id: str
    input_data: Dict[str, Any]
    output: Optional[Dict[str, Any]]
    actual_output: Dict[str, Any] | str
    repetition_number: int = 1
    run_id: str = field(default_factory=lambda: __import__("uuid").uuid4().hex)
    trace_id: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    evaluation_scores: Dict[str, float] = field(default_factory=dict)
    evaluator_metadata: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None  # Test function execution time in milliseconds
    evaluator_execution_times_ms: Dict[str, float] = field(default_factory=dict)  # Per-evaluator execution times


@dataclass
class ExperimentRun:
    """A run record returned by the stream-based experiment API."""

    run_id: str
    example_id: str
    repetition_number: int
    input_data: Dict[str, Any]
    output: Dict[str, Any]
    actual_output: Any
    evaluation_scores: Dict[str, float]
    evaluator_metadata: Dict[str, Dict[str, Any]]
    evaluations: List[Dict[str, Any]] = field(default_factory=list)
    trace_id: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    execution_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None


@dataclass
class ExperimentEvaluation:
    """Evaluation record returned by the stream-based experiment API."""

    evaluator_name: str
    score: Optional[float] = None
    label: Optional[str] = None
    explanation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class DatasetConfig:
    """Dataset configuration for creation."""

    name: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DatasetExample:
    """Lightweight dataset example for the SDK (no backend validation)."""

    input: Dict[str, Any]
    output: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    source_trace_id: Optional[str] = None
    source_node_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        # Ensure metadata mirrors tags and source fields
        meta = dict(self.metadata or {})
        if not self.tags and meta.get("tags"):
            self.tags = list(meta.get("tags", []))
        if self.tags:
            meta["tags"] = list(self.tags)
        if self.source_trace_id:
            meta.setdefault("source_trace_id", self.source_trace_id)
        if self.source_node_id:
            meta.setdefault("source_node_id", self.source_node_id)
        self.metadata = meta

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        if name == "tags":
            meta = dict(getattr(self, "metadata", {}) or {})
            if value:
                meta["tags"] = list(value)
            elif value is None:
                meta.pop("tags", None)
            # If value is empty list, keep existing metadata tags as-is
            super().__setattr__("metadata", meta)
        elif name in {"source_trace_id", "source_node_id"}:
            meta = dict(getattr(self, "metadata", {}) or {})
            if value is not None:
                meta[name] = value
            else:
                meta.pop(name, None)
            super().__setattr__("metadata", meta)


Example = DatasetExample


@dataclass
class DatasetImport:
    """Complete dataset with examples for import."""

    name: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    examples: List[DatasetExample] = field(default_factory=list)


@dataclass
class Dataset:
    """A dataset retrieved from the API."""

    id: str
    name: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    example_count: int = 0
    version: int = 1
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    examples: List[Example] = field(default_factory=list)


@dataclass
class EvaluationMetric:
    """Evaluation metric result with name, score, and metadata."""

    name: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


# Backwards compatibility alias
EvaluatorResult = EvaluationMetric


def _extract_evaluator_result(result: Any, evaluator_name: str) -> tuple[str, float, Dict[str, Any]]:
    """Extract name, score and metadata from various evaluator return types.

    Supported return types:
    - float: Just a score
    - tuple[float, dict]: Score and metadata dictionary
    - EvaluationMetric: Structured result object (preferred)
    - EvaluatorResult: Legacy alias for EvaluationMetric
    """
    if isinstance(result, (EvaluationMetric, EvaluatorResult)):
        name = getattr(result, "name", evaluator_name)  # Use evaluator_name as fallback
        return name, result.score, result.metadata
    elif isinstance(result, tuple):
        if len(result) == 2:
            score, metadata = result
            if isinstance(score, (int, float)):
                if isinstance(metadata, dict):
                    return evaluator_name, float(score), metadata
                else:
                    # Convert non-dict metadata to dict with "reason" key
                    return evaluator_name, float(score), {"reason": str(metadata)}
            else:
                raise ValueError(
                    f"Invalid tuple format for {evaluator_name}: Expected (float, dict) or (float, str), got ({type(score)}, {type(metadata)})"
                )
        else:
            raise ValueError(f"Invalid tuple length for {evaluator_name}: Expected 2 elements, got {len(result)}")
    elif isinstance(result, (int, float)):
        return evaluator_name, float(result), {}
    else:
        raise ValueError(
            f"Invalid evaluator return type for {evaluator_name}: Expected float, tuple[float, dict], or EvaluationMetric, got {type(result)}"
        )


class CATCafeClient:
    """Client for running external experiments against CAT."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        project_id: str = "default",
        session=None,
    ):
        self.base_url = base_url
        # project_id kept for backward compatibility but no longer used in URLs
        self.project_id = project_id
        self._session: Optional[Any] = session  # For testing or custom sessions
        self.offline_mode = "warn"  # Can be set later

    def _build_api_url(self, endpoint: str) -> str:
        """Build API URL for an endpoint."""
        # Remove leading slash if present
        endpoint = endpoint.lstrip("/")
        return f"/api/{endpoint}"

    @staticmethod
    def _segment(value: str) -> str:
        """URL-encode a single path segment."""
        return quote(value, safe="")

    def _make_request(self, method: str, url: str, **kwargs):
        """Make HTTP request using either httpx client or test client."""
        if self._session:
            # Use test client (for testing)
            if method.upper() == "GET":
                return self._session.get(url, **kwargs)
            elif method.upper() == "POST":
                return self._session.post(url, **kwargs)
            elif method.upper() == "PUT":
                return self._session.put(url, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        else:
            # Use httpx client
            full_url = f"{self.base_url}{url}"
            with httpx.Client() as client:
                if method.upper() == "GET":
                    return client.get(full_url, **kwargs)
                elif method.upper() == "POST":
                    return client.post(full_url, **kwargs)
                elif method.upper() == "PUT":
                    return client.put(full_url, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

    @staticmethod
    def _hydrate_dataset_metadata(metadata: Optional[Dict[str, Any]], tags: List[str]) -> Dict[str, Any]:
        """Ensure dataset metadata mirrors important top-level fields for downstream tooling."""

        base: Dict[str, Any] = dict(metadata or {})
        if tags and "tags" not in base:
            base["tags"] = list(tags)
        return base

    def get_dataset(self, dataset_id: str, version: Optional[str] = None) -> Dict:
        """Fetch dataset examples from CAT server."""
        url = self._build_api_url(f"datasets/{dataset_id}/examples")
        params = {"version": version} if version else {}
        response = self._make_request("GET", url, params=params)
        response.raise_for_status()
        return response.json()

    def start_experiment(self, experiment_config: Experiment) -> str:
        """Create experiment record, returns experiment_id."""
        url = self._build_api_url("experiments")
        response = self._make_request(
            "POST",
            url,
            json={
                "name": experiment_config.name,
                "description": experiment_config.description,
                "dataset_id": experiment_config.dataset_id,
                "dataset_version": experiment_config.dataset_version,
                "tags": experiment_config.tags,
                "metadata": experiment_config.metadata,
            },
        )
        response.raise_for_status()
        return response.json()["experiment_id"]

    def get_experiment(self, experiment_id: str) -> Dict:
        """Get experiment details."""
        url = self._build_api_url(f"experiments/{experiment_id}")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()

    def create_run(self, experiment_id: str, payload: Dict[str, Any]) -> Dict:
        """Create or overwrite a run (task result) for an experiment."""
        url = self._build_api_url(f"experiments/{experiment_id}/runs")
        response = self._make_request("PUT", url, json=payload)
        response.raise_for_status()
        return response.json()

    def list_runs(self, experiment_id: str) -> List[Dict]:
        """List runs (task + evaluations) for an experiment."""
        url = self._build_api_url(f"experiments/{experiment_id}/runs")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json().get("runs", [])

    def get_run(self, experiment_id: str, run_id: str) -> Dict:
        """Get a single run by run_id."""
        encoded_run = self._segment(run_id)
        url = self._build_api_url(f"experiments/{experiment_id}/runs/{encoded_run}")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()

    def append_evaluation(self, experiment_id: str, run_id: str, payload: Dict[str, Any]) -> Dict:
        """Append/upsert an evaluation for a run."""
        encoded_run = self._segment(run_id)
        url = self._build_api_url(f"experiments/{experiment_id}/runs/{encoded_run}/evaluations")
        response = self._make_request("PUT", url, json=payload)
        response.raise_for_status()
        return response.json()

    def list_evaluations(self, experiment_id: str, run_id: str) -> List[Dict]:
        """List evaluations for a run."""
        encoded_run = self._segment(run_id)
        url = self._build_api_url(f"experiments/{experiment_id}/runs/{encoded_run}/evaluations")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()

    def complete_experiment(self, experiment_id: str, summary: Optional[Dict[str, Any]] = None):
        """Mark experiment as completed."""
        url = self._build_api_url(f"experiments/{experiment_id}/complete")
        response = self._make_request("POST", url, json={"summary": summary or {}})
        response.raise_for_status()

    def list_experiments(self) -> List[Dict]:
        """List all experiments."""
        url = self._build_api_url("experiments")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()["experiments"]

    def list_experiments_by_dataset(self, dataset_id: str) -> List[Dict]:
        """List experiments for a specific dataset."""
        url = self._build_api_url(f"datasets/{dataset_id}/experiments")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()["experiments"]

    def compare_experiments(self, experiment_a: str, experiment_b: str) -> Dict:
        """Compare two experiments side-by-side.

        Args:
            experiment_a: ID of the first experiment
            experiment_b: ID of the second experiment

        Returns:
            Comparison data including results and summary statistics
        """
        url = self._build_api_url("experiments/compare")
        params = {"experiment_a": experiment_a, "experiment_b": experiment_b}
        response = self._make_request("GET", url, params=params)
        response.raise_for_status()
        return response.json()

    def get_experiment_timeline(self, dataset_id: str) -> Dict:
        """Get timeline data for experiments on a dataset.

        Returns timeline data optimized for visualization including
        aggregated metrics and experiment metadata.
        """
        url = self._build_api_url(f"datasets/{dataset_id}/experiments/timeline")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()

    def get_evaluation_metrics(self) -> List[Dict]:
        """Get available evaluation metrics from CAT."""
        url = self._build_api_url("evaluation-metrics")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()["metrics"]

    def create_dataset(self, dataset: DatasetConfig) -> str:
        """Create a new dataset and return its ID."""
        url = self._build_api_url("datasets")
        response = self._make_request(
            "POST",
            url,
            json={
                "name": dataset.name,
                "description": dataset.description,
                "tags": dataset.tags,
                "metadata": self._hydrate_dataset_metadata(dataset.metadata, dataset.tags),
            },
        )
        response.raise_for_status()
        return response.json()["id"]

    def get_dataset_info(self, dataset_id: str) -> Dict:
        """Get dataset information by ID."""
        url = self._build_api_url(f"datasets/{dataset_id}")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()

    def add_dataset_example(self, dataset_id: str, example: DatasetExample) -> str:
        """Add an example to a dataset and return the example ID."""
        url = self._build_api_url(f"datasets/{dataset_id}/examples")
        response = self._make_request(
            "POST",
            url,
            json={
                "input": example.input,
                "output": example.output,
                "tags": example.tags,
                "metadata": example.metadata,
            },
        )
        response.raise_for_status()
        return response.json()["example_id"]

    def get_dataset_examples(self, dataset_id: str, version: Optional[str] = None) -> List[Dict]:
        """Get examples from a dataset."""
        url = self._build_api_url(f"datasets/{dataset_id}/examples")
        params = {"version": version} if version else {}
        response = self._make_request("GET", url, params=params)
        response.raise_for_status()
        return response.json()

    def list_datasets(self) -> List[Dict]:
        """List all datasets."""
        url = self._build_api_url("datasets")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()

    def add_example_from_trace(
        self,
        dataset_id: str,
        trace_id: str,
        node_id: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a dataset example from a trace span.

        Args:
            dataset_id: Target dataset ID
            trace_id: Tempo trace identifier
            node_id: LLM span node ID within the trace
            tags: Optional tags to annotate the new example
            metadata: Optional metadata to merge into the example

        Returns:
            Response payload from the API including the created example and updated dataset metadata.
        """

        payload = {
            "trace_id": trace_id,
            "node_id": node_id,
            "tags": tags or [],
            "metadata": metadata or {},
        }

        url = self._build_api_url(f"datasets/{dataset_id}/examples/from-span")
        response = self._make_request("POST", url, json=payload)
        response.raise_for_status()

        result = response.json()

        return result

    def find_dataset_by_name(self, name: str) -> Optional[Dict]:
        """Find a dataset by name. Returns None if not found."""
        datasets = self.list_datasets()
        for dataset in datasets:
            if dataset.get("name") == name:
                return dataset
        return None

    def fetch_dataset(self, dataset_id: str, version: Optional[str] = None) -> Dataset:
        """Fetch a complete dataset with its examples as structured objects.

        Args:
            dataset_id: The dataset ID to fetch
            version: Optional specific version to fetch

        Returns:
            Dataset object with examples
        """
        try:
            # Get dataset info
            dataset_info = self.get_dataset_info(dataset_id)

            # Get examples
            examples_data = self.get_dataset_examples(dataset_id, version=version)

            # Convert examples to structured objects
            examples = []
            for example_data in examples_data:
                metadata = dict(example_data.get("metadata", {}))
                if "tags" in example_data:
                    metadata.setdefault("tags", example_data.get("tags", []))
                if example_data.get("source_trace_id") is not None:
                    metadata["source_trace_id"] = example_data["source_trace_id"]
                if example_data.get("source_node_id") is not None:
                    metadata["source_node_id"] = example_data["source_node_id"]

                example = Example(
                    input=example_data.get("input", {}),
                    output=example_data.get("output", {}),
                    metadata=metadata,
                    id=example_data.get("id"),
                    created_at=example_data.get("created_at"),
                    updated_at=example_data.get("updated_at"),
                )
                examples.append(example)

            # Create structured dataset object
            dataset = Dataset(
                id=dataset_info["id"],
                name=dataset_info["name"],
                description=dataset_info.get("description"),
                tags=dataset_info.get("tags", []),
                metadata=dict(dataset_info.get("metadata", {})),
                example_count=dataset_info.get("example_count", 0),
                version=dataset_info.get("version", 1),
                created_at=dataset_info.get("created_at"),
                updated_at=dataset_info.get("updated_at"),
                examples=examples,
            )

            return dataset

        except Exception:
            # Re-raise if no cache available
            raise

    def fetch_dataset_by_name(self, name: str) -> Optional[Dataset]:
        """Fetch a complete dataset by name with its examples as structured objects."""
        dataset_info = self.find_dataset_by_name(name)
        if not dataset_info:
            return None

        return self.fetch_dataset(dataset_info["id"])

    def import_dataset(self, dataset_import: DatasetImport) -> Dict:
        """Import a complete dataset with examples in one API call."""
        url = self._build_api_url("datasets/import")

        # Convert DatasetExample objects to dictionaries
        examples_data = []
        for example in dataset_import.examples:
            input_payload = example.input
            if isinstance(input_payload, dict) and "messages" in input_payload:
                input_payload = input_payload["messages"]

            output_payload = example.output
            if isinstance(output_payload, dict) and "messages" in output_payload:
                output_payload = output_payload["messages"]

            example_dict = {
                "input": input_payload,
                "output": output_payload,
                "tags": list(example.tags),
                "metadata": example.metadata,
            }
            # Add source fields if present
            if example.source_trace_id is not None:
                example_dict["source_trace_id"] = example.source_trace_id
            if example.source_node_id is not None:
                example_dict["source_node_id"] = example.source_node_id
            examples_data.append(example_dict)

        response = self._make_request(
            "POST",
            url,
            json={
                "name": dataset_import.name,
                "description": dataset_import.description,
                "tags": dataset_import.tags,
                "metadata": dataset_import.metadata,
                "examples": examples_data,
            },
        )
        response.raise_for_status()
        return response.json()

    def _prepare_dataset(self, dataset: Union[Dataset, str, Dict]) -> Dataset:
        """Prepare dataset object from various input types."""
        if isinstance(dataset, str):
            # Fetch dataset by ID
            return self.fetch_dataset(dataset)
        elif isinstance(dataset, dict):
            # Convert dict to Dataset object
            return self._dataset_from_dict(dataset)
        else:
            # Already a Dataset object
            return dataset

    def _dataset_from_dict(self, dataset_dict: Dict) -> Dataset:
        """Convert a dictionary to a Dataset object."""
        examples = []
        for ex_data in dataset_dict.get("examples", []):
            metadata = dict(ex_data.get("metadata", {}))
            if "tags" in ex_data:
                metadata.setdefault("tags", ex_data.get("tags", []))
            if ex_data.get("source_trace_id") is not None:
                metadata["source_trace_id"] = ex_data["source_trace_id"]
            if ex_data.get("source_node_id") is not None:
                metadata["source_node_id"] = ex_data["source_node_id"]
            example = Example(
                input=ex_data.get("input", {}),
                output=ex_data.get("output", {}),
                metadata=metadata,
                id=ex_data.get("id"),
                created_at=ex_data.get("created_at"),
                updated_at=ex_data.get("updated_at"),
            )
            examples.append(example)

        return Dataset(
            id=dataset_dict.get("id", "unknown"),
            name=dataset_dict.get("name", "Unknown Dataset"),
            description=dataset_dict.get("description"),
            tags=dataset_dict.get("tags", []),
            metadata=dataset_dict.get("metadata", {}),
            example_count=len(examples),
            version=dataset_dict.get("version", 1),
            examples=examples,
        )

    def _dataset_from_cache_data(self, cache_data: Dict) -> Dataset:
        """Convert cached dataset data to Dataset object."""
        examples = []
        for ex_data in cache_data.get("examples", []):
            metadata = dict(ex_data.get("metadata", {}))
            if "tags" in ex_data:
                metadata.setdefault("tags", ex_data.get("tags", []))
            if ex_data.get("source_trace_id") is not None:
                metadata["source_trace_id"] = ex_data["source_trace_id"]
            if ex_data.get("source_node_id") is not None:
                metadata["source_node_id"] = ex_data["source_node_id"]
            example = Example(
                input=ex_data.get("input", {}),
                output=ex_data.get("output", {}),
                metadata=metadata,
                id=ex_data.get("id"),
                created_at=ex_data.get("created_at"),
                updated_at=ex_data.get("updated_at"),
            )
            examples.append(example)

        return Dataset(
            id=cache_data["id"],
            name=cache_data["name"],
            description=cache_data.get("description"),
            tags=cache_data.get("tags", []),
            metadata=cache_data.get("metadata", {}),
            example_count=cache_data.get("example_count", len(examples)),
            version=cache_data.get("version", 1),
            examples=examples,
        )

    def _apply_sampling(self, dataset: Dataset, sample_rate: float, random_seed: Optional[int] = None) -> Dataset:
        """Apply sampling to dataset examples based on sample_rate.

        For N examples:
        - sample_rate = 0.3: Run 30% of examples once (0.3 * N examples)
        - sample_rate = 1.0: Run each example once (N examples)
        - sample_rate = 1.3: Run each example once + 30% again (1.3 * N total runs)
        - sample_rate = 2.7: Run each example twice + 70% a third time (2.7 * N total runs)

        Args:
            dataset: Original dataset
            sample_rate: Float indicating sampling rate
            random_seed: Random seed for deterministic sampling

        Returns:
            Dataset with sampled examples
        """
        import random

        if random_seed is not None:
            random.seed(random_seed)

        examples = dataset.examples
        total_examples = len(examples)

        if sample_rate <= 0:
            # No examples to run
            return Dataset(
                id=dataset.id,
                name=dataset.name,
                description=dataset.description,
                metadata={**dataset.metadata, "sample_rate": sample_rate, "random_seed": random_seed},
                example_count=0,
                version=dataset.version,
                created_at=dataset.created_at,
                updated_at=dataset.updated_at,
                examples=[],
            )

        # Calculate total runs we want
        target_total_runs = int(sample_rate * total_examples)

        sampled_examples = []

        if sample_rate < 1.0:
            # Run subset of examples once
            num_to_run = target_total_runs
            selected_examples = random.sample(examples, min(num_to_run, total_examples))
            sampled_examples = selected_examples

        else:
            # Run each example at least floor(sample_rate) times
            base_runs_per_example = int(sample_rate)

            # Add base runs for each example
            for example in examples:
                for run_num in range(base_runs_per_example):
                    if base_runs_per_example == 1:
                        # Single run - keep original example
                        sampled_examples.append(example)
                    else:
                        # Multiple runs - create copy with unique ID
                        sampled_example = Example(
                            id=f"{example.id}_run_{run_num + 1}",
                            input=example.input,
                            output=example.output,
                            source_trace_id=example.source_trace_id,
                            source_node_id=example.source_node_id,
                            metadata={**example.metadata, "sample_run": run_num + 1, "original_id": example.id},
                            tags=example.tags + [f"run_{run_num + 1}"],
                            created_at=example.created_at,
                            updated_at=example.updated_at,
                        )
                        sampled_examples.append(sampled_example)

            # Calculate how many additional runs we need
            runs_so_far = total_examples * base_runs_per_example
            additional_runs_needed = target_total_runs - runs_so_far

            # Add additional runs by randomly selecting examples
            if additional_runs_needed > 0:
                additional_examples = random.sample(examples, min(additional_runs_needed, total_examples))
                for example in additional_examples:
                    sampled_example = Example(
                        id=f"{example.id}_run_{base_runs_per_example + 1}",
                        input=example.input,
                        output=example.output,
                        source_trace_id=example.source_trace_id,
                        source_node_id=example.source_node_id,
                        metadata={
                            **example.metadata,
                            "sample_run": base_runs_per_example + 1,
                            "original_id": example.id,
                        },
                        tags=example.tags + [f"run_{base_runs_per_example + 1}"],
                        created_at=example.created_at,
                        updated_at=example.updated_at,
                    )
                    sampled_examples.append(sampled_example)

        # Return new dataset with sampled examples
        return Dataset(
            id=dataset.id,
            name=dataset.name,
            description=dataset.description,
            metadata={**dataset.metadata, "sample_rate": sample_rate, "random_seed": random_seed},
            example_count=len(sampled_examples),
            version=dataset.version,
            created_at=dataset.created_at,
            updated_at=dataset.updated_at,
            examples=sampled_examples,
        )
