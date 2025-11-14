import dspy
import json
import random
from typing import Tuple, List, Dict

from ..dspy_components.utility_signatures import ExtractFieldsFromSchema
from ..dspy_components.signatures import CombinePatientPopulationCharacteristics
from ..utils.json_parser import safe_json_parse


def sample_json_records(target_file: str, max_samples: int = 5) -> str:
    """
    Load a JSON file and return up to `max_samples` random records as a formatted JSON string.
    Parameters:
        target_file (str): Path to the JSON file.
        max_samples (int): Maximum number of records to sample (default = 5).
    Returns:
        str: Formatted JSON string of sampled records.
    """
    with open(target_file, 'r') as f:
        data = json.load(f)

    if isinstance(data, list):
        num_samples = min(max_samples, len(data))
        sample_records = random.sample(data, num_samples)
    elif isinstance(data, dict):
        sample_records = [data]
    else:
        sample_records = []

    return json.dumps(sample_records, indent=2)


# DSPy Signature for Auto-Extracting Fields from Schema


def extract_fields_from_signature(signature_class, target_file: str, verbose: bool = True) -> Tuple[List[str], List[str], List[str], Dict]:
    """
    Use DSPy to automatically extract and classify fields from a signature.

    Args:
        signature_class: DSPy signature class (e.g., StructureTrialCharacteristics)
        target_file: Path to target JSON file for sampling
        verbose: Whether to print reasoning and validation

    Returns:
        tuple: (required_fields, semantic_fields, exact_fields, groupable_patterns)
    """
    # Get schema description from the signature (proper DSPy field access)
    schema_desc = signature_class.model_fields['complete_characteristics_json'].json_schema_extra.get(
        'desc', '')

    # Use DSPy to parse and classify fields
    extractor = dspy.ChainOfThought(ExtractFieldsFromSchema)
    result = extractor(schema_description=schema_desc,
                       ground_truth_json=sample_json_records(target_file))

    print(result)
    # Parse results
    required_fields = safe_json_parse(result.all_required_fields, fallback=[])
    semantic_fields = safe_json_parse(result.semantic_fields, fallback=[])
    exact_fields = safe_json_parse(result.exact_fields, fallback=[])
    groupable_patterns = safe_json_parse(
        result.groupable_field_patterns, fallback={})

    if verbose:
        print(f"\n{'='*70}")
        print(f"AUTO-EXTRACTED FIELDS FROM SIGNATURE")
        print(f"{'='*70}")
        print(f"\n📋 Total Fields: {len(required_fields)}")
        print(f"🔤 Semantic Fields: {len(semantic_fields)}")
        print(f"🎯 Exact Fields: {len(exact_fields)}")
        print(f"🔄 Groupable Patterns: {len(groupable_patterns)}")

        # Validate
        all_defined = set(semantic_fields) | set(exact_fields)
        required_set = set(required_fields)

        if all_defined != required_set:
            print(f"\n⚠️  VALIDATION WARNING:")
            missing = required_set - all_defined
            extra = all_defined - required_set
            if missing:
                print(f"   Missing from semantic/exact: {missing}")
            if extra:
                print(f"   Extra in semantic/exact: {extra}")

        if groupable_patterns:
            print(f"\n🔄 Detected Groupable Patterns:")
            for group_name, config in groupable_patterns.items():
                print(f"   • {group_name}: {config.get('pattern', 'N/A')}")
                print(
                    f"     - Key fields for matching: {config.get('key_matching_fields', [])}")
                print(f"     - Max index: {config.get('max_index', 'N/A')}")

        print(f"{'='*70}\n")

    return required_fields, semantic_fields, exact_fields, groupable_patterns
