from dataclasses import dataclass
from typing import Any

from core.config import DEFAULT_OUTPUT_DIR, DEFAULT_CSV_DIR, DEFAULT_JSON_DIR
from core.evaluation import AsyncMedicalExtractionEvaluator
from core.file_handler import AsyncMedicalFileHandler
from schemas.base import SchemaDefinition


@dataclass
class SchemaRuntime:
    """Runtime components for a specific schema."""
    schema: SchemaDefinition
    pipeline: Any
    evaluator: Any
    file_handler: Any

    def close(self) -> None:
        """Release any resources held by runtime components."""
        self.evaluator.close()


def build_schema_runtime(definition: SchemaDefinition, target_file: str = None) -> SchemaRuntime:
    """
    Instantiate pipeline, evaluator, and file handler for a schema definition.
    """
    pipeline = definition.pipeline_factory()
    evaluator = AsyncMedicalExtractionEvaluator(
        signature_class=definition.signature_class,
        output_field_name=definition.output_field_name,
        field_cache_file=definition.field_cache_file,
        target_file=target_file,
        use_semantic=True,
        max_concurrent=10,
        cache_dir="."
    )
    file_handler = AsyncMedicalFileHandler(
        default_output_dir=DEFAULT_OUTPUT_DIR,
        default_csv_dir=DEFAULT_CSV_DIR,
        default_json_dir=DEFAULT_JSON_DIR,
        csv_filename=f"{definition.name}_evaluation_results.csv",
        json_filename=f"{definition.name}_evaluation_results.json",
        schema_name=definition.name
    )
    return SchemaRuntime(
        schema=definition,
        pipeline=pipeline,
        evaluator=evaluator,
        file_handler=file_handler
    )
