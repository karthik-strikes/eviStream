#!/usr/bin/env python3
"""
Simple wrapper script for PDF processing.
For MVP use, import PDFProcessor directly in Streamlit instead of using this script.
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Resolve the shared `Dental` root so we can point into the sibling `Data` dir
_THIS_FILE = Path(__file__).resolve()
_DENTAL_ROOT = _THIS_FILE.parents[2]


def main():
    """
    Example usage of PDFProcessor for batch processing.
    For Streamlit MVP, use PDFProcessor directly instead.
    """
    # Set up paths relative to the project layout (no user-specific absolute paths)
    pdf_directory = str(_DENTAL_ROOT / "Data" / "oral_cancer_pdfs")
    output_directory = str(_DENTAL_ROOT / "Data" / "oral_cancer_mds")

    # Create output directory
    os.makedirs(output_directory, exist_ok=True)

    print("="*80)
    print("PDF PROCESSOR - BATCH PROCESSING")
    print("="*80)

    # Get all PDF files
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDF files in {pdf_directory}")

    # Initialize the PDF processor
    try:
        from pdf_processor.pdf_processor import PDFProcessor

        # Configure the processor
        config = {
            "extract_images": False,  # Set to True if you want to extract images
            "cache_dir": "cache",
            "output_dir": output_directory
        }

        processor = PDFProcessor(config)
        print("✓ PDF Processor initialized successfully")

    except Exception as e:
        print(f"✗ Failed to initialize PDF processor: {e}")
        print("Make sure you have:")
        print("1. Installed dependencies: pip install -r requirements.txt")
        print("2. Set up your .env file with DATALAB_API_KEY")
        return 1

    # Process each PDF
    successful = 0
    failed = 0
    results = []

    for i, pdf_file in enumerate(pdf_files[:50], 1):
        pdf_path = os.path.join(pdf_directory, pdf_file)

        base_name = Path(pdf_file).stem  # e.g. "10_Zelenakas"
        output_subdir = os.path.join(output_directory, f"{base_name}_md")

    # Skip if already processed (output directory exists)
        if os.path.isdir(output_subdir):
            print(
                f"\n[{i}/{len(pdf_files)}] Skipping (already processed): {pdf_file}")
            continue

        print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file}")

        try:
            # Process the PDF
            result = processor.process(pdf_path, force_reprocess=False)

            if result.get('status') == 'success':
                successful += 1
                print(f"  ✓ Success: {pdf_file}")

                # Save individual result

                results.append({
                    "file": pdf_file,
                    "status": "success"
                })
            else:
                failed += 1
                print(f"  ✗ Failed: {result.get('status', 'Unknown error')}")
                results.append({
                    "file": pdf_file,
                    "status": "failed",
                    "error": result.get('status', 'Unknown error')
                })

        except Exception as e:
            failed += 1
            print(f"  ✗ Error: {str(e)}")
            results.append({
                "file": pdf_file,
                "status": "error",
                "error": str(e)
            })

    # Save batch summary
    summary = {
        "total_files": len(pdf_files),
        "successful": successful,
        "failed": failed,
        "results": results
    }

    summary_file = os.path.join(output_directory, "batch_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Show final results
    print("\n" + "="*80)
    print("BATCH PROCESSING COMPLETED")
    print("="*80)
    print(f"Total files: {len(pdf_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/len(pdf_files)*100):.1f}%")
    print(f"\nResults saved to: {output_directory}")
    print(f"Summary saved to: {summary_file}")

    # Show cost information if available
    try:
        cost_info = processor.get_cost_info()
        print(f"\nCost Information:")
        print(f"  Current session: {cost_info.get('current_session', {})}")
        print(f"  Historical total: {cost_info.get('historical_total', {})}")
        print(f"  Budget info: {cost_info.get('budget_info', {})}")
    except Exception as e:
        print(f"Could not retrieve cost information: {e}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
