from dataclasses import dataclass
from typing import Callable, Dict, List, Any


@dataclass(frozen=True)
class SchemaDefinition:
    """Configuration bundle describing a single systematic-review schema."""

    name: str
    description: str
    required_fields: List[str]
    semantic_fields: List[str]
    exact_fields: List[str]
    groupable_patterns: Dict[str, Dict]
    pipeline_factory: Callable[[], Any]
    csv_filename: str
    json_filename: str
