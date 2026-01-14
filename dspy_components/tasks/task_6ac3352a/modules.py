import asyncio
import json
from typing import Dict, Any

import dspy

from utils.json_parser import safe_json_parse
from dspy_components.tasks.task_6ac3352a.signatures import (
    ExtractTextualFields,
    ExtractNumericFields,
)


# ============================================================================
# MODULES - TASK 6AC3352A
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
            "study_title": getattr(result, "study_title", "NR"),
            "interventions": getattr(result, "interventions", "NR"),
            "outcomes": getattr(result, "outcomes", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncExtractTextualFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "study_title": "NR",
            "interventions": "NR",
            "outcomes": "NR"
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
        }
        except Exception as e:
            print(f"Error in AsyncExtractNumericFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "total_participants": "NR"
}






__all__ = [
    "AsyncExtractTextualFieldsExtractor",
    "AsyncExtractNumericFieldsExtractor",
]