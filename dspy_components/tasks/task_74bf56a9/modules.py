import asyncio
import json
from typing import Dict, Any

import dspy

from utils.json_parser import safe_json_parse
from dspy_components.tasks.task_74bf56a9.signatures import (
    ExtractTextualFields,
    ExtractNumericFields,
    ClassifyEnumFields,
    DetermineBooleanFields,
)


# ============================================================================
# MODULES - TASK 74BF56A9
# ============================================================================


import asyncio
from typing import Dict, Any
import dspy


class AsyncExtractTextualFieldsExtractor(dspy.Module):
    """Async module to extract data using ExtractTextualFields signature."""

    def __init__(self):
        super().__init__()
        # Use ChainOfThought for better reasoning
        self.extract = dspy.ChainOfThought(ExtractTextualFields)

    async def __call__(self, markdown_content: str, **kwargs) -> Dict[str, Any]:
        """
        Extract data from markdown content.
        
        Args:
            markdown_content: Full markdown text to extract from
            **kwargs: Additional context fields if needed
            
        Returns:
            Dict with extracted field values
        """
        loop = asyncio.get_running_loop()

        def _extract():
            return self.extract(markdown_content=markdown_content, **kwargs)

        try:
            result = await loop.run_in_executor(None, _extract)
            # Extract all output fields from result
            return {
            "primary_outcome_name": getattr(result, "primary_outcome_name", "NR"),
            "primary_outcome_definition": getattr(result, "primary_outcome_definition", "NR"),
            "confidence_interval": getattr(result, "confidence_interval", "NR"),
            "p_value": getattr(result, "p_value", "NR"),
            "time_point": getattr(result, "time_point", "NR"),
            "secondary_outcomes": getattr(result, "secondary_outcomes", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncExtractTextualFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "primary_outcome_name": "NR",
            "primary_outcome_definition": "NR",
            "confidence_interval": "NR",
            "p_value": "NR",
            "time_point": "NR",
            "secondary_outcomes": "NR"
}




import asyncio
from typing import Dict, Any
import dspy


class AsyncExtractNumericFieldsExtractor(dspy.Module):
    """Async module to extract data using ExtractNumericFields signature."""

    def __init__(self):
        super().__init__()
        # Use ChainOfThought for better reasoning
        self.extract = dspy.ChainOfThought(ExtractNumericFields)

    async def __call__(self, markdown_content: str, **kwargs) -> Dict[str, Any]:
        """
        Extract data from markdown content.
        
        Args:
            markdown_content: Full markdown text to extract from
            **kwargs: Additional context fields if needed
            
        Returns:
            Dict with extracted field values
        """
        loop = asyncio.get_running_loop()

        def _extract():
            return self.extract(markdown_content=markdown_content, **kwargs)

        try:
            result = await loop.run_in_executor(None, _extract)
            # Extract all output fields from result
            return {
            "intervention_group_events": getattr(result, "intervention_group_events", "NR"),
            "intervention_group_total": getattr(result, "intervention_group_total", "NR"),
            "control_group_events": getattr(result, "control_group_events", "NR"),
            "control_group_total": getattr(result, "control_group_total", "NR"),
            "relative_risk": getattr(result, "relative_risk", "NR"),
            "odds_ratio": getattr(result, "odds_ratio", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncExtractNumericFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "intervention_group_events": "NR",
            "intervention_group_total": "NR",
            "control_group_events": "NR",
            "control_group_total": "NR",
            "relative_risk": "NR",
            "odds_ratio": "NR"
}




import asyncio
from typing import Dict, Any
import dspy


class AsyncClassifyEnumFieldsExtractor(dspy.Module):
    """Async module to extract data using ClassifyEnumFields signature."""

    def __init__(self):
        super().__init__()
        # Use ChainOfThought for better reasoning
        self.extract = dspy.ChainOfThought(ClassifyEnumFields)

    async def __call__(self, markdown_content: str, **kwargs) -> Dict[str, Any]:
        """
        Extract data from markdown content.
        
        Args:
            markdown_content: Full markdown text to extract from
            **kwargs: Additional context fields if needed
            
        Returns:
            Dict with extracted field values
        """
        loop = asyncio.get_running_loop()

        def _extract():
            return self.extract(markdown_content=markdown_content, **kwargs)

        try:
            result = await loop.run_in_executor(None, _extract)
            # Extract all output fields from result
            return {
            "outcome_assessment_method": getattr(result, "outcome_assessment_method", "NR"),
            "blinding_status": getattr(result, "blinding_status", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncClassifyEnumFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "outcome_assessment_method": "NR",
            "blinding_status": "NR"
}




import asyncio
from typing import Dict, Any
import dspy


class AsyncDetermineBooleanFieldsExtractor(dspy.Module):
    """Async module to extract data using DetermineBooleanFields signature."""

    def __init__(self):
        super().__init__()
        # Use ChainOfThought for better reasoning
        self.extract = dspy.ChainOfThought(DetermineBooleanFields)

    async def __call__(self, markdown_content: str, **kwargs) -> Dict[str, Any]:
        """
        Extract data from markdown content.
        
        Args:
            markdown_content: Full markdown text to extract from
            **kwargs: Additional context fields if needed
            
        Returns:
            Dict with extracted field values
        """
        loop = asyncio.get_running_loop()

        def _extract():
            return self.extract(markdown_content=markdown_content, **kwargs)

        try:
            result = await loop.run_in_executor(None, _extract)
            # Extract all output fields from result
            return {
            "intention_to_treat": getattr(result, "intention_to_treat", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncDetermineBooleanFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "intention_to_treat": "NR"
}






__all__ = [
    "AsyncExtractTextualFieldsExtractor",
    "AsyncExtractNumericFieldsExtractor",
    "AsyncClassifyEnumFieldsExtractor",
    "AsyncDetermineBooleanFieldsExtractor",
]