from dataclasses import dataclass

from config import DEFAULT_OUTPUT_DIR, DEFAULT_CSV_DIR, DEFAULT_JSON_DIR
from src.evaluation import AsyncMedicalExtractionEvaluator
from src.file_handler import AsyncMedicalFileHandler
from schemas.base import SchemaDefinition


@dataclass
class SchemaRuntime:
    """Live objects needed to run extraction/evaluation for a schema."""

    definition: SchemaDefinition
    pipeline: object
    evaluator: AsyncMedicalExtractionEvaluator
    file_handler: AsyncMedicalFileHandler

    def close(self) -> None:
        """Release any resources held by runtime components."""
        self.evaluator.close()


def build_schema_runtime(definition: SchemaDefinition) -> SchemaRuntime:
    """
    Instantiate pipeline, evaluator, and file handler for a schema definition.
    """
    pipeline = definition.pipeline_factory()
    evaluator = AsyncMedicalExtractionEvaluator(
        required_fields=definition.required_fields,
        semantic_fields=definition.semantic_fields,
        exact_fields=definition.exact_fields,
        groupable_patterns=definition.groupable_patterns,
        use_semantic=True,
        max_concurrent=10,
        cache_dir="."
    )
    file_handler = AsyncMedicalFileHandler(
        default_output_dir=DEFAULT_OUTPUT_DIR,
        default_csv_dir=DEFAULT_CSV_DIR,
        default_json_dir=DEFAULT_JSON_DIR,
        csv_filename=definition.csv_filename,
        json_filename=definition.json_filename
    )
    return SchemaRuntime(
        definition=definition,
        pipeline=pipeline,
        evaluator=evaluator,
        file_handler=file_handler
    )
