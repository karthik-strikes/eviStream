import asyncio
import json
from typing import Dict, Any

import dspy

from utils.json_parser import safe_json_parse
from dspy_components.tasks.task_4bc4179e.signatures import (
    ExtractTextualFields,
    ExtractNumericFields,
    ClassifyEnumFields,
    SynthesizeRiskStratification,
    SynthesizeMedicationReview,
    SynthesizeLifestyleRecommendations,
    AggregateClinicalSummary,
)


# ============================================================================
# MODULES - TASK 4BC4179E
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
            "chief_complaint": getattr(result, "chief_complaint", "NR"),
            "symptom_duration": getattr(result, "symptom_duration", "NR"),
            "medical_history": getattr(result, "medical_history", "NR"),
            "current_medications": getattr(result, "current_medications", "NR"),
            "allergies": getattr(result, "allergies", "NR"),
            "primary_diagnosis": getattr(result, "primary_diagnosis", "NR"),
            "secondary_diagnoses": getattr(result, "secondary_diagnoses", "NR"),
            "treatment_plan": getattr(result, "treatment_plan", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncExtractTextualFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "chief_complaint": "NR",
            "symptom_duration": "NR",
            "medical_history": "NR",
            "current_medications": "NR",
            "allergies": "NR",
            "primary_diagnosis": "NR",
            "secondary_diagnoses": "NR",
            "treatment_plan": "NR"
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
            "patient_age": getattr(result, "patient_age", "NR"),
            "blood_pressure_systolic": getattr(result, "blood_pressure_systolic", "NR"),
            "blood_pressure_diastolic": getattr(result, "blood_pressure_diastolic", "NR"),
            "heart_rate": getattr(result, "heart_rate", "NR"),
            "body_temperature": getattr(result, "body_temperature", "NR"),
            "bmi": getattr(result, "bmi", "NR"),
            "lab_hemoglobin": getattr(result, "lab_hemoglobin", "NR"),
            "lab_creatinine": getattr(result, "lab_creatinine", "NR"),
            "lab_glucose": getattr(result, "lab_glucose", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncExtractNumericFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "patient_age": "NR",
            "blood_pressure_systolic": "NR",
            "blood_pressure_diastolic": "NR",
            "heart_rate": "NR",
            "body_temperature": "NR",
            "bmi": "NR",
            "lab_hemoglobin": "NR",
            "lab_creatinine": "NR",
            "lab_glucose": "NR"
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
            "patient_gender": getattr(result, "patient_gender", "NR"),
            "smoking_status": getattr(result, "smoking_status", "NR"),
            "alcohol_use": getattr(result, "alcohol_use", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncClassifyEnumFieldsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "patient_gender": "NR",
            "smoking_status": "NR",
            "alcohol_use": "NR"
}




import asyncio
from typing import Dict, Any
import dspy


class AsyncSynthesizeRiskStratificationExtractor(dspy.Module):
    """Async module to extract data using SynthesizeRiskStratification signature."""

    def __init__(self):
        super().__init__()
        # Use ChainOfThought for better reasoning
        self.extract = dspy.ChainOfThought(SynthesizeRiskStratification)

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
            "risk_stratification": getattr(result, "risk_stratification", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncSynthesizeRiskStratificationExtractor: {e}")
            # Return fallback structure with default values
            return {
            "risk_stratification": "NR"
}




import asyncio
from typing import Dict, Any
import dspy


class AsyncSynthesizeMedicationReviewExtractor(dspy.Module):
    """Async module to extract data using SynthesizeMedicationReview signature."""

    def __init__(self):
        super().__init__()
        # Use ChainOfThought for better reasoning
        self.extract = dspy.ChainOfThought(SynthesizeMedicationReview)

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
            "medication_review": getattr(result, "medication_review", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncSynthesizeMedicationReviewExtractor: {e}")
            # Return fallback structure with default values
            return {
            "medication_review": "NR"
}




import asyncio
from typing import Dict, Any
import dspy


class AsyncSynthesizeLifestyleRecommendationsExtractor(dspy.Module):
    """Async module to extract data using SynthesizeLifestyleRecommendations signature."""

    def __init__(self):
        super().__init__()
        # Use ChainOfThought for better reasoning
        self.extract = dspy.ChainOfThought(SynthesizeLifestyleRecommendations)

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
            "lifestyle_recommendations": getattr(result, "lifestyle_recommendations", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncSynthesizeLifestyleRecommendationsExtractor: {e}")
            # Return fallback structure with default values
            return {
            "lifestyle_recommendations": "NR"
}




import asyncio
from typing import Dict, Any
import dspy


class AsyncAggregateClinicalSummaryExtractor(dspy.Module):
    """Async module to extract data using AggregateClinicalSummary signature."""

    def __init__(self):
        super().__init__()
        # Use ChainOfThought for better reasoning
        self.extract = dspy.ChainOfThought(AggregateClinicalSummary)

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
            "clinical_summary": getattr(result, "clinical_summary", "NR"),
        }
        except Exception as e:
            print(f"Error in AsyncAggregateClinicalSummaryExtractor: {e}")
            # Return fallback structure with default values
            return {
            "clinical_summary": "NR"
}






__all__ = [
    "AsyncExtractTextualFieldsExtractor",
    "AsyncExtractNumericFieldsExtractor",
    "AsyncClassifyEnumFieldsExtractor",
    "AsyncSynthesizeRiskStratificationExtractor",
    "AsyncSynthesizeMedicationReviewExtractor",
    "AsyncSynthesizeLifestyleRecommendationsExtractor",
    "AsyncAggregateClinicalSummaryExtractor",
]