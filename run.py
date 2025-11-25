"""
eviStream - Medical Data Extraction Pipeline
Main entry point for running single or batch extractions
"""

import asyncio
import sys
import json
from pathlib import Path
from collections import defaultdict

from utils.lm_config import *
from utils.cache_cleaner import clear_cache_directories
from utils.logging import set_log_file, log_history, show_stats, log_execution_time
from data.loader import *
import time
from src.extractor import run_async_extraction_and_evaluation
from src.helpers.visualization import create_performance_dashboards
from schemas import get_schema, build_schema_runtime, list_schemas
from config import INCLUDE_FULL_PROMPTS_IN_HISTORY

# Add eviStream to path
sys.path.insert(0, str(Path(__file__).parent))


async def run_single_extraction(source_file: str, target_file: str, schema_runtime, clear_cache: bool = False):
    """
    Run extraction on a single file

    Args:
        source_file: Path to markdown source file
        target_file: Path to target JSON file
        clear_cache: Whether to clear caches before running
    """
    print("="*60)
    print("eviStream - Single Extraction Mode")
    print("="*60)
    
    start_time = time.time()

    # Optional: clear caches
    if clear_cache:
        print("\nClearing caches...")
        clear_cache_directories(cache_root=str(Path(__file__).parent))

    # Set up logging
    set_log_file("dspy_history.csv", include_full_prompts=INCLUDE_FULL_PROMPTS_IN_HISTORY)

    # Load data
    print(f"\nLoading source: {source_file}")
    print(f"Loading target: {target_file}")

    with open(source_file, 'r') as f:
        source_data = json.load(f)
    markdown_content = source_data.get("marker", {}).get("markdown", "")

    with open(target_file, 'r') as f:
        target_data = json.load(f)

    # Filter for this study
    one_study_records = [record for record in target_data if record.get(
        'filename', '').replace('_md', '') in source_file]
    if not one_study_records:
        one_study_records = target_data[:1]  # Use first record if no match

    print(f"\nFound {len(one_study_records)} target record(s)")

    # Run extraction and evaluation
    print("\nRunning extraction and evaluation...")
    # print(schema_runtime)
    result = await run_async_extraction_and_evaluation(
        markdown_content=markdown_content,
        source_file=source_file,
        one_study_records=one_study_records,
        schema_runtime=schema_runtime,
        override=False,
        run_diagnostic=False,
        print_results=False,
        field_level_analysis=True,
        print_field_table=True
    )

    # Log history
    print("\nLogging LLM history...")
    log_history()
    show_stats()

    print("\n" + "="*60)
    print("Single extraction completed!")
    print("="*60)
    
    log_execution_time(start_time, time.time(), "single", source_file, target_file, schema_runtime.schema.name)


async def run_batch_extraction(md_dir: str, target_file: str, schema_runtime, clear_cache: bool = False, max_examples: int = None, save_dashboards: bool = False):
    """
    Run extraction on multiple files

    Args:
        md_dir: Directory containing *_md folders
        target_file: Path to target JSON file
        clear_cache: Whether to clear caches before running
        max_examples: Maximum number of examples to process (None = all)
        save_dashboards: Whether to save dashboards as PNG files
    """
    print("="*60)
    print("eviStream - Batch Extraction Mode")
    print("="*60)
    
    start_time = time.time()

    # Optional: clear caches
    if clear_cache:
        print("\nClearing caches...")
        clear_cache_directories(cache_root=str(Path(__file__).parent))

    # Set up logging
    set_log_file("dspy_history_batch.csv", include_full_prompts=INCLUDE_FULL_PROMPTS_IN_HISTORY)

    # Create examples
    print(f"\nCreating examples from: {md_dir}")
    print(f"Using target: {target_file}")

    all_examples = create_examples_for_all_studies(md_dir, target_file)

    if max_examples:
        all_examples = all_examples[:max_examples]

    print(f"\nProcessing {len(all_examples)} examples...\n")

    # Metrics collection
    # Metrics collection
    f1_scores = []
    precision_scores = []
    recall_scores = []
    completeness_scores = []
    aggregated_field_counts = defaultdict(lambda: {
        'gt_count': 0,
        'extracted_count': 0,
        'matched': 0,
        'missing': 0,
        'incorrect': 0,
        'extra': 0
    })

    semantic_fields = schema_runtime.evaluator.semantic_fields
    exact_fields = schema_runtime.evaluator.exact_fields

    # Concurrency control
    from config import BATCH_CONCURRENCY
    semaphore = asyncio.Semaphore(BATCH_CONCURRENCY)
    
    async def process_example(i, example):
        async with semaphore:
            print(f"\n{'='*50}")
            print(f"STARTING EXAMPLE {i+1}/{len(all_examples)}: {example.extracted_records[0].get('filename', 'Unknown')}")
            print(f"{'='*50}")

            markdown_content = example.markdown_content
            ground_truth = example.extracted_records
            filename = ground_truth[0].get('filename', 'Unknown')

            # Construct source file path
            source_file = f"{md_dir}/{filename}_md/{filename}_md.json"

            # Run extraction
            try:
                result_dict = await run_async_extraction_and_evaluation(
                    markdown_content=markdown_content,
                    source_file=source_file,
                    one_study_records=ground_truth,
                    schema_runtime=schema_runtime,
                    override=False,
                    field_level_analysis=True,
                    print_field_table=False,
                    print_results=True
                )
                
                # Log history and clear memory after EACH example to prevent bloat
                log_history(clear_memory=True)
                
                return result_dict
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                return None

    # Run on all examples in parallel
    print(f"Processing with concurrency: {BATCH_CONCURRENCY}")
    tasks = [process_example(i, ex) for i, ex in enumerate(all_examples)]
    results = await asyncio.gather(*tasks)
    
    # Process results
    valid_results = [r for r in results if r is not None]
    
    for result_dict in valid_results:
        # Collect metrics
        evaluation = result_dict['baseline_evaluation']
        field_counts = result_dict['field_counts']

        f1_scores.append(evaluation['f1'])
        precision_scores.append(evaluation['precision'])
        recall_scores.append(evaluation['recall'])
        completeness_scores.append(evaluation['completeness'])

        # Aggregate field counts
        for field, counts in field_counts.items():
            for key in ['gt_count', 'extracted_count', 'matched', 'missing', 'incorrect', 'extra']:
                aggregated_field_counts[field][key] += counts[key]

    # Calculate final metrics
    if f1_scores:
        avg_precision = sum(precision_scores) / len(precision_scores)
        avg_recall = sum(recall_scores) / len(recall_scores)
        avg_f1 = sum(f1_scores) / len(f1_scores)
        avg_completeness = sum(completeness_scores) / len(completeness_scores)
    else:
        avg_precision = avg_recall = avg_f1 = avg_completeness = 0.0

    print(f"\n{'='*60}")
    print(f"FINAL SUMMARY ACROSS {len(f1_scores)} EXAMPLES")
    print(f"{'='*60}")
    print(f"Average Precision: {avg_precision:.3f}")
    print(f"Average Recall: {avg_recall:.3f}")
    print(f"Average F1 Score: {avg_f1:.3f}")
    print(f"Average Completeness: {avg_completeness:.1%}")

    # Generate dashboards
    print("\nGenerating performance dashboards...")
    if save_dashboards:
        dashboard_dir = Path("./dashboards")
        result = create_performance_dashboards(
            aggregated_field_counts=dict(aggregated_field_counts),
            avg_precision=avg_precision,
            avg_recall=avg_recall,
            avg_f1=avg_f1,
            semantic_fields=semantic_fields,
            exact_fields=exact_fields,
            save_to_file=True,
            output_dir=str(dashboard_dir),
            schema_name=schema_runtime.schema.name
        )
        if result:
            summary_path, action_plan_path = result
            print(f"\nDashboards saved to: {dashboard_dir.absolute()}")
            print(f"  - Executive Summary: {Path(summary_path).name}")
            print(f"  - Action Plan: {Path(action_plan_path).name}")
    else:
        print("(Dashboards displayed interactively - use --save-dashboards to save as PNG files)")
        create_performance_dashboards(
            aggregated_field_counts=dict(aggregated_field_counts),
            avg_precision=avg_precision,
            avg_recall=avg_recall,
            avg_f1=avg_f1,
            semantic_fields=semantic_fields,
            exact_fields=exact_fields,
            save_to_file=False,
            schema_name=schema_runtime.schema.name
        )

    # Final log flush
    print("\nLogging LLM history...")
    log_history(clear_memory=True)
    show_stats()

    print("\n" + "="*60)
    print("Batch extraction completed!")
    print("="*60)
    
    log_execution_time(start_time, time.time(), "batch", md_dir, target_file, schema_runtime.schema.name)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="eviStream - Medical Data Extraction Pipeline")
    parser.add_argument(
        "mode", choices=["single", "batch"], help="Extraction mode")
    parser.add_argument(
        "--source", help="Source file (single mode) or directory (batch mode)")
    parser.add_argument("--target", help="Target JSON file")
    parser.add_argument("--clear-cache", action="store_true",
                        help="Clear caches before running")
    parser.add_argument("--max-examples", type=int,
                        help="Max examples for batch mode")
    parser.add_argument("--save-dashboards", action="store_true",
                        help="Save dashboards as PNG files (default: display interactively)")
    parser.add_argument("--schema", default="patient_population", choices=list_schemas(),
                        help="Schema to run (default: patient_population)")

    args = parser.parse_args()

    schema_definition = get_schema(args.schema)
    schema_runtime = None

    try:
        schema_runtime = build_schema_runtime(
            schema_definition, target_file=args.target)

        if args.mode == "single":
            if not args.source or not args.target:
                print("Error: --source and --target are required for single mode")
                sys.exit(1)
            asyncio.run(run_single_extraction(
                args.source, args.target, schema_runtime, args.clear_cache))
        else:  # batch
            if not args.source or not args.target:
                print(
                    "Error: --source (directory) and --target are required for batch mode")
                sys.exit(1)
            asyncio.run(run_batch_extraction(args.source, args.target,
                        schema_runtime, args.clear_cache, args.max_examples, args.save_dashboards))
    finally:
        if schema_runtime is not None:
            schema_runtime.close()


if __name__ == "__main__":
    main()
