import dspy


# ============================================================================
# SIGNATURES - TASK 6AC3352A
# ============================================================================


import dspy


class ExtractTextualFields(dspy.Signature):
    """Extract structured textual information from clinical study documents including study title, interventions, and outcomes.

Form Questions:
- Study Title: "What is the title of the clinical study?"
- Interventions: "What interventions were tested in the study?"
- Outcomes: "What outcomes were measured and what were the results?"

These fields capture essential information about clinical research studies needed for systematic reviews, meta-analyses, and evidence synthesis."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the clinical study document to extract from"""
    )

    study_title: str = dspy.OutputField(
        desc="""Title of the clinical study.

Description: Title of the clinical study

Extraction Hints:
- Look in the title, abstract, or introduction section

Rules:
- Extract the complete official title of the study as written in the document
- Include subtitle if present
- Preserve original capitalization and punctuation
- Use "NR" if not reported or title is missing

Examples:
Randomized controlled trial of oral rinse for plaque reduction
A Double-Blind Study of Metformin vs Placebo in Type 2 Diabetes: The ACCORD Trial
Effects of Physical Therapy on Mobility in Elderly Patients
NR"""
    )

    interventions: str = dspy.OutputField(
        desc="""List of interventions tested in the study with details on name, type, and dosage.

Description: List of interventions tested in the study. Each intervention should include name, type, and dosage if available

Extraction Hints:
- Look in methods section, intervention description. Extract all interventions mentioned

Rules:
- Extract all interventions mentioned in the study
- Include intervention name, type, and dosage/frequency if available
- List multiple interventions separated by semicolons or commas
- Include control/placebo groups if mentioned
- Preserve specific details like dosage amounts and administration schedules
- Use "NR" if not reported or interventions are not described

Examples:
Drug A: 10mg twice daily, Placebo: matching tablets
Chlorhexidine oral rinse 0.12% twice daily; Fluoride rinse 0.05% once daily; Control: water rinse
Cognitive behavioral therapy (12 weekly sessions); Standard care (usual treatment)
NR"""
    )

    outcomes: str = dspy.OutputField(
        desc="""List of outcomes measured in the study including primary and secondary outcomes with results.

Description: List of outcomes measured in the study. Include primary and secondary outcomes with their results if available

Extraction Hints:
- Look in results section, outcomes table, or methods section where outcomes are pre-specified

Rules:
- Extract all primary and secondary outcomes mentioned
- Label outcomes as primary or secondary if specified
- Include quantitative results (means, standard deviations, percentages, p-values) if reported
- List multiple outcomes separated by semicolons or periods
- Include measurement scales or units if mentioned
- Use "NR" if not reported or outcomes are not described

Examples:
Primary: Plaque index reduction (mean 0.45, SD 0.12). Secondary: Gingival bleeding (reduced by 30%)
Primary outcome: HbA1c reduction (mean -1.2%, p<0.001); Secondary outcomes: Weight loss (mean -3.5 kg), Blood pressure reduction (systolic -8 mmHg)
6-minute walk distance increased by 45 meters (95% CI: 32-58); Quality of life score improved by 12 points on SF-36
NR"""
    )




import dspy


class ExtractNumericFields(dspy.Signature):
    """Extract numeric field information including total participant count from research documents.

Form Questions:
- Total Participants: "What is the total number of participants enrolled in the study?"

This field captures essential quantitative information about study participation needed for research analysis and meta-analysis."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the research document to extract from"""
    )

    total_participants: int = dspy.OutputField(
        desc="""Total number of participants enrolled in the study.

Description: Total number of participants enrolled

Extraction Hints:
- Look in methods section, participant flow, or results section

Rules:
- Extract the total count of participants enrolled in the study
- Must be a valid positive integer
- If multiple numbers are mentioned (e.g., enrolled vs. completed), use the total enrolled count
- Do not include dropouts or excluded participants unless specified as part of total enrollment
- Use "NR" if not reported or value is missing

Examples:
150
1250
45
NR"""
    )






__all__ = [
    "ExtractTextualFields",
    "ExtractNumericFields",
]