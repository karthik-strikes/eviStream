import asyncio
import json
from typing import Dict, Any

import dspy

from utils.json_parser import safe_json_parse
from dspy_components.tasks.task_396efcdd.signatures import (
    ExtractTextualFields,
    ExtractNumericFields,
    ClassifyEnumFields,
    DetermineBooleanFields,
)


# ============================================================================
# MODULES - TASK 396EFCDD
# ============================================================================





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
            "intervention_name": getattr(result, "intervention_name", "NR"),
            "intervention_dosage": getattr(result, "intervention_dosage", "NR"),
            "primary_outcome": getattr(result, "primary_outcome", "NR"),
            "primary_outcome_result": getattr(result, "primary_outcome_result", "NR"),
            "effect_size": getattr(result, "effect_size", "NR"),
            "follow_up_duration": getattr(result, "follow_up_duration", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncExtractTextualFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "intervention_name": "NR",
            "intervention_dosage": "NR",
            "primary_outcome": "NR",
            "primary_outcome_result": "NR",
            "effect_size": "NR",
            "follow_up_duration": "NR"
}







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
            "total_participants": getattr(result, "total_participants", "NR"),
            "p_value": getattr(result, "p_value", "NR"),
            "adverse_events_count": getattr(result, "adverse_events_count", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncExtractNumericFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "total_participants": "NR",
            "p_value": "NR",
            "adverse_events_count": "NR"
}







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
            "study_type": getattr(result, "study_type", "NR"),
            "control_group_type": getattr(result, "control_group_type", "NR"),
            "statistical_significance": getattr(result, "statistical_significance", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncClassifyEnumFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "study_type": "NR",
            "control_group_type": "NR",
            "statistical_significance": "NR"
}







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
            "adverse_events_reported": getattr(result, "adverse_events_reported", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncDetermineBooleanFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "adverse_events_reported": "NR"
}






__all__ = [
    "AsyncExtractTextualFieldsExtractor",
    "AsyncExtractNumericFieldsExtractor",
    "AsyncClassifyEnumFieldsExtractor",
    "AsyncDetermineBooleanFieldsExtractor",
]