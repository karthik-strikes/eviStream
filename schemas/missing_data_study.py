from pathlib import Path

from schemas.base import SchemaDefinition
from dspy_components.tasks.missing_data_study.modules import AsyncMissingDataPipeline
from dspy_components.tasks.missing_data_study.signatures import CombineMissingData


def _build_pipeline():
    return AsyncMissingDataPipeline()


# Define target file for field generation (if cache missing)
CACHE_FILE = "schemas/generated_fields/missing_data_study_fields.json"


MISSING_DATA_STUDY_SCHEMA = SchemaDefinition(
    name="missing_data_study",
    description="Missing data and partial verification extraction schema.",
    signature_class=CombineMissingData,
    output_field_name="complete_missing_data_json",
    field_cache_file=CACHE_FILE,
    pipeline_factory=_build_pipeline,
)
