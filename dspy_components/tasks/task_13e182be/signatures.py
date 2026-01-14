import dspy


# ============================================================================
# SIGNATURES - TASK 13E182BE
# ============================================================================


import dspy


class ExtractTextualFields(dspy.Signature):
    """Extract textual fields related to primary and secondary dichotomous outcomes from clinical research papers.

Form Questions:
- Primary Outcome Name: "What is the name of the primary dichotomous outcome measure?"
- Primary Outcome Definition: "How is the primary outcome defined in the study?"
- Confidence Interval: "What is the 95% confidence interval for the effect measure?"
- P-Value: "What is the p-value for statistical significance?"
- Time Point: "At what time point was the outcome measured?"
- Secondary Outcomes: "What secondary dichotomous outcomes were measured?"

These fields capture essential outcome measures and statistical results from clinical trials and observational studies, enabling systematic review and meta-analysis of treatment effects."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the clinical research paper"""
    )

    primary_outcome_name: str = dspy.OutputField(
        desc="""Name of the primary dichotomous outcome measure.

Description: Name of the primary dichotomous outcome measure

Rules:
- Extract the exact name or label of the primary outcome as stated in the study
- Focus on dichotomous (binary) outcomes (e.g., success/failure, present/absent)
- Look in methods, outcomes, or results sections
- Use the terminology exactly as written in the document
- Use "NR" if not reported or cannot be determined

Examples:
Treatment success
Disease recurrence
Mortality
30-day readmission
NR"""
    )

    primary_outcome_definition: str = dspy.OutputField(
        desc="""How the primary outcome is defined in the study.

Description: How the primary outcome is defined in the study

Rules:
- Extract the complete definition or criteria used to determine the outcome
- Include specific thresholds, timeframes, or measurement criteria
- Capture the operational definition verbatim when possible
- May span multiple sentences if needed for completeness
- Use "NR" if not reported or definition is not provided

Examples:
Complete resolution of symptoms at 6 months
Absence of tumor recurrence on imaging at 2-year follow-up
All-cause mortality within 30 days of hospital discharge
HbA1c level below 7% at 12 months without hypoglycemic episodes
NR"""
    )

    confidence_interval: str = dspy.OutputField(
        desc="""95% confidence interval for the effect measure.

Description: 95% confidence interval for the effect measure

Rules:
- Extract the 95% CI values for the primary outcome effect measure
- Include both lower and upper bounds
- Preserve the format as written (e.g., "1.2-2.4" or "1.2 to 2.4" or "[1.2, 2.4]")
- If multiple CIs reported, extract the one for the primary outcome
- Use "NR" if not reported or cannot be found

Examples:
1.2-2.4
0.85 to 1.45
[0.92, 1.38]
1.15-2.87
NR"""
    )

    p_value: str = dspy.OutputField(
        desc="""P-value for statistical significance.

Description: P-value for statistical significance

Rules:
- Extract the p-value associated with the primary outcome comparison
- Preserve exact format as written (e.g., "0.03", "<0.001", "p=0.045")
- If multiple p-values reported, extract the one for the primary outcome
- Include comparison operators if present (<, >, =)
- Use "NR" if not reported or cannot be determined

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
- Include units (days, weeks, months, years)
- If multiple time points, extract the primary or final assessment time
- Use exact terminology from the document
- Use "NR" if not reported or timeframe is unclear

Examples:
6 months
1 year
End of study
30 days
12 weeks post-intervention
NR"""
    )

    secondary_outcomes: str = dspy.OutputField(
        desc="""List of secondary dichotomous outcomes measured.

Description: List of secondary dichotomous outcomes measured

Rules:
- Extract all secondary dichotomous (binary) outcomes mentioned in the study
- Format as comma-separated list or JSON array string
- Include only dichotomous outcomes, not continuous measures
- Preserve outcome names as written in the document
- Use "NR" if no secondary outcomes reported or not specified

Examples:
Adverse events, Treatment adherence, Patient satisfaction
Hospital readmission, Emergency department visits, Medication compliance
Disease progression, Treatment discontinuation
Infection, Bleeding complications, Reoperation
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
- Extract the numeric count of events (e.g., adverse events, outcomes, incidents) in the intervention/treatment group
- Must be a non-negative integer
- Look in results tables, outcome sections, or statistical summaries
- If multiple event types are reported, extract the primary outcome events
- Use "NR" if not reported or value is missing

Examples:
45
120
8
0
NR"""
    )

    intervention_group_total: int = dspy.OutputField(
        desc="""Total number of participants in intervention group.

Description: Total number of participants in intervention group

Rules:
- Extract the total number of participants assigned to or analyzed in the intervention/treatment group
- Must be a positive integer
- Look in participant flow diagrams, baseline characteristics tables, or methods section
- Use the analysis population (ITT or per-protocol) as specified in the study
- Use "NR" if not reported or value is missing

Examples:
150
500
75
1000
NR"""
    )

    control_group_events: int = dspy.OutputField(
        desc="""Number of events in the control group.

Description: Number of events in the control group

Rules:
- Extract the numeric count of events (e.g., adverse events, outcomes, incidents) in the control/comparison group
- Must be a non-negative integer
- Look in results tables, outcome sections, or statistical summaries
- Should correspond to the same event type as intervention_group_events
- Use "NR" if not reported or value is missing

Examples:
30
95
12
0
NR"""
    )

    control_group_total: int = dspy.OutputField(
        desc="""Total number of participants in control group.

Description: Total number of participants in control group

Rules:
- Extract the total number of participants assigned to or analyzed in the control/comparison group
- Must be a positive integer
- Look in participant flow diagrams, baseline characteristics tables, or methods section
- Use the analysis population (ITT or per-protocol) as specified in the study
- Use "NR" if not reported or value is missing

Examples:
150
500
75
1000
NR"""
    )

    relative_risk: float = dspy.OutputField(
        desc="""Relative risk (RR) value if reported.

Description: Relative risk (RR) value if reported

Rules:
- Extract the relative risk (RR or risk ratio) value from statistical results
- Must be a positive number (typically between 0.01 and 100)
- Look in results section, abstract, or statistical analysis tables
- Extract point estimate only (not confidence intervals)
- May be reported as "RR", "Risk Ratio", or "Relative Risk"
- Use "NR" if not reported or value is missing

Examples:
1.5
0.75
2.3
0.95
NR"""
    )

    odds_ratio: float = dspy.OutputField(
        desc="""Odds ratio (OR) value if reported.

Description: Odds ratio (OR) value if reported

Rules:
- Extract the odds ratio (OR) value from statistical results
- Must be a positive number (typically between 0.01 and 100)
- Look in results section, abstract, or statistical analysis tables
- Extract point estimate only (not confidence intervals)
- May be reported as "OR" or "Odds Ratio"
- Use "NR" if not reported or value is missing

Examples:
1.8
0.65
3.2
1.0
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

These fields capture critical methodological details about how study outcomes were measured and whether assessors were blinded to treatment allocation, which are key factors in assessing study quality and risk of bias."""

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
- Look in the methods section, outcome measures, or assessment procedures
- If multiple methods used, select the primary method for the main outcome
- Choose "Other" if the method doesn't fit the standard categories
- Use "NR" if not reported or cannot be determined

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
- Look for terms like "blinded", "masked", "single-blind", "double-blind", "open-label", "unblinded"
- "Blinded" means outcome assessors were unaware of treatment allocation
- "Unblinded" means outcome assessors knew treatment allocation or study was open-label
- Use "Not reported" if blinding status is not explicitly stated
- Use "NR" if the information cannot be determined from the document

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

Intention-to-treat (ITT) analysis is a key methodological approach in clinical trials where all participants are analyzed in the groups to which they were originally randomly assigned, regardless of whether they completed the intervention or received the intended treatment."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the research document to extract from"""
    )

    intention_to_treat: bool = dspy.OutputField(
        desc="""Whether intention-to-treat analysis was used in the study.

Description: Whether intention-to-treat analysis was used

Rules:
- Return true if the document explicitly states that intention-to-treat (ITT) analysis was used
- Return true if the document mentions analyzing all randomized participants in their originally assigned groups
- Return false if the document explicitly states ITT was not used or only per-protocol analysis was performed
- Return false if only completers or compliant participants were analyzed
- Look for phrases like "intention-to-treat", "ITT analysis", "all randomized participants were analyzed", or "analyzed as randomized"
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