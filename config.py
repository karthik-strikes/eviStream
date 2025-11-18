"""
Configuration file for eviStream - Medical Data Extraction Pipeline
"""

# Default paths
DEFAULT_OUTPUT_DIR = None
DEFAULT_CSV_DIR = "/nlp/data/karthik9/Sprint1/Dental/Data/csvs"
DEFAULT_JSON_DIR = "/nlp/data/karthik9/Sprint1/Dental/Data/ev_jsons"

# DSPy History Logging
DEFAULT_HISTORY_CSV = "dspy_history.csv"

# Cache directories
CACHE_DIRS = [".semantic_cache", ".evaluation_cache"]

# Model configuration
DEFAULT_MODEL = "gemini/gemini-2.5-pro"
MAX_TOKENS = 20000
TEMPERATURE = 1.0
EVALUATION_MODEL = DEFAULT_MODEL
EVALUATION_TEMPERATURE = 0.0

# Alternative models (uncomment to use)
# DEFAULT_MODEL = "openai/gpt-5-mini-2025-08-07"
# DEFAULT_MODEL = "anthropic/claude-sonnet-4-5-20250929"
