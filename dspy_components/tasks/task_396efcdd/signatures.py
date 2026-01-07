import dspy


# ============================================================================
# SIGNATURES - TASK 396EFCDD
# ============================================================================


import dspy


class ExtractTextualFields(dspy.Signature):
    """Extract intervention details, outcomes, and study parameters from clinical research documents.

Form Questions:
- Intervention Name: "What is the name of the primary intervention being tested?"
- Intervention Dosage: "What is the dosage or frequency of the intervention?"
- Primary Outcome: "What is the primary outcome measure of the study?"
- Primary Outcome Result: "What is the result of the primary outcome measurement?"
- Effect Size: "What is the effect size measure (e.g., Cohen's d, odds ratio, relative risk)?"
- Follow Up Duration: "What is the duration of the follow-up period?"

These fields capture essential information about clinical interventions, their administration protocols, outcome measurements, and study timelines needed for systematic reviews and meta-analyses."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the clinical research document to extract intervention and outcome data from"""
    )

    intervention_name: str = dspy.OutputField(
        desc="""Name of the primary intervention being tested.

Description: Name of the primary intervention being tested

Rules:
- Extract the complete name of the intervention as stated in the document
- Include descriptive details if they are part of the intervention name
- Look in methods, intervention, or treatment sections
- Use "NR" if not reported or value is missing

Examples:
Placebo-controlled oral rinse
Cognitive Behavioral Therapy
High-intensity interval training program
Monoclonal antibody therapy
NR"""
    )

    intervention_dosage: str = dspy.OutputField(
        desc="""Dosage or frequency of the intervention.

Description: Dosage or frequency of the intervention

Rules:
- Extract complete dosage information including amount and frequency
- Include duration if specified as part of the dosage regimen
- Preserve units of measurement (mg, ml, times per day, etc.)
- Use "NR" if not reported or value is missing

Examples:
Twice daily for 4 weeks
500mg three times daily
Once weekly for 12 weeks
30 minutes per session, 3 sessions per week
NR"""
    )

    primary_outcome: str = dspy.OutputField(
        desc="""Primary outcome measure of the study.

Description: Primary outcome measure of the study

Rules:
- Extract the primary outcome measure as defined by the study authors
- Include the measurement tool or scale if specified
- Include timing of measurement if stated (e.g., "at 4 weeks")
- Look in outcomes, endpoints, or methods sections
- Use "NR" if not reported or value is missing

Examples:
Reduction in plaque index at 4 weeks
Change in Beck Depression Inventory score from baseline to 8 weeks
All-cause mortality at 1 year
Pain score on Visual Analog Scale at 24 hours
NR"""
    )

    primary_outcome_result: str = dspy.OutputField(
        desc="""Result of the primary outcome measurement.

Description: Result of the primary outcome measurement

Rules:
- Extract the complete result including numerical values and statistical measures
- Include comparison between intervention and control groups if provided
- Preserve statistical notation (mean, SD, CI, p-values) as written
- Include units of measurement
- Use "NR" if not reported or value is missing

Examples:
Mean reduction of 0.45 (SD 0.12) in intervention group vs 0.23 (SD 0.15) in control
15% reduction in intervention group compared to 5% in placebo (p<0.001)
Hazard ratio 0.75 (95% CI 0.62-0.91)
Mean difference -2.3 points (95% CI -3.1 to -1.5)
NR"""
    )

    effect_size: str = dspy.OutputField(
        desc="""Effect size measure (e.g., Cohen's d, odds ratio, relative risk).

Description: Effect size measure (e.g., Cohen's d, odds ratio, relative risk)

Rules:
- Extract the specific effect size statistic reported
- Include the type of effect size measure (Cohen's d, OR, RR, etc.)
- Include confidence intervals if provided
- Preserve exact numerical values
- Use "NR" if not reported or value is missing

Examples:
Cohen's d = 0.65
Odds ratio 1.85 (95% CI 1.23-2.78)
Relative risk 0.82
Standardized mean difference = 0.42
NR"""
    )

    follow_up_duration: str = dspy.OutputField(
        desc="""Duration of follow-up period.

Description: Duration of follow-up period

Rules:
- Extract the complete follow-up duration as stated
- Include units (days, weeks, months, years)
- If multiple follow-up points, extract the longest duration
- Look in methods or study design sections
- Use "NR" if not reported or value is missing

Examples:
6 months
12 weeks
2 years
90 days
NR"""
    )




import dspy


class ExtractNumericFields(dspy.Signature):
    """Extract numeric data fields including participant counts, statistical values, and adverse event metrics from research documents.

Form Questions:
- Total Participants: "What is the total number of participants enrolled in the study?"
- P Value: "What is the p-value for the primary outcome?"
- Adverse Events Count: "How many adverse events were reported?"

These numeric fields are essential for quantitative analysis of clinical trial results and study outcomes."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the research document to extract numeric data from"""
    )

    total_participants: int = dspy.OutputField(
        desc="""Total number of participants enrolled in the study.

Description: Total number of participants enrolled in the study

Rules:
- Extract the total enrollment count from the study
- Look in methods section, participant demographics, or enrollment sections
- Must be a positive integer
- Include all participants across all study arms/groups
- Use "NR" if not reported or cannot be determined

Examples:
150
1250
89
NR"""
    )

    p_value: float = dspy.OutputField(
        desc="""P-value for the primary outcome.

Description: P-value for the primary outcome

Rules:
- Extract the p-value associated with the primary outcome measure
- Look in results section or statistical analysis tables
- Must be a decimal number between 0 and 1
- Use exact value as reported (e.g., 0.03, 0.001, 0.45)
- If reported as "p < 0.05", extract as 0.05
- If reported as "p < 0.001", extract as 0.001
- Use "NR" if not reported or cannot be determined

Examples:
0.03
0.001
0.45
NR"""
    )

    adverse_events_count: int = dspy.OutputField(
        desc="""Number of adverse events reported.

Description: Number of adverse events reported

Rules:
- Extract the total count of adverse events across all participants
- Look in safety section, adverse events tables, or results section
- Must be a non-negative integer (0 or greater)
- Include all severity levels unless specified otherwise
- If multiple types are listed, sum to get total count
- Use "NR" if not reported or cannot be determined

Examples:
5
0
127
NR"""
    )




import dspy


class ClassifyEnumFields(dspy.Signature):
    """Classify clinical study characteristics including study design type, control group type, and statistical significance from research papers.

Form Questions:
- Study Type: "What type of clinical study design was used?"
  Options: Randomized Controlled Trial, Cohort Study, Case-Control Study, Cross-Sectional Study, Systematic Review, Meta-Analysis, Other
- Control Group Type: "What type of control group was used in the study?"
  Options: Placebo, Active Control, No Treatment, Standard Care, Historical Control, Not Applicable
- Statistical Significance: "Did the primary outcome show statistical significance?"
  Options: Statistically Significant, Not Statistically Significant, Not Reported, Not Applicable

These classifications are essential for assessing study quality, methodology, and the reliability of research findings in clinical research."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the medical research paper"""
    )

    study_type: str = dspy.OutputField(
        desc="""Type of clinical study design.

Description: Type of clinical study design

Options:
- "Randomized Controlled Trial"
- "Cohort Study"
- "Case-Control Study"
- "Cross-Sectional Study"
- "Systematic Review"
- "Meta-Analysis"
- "Other"

Rules:
- Must be exactly one of the options listed above
- Use exact spelling and capitalization
- Look in the methods or study design section to identify the study type
- RCTs involve random assignment to intervention groups
- Cohort studies follow groups over time
- Case-control studies compare cases with controls retrospectively
- Cross-sectional studies assess at a single time point
- Systematic reviews synthesize existing literature
- Meta-analyses statistically combine results from multiple studies
- Use "NR" if study type cannot be determined

Examples:
Randomized Controlled Trial
Cohort Study
Meta-Analysis
Other
NR"""
    )

    control_group_type: str = dspy.OutputField(
        desc="""Type of control group used in the study.

Description: Type of control group used in the study

Options:
- "Placebo"
- "Active Control"
- "No Treatment"
- "Standard Care"
- "Historical Control"
- "Not Applicable"

Rules:
- Must be exactly one of the options listed above
- Use exact spelling and capitalization
- Look in the methods section for control group description
- Placebo: inactive treatment that appears identical to intervention
- Active Control: comparison with another active treatment
- No Treatment: participants receive no intervention
- Standard Care: usual or routine care as comparison
- Historical Control: comparison with past data rather than concurrent controls
- Not Applicable: for studies without control groups (e.g., case series, some observational studies)
- Use "NR" if control group type is not reported or unclear

Examples:
Placebo
Active Control
Standard Care
Not Applicable
NR"""
    )

    statistical_significance: str = dspy.OutputField(
        desc="""Whether the primary outcome showed statistical significance.

Description: Whether the primary outcome showed statistical significance

Options:
- "Statistically Significant"
- "Not Statistically Significant"
- "Not Reported"
- "Not Applicable"

Rules:
- Must be exactly one of the options listed above
- Use exact spelling and capitalization
- Look in the results section for p-values or confidence intervals for the primary outcome
- Statistically Significant: typically p < 0.05 or confidence interval excludes null value
- Not Statistically Significant: p ≥ 0.05 or confidence interval includes null value
- Not Reported: study does not clearly report statistical significance for primary outcome
- Not Applicable: for studies where statistical significance testing is not relevant (e.g., qualitative studies, descriptive studies)
- Use "NR" if information cannot be determined from the document

Examples:
Statistically Significant
Not Statistically Significant
Not Reported
Not Applicable
NR"""
    )




import dspy


class DetermineBooleanFields(dspy.Signature):
    """Determine whether adverse events were reported in the study from the research document.

Form Questions:
- Adverse Events Reported: "Were adverse events reported in the study?"

This field captures whether the study documented any adverse events, side effects, or safety concerns during the research."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the research document to extract from"""
    )

    adverse_events_reported: bool = dspy.OutputField(
        desc="""Whether adverse events were reported in the study.

Description: Whether adverse events were reported in the study

Rules:
- Return true if the document mentions any adverse events, side effects, safety concerns, or complications
- Return true if there is an adverse events section, even if no events occurred
- Return false if the document explicitly states no adverse events occurred
- Return false if adverse events are not discussed or mentioned
- Look for keywords like "adverse events", "side effects", "safety", "complications", "toxicity"
- Use "NR" if it cannot be determined whether adverse events were reported

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