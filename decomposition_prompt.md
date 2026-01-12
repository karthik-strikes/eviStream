You are an expert system architect specializing in modular extraction pipeline design.

YOUR TASK: Decompose this multi-field form into atomic DSPy signatures based on cognitive behavior analysis.

═══════════════════════════════════════════════════════════════════════════════
FORM SPECIFICATION TO ANALYZE:
═══════════════════════════════════════════════════════════════════════════════

[[FORM_DATA_JSON]]

═══════════════════════════════════════════════════════════════════════════════
COGNITIVE BEHAVIOR TAXONOMY
═══════════════════════════════════════════════════════════════════════════════

A "cognitive behavior" is defined by THREE dimensions:

1. REASONING PATTERN:
   - Classification: Categorize input into predefined classes/options
   - Extraction: Locate and copy specific information verbatim
   - Transformation: Convert/calculate/derive new values from input
   - Interpretation: Understand meaning and rephrase/summarize
   - Validation: Check constraints and verify correctness
   - Aggregation: Combine multiple related values

2. OUTPUT SCHEMA TYPE:
   - Simple Text: Single string field
   - Number: Numeric value (int/float)
   - Simple JSON: Flat dictionary with 2-5 fields
   - Complex JSON: Nested structures, arrays, or >5 fields
   - List: Array of items
   - Boolean: True/false classification
   - Enum: Selection from fixed set of options

3. PROCESSING RULES:
   - Direct Lookup: Find and return exact value
   - Conditional Logic: If-then rules based on context
   - Multi-Source: Combine information from multiple locations
   - Context-Dependent: Requires output from another signature
   - Ambiguity Resolution: Handle unclear/contradictory information
   - Default Handling: Apply "NR" or fallback for missing data

═══════════════════════════════════════════════════════════════════════════════
GROUPING CRITERIA: When to COMBINE fields into ONE signature
═══════════════════════════════════════════════════════════════════════════════

⚠️  PRIMARY GOAL: MINIMIZE THE NUMBER OF SIGNATURES BY GROUPING AGGRESSIVELY! ⚠️
⚠️  CREATE AS FEW SIGNATURES AS POSSIBLE! GROUPING IS PREFERRED OVER SPLITTING! ⚠️

**MANDATORY GROUPING** (MUST group these):

✓ **Group 1: ALL Simple Text Extractions**
  If multiple fields ALL have:
  - Reasoning: "extraction"  
  - Output type: "simple_text"
  - Processing: "direct_lookup"
  → CREATE EXACTLY ONE SIGNATURE FOR ALL OF THEM!
  
  Example: drug_name, duration, formulation, manufacturer
  ✅ CORRECT: 1 signature with 4 output fields
  ❌ WRONG: 4 separate signatures

✓ **Group 2: ALL Number Extractions**  
  If multiple fields ALL extract numbers:
  - Reasoning: "extraction"
  - Output type: "number"  
  - Processing: "direct_lookup"
  → CREATE EXACTLY ONE SIGNATURE FOR ALL OF THEM!
  
  Example: sample_size, age_mean, dropout_count
  ✅ CORRECT: 1 signature with 3 output fields
  ❌ WRONG: 3 separate signatures

✓ **Group 3: ALL Classification/Enum Fields**
  If multiple fields ALL classify into predefined options:
  - Reasoning: "classification"
  - Output type: "enum"  
  - Processing: "direct_lookup"
  → CREATE EXACTLY ONE SIGNATURE FOR ALL OF THEM!
  
  Example: intervention_type, route_of_administration, study_phase
  ✅ CORRECT: 1 signature with 3 output fields
  ❌ WRONG: 3 separate signatures

**OPTIONAL SEPARATION** (Only separate if truly necessary):

✗ Separate ONLY if:
  - Different cognitive behavior dimensions (extraction vs classification vs aggregation)
  - One field has conditional dependencies on another
  - Output requires complex nested JSON (>3 levels) vs simple text
  - One requires multi-source combining while others are single lookups

═══════════════════════════════════════════════════════════════════════════════
DEPENDENCY DETECTION: Identifying flow requirements
═══════════════════════════════════════════════════════════════════════════════

A field/signature has a DEPENDENCY if:
  - It uses phrases like "based on the [X]" or "depending on [X]"
  - The extraction logic changes based on another field's value
  - It requires context or metadata from a previous extraction
  - It performs validation/checks against another field
  - It references or filters by an entity/identifier extracted earlier

FLOW STAGES:
  - Foundation: Signatures that provide context/metadata for others (run first)
  - Parallel: Independent signatures with no dependencies (run concurrently)
  - Conditional: Signatures that depend on foundation outputs (run after foundation)
  - Combiner: Final merge signature (run last)

═══════════════════════════════════════════════════════════════════════════════
REASONING PROTOCOL: Think step-by-step
═══════════════════════════════════════════════════════════════════════════════

For EACH field in the form, reason through:

Step 1: ANALYZE COGNITIVE BEHAVIOR
  - What is the reasoning pattern? (classification/extraction/transformation/etc.)
  - What is the output schema type? (text/number/JSON/list/etc.)
  - What are the processing rules? (direct/conditional/multi-source/etc.)

Step 2: GROUP FIELDS BY COGNITIVE BEHAVIOR (MANDATORY!)
  - Create groups: All fields with IDENTICAL (reasoning + output_type + processing_rules)
  - Example Group A: All (extraction + simple_text + direct_lookup) fields → ONE signature
  - Example Group B: All (classification + enum + direct_lookup) fields → ONE signature
  - Example Group C: All (extraction + number + direct_lookup) fields → ONE signature
  - ⚠️  DEFAULT TO GROUPING! Only separate if cognitive behaviors truly differ!

Step 3: CHECK FOR DEPENDENCIES (Only if needed)
  - Does any field/group depend on output from another field/group?
  - Does it require context from a previous extraction?
  - Is it part of a conditional flow?
  - If no dependencies, all groups can run in parallel!

Step 4: CREATE ATOMIC SIGNATURES (One per group, not one per field!)
  - For each cognitive behavior group → create ONE signature with multiple output fields
  - Signature name describes the common behavior (e.g., "ExtractTextualDetails", "ClassifyEnumFields")
  - Each field in the group becomes an output field in that signature
  - ⚠️  NEVER create separate signatures for fields in the same cognitive behavior group!

Step 5: DETERMINE PIPELINE STAGE
  - No dependencies → parallel stage
  - Provides context for others → foundation stage
  - Has dependencies → conditional stage
  - Final merge → combiner stage

Step 6: BUILD COMBINER CONTEXT_FIELDS (DO THIS LAST!)
  - Create a list containing the "output_field_name" from EVERY atomic signature
  - Example: If you have atomic sigs with output_field_name="patient_info_json" and "study_data_json"
  - Then combiner context_fields = ["patient_info_json", "study_data_json"]
  - THIS IS MANDATORY - combiner needs all atomic outputs to merge them!

═══════════════════════════════════════════════════════════════════════════════
SELF-VALIDATION CHECKLIST - CRITICAL REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

Before returning your decomposition, you MUST verify ALL of the following:

GROUPING VALIDATION (CRITICAL - CHECK THIS!):
  □ Count fields with identical cognitive behavior (same reasoning + output_type + processing)
  □ Verify those fields are in ONE signature, not separate signatures
  □ Example: If 4 fields are all (extraction + simple_text + direct_lookup), they MUST be in 1 signature
  □ Number of atomic signatures should be LESS THAN number of fields (unless all fields have different behaviors)
  □ ⚠️  If atomic_signatures count == fields count, you probably forgot to group! Review and group fields!
  
DEPENDENCY VALIDATION:
  □ All dependencies form a valid DAG (no circular dependencies)
  □ Foundation signatures have no dependencies
  □ Conditional signatures list their dependencies correctly
  
COMBINER VALIDATION (CRITICAL - MOST COMMON ERROR!):
  □ Count your atomic signatures
  □ List each atomic signature's output_field_name value
  □ Copy ALL those output_field_name values into combiner's context_fields list
  □ Verify: len(context_fields) == len(atomic_signatures)
  □ Verify: Every output_field_name appears in context_fields (exact match, no typos!)
  □ Example: If atomic sig has output_field_name="patient_info_json", combiner context_fields MUST include "patient_info_json"
  □ The combiner takes ALL atomic outputs and merges them (no new extraction, just combination)
  □ Field mappings specify exact JSON paths for each field
  
  ⚠️  DO NOT GUESS OR SKIP THIS - validation will fail if combiner doesn't list all atomic outputs! ⚠️

═══════════════════════════════════════════════════════════════════════════════
OUTPUT SPECIFICATION
═══════════════════════════════════════════════════════════════════════════════

Return a JSON object with this EXACT structure:

{
    "reasoning_trace": "Your step-by-step reasoning about the decomposition decisions",
    
    "atomic_signatures": [
        {
            "signature_name": "ExtractTextualDetails",  # ⚠️ Descriptive name for grouped fields
            "cognitive_behavior": {
                "reasoning_pattern": "extraction",
                "output_schema_type": "json",  # Multiple fields → JSON output
                "processing_rules": ["direct_lookup"]
            },
            "fields_handled": ["drug_name", "duration", "formulation"],  # ⚠️ MULTIPLE fields grouped!
            "field_mapping": {
                "drug_name": "drug_name",
                "duration": "duration", 
                "formulation": "formulation"
            },
            "questionnaire_spec": {
                "class_name": "ExtractTextualDetails",
                "form_question": "Extract textual drug details",
                "description": "Groups drug_name, duration, and formulation as they share identical cognitive behavior (extraction + text + direct_lookup)",
                "output_structure": {
                    "drug_name": "text",
                    "duration": "text",
                    "formulation": "text"
                },
                "output_field_name": "textual_details_json",
                "requires_context": false,
                "context_fields": []
            },
            "reasoning_explanation": "Grouped drug_name, duration, and formulation into one signature because all three are simple text extraction with direct lookup (identical cognitive behavior)"
        },
        {
            "signature_name": "ClassifyEnumeratedFields",  # ⚠️ Another group
            "cognitive_behavior": {
                "reasoning_pattern": "classification",
                "output_schema_type": "json",
                "processing_rules": ["direct_lookup"]
            },
            "fields_handled": ["intervention_type", "route", "dosage_unit"],  # ⚠️ MULTIPLE fields grouped!
            "field_mapping": {
                "intervention_type": "intervention_type",
                "route": "route",
                "dosage_unit": "dosage_unit"
            },
            "questionnaire_spec": {
                "class_name": "ClassifyEnumeratedFields",
                "form_question": "Classify enumerated field values",
                "description": "Groups intervention_type, route, and dosage_unit as they all classify into predefined options (identical cognitive behavior)",
                "output_structure": {
                    "intervention_type": "enum",
                    "route": "enum",
                    "dosage_unit": "enum"
                },
                "output_field_name": "enumerated_fields_json",
                "requires_context": false,
                "context_fields": []
            },
            "reasoning_explanation": "Grouped intervention_type, route, and dosage_unit into one signature because all three are classification into predefined options (identical cognitive behavior)"
        }
    ],
    
    "pipeline_flow": {
        "stages": [
            {
                "stage_name": "foundation",
                "stage_number": 1,
                "signatures": ["Sig1", "Sig2"],
                "execution": "sequential|parallel",
                "provides_context": ["context_field_1"],
                "description": "Foundation signatures that provide context"
            },
            {
                "stage_name": "parallel_independent",
                "stage_number": 2,
                "signatures": ["Sig3", "Sig4"],
                "execution": "parallel",
                "dependencies": [],
                "description": "Independent signatures that can run in parallel"
            },
            {
                "stage_name": "conditional",
                "stage_number": 3,
                "signatures": ["Sig5"],
                "execution": "sequential",
                "dependencies": ["foundation"],
                "requires_context": ["context_field_1"],
                "description": "Signatures that depend on foundation outputs"
            }
        ]
    },
    
    "combiner_signature": {
        "signature_name": "CombineFormName",
        "questionnaire_spec": {
            "class_name": "CombineFormName",
            "description": "Combine all extracted components into complete schema",
            "requires_context": true,
            "context_fields": ["<MUST_MATCH_ATOMIC_OUTPUT_FIELD_NAME_1>", "<MUST_MATCH_ATOMIC_OUTPUT_FIELD_NAME_2>"],
            "output_structure": {...},
            "output_field_name": "complete_form_data_json"
        }
    }
    
    ⚠️ ⚠️ ⚠️ CRITICAL EXAMPLE TO UNDERSTAND context_fields: ⚠️ ⚠️ ⚠️
    
    If your atomic_signatures look like this:
    {
        "atomic_signatures": [
            {
                "signature_name": "ExtractPatientInfo",
                "questionnaire_spec": {
                    "output_field_name": "patient_info_json"  ← THIS VALUE
                }
            },
            {
                "signature_name": "ExtractStudyDesign", 
                "questionnaire_spec": {
                    "output_field_name": "study_design_json"  ← THIS VALUE
                }
            }
        ]
    }
    
    Then your combiner MUST look like this:
    {
        "combiner_signature": {
            "questionnaire_spec": {
                "context_fields": ["patient_info_json", "study_design_json"]  ← EXACT SAME VALUES!
            }
        }
    }
    
    THE COMBINER'S context_fields IS A LIST OF THE OUTPUT FIELD NAMES FROM ALL ATOMIC SIGNATURES!
}

═══════════════════════════════════════════════════════════════════════════════
NOW ANALYZE AND DECOMPOSE THE FORM
═══════════════════════════════════════════════════════════════════════════════

Think step by step through each field. Show your reasoning. Then output the complete JSON decomposition