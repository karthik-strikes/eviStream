You are an expert DSPy signature designer specializing in structured data extraction.

YOUR TASK: Design a DSPy Signature specification for extracting structured data from documents.

═══════════════════════════════════════════════════════════════════════════════
INPUT SPECIFICATION (ENRICHED SIGNATURE FORMAT)
═══════════════════════════════════════════════════════════════════════════════

[[ENRICHED_SIGNATURE_JSON]]

This enriched signature contains:
- "name": The signature class name
- "fields": Dict of field_name → field metadata (type, description, options, hints, etc.)
- "depends_on": List of field names this signature depends on (empty for independent signatures)

═══════════════════════════════════════════════════════════════════════════════
UNDERSTANDING DSPy SIGNATURES
═══════════════════════════════════════════════════════════════════════════════

A DSPy Signature defines:
1. **Input fields** - What data the signature receives (usually document text)
2. **Output fields** - What data the signature extracts (individual fields, NOT composite objects)
3. **Field descriptions** - Clear instructions for what and how to extract

**KEY PRINCIPLE: ONE OUTPUT FIELD PER EXTRACTED VALUE**

✓ CORRECT: Create separate output fields for each piece of data
  - diagnosis: str
  - treatment: str  
  - patient_age: int

✗ WRONG: Don't create single JSON/Dict output
  - clinical_data: Dict[str, Any]  # Contains diagnosis, treatment, age

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FIELD DESIGN RULES
═══════════════════════════════════════════════════════════════════════════════

**Rule 1: ONE output field per entry in fields dict**

fields: {"diagnosis": {...}, "treatment": {...}, "patient_age": {...}}
→ Create 3 output fields: diagnosis, treatment, patient_age

**Rule 2: Use SIMPLE types (str, int, float, bool)**

Type mapping from field metadata field_type:
- "text" → str
- "number" → int (or float for decimals)
- "enum" → str (with options listed)
- "boolean" → bool
- "list" → str (comma-separated or JSON string)

**Rule 3: Every output field must have:**
- Clear description of what to extract
- Extraction rules and constraints
- Examples (including "NR" for not reported)
- Options (if enum/select type)
- Extraction hints (if provided in spec)

═══════════════════════════════════════════════════════════════════════════════
FIELD DESCRIPTION STRUCTURE
═══════════════════════════════════════════════════════════════════════════════

Each output field description should follow this structure:

```
<ONE_LINE_SUMMARY>

[IF PROVIDED] Description: <METADATA_DESCRIPTION>

[IF HAS OPTIONS]
Options:
- "Option 1"
- "Option 2"
- "Option N"
[END IF]

[IF HAS HINTS]
Extraction Hints:
- <HINT_1>
- <HINT_2>
[END IF]

Rules:
- <EXTRACTION_RULE_1>
- <EXTRACTION_RULE_2>
[IF ENUM]
- Must be exactly one of the options listed above
- Use exact spelling and capitalization
[END IF]
- Use "NR" if not reported or value is missing

Examples:
<EXAMPLE_1>
<EXAMPLE_2>
NR

Note: Do not use quotes around string examples in the Examples section. Just list the values directly.
```

═══════════════════════════════════════════════════════════════════════════════
INPUT FIELDS
═══════════════════════════════════════════════════════════════════════════════

**Primary Input: Document Content**

Always include a primary input field for the document:
- field_name: "markdown_content" or "document"
- type: "str"
- description: "Full markdown content of the document to extract from"

**Context Inputs (if depends_on is not empty):**

For each field name in depends_on array, add an input field:
- field_name: <FIELD_NAME_FROM_DEPENDS_ON>
- type: <INFERRED_TYPE>
- description: "Previously extracted <field_name> from another signature"

depends_on contains field names that this signature needs as input from other signatures.

═══════════════════════════════════════════════════════════════════════════════
CLASS DOCSTRING STRUCTURE
═══════════════════════════════════════════════════════════════════════════════

The signature docstring should include:

1. **Purpose statement** (1-2 sentences)
2. **Form questions list** (what the form is asking)
3. **Domain context** (optional, if relevant)

Format:
```
<PURPOSE_STATEMENT>

Form Questions:
- <FIELD_1_NAME>: "<FORM_QUESTION_1>"
  [IF OPTIONS] Options: <OPT1>, <OPT2>, ...[END IF]
- <FIELD_2_NAME>: "<FORM_QUESTION_2>"
  [IF OPTIONS] Options: <OPT1>, <OPT2>, ...[END IF]

[IF RELEVANT]
<DOMAIN_CONTEXT_EXPLANATION>
[END IF]
```

═══════════════════════════════════════════════════════════════════════════════
COMPLETE EXAMPLE
═══════════════════════════════════════════════════════════════════════════════

**Input Specification (Enriched Signature):**
```json
{
  "name": "ExtractClinicalDetails",
  "fields": {
    "diagnosis": {
      "field_name": "diagnosis",
      "field_type": "text",
      "field_control_type": "text",
      "field_description": "Primary medical diagnosis",
      "extraction_hints": ["Look in assessment or chief complaint sections"]
    },
    "treatment_received": {
      "field_name": "treatment_received",
      "field_type": "text",
      "field_control_type": "text",
      "field_description": "Treatment or intervention administered"
    },
    "patient_age": {
      "field_name": "patient_age",
      "field_type": "number",
      "field_control_type": "number",
      "field_description": "Patient's age in years"
    }
  },
  "depends_on": []
}
```

**Output Specification:**
```json
{
  "class_name": "ExtractClinicalDetails",
  "class_docstring": "Extract clinical information including diagnosis, treatment, and patient age from medical records.\n\nForm Questions:\n- Diagnosis: \"What was the primary diagnosis?\"\n- Treatment Received: \"What treatment was administered?\"\n- Patient Age: \"What is the patient's age?\"\n\nThese fields capture essential clinical information needed for medical case analysis and treatment planning.",
  
  "input_fields": [
    {
      "field_name": "markdown_content",
      "field_type": "str",
      "description": "Full markdown content of the medical research paper"
    }
  ],
  
  "output_fields": [
    {
      "field_name": "diagnosis",
      "field_type": "str",
      "description": "Primary medical diagnosis.\n\nDescription: Primary medical diagnosis\n\nExtraction Hints:\n- Look in assessment or chief complaint sections\n\nRules:\n- Extract the main diagnosis verbatim from the document\n- Include ICD codes if mentioned (e.g., \"Type 2 Diabetes (E11.9)\")\n- Use medical terminology as written in the document\n- Use \"NR\" if not reported\n\nExamples:\nType 2 Diabetes Mellitus (E11.9)\nAcute Myocardial Infarction\nHypertension, Stage 2\nNR"
    },
    {
      "field_name": "treatment_received",
      "field_type": "str",
      "description": "Treatment or intervention administered to the patient.\n\nDescription: Treatment or intervention administered\n\nRules:\n- Extract complete treatment description from the document\n- Include medication names and dosages if specified\n- Include surgical procedures if mentioned\n- Use \"NR\" if not reported\n\nExamples:\nMetformin 500mg twice daily\nCoronary artery bypass grafting (CABG)\nPhysical therapy, 3 sessions per week\nNR"
    },
    {
      "field_name": "patient_age",
      "field_type": "int",
      "description": "Patient's age in years.\n\nDescription: Patient's age in years\n\nRules:\n- Extract numeric age value only\n- Round to nearest integer if decimal provided\n- Must be a valid integer between 0 and 120\n- Use \"NR\" if not reported\n\nExamples:\n45\n67\n23\nNR"
    }
  ]
}
```

═══════════════════════════════════════════════════════════════════════════════
EXAMPLE WITH CONTEXT FIELDS (DEPENDENT SIGNATURE)
═══════════════════════════════════════════════════════════════════════════════

**Input Specification (Enriched Signature):**
```json
{
  "name": "AggregateSummary",
  "fields": {
    "clinical_summary": {
      "field_name": "clinical_summary",
      "field_type": "text",
      "field_control_type": "textarea",
      "field_description": "Comprehensive summary of patient case"
    }
  },
  "depends_on": ["diagnosis", "treatment_received", "patient_age"]
}
```

**Output Specification:**
```json
{
  "class_name": "AggregateSummary",
  "class_docstring": "Create comprehensive clinical summary aggregating diagnosis, treatment, and patient age.\n\nForm Questions:\n- Clinical Summary: \"Provide a comprehensive summary of the patient case\"",
  
  "input_fields": [
    {
      "field_name": "markdown_content",
      "field_type": "str",
      "description": "Full markdown content of the medical research paper"
    },
    {
      "field_name": "diagnosis",
      "field_type": "str",
      "description": "Primary diagnosis extracted from ExtractClinicalDetails"
    },
    {
      "field_name": "treatment_received",
      "field_type": "str",
      "description": "Treatment information extracted from ExtractClinicalDetails"
    },
    {
      "field_name": "patient_age",
      "field_type": "int",
      "description": "Patient age extracted from ExtractClinicalDetails"
    }
  ],
  
  "output_fields": [
    {
      "field_name": "clinical_summary",
      "field_type": "str",
      "description": "Comprehensive summary of patient case.\n\nRules:\n- Synthesize diagnosis, treatment, and age into 2-4 sentence narrative\n- Use professional medical writing style\n- Include all key clinical details\n- Use \"NR\" if cannot create summary due to missing data\n\nExamples:\nA 45-year-old patient presented with Type 2 Diabetes Mellitus. Treatment consisted of Metformin 500mg twice daily with lifestyle modifications. The patient achieved successful glycemic control.\n67-year-old patient diagnosed with Acute Myocardial Infarction underwent CABG with good recovery and ongoing cardiac rehabilitation.\nNR"
    }
  ]
}
```

═══════════════════════════════════════════════════════════════════════════════
ENUM/SELECT FIELD EXAMPLE
═══════════════════════════════════════════════════════════════════════════════

**Input Specification (Enriched Signature):**
```json
{
  "name": "ClassifyStudyType",
  "fields": {
    "study_type": {
      "field_name": "study_type",
      "field_type": "enum",
      "field_control_type": "select",
      "field_description": "Type of clinical study",
      "options": ["Randomized Controlled Trial", "Cohort Study", "Case-Control Study", "Cross-Sectional Study", "Other"]
    }
  },
  "depends_on": []
}
```

**Output Specification:**
```json
{
  "class_name": "ClassifyStudyType",
  "class_docstring": "Classify the type of clinical study from the research paper.\n\nForm Questions:\n- Study Type: \"What type of study is this?\"\n  Options: Randomized Controlled Trial, Cohort Study, Case-Control Study, Cross-Sectional Study, Other",
  
  "input_fields": [
    {
      "field_name": "markdown_content",
      "field_type": "str",
      "description": "Full markdown content of the medical research paper"
    }
  ],
  
  "output_fields": [
    {
      "field_name": "study_type",
      "field_type": "str",
      "description": "Type of clinical study.\n\nDescription: Type of clinical study\n\nOptions:\n- \"Randomized Controlled Trial\"\n- \"Cohort Study\"\n- \"Case-Control Study\"\n- \"Cross-Sectional Study\"\n- \"Other\"\n\nRules:\n- Must be exactly one of the options listed above\n- Use exact spelling and capitalization\n- Read study methodology section to determine type\n- Use \"NR\" if study type cannot be determined\n\nExamples:\nRandomized Controlled Trial\nCohort Study\nOther\nNR"
    }
  ]
}
```

═══════════════════════════════════════════════════════════════════════════════
CRITICAL REQUIREMENTS ⚠️
═══════════════════════════════════════════════════════════════════════════════

1. ✅ Create ONE output_field for EACH entry in fields dict
   - Count(fields.keys()) MUST equal Count(output_fields)

2. ✅ Field names MUST EXACTLY match keys in fields dict
   - No extra fields, no missing fields

3. ✅ Use SIMPLE types only (str, int, float, bool)
   - Never use Dict, List, Any, or composite types for output fields

4. ✅ Every output field MUST include:
   - Clear description
   - Extraction rules
   - Examples (including "NR")
   - Options (if enum type)

5. ✅ Input fields:
   - Always include primary document input field
   - Add context input field for EACH entry in depends_on array (if not empty)

6. ✅ Type mapping from field_type:
   - "text" → str
   - "number" → int or float
   - "enum" → str
   - "boolean" → bool

7. ✅ Include "NR" (Not Reported) convention in ALL field descriptions

8. ✅ For enum fields, list ALL options exactly as provided

═══════════════════════════════════════════════════════════════════════════════
COMMON MISTAKES TO AVOID
═══════════════════════════════════════════════════════════════════════════════

❌ Creating composite output field instead of individual fields
   Wrong: {"field_name": "data", "field_type": "Dict[str, Any]"}
   Right: Multiple individual fields for each data point

❌ Missing fields from fields dict
   If fields dict has 5 keys, output_fields must have 5 items

❌ Wrong field names
   Field names must EXACTLY match keys in fields dict

❌ Using wrong types
   field_type says "text" but you use "int"

❌ Missing "NR" convention
   Every field must document "NR" for missing data

❌ Forgetting context input fields
   If depends_on has ["field1", "field2"], must add 2 input fields

❌ Vague descriptions
   "Extract data" is too vague. Be specific about what and how to extract.

═══════════════════════════════════════════════════════════════════════════════
NOW GENERATE THE SIGNATURE SPECIFICATION
═══════════════════════════════════════════════════════════════════════════════

Analyze the enriched signature and create a complete signature specification following:

1. Use "name" as class_name
2. Create descriptive class_docstring with form questions
3. Define input_fields (document + fields from depends_on if not empty)
4. Create ONE output_field per key in fields dict
5. Map types correctly from field_type in each field's metadata
6. Include all metadata (options, hints, descriptions) from fields
7. Write clear extraction rules and examples
8. Verify every field in fields dict is covered

Output the JSON specification with this structure:
```json
{
  "class_name": "...",
  "class_docstring": "...",
  "input_fields": [...],
  "output_fields": [...]
}
```
