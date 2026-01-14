# Nested Subforms Implementation Guide (Scenario 2)

## Overview
Implement deeply nested subforms to support hierarchical data extraction like:
- Outcome → Intervention → Timepoint → Value
- Study → Arm → Patient → Measurement

## Architecture Changes

### 1. Schema Layer Enhancement

#### File: `core/form_schema_builder.py`

**Current limitation:** Only supports one level of subforms
**Enhancement needed:** Support recursive nesting

```python
def build_field_definition(
    name: str,
    data_type: str,
    control_type: str,
    description: str,
    options: Optional[List[str]] = None,
    example: Optional[str] = None,
    extraction_hints: Optional[str] = None,
    subform_fields: Optional[List[Dict[str, Any]]] = None,
    max_nesting_level: int = 3,  # NEW: Limit depth to prevent infinite nesting
) -> Dict[str, Any]:
    """
    Build field definition with support for nested subforms.
    
    Args:
        max_nesting_level: Maximum allowed nesting depth (default 3)
                          Level 1: outcomes
                          Level 2: interventions (within outcomes)
                          Level 3: timepoints (within interventions)
    """
    field: Dict[str, Any] = {
        "field_name": name.strip(),
        "field_type": data_type,
        "field_control_type": control_type,
        "field_description": description.strip(),
    }
    
    if options:
        field["options"] = options
    if example:
        field["example"] = example.strip()
    if extraction_hints:
        field["extraction_hints"] = extraction_hints.strip()
    
    # NEW: Validate and process nested subforms
    if subform_fields:
        validated_subfields = _validate_nested_subforms(
            subform_fields, 
            current_level=1, 
            max_level=max_nesting_level
        )
        field["subform_fields"] = validated_subfields
        
    return field


def _validate_nested_subforms(
    subfields: List[Dict[str, Any]], 
    current_level: int, 
    max_level: int
) -> List[Dict[str, Any]]:
    """
    Recursively validate nested subform structure.
    
    Ensures:
    - Maximum nesting depth not exceeded
    - Each level has valid field definitions
    - Circular references prevented
    """
    if current_level > max_level:
        raise ValueError(
            f"Subform nesting exceeds maximum depth of {max_level}. "
            f"Current level: {current_level}"
        )
    
    validated = []
    for subfield in subfields:
        # Check if this subfield is itself a subform
        if subfield.get("field_type") == "array" and subfield.get("subform_fields"):
            # Recursively validate nested subforms
            subfield["subform_fields"] = _validate_nested_subforms(
                subfield["subform_fields"],
                current_level + 1,
                max_level
            )
        validated.append(subfield)
    
    return validated
```

---

### 2. UI Layer Enhancement

#### File: `app/views/forms_tab.py`

**Current:** Single-level subfield builder
**Enhancement:** Recursive nested subfield builder

**Key UI Changes:**

1. **Nesting Level Indicator**
```python
def render_subfield_builder(field_name: str, nesting_level: int = 1, parent_path: str = ""):
    """
    Render subfield builder with nesting level indicator.
    
    Args:
        field_name: Name of the parent field
        nesting_level: Current nesting depth (1, 2, 3)
        parent_path: Path to parent (e.g., "outcomes.interventions")
    """
    # Visual nesting indicator
    indent = "  " * (nesting_level - 1)
    level_color = ["#3b82f6", "#10b981", "#f59e0b"][nesting_level - 1]
    
    st.markdown(f"""
    <div style="border-left: 3px solid {level_color}; padding-left: 1rem; margin-left: {nesting_level * 10}px;">
        <span style="color: {level_color}; font-weight: bold;">
            Level {nesting_level} Subfields
        </span>
    </div>
    """, unsafe_allow_html=True)
```

2. **Nested Subfield Creation**
```python
# When adding a subfield, check if it should be a nested subform
subfield_type = st.selectbox(
    "Data Type",
    options=["text", "number", "enum", "nested_subform"],  # NEW option
    key=f"subfield_type_{parent_path}_{nesting_level}"
)

if subfield_type == "nested_subform":
    if nesting_level >= 3:
        st.error("Maximum nesting level (3) reached. Cannot add more nested subforms.")
    else:
        st.info("This will create another repeating table inside this subform.")
        # Show nested builder
        render_subfield_builder(
            field_name=subfield_name,
            nesting_level=nesting_level + 1,
            parent_path=f"{parent_path}.{subfield_name}"
        )
```

3. **Visual Preview of Nested Structure**
```python
def render_nested_subform_preview(subform_structure: Dict):
    """Show tree-view of nested structure"""
    st.markdown("**Preview: Nested Structure**")
    
    def render_tree(fields, indent=0):
        for field in fields:
            prefix = "  " * indent + ("└─ " if indent > 0 else "")
            icon = "📊" if field.get("field_type") == "array" else "📝"
            
            st.markdown(f"{prefix}{icon} **{field['field_name']}** ({field['field_type']})")
            
            if field.get("subform_fields"):
                render_tree(field["subform_fields"], indent + 1)
    
    render_tree([subform_structure])
```

---

### 3. Decomposition Updates

#### File: `core/generators/prompts/decompose_form.md`

**Add section on nested subforms:**

```markdown
═══════════════════════════════════════════════════════════════════════════════
HANDLING NESTED SUBFORMS (HIERARCHICAL DATA)
═══════════════════════════════════════════════════════════════════════════════

Some subforms contain OTHER subforms - creating hierarchical relationships.

**Example: Outcome → Intervention → Timepoint**

Form structure:
{
  "field_name": "outcomes",
  "field_type": "array",
  "subform_fields": [
    {"field_name": "outcome_name", "field_type": "text"},
    {
      "field_name": "intervention_results",
      "field_type": "array",
      "subform_fields": [
        {"field_name": "intervention_name", "field_type": "text"},
        {
          "field_name": "measurements",
          "field_type": "array",
          "subform_fields": [
            {"field_name": "timepoint", "field_type": "text"},
            {"field_name": "value", "field_type": "number"}
          ]
        }
      ]
    }
  ]
}

**Decomposition approach:**

The parent subform becomes the signature name, and nesting is handled in extraction:

{
  "name": "ExtractOutcomesWithInterventionsAndTimepoints",
  "field_names": ["outcomes"],
  "depends_on": []
}

The signature will extract the ENTIRE nested structure at once.

**Rationale:**
- Nested subforms represent tightly coupled hierarchical data
- Extracting them together maintains relationships
- Alternative: Could split into dependent signatures if extraction is complex

**Alternative decomposition (if extraction is very complex):**

{
  "signatures": [
    {
      "name": "IdentifyOutcomesAndInterventions",
      "field_names": ["outcomes"],  // Extract without timepoints first
      "depends_on": []
    },
    {
      "name": "ExtractTimepointMeasurements",
      "field_names": ["timepoint_measurements"],  // Then add timepoint data
      "depends_on": ["outcomes"]
    }
  ]
}

Use this approach only if nested extraction is too complex for single pass.
```

---

### 4. Signature Generation for Nested Types

#### File: `core/generators/signature_gen.py`

**Enhancement:** Generate nested List[Dict] types

```python
def _generate_field_type_from_metadata(field_metadata: Dict) -> str:
    """
    Generate Python type hint from field metadata.
    
    Handles nested subforms by generating nested List types.
    """
    field_type = field_metadata.get("field_type")
    control_type = field_metadata.get("field_control_type")
    
    # Check for subform
    if field_type == "array" and control_type == "subform_table":
        subform_fields = field_metadata.get("subform_fields", [])
        
        # Check if any subfields are also subforms (nested)
        has_nested_subforms = any(
            sf.get("field_type") == "array" and sf.get("subform_fields")
            for sf in subform_fields
        )
        
        if has_nested_subforms:
            # Generate nested type description in docstring
            # Actual type is still List[Dict[str, Any]] but with detailed description
            return "List[Dict[str, Any]]"
        else:
            return "List[Dict[str, Any]]"
    
    # Regular field types
    elif field_type == "text":
        return "str"
    elif field_type == "number":
        return "float"
    # ... etc
```

**Enhanced field description for nested subforms:**

```python
def _generate_field_description_for_nested_subform(field_metadata: Dict) -> str:
    """
    Generate detailed description for nested subform fields.
    
    Example output:
    "Array of outcomes. Each outcome contains:
    - outcome_name (str): Name of the outcome
    - intervention_results (array): Nested array of interventions, each containing:
      - intervention_name (str): Name of intervention
      - measurements (array): Nested array of timepoints, each containing:
        - timepoint (str): Time label
        - value (float): Measurement value
    
    Example:
    [
      {
        'outcome_name': 'Pain Reduction',
        'intervention_results': [
          {
            'intervention_name': 'Drug A',
            'measurements': [
              {'timepoint': 'Baseline', 'value': 7.2},
              {'timepoint': 'Week 4', 'value': 4.5}
            ]
          }
        ]
      }
    ]"
    """
    def describe_subfields(subfields, indent=0):
        desc = ""
        for sf in subfields:
            indent_str = "  " * indent
            sf_name = sf["field_name"]
            sf_type = sf["field_type"]
            sf_desc = sf.get("field_description", "")
            
            if sf_type == "array" and sf.get("subform_fields"):
                desc += f"{indent_str}- {sf_name} (array): Nested array, each containing:\n"
                desc += describe_subfields(sf["subform_fields"], indent + 1)
            else:
                type_hint = _get_python_type(sf_type)
                desc += f"{indent_str}- {sf_name} ({type_hint}): {sf_desc}\n"
        
        return desc
    
    base_desc = field_metadata.get("field_description", "")
    subfields_desc = describe_subfields(field_metadata.get("subform_fields", []))
    
    return f"{base_desc}\n\nStructure:\n{subfields_desc}"
```

---

### 5. Module Generation for Nested Extraction

#### File: `core/generators/module_gen.py`

**Challenge:** Generate code that extracts nested structures

**Approach 1: Single-pass extraction (Let LLM handle nesting)**

```python
class ExtractOutcomesWithNesting(dspy.Module):
    def __init__(self):
        super().__init__()
        self.extract = dspy.ChainOfThought(ExtractNestedOutcomesSignature)
    
    def forward(self, context):
        # Single call extracts entire nested structure
        result = self.extract(context=context)
        
        # Validate nested structure
        outcomes = json.loads(result.outcomes)
        
        # Validate each level
        for outcome in outcomes:
            assert "outcome_name" in outcome
            assert "intervention_results" in outcome
            assert isinstance(outcome["intervention_results"], list)
            
            for intervention in outcome["intervention_results"]:
                assert "intervention_name" in intervention
                assert "measurements" in intervention
                assert isinstance(intervention["measurements"], list)
        
        return dspy.Prediction(outcomes=outcomes)
```

**Approach 2: Multi-stage extraction (Safer, more reliable)**

```python
class ExtractNestedOutcomes(dspy.Module):
    def __init__(self):
        super().__init__()
        self.extract_outcomes = dspy.ChainOfThought(ExtractOutcomeNamesSignature)
        self.extract_interventions = dspy.ChainOfThought(ExtractInterventionsForOutcomeSignature)
        self.extract_measurements = dspy.ChainOfThought(ExtractMeasurementsSignature)
    
    def forward(self, context):
        # Stage 1: Find all outcomes
        outcomes_result = self.extract_outcomes(context=context)
        outcome_names = json.loads(outcomes_result.outcome_names)
        
        outcomes = []
        
        # Stage 2: For each outcome, find interventions
        for outcome_name in outcome_names:
            outcome_context = f"For outcome '{outcome_name}', " + context
            interventions_result = self.extract_interventions(context=outcome_context)
            intervention_names = json.loads(interventions_result.intervention_names)
            
            interventions = []
            
            # Stage 3: For each intervention, find measurements
            for intervention_name in intervention_names:
                measurement_context = f"For outcome '{outcome_name}' and intervention '{intervention_name}', " + context
                measurements_result = self.extract_measurements(context=measurement_context)
                measurements = json.loads(measurements_result.measurements)
                
                interventions.append({
                    "intervention_name": intervention_name,
                    "measurements": measurements
                })
            
            outcomes.append({
                "outcome_name": outcome_name,
                "intervention_results": interventions
            })
        
        return dspy.Prediction(outcomes=outcomes)
```

---

### 6. Example: Complete Nested Form Definition

```json
{
  "form_name": "Clinical Trial Hierarchical Extraction",
  "form_description": "Extract outcomes with nested intervention results and timepoint measurements",
  "fields": [
    {
      "field_name": "study_title",
      "field_type": "text",
      "field_description": "Title of the study"
    },
    {
      "field_name": "outcomes",
      "field_type": "array",
      "field_control_type": "subform_table",
      "field_description": "Extract ALL outcomes measured. For each outcome, extract all interventions tested and their measurements at each timepoint.",
      "extraction_hints": "Look in results section for outcome tables. Each outcome will have intervention groups with measurements over time.",
      "subform_fields": [
        {
          "field_name": "outcome_name",
          "field_type": "text",
          "field_description": "Name of the outcome measure (e.g., 'Pain Reduction', 'Adverse Events')"
        },
        {
          "field_name": "outcome_type",
          "field_type": "enum",
          "field_description": "Type of outcome",
          "options": ["Primary", "Secondary", "Exploratory"]
        },
        {
          "field_name": "intervention_results",
          "field_type": "array",
          "field_control_type": "subform_table",
          "field_description": "Results for each intervention group tested for this outcome",
          "subform_fields": [
            {
              "field_name": "intervention_name",
              "field_type": "text",
              "field_description": "Name of the intervention group"
            },
            {
              "field_name": "group_size",
              "field_type": "number",
              "field_description": "Number of participants in this group"
            },
            {
              "field_name": "timepoint_measurements",
              "field_type": "array",
              "field_control_type": "subform_table",
              "field_description": "Measurements at each timepoint for this intervention and outcome",
              "subform_fields": [
                {
                  "field_name": "timepoint",
                  "field_type": "text",
                  "field_description": "Time label (e.g., 'Baseline', 'Week 4', 'Month 6')"
                },
                {
                  "field_name": "mean_value",
                  "field_type": "number",
                  "field_description": "Mean measurement value"
                },
                {
                  "field_name": "sd_value",
                  "field_type": "number",
                  "field_description": "Standard deviation"
                },
                {
                  "field_name": "n_measured",
                  "field_type": "number",
                  "field_description": "Number of participants measured at this timepoint"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

**Expected Output:**
```json
{
  "study_title": "RCT of Drug A vs Drug B for Pain Management",
  "outcomes": [
    {
      "outcome_name": "Pain Reduction (VAS)",
      "outcome_type": "Primary",
      "intervention_results": [
        {
          "intervention_name": "Drug A 10mg",
          "group_size": 50,
          "timepoint_measurements": [
            {"timepoint": "Baseline", "mean_value": 7.2, "sd_value": 1.1, "n_measured": 50},
            {"timepoint": "Week 4", "mean_value": 4.5, "sd_value": 1.3, "n_measured": 48},
            {"timepoint": "Week 8", "mean_value": 3.1, "sd_value": 1.2, "n_measured": 47},
            {"timepoint": "Week 12", "mean_value": 2.8, "sd_value": 1.0, "n_measured": 45}
          ]
        },
        {
          "intervention_name": "Drug B 20mg",
          "group_size": 52,
          "timepoint_measurements": [
            {"timepoint": "Baseline", "mean_value": 7.1, "sd_value": 1.2, "n_measured": 52},
            {"timepoint": "Week 4", "mean_value": 5.0, "sd_value": 1.4, "n_measured": 50},
            {"timepoint": "Week 8", "mean_value": 4.2, "sd_value": 1.3, "n_measured": 49},
            {"timepoint": "Week 12", "mean_value": 3.9, "sd_value": 1.1, "n_measured": 48}
          ]
        },
        {
          "intervention_name": "Placebo",
          "group_size": 51,
          "timepoint_measurements": [
            {"timepoint": "Baseline", "mean_value": 7.0, "sd_value": 1.0, "n_measured": 51},
            {"timepoint": "Week 4", "mean_value": 6.5, "sd_value": 1.1, "n_measured": 49},
            {"timepoint": "Week 8", "mean_value": 6.2, "sd_value": 1.2, "n_measured": 48},
            {"timepoint": "Week 12", "mean_value": 6.0, "sd_value": 1.0, "n_measured": 47}
          ]
        }
      ]
    },
    {
      "outcome_name": "Adverse Events",
      "outcome_type": "Secondary",
      "intervention_results": [
        // ... similar structure
      ]
    }
  ]
}
```

---

## Implementation Checklist

### Phase 1: Foundation (Do First)
- [ ] Update `build_field_definition()` to validate nested subforms
- [ ] Add `_validate_nested_subforms()` helper function
- [ ] Add max nesting level validation (recommend limit of 3)
- [ ] Test schema builder with nested structure

### Phase 2: UI Enhancement
- [ ] Add nesting level indicator to subfield builder
- [ ] Add "nested_subform" as subfield type option
- [ ] Implement recursive subfield builder UI
- [ ] Add visual tree preview of nested structure
- [ ] Add validation preventing excessive nesting
- [ ] Test creating 3-level nested form in UI

### Phase 3: Decomposition
- [ ] Update `decompose_form.md` with nested subform examples
- [ ] Test decomposition with nested structures
- [ ] Verify single signature created for nested subforms

### Phase 4: Signature Generation
- [ ] Enhance type generation for nested structures
- [ ] Generate detailed nested descriptions
- [ ] Add examples showing nested JSON structure
- [ ] Test generated signatures

### Phase 5: Module Generation
- [ ] Implement multi-stage extraction approach (recommended)
- [ ] Add validation for each nesting level
- [ ] Test extraction with sample PDFs

### Phase 6: Testing
- [ ] Create test form with 3-level nesting
- [ ] Test extraction from sample PDF
- [ ] Verify output structure matches expected format
- [ ] Performance testing with complex nested data

---

## Recommended Implementation Order

1. **Start simple**: Get 2-level nesting working first
   - Outcome → Intervention (no timepoints yet)
   
2. **Add third level**: Then add timepoints
   - Outcome → Intervention → Timepoint

3. **Optimize extraction**: Use multi-stage approach for reliability

4. **Add UI polish**: Tree preview, validation, helpful messages

---

## Testing Strategy

### Test Case 1: Two-Level Nesting
```json
{
  "outcomes": [
    {
      "outcome_name": "Pain",
      "interventions": [
        {"name": "Drug A", "n": 50},
        {"name": "Placebo", "n": 48}
      ]
    }
  ]
}
```

### Test Case 2: Three-Level Nesting
```json
{
  "outcomes": [
    {
      "outcome_name": "Pain",
      "interventions": [
        {
          "name": "Drug A",
          "measurements": [
            {"timepoint": "Baseline", "value": 7.2},
            {"timepoint": "Week 4", "value": 4.5}
          ]
        }
      ]
    }
  ]
}
```

---

## Next Steps

Would you like me to:
1. **Implement Phase 1** (Schema validation for nested subforms)?
2. **Create example nested form** to test with?
3. **Start with 2-level nesting** first (simpler)?
4. **Show UI mockup** for nested subfield builder?

Choose where to start, and I'll implement it!


