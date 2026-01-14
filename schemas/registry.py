"""
Schema Registry

Unified registry for dynamic schemas.
Stores DynamicSchemaConfig objects for lookup and discovery.
"""

from typing import Dict, List
from .config import DynamicSchemaConfig

# In-memory registry (can be backed by database later)
_SCHEMA_REGISTRY: Dict[str, DynamicSchemaConfig] = {}


def register_schema(config: DynamicSchemaConfig) -> None:
    """
    Register a dynamic schema in the registry.

    Args:
        config: DynamicSchemaConfig to register
    """
    is_new = config.schema_name not in _SCHEMA_REGISTRY
    _SCHEMA_REGISTRY[config.schema_name] = config


def get_schema(schema_name: str) -> DynamicSchemaConfig:
    """
    Get schema configuration by name.

    Args:
        schema_name: Name of the schema

    Returns:
        DynamicSchemaConfig object

    Raises:
        ValueError: If schema not found
    """
    if schema_name not in _SCHEMA_REGISTRY:
        available = sorted(_SCHEMA_REGISTRY.keys())
        raise ValueError(
            f"Unknown schema '{schema_name}'. Available: {', '.join(available)}"
        )
    return _SCHEMA_REGISTRY[schema_name]


def list_schemas() -> List[str]:
    """
    List all registered schema names.

    Returns:
        Sorted list of schema names
    """
    return sorted(_SCHEMA_REGISTRY.keys())


def refresh_registry():
    """
    Refresh registry (placeholder for future database-backed loading).

    Returns:
        List of schema names
    """
    # Future: Load from database
    return list_schemas()
