"""
Configuration file for eviStream - Medical Data Extraction Pipeline
"""

import os
from pathlib import Path
from dotenv import load_dotenv

#
# Path configuration
#
# Resolve important project directories relative to this file so we don't rely
# on machine-specific absolute paths tied to a particular user or machine.
_THIS_FILE = Path(__file__).resolve()
# eviStream project root (…/Sprint1/Dental/eviStream)
PROJECT_ROOT = _THIS_FILE.parents[1]
# Parent Dental directory which contains both `eviStream` and `Data`
_DENTAL_ROOT = _THIS_FILE.parents[2]

# Load environment variables from .env file
load_dotenv()

# Default paths
# Keep as strings for compatibility with code that expects string paths.
DEFAULT_OUTPUT_DIR = None
DEFAULT_CSV_DIR = str(_DENTAL_ROOT / "Data" / "eval_csvs")
DEFAULT_JSON_DIR = str(_DENTAL_ROOT / "Data" / "eval_jsons")

# DSPy History Logging
DEFAULT_HISTORY_CSV = str(PROJECT_ROOT / "outputs" /
                          "logs" / "dspy_history.csv")
# Set to True to log full prompts (increases CSV size significantly)
INCLUDE_FULL_PROMPTS_IN_HISTORY = False


# Cache directories
CACHE_DIRS = [".semantic_cache", ".evaluation_cache"]

# Model configuration
# Model configuration
DEFAULT_MODEL = "gemini/gemini-3-pro-preview"
MAX_TOKENS = 20000
TEMPERATURE = 1.0  # Set to 1.0 to match notebook extraction
# Set to flash for faster evaluation
EVALUATION_MODEL = "gemini/gemini-2.5-flash"
EVALUATION_TEMPERATURE = 0.0

# Concurrency Settings
BATCH_CONCURRENCY = 5  # Number of papers to process in parallel
EVALUATION_CONCURRENCY = 20  # Number of concurrent semantic matching calls

# Alternative models (uncomment to use)
# DEFAULT_MODEL = "openai/gpt-5-mini-2025-08-07"
# DEFAULT_MODEL = "anthropic/claude-sonnet-4-5-20250929"

# Supabase Configuration
# Set these environment variables or update directly here.
# Supabase is used as a metadata store, while heavy artifacts like markdown
# and extracted JSON continue to live on the local filesystem
# (e.g. under `storage/processed/extracted_pdfs`).
# e.g., "https://your-project.supabase.co"
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")  # Your Supabase anon/service key
