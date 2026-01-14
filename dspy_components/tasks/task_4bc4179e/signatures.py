import dspy


# ============================================================================
# SIGNATURES - TASK 4BC4179E
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

These fields capture comprehensive clinical information essential for medical documentation, care coordination, and treatment planning."""

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
- Include duration if mentioned with the complaint
- Use the patient's own words when documented
- Keep the description concise but complete
- Use "NR" if not reported or value is missing

Examples:
Shortness of breath and chest pain for 3 days
Severe headache with nausea and vomiting
Abdominal pain, right lower quadrant, started yesterday
Fever and cough for one week
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
- Use the exact phrasing from the document when possible
- May be embedded in chief complaint or mentioned separately
- Use "NR" if not reported or value is missing

Examples:
3 days
2 weeks
Since yesterday morning
6 months
Acute onset, 4 hours
NR"""
    )

    medical_history: str = dspy.OutputField(
        desc="""Significant past medical conditions and diagnoses.

Description: Significant past medical conditions and diagnoses

Extraction Hints:
- Look in 'Past Medical History' or 'PMH' section

Rules:
- Extract all significant past medical conditions listed in the document
- Include dates or timeframes when provided (e.g., "s/p CABG 2018")
- List conditions separated by commas or semicolons
- Include surgical history if documented in this section
- Preserve medical abbreviations and terminology as written
- Use "NR" if not reported or value is missing

Examples:
Type 2 diabetes mellitus, hypertension, coronary artery disease s/p CABG 2018
Asthma, GERD, osteoarthritis
No significant past medical history
Chronic kidney disease stage 3, atrial fibrillation, prior CVA 2015
NR"""
    )

    current_medications: str = dspy.OutputField(
        desc="""List of medications patient is currently taking.

Description: List of medications patient is currently taking

Extraction Hints:
- Look in 'Medications' or 'Current Medications' section

Rules:
- Extract complete medication list with dosages and frequencies when provided
- Include medication name, dose, and frequency (e.g., "Metformin 1000mg BID")
- List medications separated by commas
- Include route of administration if specified
- Use "None" if patient is not taking any medications
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
- Extract all documented allergies with reactions in parentheses when provided
- Include the allergen and type of reaction (e.g., "Penicillin (rash)")
- List multiple allergies separated by commas
- Use "NKDA" or "No known drug allergies" if explicitly stated
- Include food or environmental allergies if documented
- Use "NR" if not reported or value is missing

Examples:
Penicillin (rash), Sulfa drugs (Stevens-Johnson syndrome)
NKDA
No known drug allergies
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
- Extract the main or primary diagnosis from the assessment section
- Include ICD codes if provided
- Use medical terminology as documented
- Should be the first or most prominent diagnosis listed
- Use "NR" if not reported or value is missing

Examples:
Acute exacerbation of heart failure
Community-acquired pneumonia
Acute appendicitis
Type 2 diabetes mellitus with hyperglycemia
ST-elevation myocardial infarction (STEMI)
NR"""
    )

    secondary_diagnoses: str = dspy.OutputField(
        desc="""Additional diagnoses or comorbidities.

Description: Additional diagnoses or comorbidities

Extraction Hints:
- Listed after primary diagnosis

Rules:
- Extract all secondary or additional diagnoses listed
- List diagnoses separated by commas or semicolons
- Include comorbidities that are being addressed during this encounter
- Exclude the primary diagnosis (already captured separately)
- Use "None" if no secondary diagnoses are documented
- Use "NR" if not reported or value is missing

Examples:
Hypertensive urgency, Chronic kidney disease stage 3
Anemia, Electrolyte imbalance
None
Atrial fibrillation, Acute kidney injury, Hyperkalemia
COPD exacerbation, Respiratory failure
NR"""
    )

    treatment_plan: str = dspy.OutputField(
        desc="""Recommended treatment plan and interventions.

Description: Recommended treatment plan and interventions

Extraction Hints:
- Look in 'Plan', 'Treatment Plan', or 'Recommendations' section

Rules:
- Extract the complete treatment plan including all interventions and recommendations
- Include admission status, medications, procedures, consultations, and follow-up plans
- List multiple interventions separated by commas
- Preserve medical terminology and abbreviations as written
- Include monitoring plans and diagnostic tests ordered
- Use "NR" if not reported or value is missing

Examples:
Admit for IV diuresis, telemetry monitoring, adjust heart failure medications, cardiology consult
Start antibiotics (Ceftriaxone and Azithromycin), chest X-ray, supportive care, discharge in 48-72 hours if improved
Emergent appendectomy, NPO, IV fluids, pre-op labs
Insulin drip, frequent glucose monitoring, correct electrolytes, endocrine consult
NR"""
    )




import dspy


class ExtractNumericFields(dspy.Signature):
    """Extract numeric clinical measurements and vital signs from medical documents.

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

These fields capture essential numeric clinical data including patient demographics, vital signs, and laboratory results needed for medical assessment and treatment planning."""

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
- Round to nearest integer if decimal provided
- Must be a valid integer between 0 and 120
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
158
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
92
NR"""
    )

    heart_rate: int = dspy.OutputField(
        desc="""Heart rate in beats per minute.

Description: Heart rate in beats per minute

Extraction Hints:
- Look in vital signs section

Rules:
- Extract numeric heart rate value only
- Must be a valid integer, typically between 40 and 200
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
- Extract serum creatinine value in mg/dL
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
- Extract blood glucose value in mg/dL
- Round to nearest integer if decimal provided
- Must be a valid integer, typically between 40 and 600
- May be labeled as glucose, blood sugar, or blood glucose
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
- Patient Gender: "What is the patient's gender?"
  Options: Male, Female, Other, Not specified
- Smoking Status: "What is the patient's smoking history?"
  Options: Never smoker, Former smoker, Current smoker, Unknown
- Alcohol Use: "What is the patient's alcohol consumption pattern?"
  Options: None, Occasional, Moderate, Heavy, Unknown

These fields capture essential demographic and social history information typically found in patient intake forms and medical records."""

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
- Risk Stratification: "What is the patient's overall cardiovascular or health risk assessment based on age, vital signs, diagnoses, and laboratory findings?"

This signature aggregates multiple clinical data points to create a holistic risk assessment that considers cardiovascular risk factors, organ function, and acute clinical presentations."""

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
        desc="""Previously extracted creatinine laboratory value from another signature"""
    )

    risk_stratification: str = dspy.OutputField(
        desc="""Comprehensive assessment of patient's cardiovascular or overall health risk based on integrated clinical data.

Description: Assessment of patient's cardiovascular or overall health risk based on age, vital signs, diagnoses, and labs

Extraction Hints:
- Synthesize from patient_age, blood_pressure values, heart_rate, primary_diagnosis, medical_history, and relevant lab values

Rules:
- Integrate all provided clinical parameters (age, vital signs, diagnoses, history, labs) into a cohesive risk assessment
- Begin with risk level classification (e.g., "High cardiovascular risk", "Moderate risk", "Low risk")
- Include patient age and relevant demographic context
- Cite specific abnormal vital signs with values (e.g., "elevated BP (142/88)", "tachycardia (HR 110)")
- Reference cardiac risk factors from medical history (diabetes, hypertension, CAD, smoking, etc.)
- Include relevant laboratory abnormalities with values (e.g., "elevated creatinine (1.8) suggesting renal impairment")
- Connect findings to primary diagnosis or presenting condition
- Use professional medical terminology and clinical reasoning
- Provide 2-4 sentence narrative that synthesizes all risk factors
- Use "NR" if insufficient data is available to create a meaningful risk assessment

Examples:
High cardiovascular risk: 67yo with multiple cardiac risk factors (diabetes, hypertension, CAD history), elevated BP (142/88), elevated creatinine (1.8) suggesting renal impairment, presenting with heart failure exacerbation
Moderate cardiovascular risk: 52yo with hypertension and borderline BP (138/85), HR 88, creatinine 1.1 within normal limits, presenting with chest pain ruled out for ACS
Low risk: 34yo healthy patient with normal vital signs (BP 118/76, HR 72), no significant medical history, normal renal function (creatinine 0.9), presenting for routine evaluation
High risk: 75yo with diabetes and chronic kidney disease (creatinine 2.3), hypertensive urgency (BP 178/102), tachycardic (HR 115), diagnosed with acute coronary syndrome
NR"""
    )




import dspy


class SynthesizeMedicationReview(dspy.Signature):
    """Synthesize a comprehensive medication review assessment based on current medications, diagnoses, and vital signs.

Form Questions:
- Medication Review: "What is the assessment of current medication appropriateness given the patient's diagnoses and clinical status?"

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
- Assess medication appropriateness for each diagnosis
- Identify potential dose adjustments or medication changes

Rules:
- Synthesize a comprehensive narrative assessment (2-5 sentences)
- Evaluate whether current medications are appropriate for the diagnoses
- Comment on potential dose adjustments based on vital signs (especially blood pressure)
- Include recommendations for medication continuation, adjustment, or addition
- Reference specific medications and diagnoses in the assessment
- Use professional clinical language
- Use "NR" if insufficient information to create a meaningful review

Examples:
Current medications appropriate for diabetes and cardiac history. Consider increasing Lisinopril dose given elevated BP. Continue aspirin and statin for secondary prevention. May need diuretic adjustment for heart failure management
Metformin and insulin regimen appropriate for Type 2 Diabetes management. Blood pressure well-controlled on current ACE inhibitor. Continue current medications with routine monitoring of renal function and HbA1c
Anticoagulation with Warfarin appropriate for atrial fibrillation. Beta-blocker dose adequate for rate control. Consider adding statin therapy given dyslipidemia diagnosis. Blood pressure within target range
NR"""
    )




import dspy


class SynthesizeLifestyleRecommendations(dspy.Signature):
    """Synthesize comprehensive lifestyle modification recommendations based on patient's smoking status, alcohol use, BMI, and primary diagnosis.

Form Questions:
- Lifestyle Recommendations: "What lifestyle modifications should be recommended based on the patient's risk factors and diagnoses?"

This signature aggregates multiple health indicators to provide personalized lifestyle guidance for disease management and prevention."""

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
- Consider interactions between multiple risk factors
- Tailor recommendations to the specific diagnosis
- Include specific, actionable guidance when possible

Rules:
- Synthesize comprehensive lifestyle recommendations considering all provided context fields (smoking_status, alcohol_use, bmi, primary_diagnosis)
- Address smoking cessation or continuation if smoking_status indicates current or former smoker
- Include alcohol consumption guidance based on alcohol_use and how it relates to the diagnosis
- Provide weight management recommendations if BMI indicates overweight or obesity
- Include disease-specific recommendations (e.g., sodium restriction for heart failure, glucose monitoring for diabetes)
- Mention exercise recommendations as appropriate for the condition
- Use professional medical language
- Provide 2-5 specific recommendations in a cohesive narrative or list format
- Use "NR" if insufficient information is available to make recommendations

Examples:
Continue smoking cessation (former smoker - positive). Recommend limiting alcohol to occasional use given heart failure. Weight management important given BMI 28.4. Sodium restriction <2g/day for heart failure. Regular exercise as tolerated
Patient is a current smoker - strongly recommend smoking cessation program. Limit alcohol consumption to no more than 1 drink per day given hypertension. BMI 32.1 indicates obesity - recommend weight loss goal of 10% body weight through diet and exercise. DASH diet recommended for blood pressure control
Non-smoker with normal BMI 22.3. Continue moderate alcohol use (social drinking). Maintain healthy weight through balanced diet. Regular aerobic exercise 150 minutes per week recommended for cardiovascular health and diabetes management
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
- Create a cohesive narrative that integrates patient demographics, presenting complaint, relevant medical history, vital signs, laboratory findings, diagnoses, risk assessment, medication information, and treatment plan
- Use professional medical documentation style with appropriate abbreviations (e.g., PMH, s/p, SOB)
- Structure the summary logically: patient demographics and history → presentation → physical findings → lab results → diagnoses → risk assessment → medications → treatment plan
- Include specific numeric values for vital signs and lab results when available
- Synthesize information from all provided context fields into a flowing narrative of 4-8 sentences
- Emphasize key clinical decision points and recommendations
- Use "NR" if insufficient data is available to create a meaningful summary

Examples:
67yo female with PMH of T2DM, HTN, and CAD s/p CABG presents with 3-day history of SOB and chest pain. Exam notable for elevated BP 142/88, HR 92. Labs show elevated creatinine 1.8 and glucose 156. Diagnosed with acute heart failure exacerbation and hypertensive urgency. Risk assessment indicates high cardiovascular risk. Current medications reviewed and adjustments recommended. Plan: admit for IV diuresis, telemetry, and cardiology consultation. Emphasized lifestyle modifications including sodium restriction and weight management
52yo male with history of COPD and smoking presents with worsening dyspnea over 5 days. Vital signs show BP 138/82, HR 88, elevated respiratory rate. Labs reveal normal renal function and mild hyperglycemia. Primary diagnosis of COPD exacerbation with secondary bacterial pneumonia. Moderate risk stratification for respiratory failure. Medication review shows poor inhaler compliance. Treatment plan includes antibiotics, bronchodilators, smoking cessation counseling, and pulmonary rehabilitation referral
34yo previously healthy female presents with acute onset severe headache and photophobia. Vital signs stable with BP 118/76, HR 72. Labs unremarkable. Diagnosed with migraine without aura. Low risk for secondary headache disorders. No current migraine prophylaxis. Plan includes acute treatment with triptans, lifestyle trigger identification, and neurology follow-up if symptoms persist
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