import dspy


# ============================================================================
# SIGNATURES - TASK 58E8D8A2
# ============================================================================


import dspy


class ExtractNumericFields(dspy.Signature):
    """Extract numeric patient age information from medical documents.

Form Questions:
- Female Patient Age Mean: "What is the patient's age in years?"

This field captures essential demographic information needed for patient records and clinical analysis."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the document to extract from"""
    )

    female_patient_age_mean: int = dspy.OutputField(
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
72
NR"""
    )




import dspy


class ClassifyEnumFields(dspy.Signature):
    """Classify patient gender from medical document demographics section.

Form Questions:
- most_patient_gender: "What is the patient's gender?"
  Options: Male, Female, Other, Not specified

This field captures essential demographic information typically found in patient intake forms or medical record headers."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the document to extract patient gender from"""
    )

    most_patient_gender: str = dspy.OutputField(
        desc="""Patient's gender.

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
- Look for gender information in patient demographics, intake forms, or header sections
- If multiple gender references exist, use the most authoritative source (e.g., official demographics section)
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