"""
Configuration file for eviStream - Medical Data Extraction Pipeline
"""

# Default paths
DEFAULT_OUTPUT_DIR = None
DEFAULT_CSV_DIR = "/nlp/data/karthik9/Sprint1/Dental/Data/eval_csvs"
DEFAULT_JSON_DIR = "/nlp/data/karthik9/Sprint1/Dental/Data/eval_jsons"

# DSPy History Logging
DEFAULT_HISTORY_CSV = "dspy_history.csv"
INCLUDE_FULL_PROMPTS_IN_HISTORY = False  # Set to True to log full prompts (increases CSV size significantly)



# Cache directories
CACHE_DIRS = [".semantic_cache", ".evaluation_cache"]

# Model configuration
# Model configuration
DEFAULT_MODEL = "gemini/gemini-3-pro-preview"
MAX_TOKENS = 20000
TEMPERATURE = 1.0  # Set to 1.0 to match notebook extraction
EVALUATION_MODEL = "gemini/gemini-2.5-flash" # Set to flash for faster evaluation
EVALUATION_TEMPERATURE = 0.0

# Alternative models (uncomment to use)
# DEFAULT_MODEL = "openai/gpt-5-mini-2025-08-07"
# DEFAULT_MODEL = "anthropic/claude-sonnet-4-5-20250929"
