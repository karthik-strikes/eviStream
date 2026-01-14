import asyncio
import json
from typing import Dict, Any

import dspy

from utils.json_parser import safe_json_parse
from dspy_components.tasks.task_496f2c0f.signatures import (
    ExtractTextualFields,
    ExtractNumericFields,
)


# ============================================================================
# MODULES - TASK 496F2C0F
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
            "most_discussed_gender": getattr(result, "most_discussed_gender", "NR"),
            "author": getattr(result, "author", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncExtractTextualFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "most_discussed_gender": "NR",
            "author": "NR"
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
            "Mean_age_study1": getattr(result, "Mean_age_study1", "NR"),
            "Mean_age_study2": getattr(result, "Mean_age_study2", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncExtractNumericFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "Mean_age_study1": "NR",
            "Mean_age_study2": "NR"
}






__all__ = [
    "AsyncExtractTextualFieldsExtractor",
    "AsyncExtractNumericFieldsExtractor",
]