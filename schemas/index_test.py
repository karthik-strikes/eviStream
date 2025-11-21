from pathlib import Path

from schemas.base import SchemaDefinition
from dspy_components.tasks.index_test.modules import AsyncIndexTestPipeline
from dspy_components.tasks.index_test.signatures import IndexTestRecord


def _build_pipeline():
    return AsyncIndexTestPipeline()


# Define target file for field generation (if cache missing)
CACHE_FILE = "schemas/generated_fields/index_test_fields.json"


INDEX_TEST_SCHEMA = SchemaDefinition(
    name="index_test",
    description="Index test characteristics extraction schema.",
    signature_class=IndexTestRecord,
    output_field_name="index_test_json",
    field_cache_file=CACHE_FILE,
    pipeline_factory=_build_pipeline,
)
