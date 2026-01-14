import dspy


# ============================================================================
# SIGNATURES - TASK 56E24774
# ============================================================================


import dspy


class ExtractTextualFields(dspy.Signature):
    """Extract key textual clinical information from medical documents including chief complaint, medical history, diagnoses, and treatment plans.

Form Questions:
- Chief Complaint: "What is the primary reason for the medical visit or admission?"
- Symptom Duration: "How long has the patient experienced these symptoms?"
- Medical History: "What are the patient's significant past medical conditions and diagnoses?"
- Current Medications: "What medications is the patient currently taking?"
- Allergies: "What are the patient's known drug or other allergies?"
- Primary Diagnosis: "What is the primary diagnosis or assessment?"
- Secondary Diagnoses: "What are the additional diagnoses or comorbidities?"
- Treatment Plan: "What is the recommended treatment plan and interventions?"

These fields capture essential clinical documentation elements needed for comprehensive patient care and medical record keeping."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the medical document to extract clinical information from"""
    )

    chief_complaint: str = dspy.OutputField(
        desc="""Primary reason for medical visit or admission.

Description: Primary reason for medical visit or admission

Extraction Hints:
- Often at the beginning of clinical notes under 'Chief Complaint' or 'Presenting Problem'

Rules:
- Extract the patient's main presenting complaint verbatim from the document
- Include symptom descriptions and duration if mentioned together
- Preserve medical terminology as written
- Use "NR" if not reported or value is missing

Examples:
Shortness of breath and chest pain for 3 days
Severe headache with visual disturbances
Abdominal pain, nausea, and vomiting since yesterday
NR"""
    )

    symptom_duration: str = dspy.OutputField(
        desc="""How long patient has experienced symptoms.

Description: How long patient has experienced symptoms

Extraction Hints:
- Usually mentioned with chief complaint

Rules:
- Extract the time period the patient has been experiencing symptoms
- Include units (days, weeks, months, years, hours)
- Preserve the exact phrasing from the document
- Use "NR" if not reported or value is missing

Examples:
3 days
2 weeks
Since yesterday morning
6 months
NR"""
    )

    medical_history: str = dspy.OutputField(
        desc="""Significant past medical conditions and diagnoses.

Description: Significant past medical conditions and diagnoses

Extraction Hints:
- Look in 'Past Medical History' or 'PMH' section

Rules:
- Extract all significant past medical conditions listed
- Include dates or temporal information if provided (e.g., s/p CABG 2018)
- Preserve medical abbreviations and terminology as written
- List multiple conditions separated by commas
- Use "NR" if not reported or value is missing

Examples:
Type 2 diabetes mellitus, hypertension, coronary artery disease s/p CABG 2018
Asthma, GERD, osteoarthritis
No significant past medical history
Hyperlipidemia, chronic kidney disease stage 3, prior stroke 2015
NR"""
    )

    current_medications: str = dspy.OutputField(
        desc="""List of medications patient is currently taking.

Description: List of medications patient is currently taking

Extraction Hints:
- Look in 'Medications' or 'Current Medications' section

Rules:
- Extract all current medications with dosages and frequencies if provided
- Include medication name, strength, and dosing schedule
- Preserve medical abbreviations (BID, daily, QID, etc.)
- List multiple medications separated by commas
- Use "NR" if not reported or value is missing

Examples:
Metformin 1000mg BID, Lisinopril 20mg daily, Aspirin 81mg daily, Atorvastatin 40mg daily
Albuterol inhaler PRN, Omeprazole 20mg daily
None
Warfarin 5mg daily, Metoprolol 50mg BID
NR"""
    )

    allergies: str = dspy.OutputField(
        desc="""Known drug or other allergies.

Description: Known drug or other allergies

Extraction Hints:
- Usually prominently noted in allergies section

Rules:
- Extract all documented allergies with reactions if specified
- Include the allergen and type of reaction in parentheses
- List multiple allergies separated by commas
- Include "NKDA" or "No known drug allergies" if explicitly stated
- Use "NR" if not reported or value is missing

Examples:
Penicillin (rash), Sulfa drugs (Stevens-Johnson syndrome)
NKDA
Codeine (nausea), Latex (contact dermatitis)
No known drug allergies
NR"""
    )

    primary_diagnosis: str = dspy.OutputField(
        desc="""Primary diagnosis or assessment.

Description: Primary diagnosis or assessment

Extraction Hints:
- Look in 'Assessment', 'Diagnosis', or 'Impression' section

Rules:
- Extract the main or primary diagnosis from the document
- Include ICD codes if mentioned
- Preserve medical terminology and specificity as written
- Use the most definitive diagnosis stated
- Use "NR" if not reported or value is missing

Examples:
Acute exacerbation of heart failure
Community-acquired pneumonia
Acute appendicitis
Type 2 diabetes mellitus with hyperglycemia
NR"""
    )

    secondary_diagnoses: str = dspy.OutputField(
        desc="""Additional diagnoses or comorbidities.

Description: Additional diagnoses or comorbidities

Extraction Hints:
- Listed after primary diagnosis

Rules:
- Extract all secondary or additional diagnoses mentioned
- List multiple diagnoses separated by commas
- Include comorbid conditions that impact care
- Preserve medical terminology as written
- Use "NR" if not reported or value is missing

Examples:
Hypertensive urgency, Chronic kidney disease stage 3
Anemia, Electrolyte imbalance
None
COPD exacerbation, Acute kidney injury
NR"""
    )

    treatment_plan: str = dspy.OutputField(
        desc="""Recommended treatment plan and interventions.

Description: Recommended treatment plan and interventions

Extraction Hints:
- Look in 'Plan', 'Treatment Plan', or 'Recommendations' section

Rules:
- Extract the complete treatment plan including medications, procedures, and follow-up
- Include specific interventions, consultations, and monitoring plans
- Preserve medical terminology and abbreviations
- List multiple components separated by commas
- Use "NR" if not reported or value is missing

Examples:
Admit for IV diuresis, telemetry monitoring, adjust heart failure medications, cardiology consult
Start antibiotics (Ceftriaxone 1g IV daily), chest X-ray, supportive care
Discharge home with new prescriptions, follow-up in 2 weeks
Emergency appendectomy, NPO, IV fluids, surgical consult
NR"""
    )




import dspy


class ExtractNumericFields(dspy.Signature):
    """Extract numeric clinical measurements and vital signs from medical documents.

Form Questions:
- Female Patient Age Mean: "What is the patient's age in years?"
- Blood Pressure Systolic: "What is the systolic blood pressure reading in mmHg?"
- Blood Pressure Diastolic: "What is the diastolic blood pressure reading in mmHg?"
- Heart Rate: "What is the heart rate in beats per minute?"
- Body Temperature: "What is the body temperature in Celsius?"
- BMI: "What is the Body Mass Index?"
- Lab Hemoglobin: "What is the hemoglobin level in g/dL?"
- Lab Creatinine: "What is the serum creatinine in mg/dL?"
- Lab Glucose: "What is the blood glucose level in mg/dL?"

These numeric fields capture essential vital signs, patient demographics, and laboratory results needed for clinical assessment and medical analysis."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the medical document to extract numeric fields from"""
    )

    female_patient_age_mean: float = dspy.OutputField(
        desc="""Patient's age in years.

Description: Patient's age in years

Extraction Hints:
- Look in patient demographics or header section

Rules:
- Extract numeric age value only
- Can be integer or decimal (e.g., 67.5 for age in years with months)
- Must be a valid number between 0 and 120
- Use "NR" if not reported or value is missing

Examples:
67
45.5
23
NR"""
    )

    blood_pressure_systolic: float = dspy.OutputField(
        desc="""Systolic blood pressure reading in mmHg.

Description: Systolic blood pressure reading in mmHg

Extraction Hints:
- Look in vital signs section

Rules:
- Extract the systolic (first/higher) number from blood pressure reading
- Value should be in mmHg (millimeters of mercury)
- Typical range is 90-180 mmHg
- If BP is written as "142/88", extract 142
- Use "NR" if not reported or value is missing

Examples:
142
120
156.5
NR"""
    )

    blood_pressure_diastolic: float = dspy.OutputField(
        desc="""Diastolic blood pressure reading in mmHg.

Description: Diastolic blood pressure reading in mmHg

Extraction Hints:
- Look in vital signs section

Rules:
- Extract the diastolic (second/lower) number from blood pressure reading
- Value should be in mmHg (millimeters of mercury)
- Typical range is 60-100 mmHg
- If BP is written as "142/88", extract 88
- Use "NR" if not reported or value is missing

Examples:
88
80
72.5
NR"""
    )

    heart_rate: float = dspy.OutputField(
        desc="""Heart rate in beats per minute.

Description: Heart rate in beats per minute

Extraction Hints:
- Look in vital signs section

Rules:
- Extract numeric heart rate value
- Value should be in beats per minute (bpm)
- Typical range is 40-120 bpm for adults
- May be labeled as HR, pulse, or heart rate
- Use "NR" if not reported or value is missing

Examples:
92
72
105.5
NR"""
    )

    body_temperature: float = dspy.OutputField(
        desc="""Body temperature in Celsius.

Description: Body temperature in Celsius

Extraction Hints:
- Look in vital signs section

Rules:
- Extract numeric temperature value in Celsius
- If temperature is in Fahrenheit, convert to Celsius: (F - 32) × 5/9
- Normal range is approximately 36.0-38.0°C
- Include decimal precision as provided
- Use "NR" if not reported or value is missing

Examples:
37.2
36.8
38.5
NR"""
    )

    bmi: float = dspy.OutputField(
        desc="""Body Mass Index.

Description: Body Mass Index

Extraction Hints:
- May be calculated or stated in vital signs

Rules:
- Extract BMI value as provided in the document
- BMI is calculated as weight(kg) / height(m)²
- Typical range is 15-50 for adults
- Include decimal precision (e.g., 28.4)
- Use "NR" if not reported or value is missing

Examples:
28.4
22.1
31.7
NR"""
    )

    lab_hemoglobin: float = dspy.OutputField(
        desc="""Hemoglobin level in g/dL.

Description: Hemoglobin level in g/dL

Extraction Hints:
- Look in laboratory results section

Rules:
- Extract hemoglobin (Hb or Hgb) value from lab results
- Value should be in g/dL (grams per deciliter)
- Normal range is approximately 12-18 g/dL for adults
- Include decimal precision as provided
- Use "NR" if not reported or value is missing

Examples:
13.2
14.8
11.5
NR"""
    )

    lab_creatinine: float = dspy.OutputField(
        desc="""Serum creatinine in mg/dL.

Description: Serum creatinine in mg/dL

Extraction Hints:
- Look in laboratory results section

Rules:
- Extract serum creatinine value from lab results
- Value should be in mg/dL (milligrams per deciliter)
- Normal range is approximately 0.6-1.3 mg/dL for adults
- Include decimal precision as provided
- Use "NR" if not reported or value is missing

Examples:
1.8
0.9
2.3
NR"""
    )

    lab_glucose: float = dspy.OutputField(
        desc="""Blood glucose level in mg/dL.

Description: Blood glucose level in mg/dL

Extraction Hints:
- Look in laboratory results section

Rules:
- Extract blood glucose value from lab results
- Value should be in mg/dL (milligrams per deciliter)
- May be fasting or random glucose
- Normal fasting range is approximately 70-100 mg/dL
- Include decimal precision if provided
- Use "NR" if not reported or value is missing

Examples:
156
92
210.5
NR"""
    )




import dspy


class ClassifyEnumFields(dspy.Signature):
    """Extract patient demographic and social history information including gender, smoking status, and alcohol use from medical documents.

Form Questions:
- Most Patient Gender: "What is the patient's gender?"
  Options: Male, Female, Other, Not specified
- Smoking Status: "What is the patient's smoking history?"
  Options: Never smoker, Former smoker, Current smoker, Unknown
- Alcohol Use: "What is the patient's alcohol consumption pattern?"
  Options: None, Occasional, Moderate, Heavy, Unknown

These fields capture essential demographic and social history information typically found in patient intake forms and medical records."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the medical document to extract patient information from"""
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
- Look for gender information in patient demographics or registration sections
- Use "NR" if not reported or value is missing

Examples:
Female
Male
Other
NR"""
    )

    smoking_status: str = dspy.OutputField(
        desc="""Patient's smoking history.

Description: Patient's smoking history

Options:
- "Never smoker"
- "Former smoker"
- "Current smoker"
- "Unknown"

Extraction Hints:
- Look in social history section

Rules:
- Must be exactly one of the options listed above
- Use exact spelling and capitalization
- Check social history, lifestyle, or habits sections for smoking information
- Use "NR" if not reported or value is missing

Examples:
Former smoker
Never smoker
Current smoker
NR"""
    )

    alcohol_use: str = dspy.OutputField(
        desc="""Patient's alcohol consumption pattern.

Description: Patient's alcohol consumption pattern

Options:
- "None"
- "Occasional"
- "Moderate"
- "Heavy"
- "Unknown"

Extraction Hints:
- Look in social history section

Rules:
- Must be exactly one of the options listed above
- Use exact spelling and capitalization
- Check social history, lifestyle, or habits sections for alcohol consumption information
- Use "NR" if not reported or value is missing

Examples:
Occasional
None
Moderate
NR"""
    )




import dspy


class SynthesizeRiskStratification(dspy.Signature):
    """Synthesize comprehensive cardiovascular and overall health risk assessment by integrating patient demographics, vital signs, diagnoses, medical history, and laboratory values.

Form Questions:
- Risk Stratification: "What is the patient's cardiovascular or overall health risk assessment based on age, vital signs, diagnoses, and laboratory results?"

This signature aggregates multiple previously extracted clinical data points to create a holistic risk assessment that considers the interplay between age, hemodynamic status, cardiac diagnoses, comorbidities, and renal function markers."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the medical document to extract from"""
    )

    female_patient_age_mean: float = dspy.InputField(
        desc="""Previously extracted mean age of female patients from another signature"""
    )

    blood_pressure_systolic: int = dspy.InputField(
        desc="""Previously extracted systolic blood pressure value from another signature"""
    )

    blood_pressure_diastolic: int = dspy.InputField(
        desc="""Previously extracted diastolic blood pressure value from another signature"""
    )

    heart_rate: int = dspy.InputField(
        desc="""Previously extracted heart rate value from another signature"""
    )

    primary_diagnosis: str = dspy.InputField(
        desc="""Previously extracted primary diagnosis from another signature"""
    )

    medical_history: str = dspy.InputField(
        desc="""Previously extracted medical history from another signature"""
    )

    lab_creatinine: float = dspy.InputField(
        desc="""Previously extracted creatinine laboratory value from another signature"""
    )

    risk_stratification: str = dspy.OutputField(
        desc="""Assessment of patient's cardiovascular or overall health risk based on age, vital signs, diagnoses, and labs.

Description: Assessment of patient's cardiovascular or overall health risk based on age, vital signs, diagnoses, and labs

Extraction Hints:
- Synthesize from patient_age, blood_pressure values, heart_rate, primary_diagnosis, medical_history, and relevant lab values
- Integrate hemodynamic parameters (BP, HR) with diagnostic and laboratory findings
- Consider age-related risk factors and comorbidity burden
- Assess renal function impact on overall cardiovascular risk
- Identify acute presentations versus chronic disease states

Rules:
- Create a comprehensive 1-3 sentence risk assessment narrative
- Begin with risk level classification (e.g., "High cardiovascular risk", "Moderate risk", "Low risk")
- Include patient age with relevant context
- Incorporate abnormal vital signs with specific values if elevated/abnormal
- Reference key diagnoses and relevant medical history
- Include pertinent laboratory abnormalities with values
- Synthesize the clinical picture showing how factors interact to determine risk
- Use professional medical terminology
- Use "NR" if insufficient data available to create meaningful risk assessment

Examples:
High cardiovascular risk: 67yo with multiple cardiac risk factors (diabetes, hypertension, CAD history), elevated BP (142/88), elevated creatinine (1.8) suggesting renal impairment, presenting with heart failure exacerbation
Moderate cardiovascular risk: 54yo patient with controlled hypertension (BP 128/82), normal heart rate (72 bpm), history of hyperlipidemia, creatinine within normal limits (1.0), presenting for routine follow-up
Low risk: 42yo with no significant medical history, normal vital signs (BP 118/76, HR 68), normal renal function (creatinine 0.9), presenting with minor musculoskeletal complaint
High risk: 71yo with acute coronary syndrome, tachycardic (HR 110), hypertensive (BP 156/94), elevated creatinine (2.1) indicating acute kidney injury, extensive cardiac history including prior MI and CABG
NR"""
    )




import dspy


class SynthesizeMedicationReview(dspy.Signature):
    """Synthesize a comprehensive medication review assessment based on current medications, diagnoses, and vital signs.

Form Questions:
- Medication Review: "Provide an assessment of current medication appropriateness given the patient's diagnoses and clinical status"

This signature aggregates previously extracted clinical data (medications, diagnoses, vital signs) to generate a comprehensive medication review that evaluates appropriateness, identifies potential adjustments, and provides clinical recommendations."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the medical document"""
    )

    current_medications: str = dspy.InputField(
        desc="""Previously extracted current medications from another signature"""
    )

    primary_diagnosis: str = dspy.InputField(
        desc="""Previously extracted primary diagnosis from another signature"""
    )

    secondary_diagnoses: str = dspy.InputField(
        desc="""Previously extracted secondary diagnoses from another signature"""
    )

    blood_pressure_systolic: int = dspy.InputField(
        desc="""Previously extracted systolic blood pressure from another signature"""
    )

    blood_pressure_diastolic: int = dspy.InputField(
        desc="""Previously extracted diastolic blood pressure from another signature"""
    )

    medication_review: str = dspy.OutputField(
        desc="""Assessment of current medication appropriateness given diagnoses and clinical status.

Description: Assessment of current medication appropriateness given diagnoses and clinical status

Extraction Hints:
- Synthesize from current_medications, primary_diagnosis, secondary_diagnoses, and vital signs
- Consider blood pressure values when evaluating cardiovascular medications
- Assess medication-diagnosis alignment
- Identify potential dose adjustments or additions

Rules:
- Synthesize a comprehensive 2-5 sentence assessment evaluating medication appropriateness
- Reference specific medications and how they relate to the diagnoses
- Include recommendations for dose adjustments, additions, or continuations as appropriate
- Consider vital signs (especially blood pressure) in the assessment
- Use professional clinical language and terminology
- Provide actionable clinical insights when possible
- Use "NR" if cannot create assessment due to insufficient data

Examples:
Current medications appropriate for diabetes and cardiac history. Consider increasing Lisinopril dose given elevated BP. Continue aspirin and statin for secondary prevention. May need diuretic adjustment for heart failure management
Metformin and insulin regimen appropriate for Type 2 Diabetes management. Blood pressure well-controlled on current ACE inhibitor. Continue current medications with regular monitoring of renal function and HbA1c
Anticoagulation with warfarin appropriate for atrial fibrillation. Blood pressure elevated at 158/92 suggests need for antihypertensive optimization. Consider adding calcium channel blocker or increasing current beta-blocker dose
NR"""
    )




import dspy


class SynthesizeLifestyleRecommendations(dspy.Signature):
    """Synthesize personalized lifestyle modification recommendations based on patient's smoking status, alcohol use, BMI, and primary diagnosis.

Form Questions:
- Lifestyle Recommendations: "What lifestyle modifications should be recommended based on the patient's diagnoses and risk factors?"

This signature aggregates previously extracted health indicators to generate comprehensive, evidence-based lifestyle guidance tailored to the patient's specific clinical profile."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the medical document"""
    )

    smoking_status: str = dspy.InputField(
        desc="""Previously extracted smoking status from another signature"""
    )

    alcohol_use: str = dspy.InputField(
        desc="""Previously extracted alcohol use information from another signature"""
    )

    bmi: str = dspy.InputField(
        desc="""Previously extracted BMI (Body Mass Index) from another signature"""
    )

    primary_diagnosis: str = dspy.InputField(
        desc="""Previously extracted primary diagnosis from another signature"""
    )

    lifestyle_recommendations: str = dspy.OutputField(
        desc="""Lifestyle modification recommendations based on diagnoses and risk factors.

Description: Lifestyle modification recommendations based on diagnoses and risk factors

Extraction Hints:
- Synthesize from smoking_status, alcohol_use, bmi, and primary_diagnosis
- Consider interactions between different risk factors and the primary diagnosis
- Include specific, actionable recommendations for each relevant factor
- Address smoking cessation status and maintenance
- Provide alcohol consumption guidance appropriate to the diagnosis
- Include weight management recommendations based on BMI
- Add disease-specific lifestyle modifications (e.g., sodium restriction for heart failure)
- Include exercise recommendations as appropriate for the condition

Rules:
- Synthesize comprehensive lifestyle recommendations integrating all provided health indicators
- Address each relevant risk factor (smoking, alcohol, BMI) in context of the primary diagnosis
- Provide specific, measurable recommendations where possible (e.g., "<2g/day sodium" not just "reduce sodium")
- Use professional medical language appropriate for clinical documentation
- Include positive reinforcement for healthy behaviors (e.g., smoking cessation success)
- Tailor recommendations to the specific diagnosis (e.g., heart failure requires sodium restriction)
- Format as coherent narrative with multiple specific recommendations
- Use "NR" if insufficient information is available to generate meaningful recommendations

Examples:
Continue smoking cessation (former smoker - positive). Recommend limiting alcohol to occasional use given heart failure. Weight management important given BMI 28.4. Sodium restriction <2g/day for heart failure. Regular exercise as tolerated
Patient is current smoker - strongly recommend smoking cessation program given COPD diagnosis. Limit alcohol to moderate use (1 drink/day). BMI 32.1 indicates obesity - recommend weight loss goal of 10% body weight over 6 months. Low-impact aerobic exercise 30 minutes daily as tolerated
Maintain smoking abstinence. Continue moderate alcohol use (within guidelines). BMI 22.3 is healthy - maintain current weight through balanced diet and regular physical activity. No specific restrictions related to diagnosis
NR"""
    )




import dspy


class AggregateClinicalSummary(dspy.Signature):
    """Create a comprehensive clinical summary by synthesizing all key findings, assessments, and recommendations from previously extracted clinical data.

Form Questions:
- Clinical Summary: "Provide a comprehensive clinical summary synthesizing all key findings, assessments, and recommendations"

This signature aggregates multiple clinical data points including patient presentation, medical history, vital signs, laboratory results, diagnoses, risk assessment, medications, and treatment plans into a cohesive narrative summary suitable for clinical documentation and handoff communication."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the clinical document"""
    )

    chief_complaint: str = dspy.InputField(
        desc="""Previously extracted chief complaint from another signature"""
    )

    medical_history: str = dspy.InputField(
        desc="""Previously extracted medical history from another signature"""
    )

    blood_pressure_systolic: int = dspy.InputField(
        desc="""Previously extracted systolic blood pressure from another signature"""
    )

    blood_pressure_diastolic: int = dspy.InputField(
        desc="""Previously extracted diastolic blood pressure from another signature"""
    )

    heart_rate: int = dspy.InputField(
        desc="""Previously extracted heart rate from another signature"""
    )

    lab_creatinine: float = dspy.InputField(
        desc="""Previously extracted creatinine lab value from another signature"""
    )

    lab_glucose: float = dspy.InputField(
        desc="""Previously extracted glucose lab value from another signature"""
    )

    primary_diagnosis: str = dspy.InputField(
        desc="""Previously extracted primary diagnosis from another signature"""
    )

    secondary_diagnoses: str = dspy.InputField(
        desc="""Previously extracted secondary diagnoses from another signature"""
    )

    risk_stratification: str = dspy.InputField(
        desc="""Previously extracted risk stratification from another signature"""
    )

    medication_review: str = dspy.InputField(
        desc="""Previously extracted medication review from another signature"""
    )

    treatment_plan: str = dspy.InputField(
        desc="""Previously extracted treatment plan from another signature"""
    )

    clinical_summary: str = dspy.OutputField(
        desc="""Comprehensive clinical summary synthesizing all key findings, assessments, and recommendations.

Description: Comprehensive clinical summary synthesizing all key findings, assessments, and recommendations

Extraction Hints:
- Synthesize comprehensive summary from chief_complaint, medical_history, vital signs, diagnoses, risk_stratification, medication_review, and treatment_plan

Rules:
- Create a cohesive narrative that integrates all provided clinical data points
- Begin with patient demographics and presenting complaint
- Include relevant past medical history
- Incorporate vital signs and laboratory findings with specific values
- State primary and secondary diagnoses clearly
- Include risk assessment findings
- Summarize medication review and any adjustments
- Conclude with treatment plan and key recommendations
- Use professional medical writing style with appropriate abbreviations
- Aim for 4-8 sentences that capture the complete clinical picture
- Ensure all critical information from dependent fields is represented
- Use "NR" if cannot create summary due to insufficient data

Examples:
67yo female with PMH of T2DM, HTN, and CAD s/p CABG presents with 3-day history of SOB and chest pain. Exam notable for elevated BP 142/88, HR 92. Labs show elevated creatinine 1.8 and glucose 156. Diagnosed with acute heart failure exacerbation and hypertensive urgency. Risk assessment indicates high cardiovascular risk. Current medications reviewed and adjustments recommended. Plan: admit for IV diuresis, telemetry, and cardiology consultation. Emphasized lifestyle modifications including sodium restriction and weight management
52yo male with history of COPD and smoking presents with acute dyspnea and productive cough. Vital signs show BP 138/82, HR 98, SpO2 88% on room air. Labs reveal WBC 14.2 and procalcitonin 0.8. Primary diagnosis of acute COPD exacerbation with bacterial pneumonia. Moderate-to-high risk for respiratory failure. Currently on albuterol and ipratropium; adding azithromycin and prednisone taper. Plan includes admission for oxygen therapy, nebulizer treatments, and pulmonary consultation with smoking cessation counseling
45yo male with no significant PMH presents for routine physical. Vital signs WNL: BP 118/76, HR 72. Labs show creatinine 0.9, glucose 92. No acute diagnoses identified. Low cardiovascular risk. No current medications. Plan: continue annual preventive care, maintain healthy lifestyle, and follow up in one year
NR"""
    )






__all__ = [
    "ExtractTextualFields",
    "ExtractNumericFields",
    "ClassifyEnumFields",
    "SynthesizeRiskStratification",
    "SynthesizeMedicationReview",
    "SynthesizeLifestyleRecommendations",
    "AggregateClinicalSummary",
]