from pathlib import Path

from schemas.base import SchemaDefinition
from dspy_components.tasks.reference_standard.modules import AsyncReferenceStandardPipeline
from dspy_components.tasks.reference_standard.signatures import CombineReferenceStandardData


def _build_pipeline():
    return AsyncReferenceStandardPipeline()


# Define target file for field generation (if cache missing)
CACHE_FILE = "schemas/generated_fields/reference_standard_fields.json"


REFERENCE_STANDARD_SCHEMA = SchemaDefinition(
    name="reference_standard",
    description="Reference standard and biopsy information extraction schema.",
    signature_class=CombineReferenceStandardData,
    output_field_name="complete_reference_standard_json",
    field_cache_file=CACHE_FILE,
    pipeline_factory=_build_pipeline,
)
