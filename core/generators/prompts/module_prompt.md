Generate a production-quality Async DSPy Module following real patterns:

SIGNATURE TO WRAP: [[SIGNATURE_CLASS_NAME]]
OUTPUT FIELD: [[OUTPUT_FIELD_NAME]]
FALLBACK STRUCTURE: [[FALLBACK_STRUCTURE]]

REAL-WORLD PATTERN (from production code):
```python
import asyncio
from typing import Dict, Any
import dspy
from utils.json_parser import safe_json_parse


class Async[[SIGNATURE_CLASS_NAME]]Extractor(dspy.Module):
    """Async module to extract [description]."""

    def __init__(self):
        super().__init__()
        # Use ChainOfThought for reasoning (better accuracy for complex medical text)
        self.extract = dspy.ChainOfThought([[SIGNATURE_CLASS_NAME]])

    async def __call__(self, markdown_content: str, **kwargs) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()

        def _extract():
            return self.extract(markdown_content=markdown_content, **kwargs)

        try:
            result = await loop.run_in_executor(None, _extract)
            # Parse JSON output to Python dict
            return safe_json_parse(result.[[OUTPUT_FIELD_NAME]])
        except Exception as e:
            print(f"Error in extraction: {e}")
            # Return fallback default structure
            return [[FALLBACK_STRUCTURE]]

    def forward_sync(self, markdown_content: str, **kwargs) -> Dict[str, Any]:
        """Synchronous method for DSPy optimizers"""
        result = self.extract(markdown_content=markdown_content, **kwargs)
        return safe_json_parse(result.[[OUTPUT_FIELD_NAME]])
```

REQUIREMENTS:
1. Inherit from dspy.Module
2. Use dspy.ChainOfThought wrapper (better for complex extraction)
3. Async __call__ method with run_in_executor pattern
4. Sync forward_sync method for optimizers
5. Comprehensive error handling with fallback
6. Type hints for all parameters and returns
7. Clear docstring

Generate ONLY the Python code.


