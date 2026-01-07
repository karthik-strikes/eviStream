import dspy


# ============================================================================
# SIGNATURES - TASK 2AC18892
# ============================================================================


import dspy


class ExtractTextualFields(dspy.Signature):
    """Extract textual fields related to primary and secondary outcomes from clinical research papers.

Form Questions:
- Primary Outcome Name: "What is the name of the primary dichotomous outcome measure?"
- Primary Outcome Definition: "How is the primary outcome defined in the study?"
- Confidence Interval: "What is the 95% confidence interval for the effect measure?"
- P-Value: "What is the p-value for statistical significance?"
- Time Point: "At what time point was the outcome measured?"
- Secondary Outcomes: "What are the secondary dichotomous outcomes measured?"

These fields capture essential statistical and outcome information from clinical trials and research studies, including effect measures, statistical significance, and outcome definitions."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the clinical research paper"""
    )

    primary_outcome_name: str = dspy.OutputField(
        desc="""Name of the primary dichotomous outcome measure.

Description: Name of the primary dichotomous outcome measure

Rules:
- Extract the exact name of the primary outcome as stated in the study
- Focus on dichotomous (binary) outcomes (yes/no, success/failure, present/absent)
- Look in methods, objectives, or results sections
- Use the terminology exactly as written in the document
- Use "NR" if not reported or value is missing

Examples:
Treatment success
Disease recurrence
Mortality
30-day survival
NR"""
    )

    primary_outcome_definition: str = dspy.OutputField(
        desc="""How the primary outcome is defined in the study.

Description: How the primary outcome is defined in the study

Rules:
- Extract the complete definition or criteria for the primary outcome
- Include specific thresholds, timeframes, or measurement criteria
- Look in methods section for detailed outcome definitions
- Capture the full definition verbatim when possible
- Use "NR" if not reported or value is missing

Examples:
Complete resolution of symptoms at 6 months
Absence of tumor recurrence on imaging at 12-month follow-up
Achievement of HbA1c < 7% at end of treatment period
Reduction in pain score by at least 50% from baseline
NR"""
    )

    confidence_interval: str = dspy.OutputField(
        desc="""95% confidence interval for the effect measure.

Description: 95% confidence interval for the effect measure

Rules:
- Extract the 95% confidence interval (CI) for the primary effect measure
- Include both lower and upper bounds
- Preserve the format as written (e.g., "1.2-2.4" or "1.2 to 2.4" or "[1.2, 2.4]")
- Look in results or abstract sections
- Use "NR" if not reported or value is missing

Examples:
1.2-2.4
0.85 to 1.45
[1.15, 2.87]
95% CI: 0.92-1.38
NR"""
    )

    p_value: str = dspy.OutputField(
        desc="""P-value for statistical significance.

Description: P-value for statistical significance

Rules:
- Extract the p-value associated with the primary outcome
- Include exact value when provided (e.g., "0.03", "0.001")
- Include inequality notation if used (e.g., "<0.05", "<0.001")
- Look in results section or statistical analysis tables
- Use "NR" if not reported or value is missing

Examples:
0.03
<0.001
p=0.045
0.12
NR"""
    )

    time_point: str = dspy.OutputField(
        desc="""Time point at which outcome was measured.

Description: Time point at which outcome was measured

Rules:
- Extract the specific time point when the primary outcome was assessed
- Include units (months, years, weeks, days)
- May be a single time point or range
- Look in methods or results sections for follow-up duration
- Use "NR" if not reported or value is missing

Examples:
6 months
1 year
End of study
12-month follow-up
30 days post-intervention
NR"""
    )

    secondary_outcomes: str = dspy.OutputField(
        desc="""List of secondary dichotomous outcomes measured.

Description: List of secondary dichotomous outcomes measured

Rules:
- Extract all secondary dichotomous outcomes mentioned in the study
- Format as comma-separated list
- Focus on binary/dichotomous outcomes (not continuous measures)
- Look in methods section under secondary outcomes or endpoints
- Include outcome names as stated in the document
- Use "NR" if not reported or value is missing

Examples:
Adverse events, Treatment adherence, Patient satisfaction
Disease progression, Quality of life improvement, Hospitalization
All-cause mortality, Cardiovascular events, Treatment discontinuation
Infection rate, Readmission within 30 days
NR"""
    )




import dspy


class ExtractNumericFields(dspy.Signature):
    """Extract numeric data from clinical trial results including intervention and control group statistics, and effect measures.

Form Questions:
- Intervention Group Events: "How many events occurred in the intervention group?"
- Intervention Group Total: "What was the total number of participants in the intervention group?"
- Control Group Events: "How many events occurred in the control group?"
- Control Group Total: "What was the total number of participants in the control group?"
- Relative Risk: "What is the relative risk (RR) value if reported?"
- Odds Ratio: "What is the odds ratio (OR) value if reported?"

These fields capture essential statistical data for meta-analysis and systematic review of clinical trial outcomes."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the clinical trial document to extract numeric data from"""
    )

    intervention_group_events: int = dspy.OutputField(
        desc="""Number of events in the intervention group.

Description: Number of events in the intervention group

Rules:
- Extract the numeric count of events (e.g., adverse events, outcomes, incidents) in the intervention/treatment group
- Must be a non-negative integer
- Look in results tables, outcome sections, or statistical summaries
- Use "NR" if not reported or value is missing

Examples:
45
120
8
NR"""
    )

    intervention_group_total: int = dspy.OutputField(
        desc="""Total number of participants in intervention group.

Description: Total number of participants in intervention group

Rules:
- Extract the total number of participants enrolled or analyzed in the intervention/treatment group
- Must be a positive integer
- Look in participant flow diagrams, baseline characteristics tables, or methods section
- Use "NR" if not reported or value is missing

Examples:
150
500
75
NR"""
    )

    control_group_events: int = dspy.OutputField(
        desc="""Number of events in the control group.

Description: Number of events in the control group

Rules:
- Extract the numeric count of events (e.g., adverse events, outcomes, incidents) in the control/placebo group
- Must be a non-negative integer
- Look in results tables, outcome sections, or statistical summaries
- Use "NR" if not reported or value is missing

Examples:
30
95
12
NR"""
    )

    control_group_total: int = dspy.OutputField(
        desc="""Total number of participants in control group.

Description: Total number of participants in control group

Rules:
- Extract the total number of participants enrolled or analyzed in the control/placebo group
- Must be a positive integer
- Look in participant flow diagrams, baseline characteristics tables, or methods section
- Use "NR" if not reported or value is missing

Examples:
150
500
80
NR"""
    )

    relative_risk: float = dspy.OutputField(
        desc="""Relative risk (RR) value if reported.

Description: Relative risk (RR) value if reported

Rules:
- Extract the relative risk value from statistical analysis sections
- Must be a positive number (typically between 0.01 and 100)
- May be reported as RR, risk ratio, or rate ratio
- Extract the point estimate only (not confidence intervals)
- Use "NR" if not reported or value is missing

Examples:
1.5
0.75
2.3
NR"""
    )

    odds_ratio: float = dspy.OutputField(
        desc="""Odds ratio (OR) value if reported.

Description: Odds ratio (OR) value if reported

Rules:
- Extract the odds ratio value from statistical analysis sections
- Must be a positive number (typically between 0.01 and 100)
- Extract the point estimate only (not confidence intervals)
- Look for OR in logistic regression results or effect measure tables
- Use "NR" if not reported or value is missing

Examples:
1.8
0.65
3.2
NR"""
    )




import dspy


class ClassifyEnumFields(dspy.Signature):
    """Classify outcome assessment methodology and blinding status from research documents.

Form Questions:
- Outcome Assessment Method: "How was the outcome assessed?"
  Options: Clinical examination, Patient reported, Laboratory test, Imaging, Other
- Blinding Status: "Was the outcome assessment blinded?"
  Options: Blinded, Unblinded, Not reported

These fields capture critical methodological details about outcome measurement and potential bias in clinical research studies."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the research document to extract from"""
    )

    outcome_assessment_method: str = dspy.OutputField(
        desc="""How the outcome was assessed.

Description: How the outcome was assessed

Options:
- "Clinical examination"
- "Patient reported"
- "Laboratory test"
- "Imaging"
- "Other"

Rules:
- Must be exactly one of the options listed above
- Use exact spelling and capitalization
- Look in the methods or outcome assessment sections of the document
- Choose the primary method if multiple assessment methods are mentioned
- Use "NR" if not reported or value is missing

Examples:
Clinical examination
Patient reported
Laboratory test
Imaging
Other
NR"""
    )

    blinding_status: str = dspy.OutputField(
        desc="""Whether outcome assessment was blinded.

Description: Whether outcome assessment was blinded

Options:
- "Blinded"
- "Unblinded"
- "Not reported"

Rules:
- Must be exactly one of the options listed above
- Use exact spelling and capitalization
- Look for mentions of blinding, masking, or concealment in outcome assessment
- "Blinded" includes single-blind, double-blind, or triple-blind for outcome assessment
- "Unblinded" means outcome assessors knew treatment allocation
- "Not reported" means the document does not specify blinding status
- Use "NR" if not reported or value is missing

Examples:
Blinded
Unblinded
Not reported
NR"""
    )




import dspy


class DetermineBooleanFields(dspy.Signature):
    """Determine whether intention-to-treat analysis was used in the research study.

Form Questions:
- Intention to Treat: "Was intention-to-treat analysis used in this study?"

Intention-to-treat (ITT) analysis is a key methodological approach in clinical trials where all participants are analyzed in the groups to which they were originally randomized, regardless of whether they completed the study or received the intended treatment."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the research document to extract from"""
    )

    intention_to_treat: bool = dspy.OutputField(
        desc="""Whether intention-to-treat analysis was used in the study.

Description: Whether intention-to-treat analysis was used

Rules:
- Return true if the document explicitly states that intention-to-treat (ITT) analysis was used
- Return true if the document mentions analyzing all randomized participants in their original groups regardless of protocol adherence
- Return false if the document explicitly states ITT was not used or uses per-protocol analysis only
- Return false if only participants who completed the study were analyzed
- Look for phrases like "intention-to-treat", "ITT analysis", "analyzed as randomized", or "all randomized participants were included in the analysis"
- Check the Methods/Statistical Analysis section for ITT methodology
- Use "NR" if the analysis approach is not reported or cannot be determined

Examples:
true
false
NR"""
    )






__all__ = [
    "ExtractTextualFields",
    "ExtractNumericFields",
    "ClassifyEnumFields",
    "DetermineBooleanFields",
]