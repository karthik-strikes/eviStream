import asyncio
import json
from typing import Dict, Any

import dspy

from utils.json_parser import safe_json_parse
from dspy_components.tasks.task_521e56a7.signatures import (
    ExtractTextualFields,
    ExtractNumericFields,
    ClassifyEnumFields,
    SynthesizeRiskStratification,
    SynthesizeMedicationReview,
    SynthesizeLifestyleRecommendations,
    AggregateClinicalSummary,
)


# ============================================================================
# MODULES - TASK 521E56A7
# ============================================================================

