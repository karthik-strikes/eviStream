import dspy


# ============================================================================
# SIGNATURES - TASK 496F2C0F
# ============================================================================


import dspy


class ExtractTextualFields(dspy.Signature):
    """Extract textual information including the most discussed gender and authors from research papers.

Form Questions:
- Most Discussed Gender: "What is the most discussed gender in the paper?"
- Author: "Who are the authors of the paper?"

These fields capture key metadata about the paper's content focus and authorship."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the research paper to extract from"""
    )

    most_discussed_gender: str = dspy.OutputField(
        desc="""The most discussed gender in the paper.

Description: most_discussed_gender in paper

Rules:
- Identify which gender (e.g., male, female, non-binary, mixed) is most frequently discussed or is the primary focus
- Look for gender mentions in study populations, participant demographics, or analysis sections
- Extract the gender category as written in the document
- If multiple genders are equally discussed, specify "mixed" or "both"
- Use "NR" if not reported or cannot be determined

Examples:
male
female
mixed
both male and female
non-binary
NR"""
    )

    author: str = dspy.OutputField(
        desc="""Authors of the paper.

Description: authors of the paper

Rules:
- Extract all author names as listed in the paper
- Preserve the order and format as written (e.g., "Last, First" or "First Last")
- Separate multiple authors with commas or semicolons as appropriate
- Include all authors, not just first or corresponding author
- Use "NR" if not reported or author information is missing

Examples:
John Smith, Jane Doe, Robert Johnson
Smith J, Doe J, Johnson R
Maria Garcia et al.
Dr. Sarah Chen, Prof. Michael Brown
NR"""
    )




import dspy


class ExtractNumericFields(dspy.Signature):
    """Extract numeric age values from two different studies for comparative analysis.

Form Questions:
- Mean_age_study1: "What is the mean age in study 1?"
- Mean_age_study2: "What is the mean age in study 2?"

These fields capture age statistics from multiple studies to enable cross-study comparison and meta-analysis."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the document to extract from"""
    )

    Mean_age_study1: float = dspy.OutputField(
        desc="""Mean age in study 1.

Description: Mean_age_study1

Rules:
- Extract the numeric mean age value for study 1
- Include decimal values if provided (e.g., 45.5)
- Look for age statistics in study 1 results or demographics section
- Must be a valid number (can be integer or decimal)
- Use "NR" if not reported or value is missing

Examples:
45.5
62.3
38.0
NR"""
    )

    Mean_age_study2: float = dspy.OutputField(
        desc="""Mean age in study 2.

Description: Mean_age_study2

Rules:
- Extract the numeric mean age value for study 2
- Include decimal values if provided (e.g., 47.2)
- Look for age statistics in study 2 results or demographics section
- Must be a valid number (can be integer or decimal)
- Use "NR" if not reported or value is missing

Examples:
47.2
59.8
41.0
NR"""
    )






__all__ = [
    "ExtractTextualFields",
    "ExtractNumericFields",
]