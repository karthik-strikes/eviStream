import dspy


# ============================================================================
# SIGNATURES - TASK 0120084B
# ============================================================================


import dspy


class ExtractNumericFields(dspy.Signature):
    """Extract numeric patient age information from medical documents.

Form Questions:
- Patient Age: "What is the patient's age in years?"

This field captures essential demographic information needed for medical case analysis and age-related treatment considerations."""

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
    """Classify patient gender from medical documents.

Form Questions:
- Patient Gender: "What is the patient's gender?"
  Options: Male, Female, Other, Not specified

This field captures demographic information typically found in patient intake forms or medical record headers."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the document to extract patient gender from"""
    )

    patient_gender: str = dspy.OutputField(
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
- If document uses synonyms (M/F, man/woman), map to the appropriate option
- Use "Not specified" if gender is explicitly stated as unknown or not provided
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