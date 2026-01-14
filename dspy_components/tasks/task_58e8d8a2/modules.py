import asyncio
import json
from typing import Dict, Any

import dspy

from utils.json_parser import safe_json_parse
from dspy_components.tasks.task_58e8d8a2.signatures import (
    ExtractNumericFields,
    ClassifyEnumFields,
)


# ============================================================================
# MODULES - TASK 58E8D8A2
# ============================================================================





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
            "female_patient_age_mean": getattr(result, "female_patient_age_mean", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncExtractNumericFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "female_patient_age_mean": "NR"
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
            "most_patient_gender": getattr(result, "most_patient_gender", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncClassifyEnumFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "most_patient_gender": "NR"
}






__all__ = [
    "AsyncExtractNumericFieldsExtractor",
    "AsyncClassifyEnumFieldsExtractor",
]