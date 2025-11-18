"""
Configuration file for eviStream - Medical Data Extraction Pipeline
"""

# Default paths
DEFAULT_OUTPUT_DIR = None
DEFAULT_CSV_DIR = "/nlp/data/karthik9/Sprint1/Dental/Data/csvs"
DEFAULT_JSON_PATH = "/nlp/data/karthik9/Sprint1/Dental/Data/ev_jsons/patient_population_evaluation_results.json"

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

# ============================================================================
# FIELD CONFIGURATION FOR PATIENT POPULATION CHARACTERISTICS
# ============================================================================

# All required fields (flattened structure)
REQUIRED_FIELD = [
    # Population fields
    "population.innocuous_lesions.selected",
    "population.innocuous_lesions.comment",
    "population.suspicious_or_malignant_lesions.selected",
    "population.suspicious_or_malignant_lesions.comment",
    "population.healthy_without_lesions.selected",
    "population.healthy_without_lesions.comment",
    "population.other.selected",
    "population.other.comment",
    "population.unclear.selected",
    "population.unclear.comment",
    "population.statement",

    # Patient selection and demographics
    "patient_selection_method",
    "population_ses",
    "population_ethnicity",
    "population_risk_factors",

    # Age characteristics
    "age_central_tendency.mean.selected",
    "age_central_tendency.mean.value",
    "age_central_tendency.median.selected",
    "age_central_tendency.median.value",
    "age_central_tendency.not_reported",
    "age_variability.sd.selected",
    "age_variability.sd.value",
    "age_variability.range.selected",
    "age_variability.range.value",
    "age_variability.not_reported",

    # Baseline participants
    "baseline_participants.total.selected",
    "baseline_participants.total.value",
    "baseline_participants.female_n.selected",
    "baseline_participants.female_n.value",
    "baseline_participants.female_percent.selected",
    "baseline_participants.female_percent.value",
    "baseline_participants.male_n.selected",
    "baseline_participants.male_n.value",
    "baseline_participants.male_percent.selected",
    "baseline_participants.male_percent.value",
    "baseline_participants.not_reported.selected",
    "baseline_participants.not_reported.value",
    "baseline_participants.other.selected",
    "baseline_participants.other.value",

    # Target condition
    "target_condition.opmd.selected",
    "target_condition.opmd.comment",
    "target_condition.oral_cancer.selected",
    "target_condition.oral_cancer.comment",
    "target_condition.other.selected",
    "target_condition.other.comment",
    "target_condition_severity",
    "target_condition_site",

    # Metadata
    "filename"
]

# Fields that should use semantic matching (free-text, descriptions, comments)
SEMANTIC_FIELD = [
    "population.innocuous_lesions.comment",
    "population.suspicious_or_malignant_lesions.comment",
    "population.healthy_without_lesions.comment",
    "population.other.comment",
    "population.unclear.comment",
    "population.statement",
    "patient_selection_method",
    "population_ses",
    "population_ethnicity",
    "population_risk_factors",
    "age_central_tendency.mean.value",
    "age_central_tendency.median.value",
    "age_variability.sd.value",
    "age_variability.range.value",
    "baseline_participants.total.value",
    "baseline_participants.female_n.value",
    "baseline_participants.female_percent.value",
    "baseline_participants.male_n.value",
    "baseline_participants.male_percent.value",
    "baseline_participants.not_reported.value",
    "baseline_participants.other.value",
    "target_condition.opmd.comment",
    "target_condition.oral_cancer.comment",
    "target_condition.other.comment",
    "target_condition_severity",
    "target_condition_site",
]

# Fields that should use exact matching (booleans, structured data, IDs)
EXACT_FIELD = [
    "population.innocuous_lesions.selected",
    "population.suspicious_or_malignant_lesions.selected",
    "population.healthy_without_lesions.selected",
    "population.other.selected",
    "population.unclear.selected",
    "age_central_tendency.mean.selected",
    "age_central_tendency.median.selected",
    "age_central_tendency.not_reported",
    "age_variability.sd.selected",
    "age_variability.range.selected",
    "age_variability.not_reported",
    "baseline_participants.total.selected",
    "baseline_participants.female_n.selected",
    "baseline_participants.female_percent.selected",
    "baseline_participants.male_n.selected",
    "baseline_participants.male_percent.selected",
    "baseline_participants.not_reported.selected",
    "baseline_participants.other.selected",
    "target_condition.opmd.selected",
    "target_condition.oral_cancer.selected",
    "target_condition.other.selected",
    "filename"
]

# Groupable field patterns (for repeating structures)
# None for patient population characteristics
GROUPABLE_PATTERN = {}
