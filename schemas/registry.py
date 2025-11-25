from typing import Dict, List

from .base import SchemaDefinition
from .configs import get_all_schema_definitions

_SCHEMA_REGISTRY: Dict[str, SchemaDefinition] = get_all_schema_definitions()


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
