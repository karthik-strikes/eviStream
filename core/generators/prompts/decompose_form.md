You are an expert system architect specializing in modular extraction pipeline design.

YOUR TASK: Analyze form fields and group them into atomic signatures based on cognitive behavior patterns.

═══════════════════════════════════════════════════════════════════════════════
FORM SPECIFICATION TO ANALYZE
═══════════════════════════════════════════════════════════════════════════════

[[FORM_DATA_JSON]]

═══════════════════════════════════════════════════════════════════════════════
UNDERSTANDING COGNITIVE BEHAVIOR
═══════════════════════════════════════════════════════════════════════════════

Each field requires a specific type of cognitive processing. Your job is to identify
the cognitive behavior and group fields that share the same behavior.

**COGNITIVE BEHAVIOR TYPES:**

1. **Direct Text Extraction**
   - Locate and extract text information verbatim from document
   - Examples: drug names, dates, descriptions, identifiers
   - Pattern: Find specific text, copy it out
   - Field type: "text"

2. **Direct Numeric Extraction**
   - Locate and extract numeric values from document
   - Examples: counts, measurements, percentages, ages
   - Pattern: Find specific numbers, extract them
   - Field type: "number"

3. **Classification into Categories**
   - Read information and classify into predefined options
   - Examples: intervention type, status, phase, category
   - Pattern: Understand context, pick correct option
   - Field type: "enum" (has "options" array)

4. **Boolean Determination**
   - Determine yes/no or true/false based on document content
   - Examples: was_randomized, has_adverse_events, is_complete
   - Pattern: Check condition, return true/false
   - Field type: "boolean"

5. **Aggregation/Synthesis**
   - Combine multiple pieces of information into summary or derived value
   - Examples: comprehensive summaries, risk assessments, combined scores
   - Pattern: Read multiple fields, synthesize into new output
   - **REQUIRES outputs from other signatures as input**

═══════════════════════════════════════════════════════════════════════════════
GROUPING STRATEGY: MINIMIZE SIGNATURES
═══════════════════════════════════════════════════════════════════════════════

⚠️  PRIMARY GOAL: Create as FEW signatures as possible by aggressive grouping!

**GROUPING RULES:**

✓ **Rule 1: Group all direct text extractions together**
  All fields with type="text" that extract directly → ONE signature
  Example: [drug_name, duration, formulation, description] → 1 signature

✓ **Rule 2: Group all direct numeric extractions together**
  All fields with type="number" that extract directly → ONE signature
  Example: [sample_size, age_mean, dropout_count, dose] → 1 signature

✓ **Rule 3: Group all enum classifications together**
  All fields with type="enum" that classify directly → ONE signature
  Example: [intervention_type, route, phase, status] → 1 signature

✓ **Rule 4: Group all boolean determinations together**
  All fields with type="boolean" → ONE signature
  Example: [was_randomized, has_control, is_complete] → 1 signature

✓ **Rule 5: Separate signatures for aggregations**
  Each field that synthesizes/combines other fields → SEPARATE signature
  These signatures have dependencies on other fields

**ONLY create separate signatures if:**
- Different cognitive behavior (extraction vs classification vs aggregation)
- Field depends on outputs from other signatures
- Field requires special contextual processing that others don't need

═══════════════════════════════════════════════════════════════════════════════
IDENTIFYING DEPENDENCIES
═══════════════════════════════════════════════════════════════════════════════

A field has dependencies if it:
- Combines/synthesizes information from other fields
- Creates summaries or derived values based on other extracted data
- References other fields in its description (e.g., "summary of drug_name and duration")
- Cannot be extracted independently from document alone

**Independent fields** (depends_on = []):
- Can be extracted directly from document
- Don't need outputs from other signatures
- Most extraction and classification fields

**Dependent fields** (depends_on = ["field1", "field2", ...]):
- Need outputs from other signatures as input
- Aggregation and synthesis fields
- List ALL field names this signature needs to create its output

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (Pydantic Enforced)
═══════════════════════════════════════════════════════════════════════════════

Return a JSON object with this EXACT structure:

{
  "reasoning_trace": "Your step-by-step analysis:\n1. Analyzed X fields from form_data\n2. Identified Y text fields, Z numeric fields...\n3.Grouped them into N signatures based on...\n4. Identified dependencies for aggregation fields...",
  "signatures": [
    {
      "name": "ExtractTextualFields",
      "field_names": ["drug_name", "duration", "formulation", "description"],
      "depends_on": []
    },
    {
      "name": "ExtractNumericFields",
      "field_names": ["sample_size", "age_mean", "dropout_count"],
      "depends_on": []
    },
    {
      "name": "ClassifyEnumFields",
      "field_names": ["intervention_type", "route", "study_phase"],
      "depends_on": []
    },
    {
      "name": "DetermineBooleanFields",
      "field_names": ["was_randomized", "has_control_group"],
      "depends_on": []
    },
    {
      "name": "AggregateClinicalSummary",
      "field_names": ["clinical_summary"],
      "depends_on": ["drug_name", "duration", "intervention_type", "sample_size"]
    }
  ]
}

**Field Specifications:**

- **reasoning_trace** (string, optional): Your step-by-step reasoning
  - Explain how you analyzed the fields
  - Justify your grouping decisions
  - Note any special cases or dependencies identified
  - Keep it concise but informative (3-8 sentences)

- **name** (string, required): Descriptive name for the signature
  - Use clear, action-oriented names: "ExtractTextualFields", "ClassifyEnumFields"
  - NOT generic names: "TextExtractor", "Classifier", "SignatureA"
  - Pattern: [Verb][ObjectType]Fields or [Verb][SpecificPurpose]

- **field_names** (array of strings, required): Field names from form_data
  - Use exact field_name values from form_data
  - Each field must appear in exactly ONE signature
  - Order doesn't matter

- **depends_on** (array of strings, required): Field names needed as input
  - Empty array [] for independent signatures
  - List field names (not signature names) for dependent signatures
  - These will become input parameters to the signature
  - Must reference fields that are outputs of other signatures

═══════════════════════════════════════════════════════════════════════════════
REASONING TRACE FORMAT
═══════════════════════════════════════════════════════════════════════════════

Your reasoning_trace should follow this structure:
```
Step 1: Field Inventory
- Found X fields in form_data
- Y text fields, Z numeric fields, A enum fields, B boolean fields, C aggregation fields

Step 2: Cognitive Behavior Analysis
- Text extractions: [field1, field2, ...]
- Numeric extractions: [field3, field4, ...]
- Enum classifications: [field5, field6, ...]
- Aggregations: [field7] (depends on field1, field3)

Step 3: Grouping Decision
- Created N signatures by grouping fields with same cognitive behavior
- Separated aggregation fields due to dependencies

Step 4: Verification
- All X fields covered
- No duplicates
- Dependencies validated
```

Keep it concise but informative - this helps with debugging and validation.

**Example reasoning_trace:**
```json
"reasoning_trace": "Step 1: Found 7 fields - 3 text (drug_name, duration, formulation), 2 numeric (sample_size, age_mean), 1 enum (intervention_type), 1 aggregation (clinical_summary). Step 2: Grouped text extractions into ExtractTextualFields, numeric into ExtractNumericFields, enum into ClassifyEnumFields. Step 3: Separated clinical_summary into AggregateClinicalSummary because it depends on drug_name, duration, intervention_type, and sample_size. Step 4: All 7 fields covered, no duplicates, dependencies valid."
```

═══════════════════════════════════════════════════════════════════════════════
SIGNATURE NAMING CONVENTIONS
═══════════════════════════════════════════════════════════════════════════════

**Good signature names:**
✓ ExtractTextualFields - Clear action + what it processes
✓ ClassifyEnumFields - Clear action + field type
✓ ExtractNumericFields - Clear action + what it extracts
✓ DetermineBooleanFields - Clear action + field type
✓ AggregateClinicalSummary - Clear action + specific purpose
✓ SynthesizeRiskAssessment - Clear action + specific purpose

**Bad signature names:**
✗ TextExtractor - Too generic, not descriptive
✗ ProcessData - What data? How?
✗ SignatureOne - No semantic meaning
✗ GetFields - Vague action
✗ Handler - What does it handle?

**Naming patterns:**
- Independent extractions: "Extract[Type]Fields" or "Classify[Type]Fields"
- Aggregations: "Aggregate[Purpose]" or "Synthesize[Purpose]"
- Use domain-specific terms when applicable: "ClinicalSummary", "RiskAssessment"

═══════════════════════════════════════════════════════════════════════════════
STEP-BY-STEP PROCESS
═══════════════════════════════════════════════════════════════════════════════

**Step 1: Inventory all fields**
List all field_name values from form_data["fields"]

**Step 2: Classify each field's cognitive behavior**
For each field, determine:
- Is it text extraction, numeric extraction, classification, boolean, or aggregation?
- Does it depend on other fields, or is it independent?
- Look at field type (text/number/enum/boolean) and description

**Step 3: Group fields by behavior**
- All independent text extractions → ONE signature
- All independent numeric extractions → ONE signature
- All independent enum classifications → ONE signature
- All independent boolean determinations → ONE signature
- Each aggregation → SEPARATE signature with dependencies

**Step 4: Name signatures descriptively**
Use clear, meaningful names following the conventions above

**Step 5: Identify dependencies**
For each aggregation signature:
- Which fields does it need to create its output?
- List those field names in depends_on array

**Step 6: Verify coverage**
- Every field from form_data appears exactly once
- No field is missing
- No field appears in multiple signatures
- All depends_on references point to valid fields

═══════════════════════════════════════════════════════════════════════════════
COMPLETE EXAMPLES
═══════════════════════════════════════════════════════════════════════════════

**Example 1: Simple form with only independent fields**

Form data:
```json
{
  "fields": [
    {"field_name": "drug_name", "type": "text", "description": "Name of drug"},
    {"field_name": "dosage", "type": "text", "description": "Dosage amount and frequency"},
    {"field_name": "sample_size", "type": "number", "description": "Number of participants"},
    {"field_name": "age_mean", "type": "number", "description": "Mean age of participants"},
    {"field_name": "intervention_type", "type": "enum", "options": ["Drug", "Surgery"], "description": "Type of intervention"},
    {"field_name": "was_randomized", "type": "boolean", "description": "Was the study randomized"}
  ]
}
```

Your output:
```json
{
  "signatures": [
    {
      "name": "ExtractTextualFields",
      "field_names": ["drug_name", "dosage"],
      "depends_on": []
    },
    {
      "name": "ExtractNumericFields",
      "field_names": ["sample_size", "age_mean"],
      "depends_on": []
    },
    {
      "name": "ClassifyEnumFields",
      "field_names": ["intervention_type"],
      "depends_on": []
    },
    {
      "name": "DetermineBooleanFields",
      "field_names": ["was_randomized"],
      "depends_on": []
    }
  ]
}
```

**Example 2: Form with aggregation field**

Form data:
```json
{
  "fields": [
    {"field_name": "drug_name", "type": "text", "description": "Name of drug"},
    {"field_name": "duration", "type": "text", "description": "Treatment duration"},
    {"field_name": "sample_size", "type": "number", "description": "Number of participants"},
    {"field_name": "intervention_type", "type": "enum", "options": ["Drug", "Surgery"], "description": "Type of intervention"},
    {"field_name": "clinical_summary", "type": "text", "description": "Comprehensive summary combining drug name, duration, intervention type, and sample size"}
  ]
}
```

Your output:
```json
{
  "signatures": [
    {
      "name": "ExtractTextualFields",
      "field_names": ["drug_name", "duration"],
      "depends_on": []
    },
    {
      "name": "ExtractNumericFields",
      "field_names": ["sample_size"],
      "depends_on": []
    },
    {
      "name": "ClassifyEnumFields",
      "field_names": ["intervention_type"],
      "depends_on": []
    },
    {
      "name": "AggregateClinicalSummary",
      "field_names": ["clinical_summary"],
      "depends_on": ["drug_name", "duration", "intervention_type", "sample_size"]
    }
  ]
}
```

**Example 3: Complex form with multiple aggregations**

Form data:
```json
{
  "fields": [
    {"field_name": "drug_name", "type": "text"},
    {"field_name": "adverse_event_count", "type": "number"},
    {"field_name": "severity", "type": "enum", "options": ["Mild", "Moderate", "Severe"]},
    {"field_name": "safety_summary", "type": "text", "description": "Summary of adverse events and severity"},
    {"field_name": "efficacy_score", "type": "number"},
    {"field_name": "overall_assessment", "type": "text", "description": "Overall assessment combining safety and efficacy"}
  ]
}
```

Your output:
```json
{
  "signatures": [
    {
      "name": "ExtractTextualFields",
      "field_names": ["drug_name"],
      "depends_on": []
    },
    {
      "name": "ExtractNumericFields",
      "field_names": ["adverse_event_count", "efficacy_score"],
      "depends_on": []
    },
    {
      "name": "ClassifyEnumFields",
      "field_names": ["severity"],
      "depends_on": []
    },
    {
      "name": "AggregateSafetySummary",
      "field_names": ["safety_summary"],
      "depends_on": ["adverse_event_count", "severity"]
    },
    {
      "name": "AggregateOverallAssessment",
      "field_names": ["overall_assessment"],
      "depends_on": ["safety_summary", "efficacy_score", "drug_name"]
    }
  ]
}
```

═══════════════════════════════════════════════════════════════════════════════
CRITICAL REQUIREMENTS ⚠️
═══════════════════════════════════════════════════════════════════════════════

1. ✅ "signatures" array MUST NOT be empty - at least 1 signature required

2. ✅ Every field from form_data["fields"] MUST appear in exactly ONE signature's field_names

3. ✅ Fields with same cognitive behavior MUST be grouped into the SAME signature

4. ✅ Use descriptive signature names following the naming conventions

5. ✅ "depends_on" lists FIELD NAMES (not signature names)
   - Empty [] for independent signatures
   - Field names for dependent signatures

6. ✅ All field names in "depends_on" must be outputs of other signatures

7. ✅ No circular dependencies allowed (A depends on B, B depends on A)

8. ✅ Minimize total number of signatures through aggressive grouping

═══════════════════════════════════════════════════════════════════════════════
COMMON MISTAKES TO AVOID
═══════════════════════════════════════════════════════════════════════════════

❌ Creating separate signatures for fields with same cognitive behavior
   Wrong: "ExtractDrugName", "ExtractDuration" (separate signatures)
   Right: "ExtractTextualFields" with ["drug_name", "duration"] (one signature)

❌ Using generic signature names
   Wrong: "Extractor1", "ProcessData", "Handler"
   Right: "ExtractTextualFields", "ClassifyEnumFields"

❌ Listing signature names in depends_on
   Wrong: "depends_on": ["ExtractTextualFields"]
   Right: "depends_on": ["drug_name", "duration"]

❌ Missing fields from form_data
   Every field must appear in exactly one signature

❌ Duplicate fields across signatures
   Each field should appear in only one signature's field_names

❌ Empty field_names array
   Each signature must have at least one field

═══════════════════════════════════════════════════════════════════════════════
NOW ANALYZE THE FORM AND CREATE SIGNATURES
═══════════════════════════════════════════════════════════════════════════════

Follow the step-by-step process:
1. Inventory all fields from form_data
2. Classify each field's cognitive behavior
3. Group aggressively by behavior (minimize signatures)
4. Name signatures descriptively
5. Identify dependencies for aggregation fields
6. Verify every field is covered exactly once

Output the JSON with the structure specified above.