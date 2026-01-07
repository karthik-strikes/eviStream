import dspy


# ============================================================================
# SIGNATURES - TASK 74BF56A9
# ============================================================================


import dspy


class ExtractTextualFields(dspy.Signature):
    """Extract textual fields related to primary and secondary dichotomous outcomes from clinical research papers.

Form Questions:
- Primary Outcome Name: "What is the name of the primary dichotomous outcome measure?"
- Primary Outcome Definition: "How is the primary outcome defined in the study?"
- Confidence Interval: "What is the 95% confidence interval for the effect measure?"
- P Value: "What is the p-value for statistical significance?"
- Time Point: "At what time point was the outcome measured?"
- Secondary Outcomes: "What secondary dichotomous outcomes were measured?"

These fields capture essential outcome measures and statistical results from clinical trials and research studies, enabling systematic review and meta-analysis of treatment effects."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the clinical research paper to extract outcome data from"""
    )

    primary_outcome_name: str = dspy.OutputField(
        desc="""Name of the primary dichotomous outcome measure.

Description: Name of the primary dichotomous outcome measure

Rules:
- Extract the exact name or label of the primary outcome as stated in the study
- Focus on dichotomous (binary) outcomes (yes/no, success/failure, present/absent)
- Look in methods, objectives, or results sections for primary outcome identification
- Use the terminology exactly as written in the document
- Use "NR" if not reported or cannot be determined

Examples:
Treatment success
Disease recurrence
Mortality
30-day survival
Clinical response
NR"""
    )

    primary_outcome_definition: str = dspy.OutputField(
        desc="""How the primary outcome is defined in the study.

Description: How the primary outcome is defined in the study

Rules:
- Extract the complete definition or criteria used to determine the primary outcome
- Include specific thresholds, timeframes, or measurement criteria if provided
- Capture the operational definition as stated by the authors
- May be multiple sentences if the definition is detailed
- Use "NR" if not reported or definition is not provided

Examples:
Complete resolution of symptoms at 6 months
Absence of tumor recurrence on imaging at 2-year follow-up
Achievement of HbA1c < 7% without hypoglycemic events
Composite of death, myocardial infarction, or stroke within 30 days
NR"""
    )

    confidence_interval: str = dspy.OutputField(
        desc="""95% confidence interval for the effect measure.

Description: 95% confidence interval for the effect measure

Rules:
- Extract the 95% confidence interval (CI) for the primary outcome effect measure
- Include both lower and upper bounds
- Preserve the format as written (e.g., "1.2-2.4" or "1.2 to 2.4" or "[1.2, 2.4]")
- If multiple CIs are reported, extract the one for the primary outcome
- Use "NR" if not reported or cannot be found

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
- Extract the p-value associated with the primary outcome analysis
- Preserve exact format as reported (e.g., "0.03", "p=0.03", "p<0.001")
- Include inequality symbols if used (< or >)
- If multiple p-values reported, extract the one for the primary outcome
- Use "NR" if not reported or cannot be determined

Examples:
0.03
p=0.045
p<0.001
0.12
p>0.05
NR"""
    )

    time_point: str = dspy.OutputField(
        desc="""Time point at which the primary outcome was measured.

Description: Time point at which outcome was measured

Rules:
- Extract the specific time point when the primary outcome was assessed
- Include units (days, weeks, months, years)
- Use the terminology as stated in the document
- If multiple time points, extract the primary assessment time
- Use "NR" if not reported or timeframe is unclear

Examples:
6 months
1 year
End of study
30 days
12 weeks post-intervention
At hospital discharge
NR"""
    )

    secondary_outcomes: str = dspy.OutputField(
        desc="""List of secondary dichotomous outcomes measured.

Description: List of secondary dichotomous outcomes measured

Rules:
- Extract all secondary dichotomous (binary) outcomes reported in the study
- Format as comma-separated list or JSON array string
- Include only dichotomous outcomes, not continuous measures
- Use outcome names as stated in the document
- If no secondary outcomes or only continuous outcomes reported, use "NR"

Examples:
Adverse events, Treatment adherence, Patient satisfaction
Hospital readmission, Medication compliance, Treatment discontinuation
["Infection", "Bleeding complications", "Device failure"]
Disease progression, Quality of life improvement
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

These fields capture essential statistical data from clinical trials needed for meta-analysis and effect size calculations."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the clinical trial document to extract numeric data from"""
    )

    intervention_group_events: int = dspy.OutputField(
        desc="""Number of events in the intervention group.

Description: Number of events in the intervention group

Rules:
- Extract the numeric count of events (e.g., adverse events, outcomes, occurrences) in the intervention/treatment group
- Must be a non-negative integer
- Look in results tables, outcome sections, or statistical summaries
- If multiple event types are reported, extract the primary outcome events
- Use "NR" if not reported or value is missing

Examples:
45
12
0
89
NR"""
    )

    intervention_group_total: int = dspy.OutputField(
        desc="""Total number of participants in intervention group.

Description: Total number of participants in intervention group

Rules:
- Extract the total number of participants enrolled or analyzed in the intervention/treatment group
- Must be a positive integer
- Look in participant flow diagrams, baseline characteristics tables, or methods section
- Use the analysis population (ITT or per-protocol) as specified in the study
- Use "NR" if not reported or value is missing

Examples:
150
200
75
1000
NR"""
    )

    control_group_events: int = dspy.OutputField(
        desc="""Number of events in the control group.

Description: Number of events in the control group

Rules:
- Extract the numeric count of events (e.g., adverse events, outcomes, occurrences) in the control/placebo group
- Must be a non-negative integer
- Look in results tables, outcome sections, or statistical summaries
- Should correspond to the same event type as intervention_group_events
- Use "NR" if not reported or value is missing

Examples:
30
8
0
56
NR"""
    )

    control_group_total: int = dspy.OutputField(
        desc="""Total number of participants in control group.

Description: Total number of participants in control group

Rules:
- Extract the total number of participants enrolled or analyzed in the control/placebo group
- Must be a positive integer
- Look in participant flow diagrams, baseline characteristics tables, or methods section
- Use the analysis population (ITT or per-protocol) as specified in the study
- Use "NR" if not reported or value is missing

Examples:
150
195
80
1000
NR"""
    )

    relative_risk: float = dspy.OutputField(
        desc="""Relative risk (RR) value if reported.

Description: Relative risk (RR) value if reported

Rules:
- Extract the relative risk value as a decimal number
- Look for "RR", "relative risk", or "risk ratio" in results or statistical analysis sections
- Include up to 2 decimal places (e.g., 1.5, 0.85, 2.34)
- Must be a positive number (typically between 0.01 and 100)
- If confidence interval is provided without point estimate, extract the point estimate only
- Use "NR" if not reported or value is missing

Examples:
1.5
0.85
2.34
1.0
NR"""
    )

    odds_ratio: float = dspy.OutputField(
        desc="""Odds ratio (OR) value if reported.

Description: Odds ratio (OR) value if reported

Rules:
- Extract the odds ratio value as a decimal number
- Look for "OR", "odds ratio" in results or statistical analysis sections
- Include up to 2 decimal places (e.g., 1.8, 0.92, 3.45)
- Must be a positive number (typically between 0.01 and 100)
- If confidence interval is provided without point estimate, extract the point estimate only
- Use "NR" if not reported or value is missing

Examples:
1.8
0.92
3.45
1.0
NR"""
    )




import dspy


class ClassifyEnumFields(dspy.Signature):
    """Classify outcome assessment methodology and blinding status from research documents.

Form Questions:
- Outcome Assessment Method: "How was the outcome assessed?"
  Options: Clinical examination, Patient reported, Laboratory test, Imaging, Other
- Blinding Status: "Whether outcome assessment was blinded"
  Options: Blinded, Unblinded, Not reported

These fields capture critical methodological details about how study outcomes were measured and whether assessors were blinded to treatment allocation, which are key quality indicators in clinical research."""

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
- Look in the methods section for outcome measurement procedures
- If multiple methods used, select the primary method
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
- Look for terms like "masked", "blinded", "single-blind", "double-blind" in methods section
- "Blinded" includes single-blind, double-blind, or any blinding of outcome assessors
- "Unblinded" means explicitly stated as open-label or unblinded
- "Not reported" if blinding status is not mentioned
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

Intention-to-treat (ITT) analysis is a key methodological consideration in clinical trials where all participants are analyzed in the groups to which they were originally randomly assigned, regardless of whether they completed the intervention or received it as planned."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the research document to extract from"""
    )

    intention_to_treat: bool = dspy.OutputField(
        desc="""Whether intention-to-treat analysis was used in the study.

Description: Whether intention-to-treat analysis was used

Rules:
- Return true if the document explicitly states that intention-to-treat (ITT) analysis was performed
- Return true if the document mentions analyzing all randomized participants in their original assigned groups
- Return false if the document explicitly states no ITT analysis or uses per-protocol analysis only
- Return false if only completers or adherent participants were analyzed
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