import json
from pathlib import Path
from typing import Optional, Tuple, List, Dict

from src.field_extractor import extract_fields_from_signature

GENERATED_FIELDS_DIR = Path(__file__).resolve().parent / "generated_fields"
GENERATED_FIELDS_DIR.mkdir(parents=True, exist_ok=True)


def load_or_create_field_config(
    signature_class,
    cache_filename: str,
    target_file: Optional[str] = None,
    output_field_name: str = "complete_characteristics_json",
    verbose: bool = False
) -> Tuple[List[str], List[str], List[str], Dict]:
    """
    Load cached field classifications for a signature, or generate them if absent.
    """
    cache_path = GENERATED_FIELDS_DIR / cache_filename
    if cache_path.exists():
        with cache_path.open('r') as f:
            data = json.load(f)
        return (
            data["required_fields"],
            data["semantic_fields"],
            data["exact_fields"],
            data["groupable_patterns"],
        )

    required_fields, semantic_fields, exact_fields, groupable_patterns = extract_fields_from_signature(
        signature_class=signature_class,
        target_file=target_file,
        output_field_name=output_field_name,
        verbose=verbose
    )

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open('w') as f:
        json.dump({
            "required_fields": required_fields,
            "semantic_fields": semantic_fields,
            "exact_fields": exact_fields,
            "groupable_patterns": groupable_patterns
        }, f, indent=2)

    return required_fields, semantic_fields, exact_fields, groupable_patterns
