from typing import Dict, List

from .base import SchemaDefinition
from .configs import get_all_schema_definitions

# Use a mutable container so we can update the reference
_SCHEMA_REGISTRY_CONTAINER = {'registry': get_all_schema_definitions()}


def _get_registry() -> Dict[str, SchemaDefinition]:
    """Get the current schema registry."""
    return _SCHEMA_REGISTRY_CONTAINER['registry']


def get_schema(schema_name: str) -> SchemaDefinition:
    """Return schema definition by name."""
    registry = _get_registry()
    try:
        return registry[schema_name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown schema '{schema_name}'. Available: {', '.join(registry.keys())}"
        ) from exc


def list_schemas() -> List[str]:
    """List available schema names."""
    return sorted(_get_registry().keys())


def list_available_schemas() -> List[str]:
    """Alias for list_schemas() - list available schema names."""
    return list_schemas()


def refresh_registry():
    """Refresh the schema registry from configs."""
    _SCHEMA_REGISTRY_CONTAINER['registry'] = get_all_schema_definitions()
    return list_schemas()
