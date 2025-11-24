from typing import Dict, List

from .patient_population import PATIENT_POPULATION_SCHEMA
from .index_test import INDEX_TEST_SCHEMA
from .outcomes_study import OUTCOMES_STUDY_SCHEMA
from .missing_data_study import MISSING_DATA_STUDY_SCHEMA
from .reference_standard import REFERENCE_STANDARD_SCHEMA
from .base import SchemaDefinition

_SCHEMA_REGISTRY: Dict[str, SchemaDefinition] = {
    "patient_population": PATIENT_POPULATION_SCHEMA,
    "index_test": INDEX_TEST_SCHEMA,
    "outcomes_study": OUTCOMES_STUDY_SCHEMA,
    "missing_data_study": MISSING_DATA_STUDY_SCHEMA,
    "reference_standard": REFERENCE_STANDARD_SCHEMA,
}


def get_schema(schema_name: str) -> SchemaDefinition:
    """Return schema definition by name."""
    try:
        return _SCHEMA_REGISTRY[schema_name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown schema '{schema_name}'. Available: {', '.join(_SCHEMA_REGISTRY.keys())}"
        ) from exc


def list_schemas() -> List[str]:
    """List available schema names."""
    return sorted(_SCHEMA_REGISTRY.keys())
