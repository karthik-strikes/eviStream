import dspy


# ============================================================================
# SIGNATURES - TASK 8FECF5A3
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

These fields capture comprehensive clinical documentation essential for patient care coordination, medical decision-making, and continuity of care across healthcare settings."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the medical document to extract clinical information from"""
    )

    chief_complaint: str = dspy.OutputField(
        desc="""Primary reason for medical visit or admission.

Description: Primary reason for medical visit or admission

Extraction Hints:
- Often at the beginning of clinical notes under 'Chief Complaint' or 'Presenting Problem'

Rules:
- Extract the patient's main presenting complaint as documented
- Include duration if mentioned with the complaint
- Use the exact wording from the document when possible
- Capture both symptom and timeframe if stated together
- Use "NR" if not reported or value is missing

Examples:
Shortness of breath and chest pain for 3 days
Severe headache with nausea since this morning
Abdominal pain, right lower quadrant, 24 hours
Fever and cough for one week
NR"""
    )

    symptom_duration: str = dspy.OutputField(
        desc="""How long patient has experienced symptoms.

Description: How long patient has experienced symptoms

Extraction Hints:
- Usually mentioned with chief complaint

Rules:
- Extract the specific timeframe of symptom onset
- Include units (hours, days, weeks, months, years)
- May be stated as "for X days" or "since [date/time]"
- If multiple symptoms have different durations, note the primary symptom duration
- Use "NR" if not reported or value is missing

Examples:
3 days
24 hours
2 weeks
Since yesterday evening
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
- Include dates or status indicators when provided (e.g., "s/p CABG 2018")
- Preserve medical terminology and abbreviations as written
- List multiple conditions separated by commas or as written in document
- Include chronic conditions and major past events
- Use "NR" if not reported or value is missing

Examples:
Type 2 diabetes mellitus, hypertension, coronary artery disease s/p CABG 2018
Asthma, GERD, osteoarthritis
Hypertension (diagnosed 2015), hyperlipidemia, prior stroke (2019)
No significant past medical history
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
- Preserve medical abbreviations (e.g., BID, daily, PRN)
- List multiple medications separated by commas or as formatted in document
- Include both prescription and significant OTC medications if listed
- Use "NR" if not reported or value is missing

Examples:
Metformin 1000mg BID, Lisinopril 20mg daily, Aspirin 81mg daily, Atorvastatin 40mg daily
Levothyroxine 50mcg daily, Omeprazole 20mg daily
Albuterol inhaler PRN, Fluticasone 110mcg 2 puffs BID
None
NR"""
    )

    allergies: str = dspy.OutputField(
        desc="""Known drug or other allergies.

Description: Known drug or other allergies

Extraction Hints:
- Usually prominently noted in allergies section

Rules:
- Extract all documented allergies with reactions when specified
- Include allergen name and reaction type in parentheses if provided
- List multiple allergies separated by commas
- Include drug allergies, food allergies, and environmental allergies if documented
- Note if "NKDA" (No Known Drug Allergies) or similar is stated
- Use "NR" if not reported or value is missing

Examples:
Penicillin (rash), Sulfa drugs (Stevens-Johnson syndrome)
NKDA
Codeine (nausea), Latex (contact dermatitis)
Shellfish (anaphylaxis)
No known allergies
NR"""
    )

    primary_diagnosis: str = dspy.OutputField(
        desc="""Primary diagnosis or assessment.

Description: Primary diagnosis or assessment

Extraction Hints:
- Look in 'Assessment', 'Diagnosis', or 'Impression' section

Rules:
- Extract the main or primary diagnosis as stated by the clinician
- Include ICD codes if documented
- Use medical terminology as written in the document
- This should be the principal condition being addressed
- Use "NR" if not reported or value is missing

Examples:
Acute exacerbation of heart failure
Community-acquired pneumonia
Acute appendicitis
Type 2 diabetes mellitus, uncontrolled
Migraine without aura
NR"""
    )

    secondary_diagnoses: str = dspy.OutputField(
        desc="""Additional diagnoses or comorbidities.

Description: Additional diagnoses or comorbidities

Extraction Hints:
- Listed after primary diagnosis

Rules:
- Extract all secondary or additional diagnoses documented
- Include comorbid conditions being addressed during this encounter
- List multiple diagnoses separated by commas or as formatted in document
- May include complications or related conditions
- Use "NR" if not reported or value is missing

Examples:
Hypertensive urgency, Chronic kidney disease stage 3
Anemia, Dehydration
Acute kidney injury, Hyperkalemia
None
NR"""
    )

    treatment_plan: str = dspy.OutputField(
        desc="""Recommended treatment plan and interventions.

Description: Recommended treatment plan and interventions

Extraction Hints:
- Look in 'Plan', 'Treatment Plan', or 'Recommendations' section

Rules:
- Extract the complete treatment plan as documented
- Include medications, procedures, monitoring, consultations, and follow-up
- Preserve the structure and detail level from the document
- May include admission orders, discharge plans, or outpatient management
- Capture both immediate and ongoing interventions
- Use "NR" if not reported or value is missing

Examples:
Admit for IV diuresis, telemetry monitoring, adjust heart failure medications, cardiology consult
Start Azithromycin 500mg daily x5 days, supportive care, follow-up in 1 week
NPO, IV fluids, surgical consult for appendectomy, CBC and CMP in AM
Increase Metformin to 1000mg BID, diabetes education, recheck HbA1c in 3 months
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

This signature aggregates multiple clinical data points (age, blood pressure, heart rate, diagnoses, medical history, and lab values) to create a comprehensive risk assessment that guides clinical decision-making and treatment planning."""

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
        desc="""Comprehensive assessment of patient's cardiovascular or overall health risk based on age, vital signs, diagnoses, and laboratory values.

Description: Assessment of patient's cardiovascular or overall health risk based on age, vital signs, diagnoses, and labs

Extraction Hints:
- Synthesize from patient_age, blood_pressure values, heart_rate, primary_diagnosis, medical_history, and relevant lab values

Rules:
- Integrate all available clinical data points (age, BP systolic/diastolic, heart rate, diagnoses, history, creatinine) into a coherent risk assessment
- Begin with risk level classification (e.g., "High cardiovascular risk", "Moderate risk", "Low risk")
- Include patient age and relevant demographic factors
- Cite specific vital sign abnormalities with values (e.g., "elevated BP (142/88)", "tachycardia (HR 110)")
- Reference cardiac risk factors from medical history (diabetes, hypertension, CAD, smoking, etc.)
- Include relevant lab abnormalities with values (e.g., "elevated creatinine (1.8) suggesting renal impairment")
- Connect findings to primary diagnosis or presenting condition
- Use professional medical terminology and clinical reasoning
- Synthesize into 1-3 sentences that provide actionable clinical context
- Use "NR" if insufficient data available to create meaningful risk assessment

Examples:
High cardiovascular risk: 67yo with multiple cardiac risk factors (diabetes, hypertension, CAD history), elevated BP (142/88), elevated creatinine (1.8) suggesting renal impairment, presenting with heart failure exacerbation
Moderate cardiovascular risk: 52yo with hypertension and borderline elevated BP (138/86), normal heart rate (72), creatinine within normal limits (1.0), presenting for routine follow-up
Low risk: 34yo healthy patient with normal vital signs (BP 118/76, HR 68), no significant medical history, normal renal function (creatinine 0.9), presenting with minor upper respiratory infection
High risk: 78yo with severe hypertension (BP 168/98), tachycardia (HR 105), chronic kidney disease (creatinine 2.4), history of stroke and atrial fibrillation, presenting with acute chest pain
NR"""
    )




import dspy


class SynthesizeMedicationReview(dspy.Signature):
    """Synthesize a comprehensive medication review assessment based on current medications, diagnoses, and vital signs.

Form Questions:
- Medication Review: "Provide an assessment of current medication appropriateness given the patient's diagnoses and clinical status"

This signature aggregates previously extracted clinical data to create a holistic medication review that evaluates appropriateness, identifies potential adjustments, and considers the patient's complete clinical picture including diagnoses and vital signs."""

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
- Consider medication appropriateness for the diagnosed conditions
- Evaluate if vital signs suggest medication adjustments are needed
- Identify medications for secondary prevention or disease management
- Note any potential medication changes or additions

Rules:
- Create a comprehensive 2-5 sentence assessment that evaluates medication appropriateness
- Reference specific medications by name when discussing appropriateness or adjustments
- Consider the relationship between medications and both primary and secondary diagnoses
- Include vital sign considerations (especially blood pressure) when relevant to medication management
- Mention specific medication classes (e.g., diuretics, statins, ACE inhibitors) when appropriate
- Use professional clinical language and terminology
- Address both current appropriateness and potential adjustments or additions
- Use "NR" if insufficient information is available to create a meaningful review

Examples:
Current medications appropriate for diabetes and cardiac history. Consider increasing Lisinopril dose given elevated BP. Continue aspirin and statin for secondary prevention. May need diuretic adjustment for heart failure management
Metformin and insulin regimen appropriate for Type 2 Diabetes management. Blood pressure well-controlled on current antihypertensive therapy. Statin therapy appropriate for cardiovascular risk reduction given dyslipidemia diagnosis.
Anticoagulation with warfarin appropriate for atrial fibrillation. Beta-blocker dose adequate for rate control. Consider adding ACE inhibitor given hypertension diagnosis and elevated systolic readings.
NR"""
    )




import dspy


class SynthesizeLifestyleRecommendations(dspy.Signature):
    """Synthesize personalized lifestyle modification recommendations based on patient's smoking status, alcohol use, BMI, and primary diagnosis.

Form Questions:
- Lifestyle Recommendations: "What lifestyle modifications should be recommended based on the patient's diagnoses and risk factors?"

This signature aggregates previously extracted health indicators to generate comprehensive, evidence-based lifestyle guidance tailored to the patient's specific clinical profile."""

    markdown_content: str = dspy.InputField(
        desc="""Full markdown content of the document to extract from"""
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
- Provide specific, actionable recommendations tailored to the patient's profile
- Address each relevant risk factor (smoking, alcohol, weight, disease-specific needs)

Rules:
- Synthesize comprehensive lifestyle recommendations that address all relevant risk factors
- Include smoking cessation guidance if patient is current or former smoker
- Provide alcohol consumption recommendations appropriate for the diagnosis
- Include weight management advice if BMI indicates overweight or obesity
- Add disease-specific lifestyle modifications (e.g., sodium restriction for heart failure, glucose monitoring for diabetes)
- Include exercise recommendations as appropriate for the condition
- Use professional medical language but keep recommendations clear and actionable
- Combine multiple recommendations into a cohesive narrative (2-5 sentences)
- Use "NR" if insufficient information is available to generate meaningful recommendations

Examples:
Continue smoking cessation (former smoker - positive). Recommend limiting alcohol to occasional use given heart failure. Weight management important given BMI 28.4. Sodium restriction <2g/day for heart failure. Regular exercise as tolerated
Patient is a current smoker - strongly recommend smoking cessation program. Limit alcohol to moderate use (1 drink/day). BMI 32.1 indicates obesity - recommend weight loss goal of 10% body weight through diet and exercise. Monitor blood glucose regularly given Type 2 Diabetes diagnosis
Non-smoker with normal BMI 22.3. Continue moderate alcohol use. Maintain heart-healthy diet low in saturated fats given coronary artery disease. Cardiac rehabilitation program recommended with gradual increase in aerobic exercise
NR"""
    )




import dspy


class AggregateClinicalSummary(dspy.Signature):
    """Create a comprehensive clinical summary synthesizing all key findings, assessments, and recommendations from previously extracted clinical data.

Form Questions:
- Clinical Summary: "Provide a comprehensive clinical summary synthesizing all key findings, assessments, and recommendations"

This signature aggregates multiple clinical data points including chief complaint, medical history, vital signs, laboratory results, diagnoses, risk assessment, medications, and treatment plan into a cohesive narrative summary suitable for clinical documentation and care coordination."""

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
- Begin with patient demographics (age, gender) and past medical history if available
- Include presenting complaint and relevant clinical findings
- Incorporate vital signs (blood pressure, heart rate) and laboratory results (creatinine, glucose) with values
- State primary and secondary diagnoses clearly
- Include risk assessment findings
- Summarize medication review and any adjustments
- Conclude with treatment plan and key recommendations
- Use professional medical writing style with appropriate abbreviations
- Maintain logical flow: presentation → findings → assessment → plan
- Aim for 4-8 sentences that capture all essential clinical information
- Use "NR" if cannot create summary due to insufficient data

Examples:
67yo female with PMH of T2DM, HTN, and CAD s/p CABG presents with 3-day history of SOB and chest pain. Exam notable for elevated BP 142/88, HR 92. Labs show elevated creatinine 1.8 and glucose 156. Diagnosed with acute heart failure exacerbation and hypertensive urgency. Risk assessment indicates high cardiovascular risk. Current medications reviewed and adjustments recommended. Plan: admit for IV diuresis, telemetry, and cardiology consultation. Emphasized lifestyle modifications including sodium restriction and weight management
45yo male with history of asthma presents with acute exacerbation following URI. Vital signs show HR 88, BP 128/76. Labs unremarkable with glucose 102, creatinine 0.9. Primary diagnosis of acute asthma exacerbation, secondary diagnosis of viral URI. Low risk stratification. Medication review shows poor inhaler compliance. Treatment plan includes nebulizer treatments, oral steroids, and inhaler education with pulmonology follow-up in 2 weeks
NR"""
    )






__all__ = [
    "ExtractTextualFields",
    "ClassifyEnumFields",
    "SynthesizeRiskStratification",
    "SynthesizeMedicationReview",
    "SynthesizeLifestyleRecommendations",
    "AggregateClinicalSummary",
]