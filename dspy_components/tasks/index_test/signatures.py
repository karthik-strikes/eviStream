import dspy

# ==================== SIGNATURES ====================

class ExtractIndexTestCount(dspy.Signature):
    """Extract the total number of index tests evaluated in the diagnostic accuracy study."""
    
    markdown_content: str = dspy.InputField(desc="Full markdown content of the diagnostic accuracy research paper")
    
    number_index_tests: int = dspy.OutputField(
        desc="Total number of distinct index tests evaluated in the study. Must be an integer (e.g., 1, 2)."
    )


class ExtractIndexTestType(dspy.Signature):
    """Extract the test type classification for a specific index test."""
    
    markdown_content: str = dspy.InputField(desc="Full markdown content of the diagnostic accuracy research paper")
    test_number: int = dspy.InputField(desc="Index test number to extract (1-based indexing)")
    total_tests: int = dspy.InputField(desc="Total number of index tests in the study")
    
    test_type_category: str = dspy.OutputField(
        desc="The primary category (cytology, vital_staining, autofluorescence, tissue_reflectance, or other). "
        "Return ONLY the category name in lowercase with underscores."
    )
    
    test_type_comment: str = dspy.OutputField(
        desc="Brief descriptive comment about the test (e.g., '1% Toluidine Blue', '5% Acetic acid'). "
        "Extract from the paper. If not mentioned, return 'NR'."
    )


class ExtractIndexTestBasicInfo(dspy.Signature):
    """Extract basic identification information for a specific index test."""
    
    markdown_content: str = dspy.InputField(desc="Full markdown content of the diagnostic accuracy research paper")
    test_number: int = dspy.InputField(desc="Index test number to extract (1-based indexing)")
    total_tests: int = dspy.InputField(desc="Total number of index tests in the study")
    
    subform: str = dspy.OutputField(
        desc="The specific test description combining category and details (e.g., 'Vital Staining (1% Toluidine Blue)', 'acetic acid'). "
        "This is the primary identifier for the test."
    )
    
    brand_name: str = dspy.OutputField(
        desc="Commercial name/brand of test kit if mentioned (e.g., 'VELscope'). If not mentioned, return 'NR'."
    )


class ExtractIndexTestMethodology(dspy.Signature):
    """Extract specimen collection and processing methodology for a specific index test."""
    
    markdown_content: str = dspy.InputField(desc="Full markdown content of the diagnostic accuracy research paper")
    test_name: str = dspy.InputField(desc="Name of the specific index test (subform) to extract methodology for")
    
    site_selection: str = dspy.OutputField(
        desc="Anatomical site(s) or selection criteria. May include multiple lines. If not reported, return 'NR'."
    )
    
    specimen_collection: str = dspy.OutputField(
        desc="How specimen was collected. For visual/staining tests, return empty string. "
        "Do NOT infer or write explanations."
    )
    
    collection_device: str = dspy.OutputField(
        desc="Device used for collection. If not explicitly stated, return empty string. "
        "Do NOT return 'NR' or infer devices unless explicitly stated."
    )
    
    technique: str = dspy.OutputField(
        desc="The detailed, step-by-step procedure for administering the test. "
        "Often a direct quote from the paper. Include all procedural details."
    )
    
    staining_procedure: str = dspy.OutputField(
        desc="ONLY return a value if the paper specifies a staining method *separate* from the index test itself. "
        "If the test *is* a stain (e.g., Toluidine Blue), this field MUST be empty. Do NOT infer."
    )
    
    sample_collection: str = dspy.OutputField(
        desc="This field is not used. Always return empty string. The procedure is in the 'technique' field."
    )


class ExtractIndexTestAnalysis(dspy.Signature):
    """Extract analysis and interpretation methods for a specific index test."""
    
    markdown_content: str = dspy.InputField(desc="Full markdown content of the diagnostic accuracy research paper")
    test_name: str = dspy.InputField(desc="Name of the specific index test (subform) to extract analysis methods for")
    
    analysis_methods: str = dspy.OutputField(
        desc="Specific named analysis method (e.g., 'Bethesda system'). "
        "If not stated, return empty string. Do NOT summarize the paper's validation."
    )
    
    ai_analysis: str = dspy.OutputField(
        desc="Whether AI was used. Only 'yes' or 'no' if explicitly stated. "
        "If not mentioned, return empty string. Do NOT infer."
    )
    
    positivity_threshold: str = dspy.OutputField(
        desc="The original positivity threshold as stated in paper. "
        "Include the full definition or quote (e.g., 'A stain was considered as positive...'). "
        "May include multiple lines with additional context."
    )
    
    positivity_threshold_transformed: str = dspy.OutputField(
        desc="A standardized or simplified threshold summary. "
        "If the paper does not provide a transformed summary, return empty string. Do NOT create your own."
    )
    
    atypical_positive_negative: str = dspy.OutputField(
        desc="How atypical/borderline results were classified. "
        "If not explicitly stated, return empty string. Do NOT infer or summarize."
    )


class ExtractIndexTestNumbers(dspy.Signature):
    """Extract participant and lesion numbers for a specific index test."""
    
    markdown_content: str = dspy.InputField(desc="Full markdown content of the diagnostic accuracy research paper")
    test_name: str = dspy.InputField(desc="Name of the specific index test (subform) to extract numbers for")
    
    patients_received_n: str = dspy.OutputField(
        desc="Number of patients who received the index test. Return as string or integer. 'NR' if not reported."
    )
    
    patients_analyzed_n: str = dspy.OutputField(
        desc="Number of patients whose test results were analyzed. Return as string or integer. 'NR' if not reported."
    )
    
    lesions_received_n: str = dspy.OutputField(
        desc="Number of lesions tested. Return as string or 'NR' if not reported."
    )
    
    lesions_analyzed_n: str = dspy.OutputField(
        desc="Number of lesions analyzed. Return as string or 'NR' if not reported."
    )


class ExtractIndexTestQuality(dspy.Signature):
    """Extract quality assessment measures for a specific index test."""
    
    markdown_content: str = dspy.InputField(desc="Full markdown content of the diagnostic accuracy research paper")
    test_name: str = dspy.InputField(desc="Name of the specific index test (subform) to extract quality measures for")
    
    assessor_training: str = dspy.OutputField(
        desc="Information about calibration/training of test assessors, often a quote. 'NR' if not reported."
    )
    
    assessor_blinding: str = dspy.OutputField(
        desc="Whether assessors (clinicians) were blinded to reference standard results. 'NR' if not reported. "
        "Do NOT infer 'Yes' from the study design."
    )
    
    examiner_blinding: str = dspy.OutputField(
        desc="Whether examiners (e.g., pathologists) were blinded to the index test results, often a quote. "
        "'NR' if not reported."
    )
    
    additional_comments: str = dspy.OutputField(
        desc="ONLY for brief, specific notes from the data extractor (e.g., 'Only Group B received index test.'). "
        "Return empty string unless there is a specific data ambiguity. Do NOT write summaries."
    )



class IndexTestRecord(dspy.Signature):
    """Represents the schema for a single index test record with nested structure matching ground truth."""
    
    markdown_content: str = dspy.InputField(desc="Full markdown content")
    
    index_test_json: str = dspy.OutputField(
        desc="""JSON string representing a single index test with this EXACT nested structure:
        {
            "type": {
                "cytology": {
                    "selected": boolean,
                    "comment": "string"
                },
                "vital_staining": {
                    "selected": boolean,
                    "comment": "string"
                },
                "autofluorescence": {
                    "selected": boolean,
                    "comment": "string"
                },
                "tissue_reflectance": {
                    "selected": boolean,
                    "comment": "string"
                },
                "other": {
                    "selected": boolean,
                    "comment": "string"
                }
            },
            "subform": "string",
            "brand_name": "string",
            "site_selection": "string",
            "specimen_collection": "string",
            "collection_device": "string",
            "technique": "string",
            "staining_procedure": "string",
            "sample_collection": "string",
            "analysis_methods": "string",
            "ai_analysis": "string",
            "patients_received_n": string_or_number,
            "patients_analyzed_n": string_or_number,
            "lesions_received_n": string_or_number,
            "lesions_analyzed_n": string_or_number,
            "positivity_threshold": "string",
            "positivity_threshold_transformed": "string",
            "atypical_positive_negative": "string",
            "assessor_training": "string",
            "assessor_blinding": "string",
            "examiner_blinding": "string",
            "additional_comments": "string"
        }
        
        IMPORTANT: Keep the nested structure for 'type'. Do NOT flatten it."""
    )
