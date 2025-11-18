from pathlib import Path

from schemas.base import SchemaDefinition
from schemas.field_utils import load_or_create_field_config
from dspy_components.modules import AsyncPatientPopulationCharacteristicsPipeline
from dspy_components.signatures import CombinePatientPopulationCharacteristics
from config import DEFAULT_JSON_DIR


def _build_pipeline():
    return AsyncPatientPopulationCharacteristicsPipeline()


def _load_field_config():
    target_file = str(
        Path(DEFAULT_JSON_DIR) / "patient_population_evaluation_results.json"
    )
    return load_or_create_field_config(
        signature_class=CombinePatientPopulationCharacteristics,
        cache_filename="patient_population_fields.json",
        target_file=target_file,
        output_field_name="complete_characteristics_json",
        verbose=False
    )


REQUIRED_FIELDS, SEMANTIC_FIELDS, EXACT_FIELDS, GROUPABLE_PATTERNS = _load_field_config()


PATIENT_POPULATION_SCHEMA = SchemaDefinition(
    name="patient_population",
    description="Patient population characteristics extraction schema.",
    required_fields=REQUIRED_FIELDS,
    semantic_fields=SEMANTIC_FIELDS,
    exact_fields=EXACT_FIELDS,
    groupable_patterns=GROUPABLE_PATTERNS,
    pipeline_factory=_build_pipeline,
    csv_filename="patient_population_evaluation_results.csv",
    json_filename="patient_population_evaluation_results.json",
)
