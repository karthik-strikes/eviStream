import dspy


# ============================================================================
# SIGNATURES - TASK 337538A9
# ============================================================================


import dspy


class ExtractNumericFields(dspy.Signature):
    """Extract numeric patient age information from medical documents.

Form Questions:
- Patient Age: "What is the patient's age in years?"

This field captures essential demographic information needed for patient identification and age-related medical analysis."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the document to extract from"""
    )

    patient_age: int = dspy.OutputField(
        desc="""Patient's age in years.

Description: Patient's age in years

Extraction Hints:
- Look in patient demographics or header section

Rules:
- Extract numeric age value only
- Round to nearest integer if decimal provided
- Must be a valid integer between 0 and 120
- Use "NR" if not reported or value is missing

Examples:
67
45
23
82
NR"""
    )




import dspy


class ClassifyEnumFields(dspy.Signature):
    """Classify patient gender from medical document demographics section.

Form Questions:
- Patient Gender: "What is the patient's gender?"
  Options: Male, Female, Other, Not specified

This field captures demographic information essential for patient identification and medical record keeping."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the document to extract patient gender from"""
    )

    patient_gender: str = dspy.OutputField(
        desc="""Patient's gender classification.

Description: Patient's gender

Options:
- "Male"
- "Female"
- "Other"
- "Not specified"

Extraction Hints:
- Usually in demographics section

Rules:
- Must be exactly one of the options listed above
- Use exact spelling and capitalization
- Look for gender information in patient demographics, registration, or personal information sections
- If multiple gender references exist, use the one from the official demographics section
- Use "NR" if not reported or value is missing

Examples:
Female
Male
Other
Not specified
NR"""
    )






__all__ = [
    "ExtractNumericFields",
    "ClassifyEnumFields",
]