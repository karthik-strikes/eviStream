import asyncio
import json
import traceback
from typing import Dict, List, Any
from src.helpers.print_helpers import print_extracted_vs_ground_truth, print_field_level_table, print_evaluation_summary
from utils.flatten_json import flatten_json
from schemas.runtime import SchemaRuntime


async def run_async_extraction_and_evaluation(
    markdown_content: str,
    source_file: str,
    one_study_records: List[Dict],
    schema_runtime: SchemaRuntime,
    override: bool = False,
    run_diagnostic: bool = False,
    print_results: bool = False,
    field_level_analysis: bool = False,
    print_field_table: bool = False
):
    """
    Run the complete async extraction and evaluation pipeline.
    1. Extracts records
    2. Aligns + matches
    3. Evaluates
    4. Saves results
    """

    try:
        async_pipeline = schema_runtime.pipeline
        async_evaluator = schema_runtime.evaluator
        file_handler = schema_runtime.file_handler

        # ---- 1️⃣ Extract ----
        # ---- 1️⃣ Extract ----
        baseline_prediction = await async_pipeline(markdown_content)
        print(baseline_prediction)
        
        # Dynamically get the output field based on schema definition
        # The pipeline returns a dspy.Prediction object. We need to access the field 
        # that corresponds to the schema's output_field_name OR 'extracted_records' 
        # if the pipeline uses that convention (like index_test does).
        
        # Check for 'extracted_records' first (common convention for list-based extractions)
        if hasattr(baseline_prediction, 'extracted_records'):
            baseline_results = baseline_prediction.extracted_records
        # Fallback to the specific output field name from schema
        elif hasattr(baseline_prediction, schema_runtime.schema.output_field_name):
             baseline_results = [getattr(baseline_prediction, schema_runtime.schema.output_field_name)]
        # Fallback for legacy/single-item extractions (like patient_population might be)
        elif hasattr(baseline_prediction, 'characteristics'):
             baseline_results = [baseline_prediction.characteristics]
        # Fallback for outcomes_study schema
        elif hasattr(baseline_prediction, 'outcomes'):
             baseline_results = [baseline_prediction.outcomes]
        # Fallback for missing_data_study schema
        elif hasattr(baseline_prediction, 'missing_data'):
             baseline_results = [baseline_prediction.missing_data]
        # Fallback for reference_standard schema
        elif hasattr(baseline_prediction, 'reference_standard'):
             baseline_results = [baseline_prediction.reference_standard]
        else:
            print(f"Warning: Could not find expected output field in prediction. Available keys: {baseline_prediction.keys()}")
            baseline_results = []

        # Ensure it's a list
        if not isinstance(baseline_results, list):
            baseline_results = [baseline_results]

        # print("Extracted Records:")
        # print(baseline_results)
        # print("Ground Truth Records:")
        # print(one_study_records)

        if print_results:
            print_extracted_vs_ground_truth(
                baseline_results, one_study_records)

        baseline_results = [flatten_json(rec) for rec in baseline_results]
        one_study_records = [flatten_json(rec) for rec in one_study_records]

        # ---- 2️⃣ Align + Match ----
        matches, aligned_records = await async_evaluator.get_matches_and_aligned_records(
            baseline_results, one_study_records
        )

        # ---- 3️⃣ Evaluate ----
        baseline_evaluation = await async_evaluator.evaluate(
            baseline_results, one_study_records, diagnose=False
        )

        # ---- 4️⃣ Field-Level Analysis ----
        field_counts = None
        if field_level_analysis:
            field_counts = await async_evaluator.calculate_field_counts(
                baseline_results, one_study_records
            )

            if print_field_table:
                print_field_level_table(field_counts)

        # ---- 5️⃣ Save Results ----
        aligned_extracted_for_csv = [
            aligned_records[(ext_idx, gt_idx)]['aligned_extracted']
            for ext_idx, gt_idx, _ in matches
            if (ext_idx, gt_idx) in aligned_records
        ] or baseline_results

        pipeline_path, json_path, csv_path = await asyncio.gather(
            file_handler.save_extracted_results(
                extracted_records=baseline_results,
                source_file_path=source_file,
                output_dir=None,
                override=override
            ),
            file_handler.save_evaluation_to_json(
                evaluation_results=baseline_evaluation,
                source_file=source_file
            ),
            file_handler.save_evaluation_to_csv(
                baseline_results=baseline_results,
                ground_truth=one_study_records,
                source_file=source_file,
                matches=matches,
                override=override
            )
        )

        # ---- 6️⃣ Print Summary ----
        print_evaluation_summary(baseline_evaluation)

        return {
            "baseline_results": baseline_results,
            "baseline_evaluation": baseline_evaluation,
            "field_counts": field_counts,
            "matches": matches,
            "aligned_records": aligned_records,
            "files_saved": {
                "pipeline": pipeline_path,
                "json": json_path,
                "csv": csv_path
            }
        }

    except Exception as e:
        print(f"❌ Error in async extraction: {e}")
        traceback.print_exc()
