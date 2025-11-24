from pathlib import Path

from schemas.base import SchemaDefinition
from dspy_components.tasks.outcomes_study.modules import AsyncOutcomesPipeline
from dspy_components.tasks.outcomes_study.signatures import CombineOutcomesData


def _build_pipeline():
    return AsyncOutcomesPipeline()


# Define target file for field generation (if cache missing)
CACHE_FILE = "schemas/generated_fields/outcomes_study_fields.json"


OUTCOMES_STUDY_SCHEMA = SchemaDefinition(
    name="outcomes_study",
    description="Outcomes study diagnostic test performance extraction schema.",
    signature_class=CombineOutcomesData,
    output_field_name="complete_outcomes_json",
    field_cache_file=CACHE_FILE,
    pipeline_factory=_build_pipeline,
)
