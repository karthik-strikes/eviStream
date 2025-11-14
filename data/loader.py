import os
import json
from typing import List, Dict
import dspy


def create_dspy_examples(markdown_content: str, one_study_records: List[Dict]) -> List[dspy.Example]:
    """
    Create one dspy.Example per study, with markdown_content as input
    and all structured records as the expected output.
    """
    if not markdown_content or not one_study_records:
        return []

    example = dspy.Example(
        markdown_content=markdown_content,
        extracted_records=one_study_records
    ).with_inputs("markdown_content")

    return [example]


def create_examples_for_all_studies(md_dir: str, target_file: str) -> List[dspy.Example]:
    """
    Loop through all study _md folders and build DSPy examples.

    Args:
        md_dir: directory containing *_md study folders
        target_file: path to trail_characteristics.json

    Returns:
        List of dspy.Example objects (one per study)
    """
    # Load global target data once
    with open(target_file, "r") as f:
        target_data = json.load(f)

    all_examples = []
    missing = []

    # Loop over each study folder
    for folder in os.listdir(md_dir):
        if not folder.endswith("_md"):
            continue

        study_id = folder.replace("_md", "")  # e.g., "3477_Dolci"
        source_file = os.path.join(md_dir, folder, f"{folder}.json")

        if not os.path.exists(source_file):
            print(f"⚠️ Missing source file for {folder}, skipping...")
            missing.append((study_id, "no_json"))
            continue

        # Load source JSON and extract markdown
        with open(source_file, "r") as f:
            source_data = json.load(f)
        markdown_content = source_data.get("marker", {}).get("markdown", "")

        # Get ground truth records for this study
        one_study_records = [
            rec for rec in target_data if rec.get("filename") == study_id]

        if not one_study_records:
            print(
                f"⚠️ No ground truth records found for {study_id}, skipping...")
            missing.append((study_id, "no_records"))
            continue

        # Build examples for this study
        examples = create_dspy_examples(markdown_content, one_study_records)
        all_examples.extend(examples)

    # Summary
    total_folders = len([f for f in os.listdir(md_dir) if f.endswith("_md")])

    print(f"Total folders found: {total_folders}")
    print(f"Examples created: {len(all_examples)}")
    print(f"Missed studies: {len(missing)}")
    if missing:
        for sid, reason in missing:
            print(f"  - {sid} ({reason})")

    return all_examples
