import dspy


# ============================================================================
# SIGNATURES - TASK 521E56A7
# ============================================================================


import dspy


class ExtractTextualFields(dspy.Signature):
    """Extract comprehensive clinical information from medical documents including patient presentation, history, diagnoses, and treatment plans.

Form Questions:
- Chief Complaint: "What is the primary reason for the medical visit or admission?"
- Symptom Duration: "How long has the patient experienced these symptoms?"
- Medical History: "What are the patient's significant past medical conditions and diagnoses?"
- Current Medications: "What medications is the patient currently taking?"
- Allergies: "What are the patient's known drug or other allergies?"
- Primary Diagnosis: "What is the primary diagnosis or assessment?"
- Secondary Diagnoses: "What are the additional diagnoses or comorbidities?"
- Treatment Plan: "What is the recommended treatment plan and interventions?"

These fields capture essential clinical documentation elements commonly found in medical records, progress notes, and discharge summaries."""

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
- Include symptom descriptions and associated details as stated
- Preserve medical terminology and patient-reported language
- Use "NR" if not reported or value is missing

Examples:
Shortness of breath and chest pain for 3 days
Severe headache with photophobia and nausea
Abdominal pain, right lower quadrant, 8/10 severity
Fever and productive cough x 5 days
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
- Preserve the format as written in the document
- Use "NR" if not reported or value is missing

Examples:
3 days
2 weeks
6 hours
Since yesterday morning
1 month
NR"""
    )

    medical_history: str = dspy.OutputField(
        desc="""Significant past medical conditions and diagnoses.

Description: Significant past medical conditions and diagnoses

Extraction Hints:
- Look in 'Past Medical History' or 'PMH' section

Rules:
- Extract all significant past medical conditions listed in the document
- Include dates, procedures, or additional context when provided
- Preserve medical abbreviations and terminology as written
- List multiple conditions separated by commas or as written in document
- Use "NR" if not reported or value is missing

Examples:
Type 2 diabetes mellitus, hypertension, coronary artery disease s/p CABG 2018
Asthma, GERD, osteoarthritis
No significant past medical history
Chronic kidney disease stage 3, hyperlipidemia, prior stroke 2015
NR"""
    )

    current_medications: str = dspy.OutputField(
        desc="""List of medications patient is currently taking.

Description: List of medications patient is currently taking

Extraction Hints:
- Look in 'Medications' or 'Current Medications' section

Rules:
- Extract all current medications with dosages and frequencies when provided
- Include medication names, strengths, and administration schedules
- Preserve medical abbreviations (BID, daily, PRN, etc.)
- List multiple medications separated by commas or as formatted in document
- Use "NR" if not reported or value is missing

Examples:
Metformin 1000mg BID, Lisinopril 20mg daily, Aspirin 81mg daily, Atorvastatin 40mg daily
Albuterol inhaler PRN, Omeprazole 20mg daily
None
Warfarin 5mg daily, Metoprolol 50mg BID, Furosemide 40mg daily
NR"""
    )

    allergies: str = dspy.OutputField(
        desc="""Known drug or other allergies.

Description: Known drug or other allergies

Extraction Hints:
- Usually prominently noted in allergies section

Rules:
- Extract all documented allergies with reactions when specified
- Include the allergen and type of reaction in parentheses if provided
- Preserve exact allergen names and reaction descriptions
- Use "NR" if not reported or value is missing

Examples:
Penicillin (rash), Sulfa drugs (Stevens-Johnson syndrome)
NKDA (No Known Drug Allergies)
Codeine (nausea), Latex (contact dermatitis)
Shellfish (anaphylaxis)
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
- Use medical terminology as written in the document
- Extract only the primary/principal diagnosis, not secondary conditions
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
- Extract all secondary or additional diagnoses listed in the document
- Include comorbid conditions and complications
- List multiple diagnoses separated by commas or as formatted in document
- Do not include the primary diagnosis
- Use "NR" if not reported or value is missing

Examples:
Hypertensive urgency, Chronic kidney disease stage 3
Acute kidney injury, Electrolyte imbalance
Anemia, Malnutrition
Dehydration, Urinary tract infection
NR"""
    )

    treatment_plan: str = dspy.OutputField(
        desc="""Recommended treatment plan and interventions.

Description: Recommended treatment plan and interventions

Extraction Hints:
- Look in 'Plan', 'Treatment Plan', or 'Recommendations' section

Rules:
- Extract the complete treatment plan including medications, procedures, monitoring, and follow-up
- Include specific interventions, consultations, and care instructions
- Preserve medical terminology and abbreviations as written
- Capture both immediate and ongoing treatment recommendations
- Use "NR" if not reported or value is missing

Examples:
Admit for IV diuresis, telemetry monitoring, adjust heart failure medications, cardiology consult
Start antibiotics (Ceftriaxone 1g IV daily), chest PT, oxygen therapy, repeat CXR in 48 hours
Appendectomy scheduled, NPO, IV fluids, pre-op labs
Increase insulin dosing, dietary consult, diabetes education, follow-up in 2 weeks
NR"""
    )




import dspy


class ExtractNumericFields(dspy.Signature):
    """Extract numeric clinical measurements including patient demographics, vital signs, and laboratory results from medical documents.

Form Questions:
- Patient Age: "What is the patient's age in years?"
- Blood Pressure Systolic: "What is the systolic blood pressure reading in mmHg?"
- Blood Pressure Diastolic: "What is the diastolic blood pressure reading in mmHg?"
- Heart Rate: "What is the heart rate in beats per minute?"
- Body Temperature: "What is the body temperature in Celsius?"
- BMI: "What is the Body Mass Index?"
- Lab Hemoglobin: "What is the hemoglobin level in g/dL?"
- Lab Creatinine: "What is the serum creatinine level in mg/dL?"
- Lab Glucose: "What is the blood glucose level in mg/dL?"

These numeric fields capture essential quantitative clinical data used for patient assessment, diagnosis, and treatment monitoring."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the medical document to extract numeric clinical data from"""
    )

    patient_age: int = dspy.OutputField(
        desc="""Patient's age in years.

Description: Patient's age in years

Extraction Hints:
- Look in patient demographics or header section

Rules:
- Extract numeric age value only
- Must be a valid integer between 0 and 120
- Round to nearest integer if decimal provided
- Use "NR" if not reported or value is missing

Examples:
67
45
82
NR"""
    )

    blood_pressure_systolic: int = dspy.OutputField(
        desc="""Systolic blood pressure reading in mmHg.

Description: Systolic blood pressure reading in mmHg

Extraction Hints:
- Look in vital signs section

Rules:
- Extract the systolic (first/higher) number from blood pressure reading
- Must be a valid integer, typically between 70 and 250
- If BP written as "142/88", extract 142
- Use "NR" if not reported or value is missing

Examples:
142
120
165
NR"""
    )

    blood_pressure_diastolic: int = dspy.OutputField(
        desc="""Diastolic blood pressure reading in mmHg.

Description: Diastolic blood pressure reading in mmHg

Extraction Hints:
- Look in vital signs section

Rules:
- Extract the diastolic (second/lower) number from blood pressure reading
- Must be a valid integer, typically between 40 and 150
- If BP written as "142/88", extract 88
- Use "NR" if not reported or value is missing

Examples:
88
80
95
NR"""
    )

    heart_rate: int = dspy.OutputField(
        desc="""Heart rate in beats per minute.

Description: Heart rate in beats per minute

Extraction Hints:
- Look in vital signs section

Rules:
- Extract numeric heart rate value only
- Must be a valid integer, typically between 30 and 200
- May be labeled as HR, pulse, or heart rate
- Use "NR" if not reported or value is missing

Examples:
92
72
110
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
- Must be a valid number, typically between 35.0 and 42.0
- Preserve decimal precision (e.g., 37.2)
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
- Extract BMI value if explicitly stated
- If not stated but height and weight available, calculate: weight(kg) / height(m)²
- Must be a valid number, typically between 10.0 and 60.0
- Preserve decimal precision (e.g., 28.4)
- Use "NR" if not reported or cannot be calculated

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
- Extract hemoglobin (Hgb, Hb, or hemoglobin) value in g/dL
- Must be a valid number, typically between 5.0 and 20.0
- Preserve decimal precision (e.g., 13.2)
- Use "NR" if not reported or value is missing

Examples:
13.2
11.5
15.8
NR"""
    )

    lab_creatinine: float = dspy.OutputField(
        desc="""Serum creatinine in mg/dL.

Description: Serum creatinine in mg/dL

Extraction Hints:
- Look in laboratory results section

Rules:
- Extract serum creatinine (Cr, creatinine) value in mg/dL
- Must be a valid number, typically between 0.3 and 15.0
- Preserve decimal precision (e.g., 1.8)
- Use "NR" if not reported or value is missing

Examples:
1.8
0.9
2.4
NR"""
    )

    lab_glucose: int = dspy.OutputField(
        desc="""Blood glucose level in mg/dL.

Description: Blood glucose level in mg/dL

Extraction Hints:
- Look in laboratory results section

Rules:
- Extract blood glucose (glucose, blood sugar) value in mg/dL
- Must be a valid integer, typically between 40 and 600
- May be fasting or random glucose
- Round to nearest integer if decimal provided
- Use "NR" if not reported or value is missing

Examples:
156
95
210
NR"""
    )




import dspy


class ClassifyEnumFields(dspy.Signature):
    """Extract patient demographic and social history information including gender, smoking status, and alcohol use from medical documents.

Form Questions:
- Patient Gender: "What is the patient's gender?"
  Options: Male, Female, Other, Not specified
- Smoking Status: "What is the patient's smoking history?"
  Options: Never smoker, Former smoker, Current smoker, Unknown
- Alcohol Use: "What is the patient's alcohol consumption pattern?"
  Options: None, Occasional, Moderate, Heavy, Unknown

These fields capture essential demographic and social history information commonly found in patient intake forms and medical records."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the medical document to extract patient information from"""
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
- Look for gender information in patient demographics, registration, or header sections
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
- "Former smoker" includes anyone who previously smoked but quit
- "Current smoker" includes active tobacco use of any frequency
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
- Map descriptive terms to closest option (e.g., "social drinker" → "Occasional", "drinks daily" → "Moderate" or "Heavy")
- Use clinical judgment to categorize frequency/quantity descriptions
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

This signature aggregates multiple clinical data points (age, blood pressure, heart rate, diagnoses, medical history, and lab values) to create a comprehensive risk assessment that helps clinicians understand the patient's overall health status and guide treatment decisions."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the medical document to extract from"""
    )

    patient_age: int = dspy.InputField(
        desc="""Previously extracted patient age from another signature"""
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
        desc="""Previously extracted creatinine lab value from another signature"""
    )

    risk_stratification: str = dspy.OutputField(
        desc="""Assessment of patient's cardiovascular or overall health risk based on age, vital signs, diagnoses, and labs.

Description: Assessment of patient's cardiovascular or overall health risk based on age, vital signs, diagnoses, and labs

Extraction Hints:
- Synthesize from patient_age, blood_pressure values, heart_rate, primary_diagnosis, medical_history, and relevant lab values

Rules:
- Create a comprehensive 2-4 sentence narrative synthesizing all available clinical data
- Begin with risk level classification (e.g., "High cardiovascular risk", "Moderate risk", "Low risk")
- Include patient age and relevant demographic factors
- Incorporate vital sign abnormalities (elevated/low BP, abnormal HR)
- Reference key diagnoses and relevant medical history
- Include significant laboratory abnormalities (e.g., elevated creatinine suggesting renal impairment)
- Mention presenting condition or acute issues if applicable
- Use professional medical terminology
- Provide clinical context that explains why the risk level was assigned
- Use "NR" if insufficient data available to create meaningful risk assessment

Examples:
High cardiovascular risk: 67yo with multiple cardiac risk factors (diabetes, hypertension, CAD history), elevated BP (142/88), elevated creatinine (1.8) suggesting renal impairment, presenting with heart failure exacerbation
Moderate cardiovascular risk: 52yo patient with controlled hypertension (BP 128/82) and family history of CAD, normal renal function (creatinine 0.9), presenting for routine follow-up with stable chronic conditions
Low risk: 34yo healthy patient with normal vital signs (BP 118/76, HR 72), no significant medical history, normal laboratory values including creatinine 0.8, presenting for annual physical examination
High risk: 78yo with atrial fibrillation and history of stroke, tachycardic (HR 110), hypertensive (BP 156/94), elevated creatinine (2.1) indicating chronic kidney disease stage 3
NR"""
    )




import dspy


class SynthesizeMedicationReview(dspy.Signature):
    """Synthesize a comprehensive medication review assessment by analyzing current medications in the context of patient diagnoses and vital signs.

Form Questions:
- Medication Review: "What is your assessment of the current medication appropriateness given the patient's diagnoses and clinical status?"

This signature aggregates previously extracted clinical data (medications, diagnoses, vital signs) to generate a holistic medication review that evaluates appropriateness, identifies potential adjustments, and provides clinical recommendations."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the medical document to extract from"""
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
- Evaluate whether medications align with documented diagnoses
- Consider vital signs (blood pressure) when assessing medication appropriateness
- Identify potential dose adjustments or medication changes needed
- Comment on preventive medications and disease management strategies

Rules:
- Provide a comprehensive 2-5 sentence assessment of medication appropriateness
- Reference specific medications and how they relate to diagnoses
- Include recommendations for dose adjustments if vital signs suggest need
- Comment on preventive therapy appropriateness (e.g., aspirin, statins)
- Mention any medication management considerations for chronic conditions
- Use professional clinical language and reasoning
- Use "NR" if not reported or insufficient information to create assessment

Examples:
Current medications appropriate for diabetes and cardiac history. Consider increasing Lisinopril dose given elevated BP. Continue aspirin and statin for secondary prevention. May need diuretic adjustment for heart failure management
Medication regimen well-aligned with diagnosis of hypertension and hyperlipidemia. Blood pressure readings within target range on current ACE inhibitor dose. Statin therapy appropriate for cardiovascular risk reduction. No adjustments needed at this time
Patient on Metformin and insulin for Type 2 Diabetes with good glycemic control. Beta-blocker and aspirin appropriate for post-MI status. Consider adding statin for lipid management given cardiovascular history
NR"""
    )




import dspy


class SynthesizeLifestyleRecommendations(dspy.Signature):
    """Synthesize comprehensive lifestyle modification recommendations based on patient's smoking status, alcohol use, BMI, and primary diagnosis.

Form Questions:
- Lifestyle Recommendations: "What lifestyle modifications should be recommended based on the patient's risk factors and diagnoses?"

This signature aggregates previously extracted health indicators to generate personalized lifestyle guidance for patient care planning."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the medical document to extract from"""
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
- Consider interactions between different risk factors
- Tailor recommendations to the specific diagnosis
- Include specific, actionable guidance

Rules:
- Synthesize comprehensive lifestyle recommendations considering all provided context fields (smoking_status, alcohol_use, bmi, primary_diagnosis)
- Address smoking cessation or continuation for former/current smokers
- Provide specific alcohol consumption guidance based on diagnosis and current use
- Include weight management recommendations if BMI indicates overweight/obesity
- Tailor dietary restrictions to diagnosis (e.g., sodium restriction for heart failure, sugar control for diabetes)
- Include exercise recommendations appropriate to patient's condition
- Provide specific quantitative targets where applicable (e.g., <2g/day sodium, BMI target range)
- Write in clear, professional medical language
- Combine multiple recommendations into a cohesive narrative
- Use "NR" if insufficient information is available to generate meaningful recommendations

Examples:
Continue smoking cessation (former smoker - positive). Recommend limiting alcohol to occasional use given heart failure. Weight management important given BMI 28.4. Sodium restriction <2g/day for heart failure. Regular exercise as tolerated
Patient is current smoker - strongly recommend smoking cessation program. Abstain from alcohol given liver disease diagnosis. BMI 32.1 indicates obesity - recommend weight loss goal of 10% body weight over 6 months. Low-fat diet and 150 minutes moderate exercise weekly
Maintain non-smoking status. Current moderate alcohol use acceptable with no contraindications. BMI 23.5 within normal range - maintain current weight. Mediterranean diet recommended for cardiovascular health. Continue regular physical activity 30 minutes daily
NR"""
    )




import dspy


class AggregateClinicalSummary(dspy.Signature):
    """Create a comprehensive clinical summary by synthesizing all previously extracted clinical data including complaints, history, vitals, diagnoses, risk assessment, medications, and treatment plans.

Form Questions:
- Clinical Summary: "Provide a comprehensive clinical summary synthesizing all key findings, assessments, and recommendations"

This signature aggregates multiple clinical data points to create a cohesive narrative summary suitable for medical documentation, handoffs, and clinical decision support."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the clinical document to extract from"""
    )

    chief_complaint: str = dspy.InputField(
        desc="""Previously extracted chief complaint from another signature"""
    )

    symptom_duration: str = dspy.InputField(
        desc="""Previously extracted symptom duration from another signature"""
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

    lab_glucose: int = dspy.InputField(
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
- Begin with patient demographics (age, gender) and relevant past medical history
- Include presenting complaint with symptom duration
- Incorporate vital signs (BP, HR) and relevant laboratory values (creatinine, glucose)
- State primary and secondary diagnoses clearly
- Include risk stratification assessment
- Summarize medication review findings and any adjustments
- Conclude with treatment plan and key recommendations
- Use professional medical writing style with appropriate abbreviations (PMH, s/p, SOB, T2DM, HTN, CAD, CABG, etc.)
- Aim for 4-8 sentences that capture the complete clinical picture
- Maintain logical flow: presentation → examination → assessment → plan
- Use "NR" if insufficient data is available to create a meaningful summary

Examples:
67yo female with PMH of T2DM, HTN, and CAD s/p CABG presents with 3-day history of SOB and chest pain. Exam notable for elevated BP 142/88, HR 92. Labs show elevated creatinine 1.8 and glucose 156. Diagnosed with acute heart failure exacerbation and hypertensive urgency. Risk assessment indicates high cardiovascular risk. Current medications reviewed and adjustments recommended. Plan: admit for IV diuresis, telemetry, and cardiology consultation. Emphasized lifestyle modifications including sodium restriction and weight management
52yo male with history of obesity and prediabetes presents with 2-week history of polyuria and polydipsia. Vital signs show BP 128/82, HR 78. Labs reveal glucose 245 and creatinine 1.1. Diagnosed with new-onset Type 2 Diabetes Mellitus with no acute complications. Risk stratification shows moderate metabolic risk. Medication review completed with initiation of metformin recommended. Plan: start metformin 500mg BID, diabetes education, dietary counseling, and follow-up in 2 weeks for glucose monitoring.
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