import dspy


# ============================================================================
# SIGNATURES - TASK 2FED7CEE
# ============================================================================


import dspy


class ExtractTextualFields(dspy.Signature):
    """Extract key clinical information from medical documents including patient presentation, history, diagnoses, and treatment plans.

Form Questions:
- Chief Complaint: "What is the primary reason for the medical visit or admission?"
- Symptom Duration: "How long has the patient experienced these symptoms?"
- Medical History: "What are the patient's significant past medical conditions and diagnoses?"
- Current Medications: "What medications is the patient currently taking?"
- Allergies: "What are the patient's known drug or other allergies?"
- Primary Diagnosis: "What is the primary diagnosis or assessment?"
- Secondary Diagnoses: "What are the additional diagnoses or comorbidities?"
- Treatment Plan: "What is the recommended treatment plan and interventions?"

These fields capture comprehensive clinical information essential for patient care documentation, medical decision-making, and continuity of care across healthcare settings."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the medical document to extract clinical information from"""
    )

    chief_complaint: str = dspy.OutputField(
        desc="""Primary reason for medical visit or admission.

Description: Primary reason for medical visit or admission

Extraction Hints:
- Often at the beginning of clinical notes under 'Chief Complaint' or 'Presenting Problem'

Rules:
- Extract the patient's main complaint or reason for seeking medical care
- Include duration if mentioned with the complaint
- Use the exact wording from the document when possible
- Keep it concise but complete (typically 1-2 sentences)
- Use "NR" if not reported or value is missing

Examples:
Shortness of breath and chest pain for 3 days
Severe headache with nausea and vomiting
Abdominal pain, right lower quadrant, onset 6 hours ago
Fever and cough for 1 week
NR"""
    )

    symptom_duration: str = dspy.OutputField(
        desc="""How long patient has experienced symptoms.

Description: How long patient has experienced symptoms

Extraction Hints:
- Usually mentioned with chief complaint

Rules:
- Extract the time period the patient has been experiencing symptoms
- Include units (hours, days, weeks, months, years)
- If multiple symptoms with different durations, note the primary symptom duration
- Use the format as stated in the document
- Use "NR" if not reported or value is missing

Examples:
3 days
2 weeks
6 hours
Several months
1 year
NR"""
    )

    medical_history: str = dspy.OutputField(
        desc="""Significant past medical conditions and diagnoses.

Description: Significant past medical conditions and diagnoses

Extraction Hints:
- Look in 'Past Medical History' or 'PMH' section

Rules:
- Extract all significant past medical conditions listed in the document
- Include surgical history if mentioned (use s/p for status post)
- Maintain medical terminology and abbreviations as written
- List conditions separated by commas or semicolons
- Include dates or years when provided
- Use "NR" if not reported or value is missing

Examples:
Type 2 diabetes mellitus, hypertension, coronary artery disease s/p CABG 2018
Asthma, GERD, osteoarthritis
No significant past medical history
Hypothyroidism, depression, prior DVT 2015
NR"""
    )

    current_medications: str = dspy.OutputField(
        desc="""List of medications patient is currently taking.

Description: List of medications patient is currently taking

Extraction Hints:
- Look in 'Medications' or 'Current Medications' section

Rules:
- Extract all current medications with dosages and frequencies when provided
- Include medication name, strength, and dosing schedule
- Use standard medical abbreviations (BID, daily, QID, etc.)
- Separate multiple medications with commas
- If patient takes no medications, note "None"
- Use "NR" if not reported or value is missing

Examples:
Metformin 1000mg BID, Lisinopril 20mg daily, Aspirin 81mg daily, Atorvastatin 40mg daily
Levothyroxine 100mcg daily, Omeprazole 20mg daily
None
Albuterol inhaler PRN, Fluticasone 110mcg 2 puffs BID
NR"""
    )

    allergies: str = dspy.OutputField(
        desc="""Known drug or other allergies.

Description: Known drug or other allergies

Extraction Hints:
- Usually prominently noted in allergies section

Rules:
- Extract all documented allergies with reactions when specified
- Include the allergen and type of reaction in parentheses
- If no known allergies, note "NKDA" or "No known drug allergies"
- Separate multiple allergies with commas or semicolons
- Include food or environmental allergies if documented
- Use "NR" if not reported or value is missing

Examples:
Penicillin (rash), Sulfa drugs (Stevens-Johnson syndrome)
NKDA
Codeine (nausea), Latex (contact dermatitis)
No known drug allergies
Shellfish (anaphylaxis)
NR"""
    )

    primary_diagnosis: str = dspy.OutputField(
        desc="""Primary diagnosis or assessment.

Description: Primary diagnosis or assessment

Extraction Hints:
- Look in 'Assessment', 'Diagnosis', or 'Impression' section

Rules:
- Extract the main or primary diagnosis from the assessment
- Use medical terminology as written in the document
- Include ICD codes if mentioned
- This should be the most significant or acute condition
- Use "NR" if not reported or value is missing

Examples:
Acute exacerbation of heart failure
Community-acquired pneumonia
Acute appendicitis
Type 2 diabetes mellitus, uncontrolled
Acute myocardial infarction, STEMI
NR"""
    )

    secondary_diagnoses: str = dspy.OutputField(
        desc="""Additional diagnoses or comorbidities.

Description: Additional diagnoses or comorbidities

Extraction Hints:
- Listed after primary diagnosis

Rules:
- Extract all secondary or additional diagnoses mentioned
- Separate multiple diagnoses with commas or semicolons
- Include chronic conditions and comorbidities
- Maintain medical terminology as written
- If no secondary diagnoses, note "None"
- Use "NR" if not reported or value is missing

Examples:
Hypertensive urgency, Chronic kidney disease stage 3
Anemia, Hypothyroidism
None
COPD, Atrial fibrillation, Obesity
Dehydration, Electrolyte imbalance
NR"""
    )

    treatment_plan: str = dspy.OutputField(
        desc="""Recommended treatment plan and interventions.

Description: Recommended treatment plan and interventions

Extraction Hints:
- Look in 'Plan', 'Treatment Plan', or 'Recommendations' section

Rules:
- Extract the complete treatment plan including medications, procedures, and follow-up
- Include admission status if mentioned (admit, discharge, observation)
- List consultations, monitoring requirements, and diagnostic tests
- Separate different components with commas
- Maintain medical terminology and abbreviations
- Use "NR" if not reported or value is missing

Examples:
Admit for IV diuresis, telemetry monitoring, adjust heart failure medications, cardiology consult
Start antibiotics (Ceftriaxone and Azithromycin), supportive care, chest X-ray, discharge when stable
Appendectomy, NPO, IV fluids, post-op pain management
Increase insulin dose, diabetes education, follow-up in 2 weeks
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

These numeric fields capture essential vital signs, patient demographics, and laboratory values needed for clinical assessment and medical analysis."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the medical document to extract numeric clinical data from"""
    )

    female_patient_age_mean: float = dspy.OutputField(
        desc="""Patient's age in years.

Description: Patient's age in years

Extraction Hints:
- Look in patient demographics or header section

Rules:
- Extract numeric age value only
- Can be integer or decimal (e.g., 67.5 for age in years)
- Must be a valid number between 0 and 120
- Use "NR" if not reported or value is missing

Examples:
67
45.5
72
NR"""
    )

    blood_pressure_systolic: float = dspy.OutputField(
        desc="""Systolic blood pressure reading in mmHg.

Description: Systolic blood pressure reading in mmHg

Extraction Hints:
- Look in vital signs section

Rules:
- Extract the systolic (top number) from blood pressure reading
- Value should be in mmHg units
- Typically ranges from 90 to 200 mmHg
- If BP is written as "142/88", extract 142
- Use "NR" if not reported or value is missing

Examples:
142
120
156
NR"""
    )

    blood_pressure_diastolic: float = dspy.OutputField(
        desc="""Diastolic blood pressure reading in mmHg.

Description: Diastolic blood pressure reading in mmHg

Extraction Hints:
- Look in vital signs section

Rules:
- Extract the diastolic (bottom number) from blood pressure reading
- Value should be in mmHg units
- Typically ranges from 60 to 120 mmHg
- If BP is written as "142/88", extract 88
- Use "NR" if not reported or value is missing

Examples:
88
80
92
NR"""
    )

    heart_rate: float = dspy.OutputField(
        desc="""Heart rate in beats per minute.

Description: Heart rate in beats per minute

Extraction Hints:
- Look in vital signs section

Rules:
- Extract numeric heart rate value only
- Value should be in beats per minute (bpm)
- Typically ranges from 40 to 180 bpm for adults
- May be labeled as HR, pulse, or heart rate
- Use "NR" if not reported or value is missing

Examples:
92
72
105
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
- Normal range is approximately 36.0 to 38.0°C
- Include decimal places if provided
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
- Extract BMI value as numeric decimal
- BMI is calculated as weight(kg) / height(m)²
- Typical range is 15 to 50
- Include decimal places (e.g., 28.4)
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
- Extract hemoglobin (Hgb or Hb) value in g/dL
- Normal range is approximately 12-18 g/dL for adults
- Include decimal places if provided
- May be listed in CBC (Complete Blood Count) results
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
- Extract serum creatinine value in mg/dL
- Normal range is approximately 0.6-1.3 mg/dL
- Include decimal places (typically 1-2 decimal places)
- May be listed in metabolic panel or renal function tests
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
- Extract blood glucose value in mg/dL
- Normal fasting range is approximately 70-100 mg/dL
- May be labeled as glucose, blood sugar, or blood glucose
- Include decimal places if provided, otherwise whole number
- Use "NR" if not reported or value is missing

Examples:
156
98
210
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
- Check social history, habits, or lifestyle sections for smoking information
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
- Check social history, habits, or lifestyle sections for alcohol consumption information
- Use "NR" if not reported or value is missing

Examples:
Occasional
None
Moderate
NR"""
    )




import dspy


class SynthesizeRiskStratification(dspy.Signature):
    """Synthesize comprehensive cardiovascular and overall health risk assessment based on patient demographics, vital signs, diagnoses, and laboratory values.

Form Questions:
- Risk Stratification: "What is the patient's cardiovascular or overall health risk assessment based on age, vital signs, diagnoses, and laboratory findings?"

This signature aggregates multiple clinical data points (age, blood pressure, heart rate, diagnoses, medical history, and lab values) to create a holistic risk assessment that informs clinical decision-making and treatment planning."""

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

Rules:
- Integrate all available clinical data points (age, BP systolic/diastolic, heart rate, diagnoses, history, creatinine) into a comprehensive risk assessment
- Begin with risk level classification (e.g., "High cardiovascular risk", "Moderate risk", "Low risk")
- Include patient age with relevant context
- Mention key risk factors from medical history and diagnoses
- Include abnormal vital signs with specific values (e.g., "elevated BP (142/88)")
- Include abnormal lab values with clinical interpretation (e.g., "elevated creatinine (1.8) suggesting renal impairment")
- Note presenting condition or acute issues if applicable
- Use professional medical terminology and clinical reasoning
- Create a narrative that connects all data points logically
- Use "NR" if insufficient data is available to create a meaningful risk assessment

Examples:
High cardiovascular risk: 67yo with multiple cardiac risk factors (diabetes, hypertension, CAD history), elevated BP (142/88), elevated creatinine (1.8) suggesting renal impairment, presenting with heart failure exacerbation
Moderate cardiovascular risk: 54yo female with controlled hypertension and borderline elevated BP (138/86), normal heart rate (72 bpm), no significant renal dysfunction (creatinine 1.1), stable chronic conditions
Low risk: 32yo with normal vital signs (BP 118/76, HR 68), no significant medical history, normal renal function (creatinine 0.9), presenting for routine evaluation
NR"""
    )




import dspy


class SynthesizeMedicationReview(dspy.Signature):
    """Synthesize a comprehensive medication review assessment based on current medications, diagnoses, and vital signs.

Form Questions:
- Medication Review: "Provide an assessment of current medication appropriateness given the patient's diagnoses and clinical status"

This signature aggregates previously extracted clinical data (medications, diagnoses, vital signs) to generate a holistic medication review that evaluates appropriateness, identifies potential adjustments, and considers the patient's overall clinical picture."""

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
- Evaluate whether medications align with diagnoses
- Consider vital signs (especially blood pressure) when assessing medication appropriateness
- Identify potential dose adjustments or medication changes
- Comment on preventive medications if relevant

Rules:
- Create a comprehensive 2-5 sentence assessment that integrates all provided clinical data
- Evaluate medication appropriateness for the given diagnoses
- Comment on whether vital signs suggest medication adjustments are needed
- Mention specific medications by name when making recommendations
- Include considerations for disease management and prevention
- Use professional clinical language
- Use "NR" if cannot create review due to insufficient data

Examples:
Current medications appropriate for diabetes and cardiac history. Consider increasing Lisinopril dose given elevated BP. Continue aspirin and statin for secondary prevention. May need diuretic adjustment for heart failure management
Metformin and insulin regimen appropriate for Type 2 Diabetes control. Blood pressure within normal limits on current ACE inhibitor. Statin therapy appropriate for cardiovascular risk reduction. Continue current medication plan with routine monitoring
Antihypertensive regimen appears suboptimal given systolic BP of 165 mmHg. Consider adding calcium channel blocker or increasing current beta-blocker dose. Diabetes medications appropriate but may need adjustment if renal function declines
NR"""
    )




import dspy


class SynthesizeLifestyleRecommendations(dspy.Signature):
    """Synthesize comprehensive lifestyle modification recommendations based on patient's smoking status, alcohol use, BMI, and primary diagnosis.

Form Questions:
- Lifestyle Recommendations: "What lifestyle modifications should be recommended based on the patient's diagnoses and risk factors?"

This signature aggregates previously extracted health indicators to generate personalized lifestyle guidance including smoking cessation, alcohol moderation, weight management, dietary restrictions, and exercise recommendations appropriate for the patient's medical conditions."""

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
- Consider smoking cessation guidance based on smoking_status
- Provide alcohol moderation recommendations appropriate for the diagnosis
- Include weight management advice if BMI indicates overweight/obesity
- Add diagnosis-specific dietary restrictions (e.g., sodium for heart failure, sugar for diabetes)
- Recommend appropriate exercise levels based on medical conditions

Rules:
- Synthesize comprehensive lifestyle recommendations integrating all four input factors
- Address smoking cessation if patient is current or former smoker
- Provide alcohol guidance appropriate for the primary diagnosis
- Include weight management recommendations if BMI is elevated
- Add diagnosis-specific dietary restrictions and guidelines
- Recommend exercise as tolerated based on medical conditions
- Write as coherent narrative with multiple specific recommendations
- Use professional medical advisory language
- Use "NR" if insufficient information to generate recommendations

Examples:
Continue smoking cessation (former smoker - positive). Recommend limiting alcohol to occasional use given heart failure. Weight management important given BMI 28.4. Sodium restriction <2g/day for heart failure. Regular exercise as tolerated
Smoking cessation critical given COPD diagnosis. Avoid alcohol consumption. Maintain healthy weight (current BMI 23.2). Pulmonary rehabilitation exercises recommended. Avoid respiratory irritants
No smoking history - continue abstinence. Moderate alcohol use acceptable (1 drink/day). Weight loss recommended given BMI 31.5 and Type 2 Diabetes. Carbohydrate counting and portion control. 150 minutes moderate exercise weekly
NR"""
    )




import dspy


class AggregateClinicalSummary(dspy.Signature):
    """Create a comprehensive clinical summary by synthesizing all key findings, assessments, and recommendations from previously extracted clinical data.

Form Questions:
- Clinical Summary: "Provide a comprehensive clinical summary synthesizing all key findings, assessments, and recommendations"

This signature aggregates multiple clinical data points including patient presentation, medical history, vital signs, laboratory results, diagnoses, risk assessment, medications, and treatment plans into a cohesive narrative summary suitable for clinical documentation and care coordination."""

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
- Conclude with treatment plan and recommendations
- Use professional medical writing style with appropriate abbreviations
- Aim for 4-8 sentences that capture the complete clinical picture
- Ensure logical flow from presentation through assessment to plan
- Use "NR" if insufficient data is available to create a meaningful summary

Examples:
67yo female with PMH of T2DM, HTN, and CAD s/p CABG presents with 3-day history of SOB and chest pain. Exam notable for elevated BP 142/88, HR 92. Labs show elevated creatinine 1.8 and glucose 156. Diagnosed with acute heart failure exacerbation and hypertensive urgency. Risk assessment indicates high cardiovascular risk. Current medications reviewed and adjustments recommended. Plan: admit for IV diuresis, telemetry, and cardiology consultation. Emphasized lifestyle modifications including sodium restriction and weight management
52-year-old male with history of COPD presents with acute dyspnea and productive cough. Vital signs show BP 138/82, HR 98, oxygen saturation 88% on room air. Diagnosed with acute COPD exacerbation with possible pneumonia. Chest X-ray shows right lower lobe infiltrate. Started on antibiotics, bronchodilators, and supplemental oxygen. Moderate risk for respiratory failure. Plan includes hospital admission for monitoring and respiratory therapy.
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