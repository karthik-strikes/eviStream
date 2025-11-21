import dspy
import asyncio
import json
from typing import Dict, List, Any

from utils.json_parser import safe_json_parse
from dspy_components.tasks.index_test.signatures import (
    ExtractIndexTestCount,
    ExtractIndexTestType,
    ExtractIndexTestBasicInfo,
    ExtractIndexTestMethodology,
    ExtractIndexTestAnalysis,
    ExtractIndexTestNumbers,
    ExtractIndexTestQuality
)


class AsyncIndexTestCounter(dspy.Module):
    """Async module to count all index tests in the study."""
    
    def __init__(self):
        super().__init__()
        self.count_tests = dspy.ChainOfThought(ExtractIndexTestCount)
    
    async def __call__(self, markdown_content: str) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        
        def _extract():
            return self.count_tests(markdown_content=markdown_content)
        
        try:
            result = await loop.run_in_executor(None, _extract)
            return {
                "number_index_tests": int(result.number_index_tests)
            }
        except Exception as e:
            print(f"Error counting index tests: {e}")
            return {"number_index_tests": 0}


class AsyncIndexTestTypeExtractor(dspy.Module):
    """Async module to extract test type classification."""
    
    def __init__(self):
        super().__init__()
        self.extract_type = dspy.ChainOfThought(ExtractIndexTestType)
    
    async def __call__(self, markdown_content: str, test_number: int, total_tests: int) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        
        def _extract():
            return self.extract_type(
                markdown_content=markdown_content,
                test_number=test_number,
                total_tests=total_tests
            )
        
        try:
            result = await loop.run_in_executor(None, _extract)
            return {
                "type_category": result.test_type_category,
                "type_comment": result.test_type_comment
            }
        except Exception as e:
            print(f"Error extracting test type: {e}")
            return {"type_category": "other", "type_comment": "Error extracting type"}


class AsyncIndexTestBasicExtractor(dspy.Module):
    """Async module to extract basic test information."""
    
    def __init__(self):
        super().__init__()
        self.extract_basic = dspy.ChainOfThought(ExtractIndexTestBasicInfo)
    
    async def __call__(self, markdown_content: str, test_number: int, total_tests: int) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        
        def _extract():
            return self.extract_basic(
                markdown_content=markdown_content,
                test_number=test_number,
                total_tests=total_tests
            )
        
        try:
            result = await loop.run_in_executor(None, _extract)
            return {
                "subform": result.subform,
                "brand_name": result.brand_name
            }
        except Exception as e:
            print(f"Error extracting basic info: {e}")
            return {"subform": f"Test {test_number}", "brand_name": "NR"}


class AsyncIndexTestMethodologyExtractor(dspy.Module):
    """Async module to extract test methodology."""
    
    def __init__(self):
        super().__init__()
        self.extract_methodology = dspy.ChainOfThought(ExtractIndexTestMethodology)
    
    async def __call__(self, markdown_content: str, test_name: str) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        
        def _extract():
            return self.extract_methodology(
                markdown_content=markdown_content,
                test_name=test_name
            )
        
        try:
            result = await loop.run_in_executor(None, _extract)
            return {
                "site_selection": result.site_selection,
                "specimen_collection": result.specimen_collection,
                "collection_device": result.collection_device,
                "technique": result.technique,
                "staining_procedure": result.staining_procedure,
                "sample_collection": result.sample_collection
            }
        except Exception as e:
            print(f"Error extracting methodology: {e}")
            return {k: "NR" for k in ["site_selection", "specimen_collection", "collection_device", "technique", "staining_procedure", "sample_collection"]}


class AsyncIndexTestAnalysisExtractor(dspy.Module):
    """Async module to extract analysis methods."""
    
    def __init__(self):
        super().__init__()
        self.extract_analysis = dspy.ChainOfThought(ExtractIndexTestAnalysis)
    
    async def __call__(self, markdown_content: str, test_name: str) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        
        def _extract():
            return self.extract_analysis(
                markdown_content=markdown_content,
                test_name=test_name
            )
        
        try:
            result = await loop.run_in_executor(None, _extract)
            return {
                "analysis_methods": result.analysis_methods,
                "ai_analysis": result.ai_analysis,
                "positivity_threshold": result.positivity_threshold,
                "positivity_threshold_transformed": result.positivity_threshold_transformed,
                "atypical_positive_negative": result.atypical_positive_negative
            }
        except Exception as e:
            print(f"Error extracting analysis: {e}")
            return {k: "NR" for k in ["analysis_methods", "ai_analysis", "positivity_threshold", "positivity_threshold_transformed", "atypical_positive_negative"]}


class AsyncIndexTestNumbersExtractor(dspy.Module):
    """Async module to extract participant/lesion numbers."""
    
    def __init__(self):
        super().__init__()
        self.extract_numbers = dspy.ChainOfThought(ExtractIndexTestNumbers)
    
    async def __call__(self, markdown_content: str, test_name: str) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        
        def _extract():
            return self.extract_numbers(
                markdown_content=markdown_content,
                test_name=test_name
            )
        
        try:
            result = await loop.run_in_executor(None, _extract)
            return {
                "patients_received_n": result.patients_received_n,
                "patients_analyzed_n": result.patients_analyzed_n,
                "lesions_received_n": result.lesions_received_n,
                "lesions_analyzed_n": result.lesions_analyzed_n
            }
        except Exception as e:
            print(f"Error extracting numbers: {e}")
            return {k: "NR" for k in ["patients_received_n", "patients_analyzed_n", "lesions_received_n", "lesions_analyzed_n"]}


class AsyncIndexTestQualityExtractor(dspy.Module):
    """Async module to extract quality measures."""
    
    def __init__(self):
        super().__init__()
        self.extract_quality = dspy.ChainOfThought(ExtractIndexTestQuality)
    
    async def __call__(self, markdown_content: str, test_name: str) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        
        def _extract():
            return self.extract_quality(
                markdown_content=markdown_content,
                test_name=test_name
            )
        
        try:
            result = await loop.run_in_executor(None, _extract)
            return {
                "assessor_training": result.assessor_training,
                "assessor_blinding": result.assessor_blinding,
                "examiner_blinding": result.examiner_blinding,
                "additional_comments": result.additional_comments
            }
        except Exception as e:
            print(f"Error extracting quality: {e}")
            return {k: "NR" for k in ["assessor_training", "assessor_blinding", "examiner_blinding", "additional_comments"]}


class AsyncIndexTestPipeline(dspy.Module):
    """Complete async pipeline for extracting all index tests from diagnostic accuracy papers."""
    
    def __init__(self, max_concurrent: int = 5):
        super().__init__()
        self.test_counter = AsyncIndexTestCounter()
        self.type_extractor = AsyncIndexTestTypeExtractor()
        self.basic_extractor = AsyncIndexTestBasicExtractor()
        self.methodology_extractor = AsyncIndexTestMethodologyExtractor()
        self.analysis_extractor = AsyncIndexTestAnalysisExtractor()
        self.numbers_extractor = AsyncIndexTestNumbersExtractor()
        self.quality_extractor = AsyncIndexTestQualityExtractor()
        self.max_concurrent = max_concurrent
        self._semaphore = None
    
    def _get_semaphore(self):
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent)
        return self._semaphore
    
    async def forward(self, markdown_content: str):
        """Extract all index test records from the paper."""
        
        # Step 1: Count tests
        count_result = await self.test_counter(markdown_content)
        num_tests = count_result.get("number_index_tests", 0)
        
        if num_tests == 0:
            return dspy.Prediction(extracted_records=[])
        
        # Step 2: Extract all tests concurrently
        tasks = []
        for test_num in range(1, num_tests + 1):
            task = self._process_single_test(markdown_content, test_num, num_tests)
            tasks.append(task)
        
        all_records = await asyncio.gather(*tasks)
        
        return dspy.Prediction(extracted_records=all_records)
    
    async def _process_single_test(self, markdown_content: str, test_number: int, total_tests: int):
        """Process a single index test with parallel extraction of all components."""
        semaphore = self._get_semaphore()
        
        async with semaphore:
            # Step 1: Extract type and basic info first to get test identifiers
            type_task = self.type_extractor(markdown_content, test_number, total_tests)
            basic_task = self.basic_extractor(markdown_content, test_number, total_tests)
            
            type_info, basic_info = await asyncio.gather(type_task, basic_task)
            
            test_name = basic_info.get("subform", f"Test {test_number}")
            
            # Step 2: Extract all other components in parallel
            methodology_task = self.methodology_extractor(markdown_content, test_name)
            analysis_task = self.analysis_extractor(markdown_content, test_name)
            numbers_task = self.numbers_extractor(markdown_content, test_name)
            quality_task = self.quality_extractor(markdown_content, test_name)
            
            methodology, analysis, numbers, quality = await asyncio.gather(
                methodology_task, analysis_task, numbers_task, quality_task
            )
            
            # Step 3: Build the type object structure
            type_category = type_info.get("type_category", "other")
            type_comment = type_info.get("type_comment", "")
            
            type_dict = {
                "cytology": {
                    "selected": type_category == "cytology",
                    "comment": type_comment if type_category == "cytology" else ""
                },
                "vital_staining": {
                    "selected": type_category == "vital_staining",
                    "comment": type_comment if type_category == "vital_staining" else ""
                },
                "autofluorescence": {
                    "selected": type_category == "autofluorescence",
                    "comment": type_comment if type_category == "autofluorescence" else ""
                },
                "tissue_reflectance": {
                    "selected": type_category == "tissue_reflectance",
                    "comment": type_comment if type_category == "tissue_reflectance" else ""
                },
                "other": {
                    "selected": type_category == "other",
                    "comment": type_comment if type_category == "other" else ""
                }
            }
            
            # Step 4: Combine all extracted data into new JSON structure
            structured_record = {
                "type": type_dict,
                "subform": basic_info.get("subform", ""),
                "brand_name": basic_info.get("brand_name", ""),
                "site_selection": methodology.get("site_selection", ""),
                "specimen_collection": methodology.get("specimen_collection", ""),
                "collection_device": methodology.get("collection_device", ""),
                "technique": methodology.get("technique", ""),
                "staining_procedure": methodology.get("staining_procedure", ""),
                "sample_collection": methodology.get("sample_collection", ""),
                "analysis_methods": analysis.get("analysis_methods", ""),
                "ai_analysis": analysis.get("ai_analysis", ""),
                "patients_received_n": numbers.get("patients_received_n", ""),
                "patients_analyzed_n": numbers.get("patients_analyzed_n", ""),
                "lesions_received_n": numbers.get("lesions_received_n", ""),
                "lesions_analyzed_n": numbers.get("lesions_analyzed_n", ""),
                "positivity_threshold": analysis.get("positivity_threshold", ""),
                "positivity_threshold_transformed": analysis.get("positivity_threshold_transformed", ""),
                "atypical_positive_negative": analysis.get("atypical_positive_negative", ""),
                "assessor_training": quality.get("assessor_training", ""),
                "assessor_blinding": quality.get("assessor_blinding", ""),
                "examiner_blinding": quality.get("examiner_blinding", ""),
                "additional_comments": quality.get("additional_comments", "")
            }
            
            return structured_record


class SyncIndexTestPipelineWrapper(dspy.Module):
    """Synchronous wrapper for DSPy optimizer compatibility."""
    
    def __init__(self):
        super().__init__()
        self.async_pipeline = AsyncIndexTestPipeline()
    
    def forward(self, markdown_content: str):
        """Synchronous forward method."""
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                except ImportError:
                    pass
        except RuntimeError:
            pass
        
        self.async_pipeline._semaphore = None
        result = asyncio.run(self.async_pipeline(markdown_content))
        return result
    
    def __deepcopy__(self, memo):
        return SyncIndexTestPipelineWrapper()