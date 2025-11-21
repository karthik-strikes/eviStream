from pathlib import Path

from schemas.base import SchemaDefinition
from config import DEFAULT_JSON_DIR
from dspy_components.tasks.patient_population.modules import AsyncPatientPopulationCharacteristicsPipeline
from dspy_components.tasks.patient_population.signatures import CombinePatientPopulationCharacteristics


def _build_pipeline():
    return AsyncPatientPopulationCharacteristicsPipeline()


# Define target file for field generation (if cache missing)
CACHE_FILE = "schemas/generated_fields/patient_population_fields.json"


PATIENT_POPULATION_SCHEMA = SchemaDefinition(
    name="patient_population",
    description="Patient population characteristics extraction schema.",
    signature_class=CombinePatientPopulationCharacteristics,
    output_field_name="complete_characteristics_json",
    field_cache_file=CACHE_FILE,
    pipeline_factory=_build_pipeline,
)
