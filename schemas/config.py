"""
Dynamic Schema Configuration

Self-contained configuration for dynamically generated schemas.
Stores all information needed to build and execute extraction pipelines.
"""

import importlib
import asyncio
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import dspy


@dataclass(frozen=True)
class DynamicSchemaConfig:
    """
    Configuration for dynamically generated schemas.

    Stores all information needed to:
    - Build extraction pipeline following decomposition stages
    - Load signature classes on demand
    - Discover output fields at runtime
    """

    # Identity
    schema_name: str  # Human-readable name (e.g., "ClinicalSummary")
    task_name: str    # Technical name (e.g., "task_4bc4179e")

    # Paths (for lazy loading)
    module_path: str  # e.g., "dspy_components.tasks.task_4bc4179e"
    signatures_path: str  # e.g., "dspy_components.tasks.task_4bc4179e.signatures"

    # Signatures (from decomposition.signatures)
    signature_class_names: List[str]  # All signature names in order

    # Pipeline Structure (from decomposition.pipeline)
    pipeline_stages: List[Dict[str, Any]]  # Execution stages with dependencies

    # Metadata
    project_id: str
    form_id: str
    form_name: str

    def load_signature_class(self, signature_name: str) -> Any:
        """Load a specific signature class by name."""
        signatures_module = importlib.import_module(self.signatures_path)
        return getattr(signatures_module, signature_name)

    def load_all_signature_classes(self) -> List[Any]:
        """Load all signature classes."""
        signatures_module = importlib.import_module(self.signatures_path)
        return [getattr(signatures_module, name) for name in self.signature_class_names]

    def build_pipeline(self) -> Any:
        """
        Build extraction pipeline following pipeline_stages structure.

        Respects:
        - Stage execution order
        - Parallel vs sequential execution within stages
        - Field dependencies between stages
        """
        return self._build_staged_pipeline()

    def _build_staged_pipeline(self) -> Any:
        """Build pipeline that follows pipeline_stages execution order."""
        modules_module = importlib.import_module(f"{self.module_path}.modules")

        # Map signature names to extractor instances
        extractors = {}
        for sig_name in self.signature_class_names:
            extractor_name = f"Async{sig_name}Extractor"
            if hasattr(modules_module, extractor_name):
                extractor_class = getattr(modules_module, extractor_name)
                extractors[sig_name] = extractor_class()
            else:
                print(
                    f"Warning: Extractor {extractor_name} not found in {self.module_path}.modules")

        if not extractors:
            raise ValueError(
                f"No extractors found for schema {self.schema_name}. Available classes: {[n for n in dir(modules_module) if not n.startswith('_')]}")

        class StagedPipeline(dspy.Module):
            """Pipeline that executes stages in order with dependency handling."""

            def __init__(self, stages, extractors_map):
                super().__init__()
                self.stages = stages
                self.extractors = extractors_map

            async def __call__(self, markdown_content: str, **kwargs):
                """
                Execute pipeline following stage order.

                Accumulates results from each stage and passes them to dependent stages.
                """
                accumulated_results = {}

                # Execute each stage in order
                for stage_info in self.stages:
                    stage_num = stage_info.get("stage", 0)
                    signature_names = stage_info.get("signatures", [])
                    execution_mode = stage_info.get("execution", "parallel")

                    # Get extractors for this stage
                    stage_extractors = [
                        (sig_name, self.extractors[sig_name])
                        for sig_name in signature_names
                        if sig_name in self.extractors
                    ]

                    if not stage_extractors:
                        print(
                            f"Warning: No extractors found for stage {stage_num} with signatures {signature_names}")
                        continue

                    # Merge accumulated results into kwargs for dependent signatures
                    stage_kwargs = {**kwargs, **accumulated_results}

                    if execution_mode == "parallel":
                        # Run all extractors in parallel
                        results = await asyncio.gather(
                            *[
                                extractor(markdown_content, **stage_kwargs)
                                for sig_name, extractor in stage_extractors
                            ],
                            return_exceptions=True
                        )

                        # Merge results from all extractors in this stage
                        for i, result in enumerate(results):
                            if isinstance(result, dict):
                                accumulated_results.update(result)
                            elif isinstance(result, Exception):
                                print(
                                    f"Warning: Extractor {stage_extractors[i][0]} failed: {result}")
                            else:
                                # Handle dspy.Prediction or other types
                                if hasattr(result, '__dict__'):
                                    # Convert dspy.Prediction to dict
                                    result_dict = {
                                        k: v for k, v in result.__dict__.items() if not k.startswith('_')}
                                    accumulated_results.update(result_dict)
                                else:
                                    print(
                                        f"Warning: Extractor {stage_extractors[i][0]} returned unexpected type: {type(result)}")
                    else:  # sequential
                        # Run extractors one by one, passing accumulated results forward
                        for sig_name, extractor in stage_extractors:
                            try:
                                result = await extractor(markdown_content, **stage_kwargs)
                                if isinstance(result, dict):
                                    accumulated_results.update(result)
                                    # Update kwargs for next extractor in sequence
                                    stage_kwargs.update(result)
                                elif hasattr(result, '__dict__'):
                                    # Convert dspy.Prediction to dict
                                    result_dict = {
                                        k: v for k, v in result.__dict__.items() if not k.startswith('_')}
                                    accumulated_results.update(result_dict)
                                    stage_kwargs.update(result_dict)
                            except Exception as e:
                                print(
                                    f"Warning: Extractor {sig_name} failed: {e}")
                                import traceback
                                traceback.print_exc()

                # Return final accumulated results
                return accumulated_results

        return StagedPipeline(self.pipeline_stages, extractors)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for database/JSON storage."""
        return {
            "schema_name": self.schema_name,
            "task_name": self.task_name,
            "module_path": self.module_path,
            "signatures_path": self.signatures_path,
            "signature_class_names": self.signature_class_names,
            "pipeline_stages": self.pipeline_stages,
            "project_id": self.project_id,
            "form_id": self.form_id,
            "form_name": self.form_name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DynamicSchemaConfig":
        """Deserialize from dict (database/JSON)."""
        return cls(**data)
