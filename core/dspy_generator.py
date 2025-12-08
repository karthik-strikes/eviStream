"""
Hybrid DSPy Code Generator for eviStream
Combines LLM intelligence for semantic understanding with templates for guaranteed quality
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
import importlib
import sys
import dspy
import utils.lm_config  # Auto-configure DSPy


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def sanitize_form_name(form_name: str) -> str:
    """
    Sanitize form name to create valid Python class names.

    Examples:
        " TrialCharacteristics" -> "TrialCharacteristics"
        "Trial Characteristics" -> "TrialCharacteristics"
        "trial-characteristics" -> "TrialCharacteristics"
    """
    name = form_name.strip()
    name = name.replace('_', ' ').replace('-', ' ')
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    words = name.split()

    sanitized_words = []
    for word in words:
        if word:
            sanitized_words.append(
                word[0].upper() + word[1:] if len(word) > 1 else word.upper())

    sanitized = ''.join(sanitized_words)

    if sanitized and not sanitized[0].isalpha():
        sanitized = 'Form' + sanitized

    if not sanitized:
        sanitized = 'CustomForm'

    return sanitized


def sanitize_field_key(field_name: str) -> str:
    """
    Convert field name to valid Python/JSON key (snake_case).

    Examples:
        "Study Design" -> "study_design"
        "Patient Age (years)" -> "patient_age_years"
        "Female (%)" -> "female_percent"
    """
    name = field_name.lower()
    name = name.replace('(%)', '_percent')
    name = name.replace('(n)', '_n')
    name = name.replace('%', '_percent')
    name = re.sub(r'\([^)]*\)', '', name)
    name = re.sub(r'[^a-z0-9]+', '_', name)
    name = name.strip('_')

    if name and not name[0].isalpha():
        name = 'field_' + name

    return name or 'field'


# ============================================================================
# LLM-POWERED SEMANTIC ANALYSIS (Step 1: Intelligence)
# ============================================================================

class AnalyzeFormSemantics(dspy.Signature):
    """
    Analyze form to extract semantic information for intelligent code generation.

    This signature uses LLM intelligence to understand:
    - Field relationships and dependencies
    - Domain context for each field
    - Extraction complexity levels
    - Semantic groupings
    """

    form_name: str = dspy.InputField(
        desc="Name of the form (e.g., TrialCharacteristics, PatientDemographics)"
    )
    form_description: str = dspy.InputField(
        desc="Description of what this form extracts"
    )
    fields_json: str = dspy.InputField(
        desc="""JSON array of field definitions. Each field has:
        - name: field name
        - type: data type
        - control_type: UI control (text, number, dropdown, checkbox_group_with_text)
        - description: what to extract
        - options: available options (for dropdowns/checkboxes)"""
    )

    semantic_analysis: str = dspy.OutputField(
        desc="""JSON object with comprehensive semantic analysis:
        {
            "field_dependencies": {
                "field_name": ["depends_on_field1", "depends_on_field2"],
                // Map each field to fields it depends on for context
            },
            "domain_contexts": {
                "field_name": "Domain explanation of what this field means and why it matters",
                // Rich context for each field
            },
            "extraction_complexity": {
                "field_name": "simple" | "medium" | "complex",
                // simple: direct lookup (e.g., sample size number)
                // medium: requires interpretation (e.g., study design classification)
                // complex: multi-step reasoning (e.g., calculating derived metrics)
            },
            "semantic_groups": {
                "group_name": ["field1", "field2"],
                // Group related fields (e.g., "demographics": ["age", "gender"])
            },
            "extraction_order": ["field1", "field2", "field3"],
            // Optimal order for extraction based on dependencies
            "special_instructions": {
                "field_name": "Special extraction guidance for this field",
                // Field-specific hints (e.g., "Look in Methods section", "Check tables")
            }
        }
        
        Rules:
        - Identify dependencies by analyzing field descriptions
        - Fields that provide context for others should be extracted first
        - Group semantically related fields together
        - Consider domain knowledge (medical, financial, legal, etc.)
        - Provide actionable extraction hints
        
        Example:
        For a medical form with "index_test_type" and "specimen_collection":
        - specimen_collection DEPENDS ON index_test_type (need to know test type to know if collection applies)
        - index_test_type should be in extraction_order before specimen_collection
        - Both belong to semantic_group "test_methodology"
        """
    )


class GenerateFieldPromptingStrategy(dspy.Signature):
    """
    Generate intelligent prompting strategy for a specific field.

    Uses LLM to create extraction rules, examples, and edge case handling
    tailored to the field's semantics and complexity.
    """

    field_name: str = dspy.InputField(desc="Name of the field")
    field_description: str = dspy.InputField(desc="User-provided description")
    field_type: str = dspy.InputField(desc="Data type (text, number, object)")
    control_type: str = dspy.InputField(desc="UI control type")
    options: str = dspy.InputField(
        desc="JSON array of options (for dropdowns/checkboxes)")
    domain_context: str = dspy.InputField(
        desc="Domain context from semantic analysis")
    complexity: str = dspy.InputField(
        desc="Extraction complexity (simple/medium/complex)")

    prompting_strategy: str = dspy.OutputField(
        desc="""JSON object with intelligent prompting strategy:
        {
            "extraction_rules": [
                "Rule 1: How to identify this data in the document",
                "Rule 2: How to handle ambiguous cases",
                "Rule 3: How to validate extracted data",
                ...
            ],
            "examples": [
                {
                    "scenario": "Common case description",
                    "input": "What the document might say",
                    "output": {"expected": "json", "structure": "here"}
                },
                {
                    "scenario": "Edge case description",
                    "input": "Ambiguous document text",
                    "output": {"expected": "json", "with": "NR"}
                },
                ...
            ],
            "edge_cases": [
                "Edge case 1: Not reported - use NR",
                "Edge case 2: Multiple values - select most specific",
                "Edge case 3: Conflicting information - note in comment",
                ...
            ],
            "document_hints": [
                "Look in Methods section",
                "Check Table 1 for baseline characteristics",
                "Search for keywords: 'sample size', 'enrolled', 'recruited'",
                ...
            ]
        }
        
        Generate 3-5 extraction rules, 3-4 diverse examples, 3-5 edge cases, and 2-4 document hints.
        Tailor to the field's complexity and domain context.
        """
    )


# ============================================================================
# TEMPLATE GENERATORS WITH LLM-INFORMED CONTENT (Step 2: Structure + Intelligence)
# ============================================================================

def generate_json_schema(field: Dict[str, Any]) -> str:
    """Generate JSON schema based on control type (TEMPLATE - guarantees structure)."""
    control_type = field.get('control_type', field['type'])
    field_key = sanitize_field_key(field['name'])

    if control_type == 'text':
        return f'''{{
    "{field_key}": "extracted text value or NR if not reported"
}}'''

    elif control_type == 'number':
        return f'''{{
    "{field_key}": numeric_value_or_"NR"
}}'''

    elif control_type == 'dropdown':
        options = field.get('options', [])
        opts_str = '", "'.join(options) if options else 'option1", "option2'
        return f'''{{
    "{field_key}": "one of: [\\"{opts_str}\\"] or NR"
}}'''

    elif control_type == 'checkbox_group_with_text':
        options = field.get('options', [])
        schema_lines = []
        for opt in options:
            opt_key = sanitize_field_key(opt)
            schema_lines.append(
                f'        "{opt_key}": {{"selected": true/false, "value": "extracted_value"}}')

        schema = "{\n" + ",\n".join(schema_lines) + "\n    }"
        return schema

    return f'{{"{field_key}": "value"}}'


def generate_signature_class_with_intelligence(
    field: Dict[str, Any],
    form_name: str,
    form_description: str,
    semantic_analysis: Dict[str, Any],
    prompting_strategy: Dict[str, Any]
) -> str:
    """
    Generate signature class combining TEMPLATE structure with LLM intelligence.

    Template guarantees: Pattern compliance, structure, safety
    LLM provides: Domain context, extraction rules, examples, edge cases
    """
    sanitized_form = sanitize_form_name(form_name)
    # Use the same sanitizer we use for form names so class names are always valid
    field_name_pascal = sanitize_form_name(field["name"])
    class_name = f"Extract{field_name_pascal}"

    field_key = sanitize_field_key(field['name'])
    control_type = field.get('control_type', field['type'])

    # Get LLM-generated intelligence
    domain_context = semantic_analysis['domain_contexts'].get(
        field['name'], '')
    complexity = semantic_analysis['extraction_complexity'].get(
        field['name'], 'medium')
    special_instructions = semantic_analysis['special_instructions'].get(
        field['name'], '')

    extraction_rules = prompting_strategy.get('extraction_rules', [])
    examples = prompting_strategy.get('examples', [])
    edge_cases = prompting_strategy.get('edge_cases', [])
    document_hints = prompting_strategy.get('document_hints', [])

    # PATTERN 1: Rich three-layer documentation (Template + LLM)
    layer_1_purpose = f"Extract {field['name']} from the document."

    layer_2_form_context = f"""Form Context:
    - Field: "{field['name']}"
    - Control Type: {control_type}
    - Complexity: {complexity}
    - Part of: {form_name} form
    - Description: {field.get('description', 'No description provided')}"""

    if control_type == 'checkbox_group_with_text':
        options_str = ', '.join(field.get('options', []))
        layer_2_form_context += f"\n    - Options: {options_str}"
    elif control_type == 'dropdown':
        options_str = ', '.join(field.get('options', []))
        layer_2_form_context += f"\n    - Options: {options_str}"

    # Use LLM-generated domain context
    layer_3_domain = f"""Domain Context:
    {domain_context}
    
    This field is part of {form_name.lower()} extraction: {form_description}"""

    if special_instructions:
        layer_3_domain += f"\n    Special Instructions: {special_instructions}"

    docstring = f'''"""
    {layer_1_purpose}
    
    {layer_2_form_context}
    
    {layer_3_domain}
    """'''

    # PATTERN 2: Hyper-detailed output field (Template structure + LLM content)

    # Format extraction rules from LLM
    rules_formatted = "\n        ".join(
        [f"- {rule}" for rule in extraction_rules])

    # Format examples from LLM
    examples_formatted = []
    for ex in examples:
        scenario = ex.get('scenario', 'Example')
        output = ex.get('output', {})
        examples_formatted.append(
            f"# {scenario}\n        {json.dumps(output)}")
    examples_str = "\n        \n        ".join(examples_formatted)

    # Format edge cases from LLM
    edge_cases_formatted = "\n        ".join(
        [f"- {case}" for case in edge_cases])

    # Format document hints from LLM
    hints_formatted = "\n        ".join(
        [f"- {hint}" for hint in document_hints])

    output_desc = f'''"""JSON string with {field['name']} information.
        
        Structure:
        {generate_json_schema(field)}
        
        Extraction Rules:
        {rules_formatted}
        
        Examples:
        {examples_str}
        
        Edge Cases:
        {edge_cases_formatted}
        
        Document Hints:
        {hints_formatted}
        
        Important:
        - Always return valid JSON
        - Use "NR" for not reported or unclear cases
        - Preserve data types (numbers as numbers, text as strings)
        """'''

    # Check dependencies
    dependencies = semantic_analysis['field_dependencies'].get(
        field['name'], [])

    if dependencies:
        context_params = "\n".join([
            f'    {sanitize_field_key(dep)}_context: str = dspy.InputField(desc="Context from {dep} extraction for informed decision-making")'
            for dep in dependencies
        ])

        signature_code = f'''
class {class_name}(dspy.Signature):
    {docstring}
    
    markdown_content: str = dspy.InputField(
        desc="Full markdown content of the source document"
    )
{context_params}
    
    {field_key}_json: str = dspy.OutputField(
        desc={output_desc}
    )
'''
    else:
        signature_code = f'''
class {class_name}(dspy.Signature):
    {docstring}
    
    markdown_content: str = dspy.InputField(
        desc="Full markdown content of the source document"
    )
    
    {field_key}_json: str = dspy.OutputField(
        desc={output_desc}
    )
'''

    return signature_code


def generate_combiner_signature(fields: List[Dict[str, Any]], form_name: str, semantic_analysis: Dict[str, Any]) -> str:
    """
    Generate combiner signature (TEMPLATE with LLM-informed groupings).
    """
    sanitized_form = sanitize_form_name(form_name)
    class_name = f"Combine{sanitized_form}Data"

    # Get semantic groups from LLM analysis
    semantic_groups = semantic_analysis.get('semantic_groups', {})

    # Generate input fields for each extracted component
    input_fields = []
    for field in fields:
        field_key = sanitize_field_key(field["name"])
        field_name_pascal = sanitize_form_name(field["name"])
        input_fields.append(
            f'    {field_key}_json: str = dspy.InputField(desc="JSON from Extract{field_name_pascal}")'
        )

    # Generate complete output schema
    output_schema_items = []
    for field in fields:
        field_key = sanitize_field_key(field['name'])
        control_type = field.get('control_type', field['type'])

        if control_type == 'checkbox_group_with_text':
            options = field.get('options', [])
            for opt in options:
                opt_key = sanitize_field_key(opt)
                output_schema_items.append(
                    f'            "{opt_key}": {{"selected": bool, "value": string}}')
        else:
            output_schema_items.append(f'            "{field_key}": value')

    output_schema = "{\n" + ",\n".join(output_schema_items) + "\n        }"

    # Add semantic grouping information from LLM
    if semantic_groups:
        groups_info = "\n        Semantic Groups:"
        for group_name, group_fields in semantic_groups.items():
            groups_info += f"\n        - {group_name}: {', '.join(group_fields)}"
    else:
        groups_info = ""

    combiner_code = f'''
class {class_name}(dspy.Signature):
    """Combine all extracted {form_name} components into single comprehensive record.
    {groups_info}
    """
    
{chr(10).join(input_fields)}
    
    complete_{sanitized_form.lower()}_json: str = dspy.OutputField(
        desc="""Merge all input data into a single JSON object with this structure:
        {output_schema}
        
        Instructions:
        - Parse each input JSON and extract its fields
        - Merge all fields into the top-level structure
        - Preserve nested structures exactly (e.g., checkbox groups with selected/value pairs)
        - Ensure all field names match the expected schema
        - Maintain semantic relationships between related fields
        - Return only valid JSON, no additional text"""
    )
'''

    return combiner_code


def generate_fallback_structure(field: Dict[str, Any]) -> str:
    """Generate domain-aware fallback (TEMPLATE - guarantees safety)."""
    control_type = field.get('control_type', field['type'])
    field_key = sanitize_field_key(field['name'])

    if control_type == 'text':
        return f'{{"{field_key}": "NR"}}'

    elif control_type == 'number':
        return f'{{"{field_key}": "NR"}}'

    elif control_type == 'dropdown':
        return f'{{"{field_key}": "NR"}}'

    elif control_type == 'checkbox_group_with_text':
        options = field.get('options', [])
        fallback_items = []
        for opt in options:
            opt_key = sanitize_field_key(opt)
            fallback_items.append(
                f'                "{opt_key}": {{"selected": False, "value": ""}}')

        return "{\n" + ",\n".join(fallback_items) + "\n            }"

    return f'{{"{field_key}": ""}}'


def generate_extractor_module(field: Dict[str, Any], form_name: str, semantic_analysis: Dict[str, Any]) -> str:
    """
    Generate async extractor module (TEMPLATE structure + LLM-informed dependencies).
    """
    field_name_pascal = sanitize_form_name(field["name"])
    class_name = f"Async{field_name_pascal}Extractor"
    signature_class = f"Extract{field_name_pascal}"
    field_key = sanitize_field_key(field['name'])
    control_type = field.get('control_type', field['type'])

    # Get dependencies from LLM analysis
    dependencies = semantic_analysis['field_dependencies'].get(
        field['name'], [])

    # Determine return type
    if control_type in ['text', 'dropdown']:
        return_type = 'str'
        fallback_value = '"NR"'
    elif control_type == 'number':
        return_type = 'Any'
        fallback_value = '"NR"'
    else:  # checkbox_group_with_text
        return_type = 'Dict[str, Any]'
        fallback_value = generate_fallback_structure(field)

    # Generate __call__ parameters based on dependencies
    if dependencies:
        dep_params = [
            f'{sanitize_field_key(dep)}_context: str' for dep in dependencies]
        call_params = ', '.join(['markdown_content: str'] + dep_params)
        extract_params = ', '.join(['markdown_content=markdown_content'] +
                                   [f'{sanitize_field_key(dep)}_context={sanitize_field_key(dep)}_context'
                                    for dep in dependencies])
    else:
        call_params = 'markdown_content: str'
        extract_params = 'markdown_content=markdown_content'

    extractor_code = f'''
class {class_name}(dspy.Module):
    """Async module to extract {field['name']}."""
    
    def __init__(self):
        super().__init__()
        self.extract = dspy.ChainOfThought({signature_class})
    
    async def __call__(self, {call_params}) -> {return_type}:
        loop = asyncio.get_running_loop()
        
        def _extract():
            return self.extract({extract_params})
        
        try:
            result = await loop.run_in_executor(None, _extract)
            return safe_json_parse(result.{field_key}_json)
        except Exception as e:
            print(f"Error in {field['name']} extraction: {{e}}")
            return {fallback_value}
    
    def forward_sync(self, {call_params}) -> {return_type}:
        """Synchronous version for DSPy optimizers."""
        result = self.extract({extract_params})
        return safe_json_parse(result.{field_key}_json)
'''

    return extractor_code


def generate_combiner_module(fields: List[Dict[str, Any]], form_name: str) -> str:
    """Generate combiner module (TEMPLATE with standard structure)."""
    sanitized_form = sanitize_form_name(form_name)
    class_name = f"Async{sanitized_form}Combiner"
    signature_class = f"Combine{sanitized_form}Data"

    param_names = [f"{sanitize_field_key(f['name'])}" for f in fields]
    params = ', '.join([f"{name}: Any" for name in param_names])

    combiner_args = []
    for field in fields:
        field_key = sanitize_field_key(field['name'])
        combiner_args.append(f'{field_key}_json=json.dumps({field_key})')

    combiner_args_str = ',\n                '.join(combiner_args)
    fallback_updates = '\n            '.join(
        [f'combined.update({name})' for name in param_names])

    combiner_code = f'''
class {class_name}(dspy.Module):
    """Async module to combine all {form_name} data."""
    
    def __init__(self):
        super().__init__()
        self.combiner = dspy.ChainOfThought({signature_class})
    
    async def __call__(self, {params}) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        
        def _combine():
            return self.combiner(
                {combiner_args_str}
            )
        
        try:
            result = await loop.run_in_executor(None, _combine)
            return safe_json_parse(result.complete_{sanitized_form.lower()}_json)
        except Exception as e:
            print(f"Error in combining {form_name} data: {{e}}, using fallback merge")
            combined = {{}}
            {fallback_updates}
            return combined
    
    def forward_sync(self, {params}) -> Dict[str, Any]:
        """Synchronous version for DSPy optimizers."""
        result = self.combiner(
            {combiner_args_str}
        )
        return safe_json_parse(result.complete_{sanitized_form.lower()}_json)
'''

    return combiner_code


def generate_pipeline_module(fields: List[Dict[str, Any]], form_name: str, semantic_analysis: Dict[str, Any]) -> str:
    """
    Generate async pipeline with LLM-informed execution order (HYBRID).
    """
    sanitized_form = sanitize_form_name(form_name)
    pipeline_class = f"Async{sanitized_form}Pipeline"

    # Use LLM's extraction order
    extraction_order = semantic_analysis.get(
        'extraction_order', [f['name'] for f in fields])
    field_dependencies = semantic_analysis.get('field_dependencies', {})

    # Reorder fields based on LLM's intelligent ordering
    ordered_fields = []
    for field_name in extraction_order:
        field = next((f for f in fields if f['name'] == field_name), None)
        if field:
            ordered_fields.append(field)

    # Add any fields not in extraction_order
    for field in fields:
        if field not in ordered_fields:
            ordered_fields.append(field)

    # Categorize into stages
    stage_1 = []  # Context providers
    stage_2 = []  # Independent
    stage_3 = []  # Dependent

    for field in ordered_fields:
        deps = field_dependencies.get(field['name'], [])
        is_depended_on = any(field['name'] in field_dependencies.get(f['name'], [])
                             for f in fields if f != field)

        if is_depended_on and not deps:
            stage_1.append(field)
        elif deps:
            stage_3.append(field)
        else:
            stage_2.append(field)

    # Generate extractor initializations
    extractor_inits = []
    for field in fields:
        field_name_pascal = sanitize_form_name(field["name"])
        field_key = sanitize_field_key(field["name"])
        extractor_inits.append(
            f"        self.{field_key}_extractor = Async{field_name_pascal}Extractor()"
        )
    extractor_inits.append(
        f"        self.combiner = Async{sanitized_form}Combiner()")

    # Generate Stage 1 (Context fields - sequential)
    stage_1_code = []
    stage_1_results = {}
    if stage_1:
        stage_1_code.append(
            "        # Stage 1: Extract context fields (sequential) - LLM identified these as dependencies")
        for field in stage_1:
            field_key = sanitize_field_key(field['name'])
            stage_1_code.append(
                f"        {field_key} = await self.{field_key}_extractor(markdown_content)")
            stage_1_results[field['name']] = field_key

    # Generate Stage 2 (Independent fields - parallel)
    stage_2_code = []
    stage_2_tasks = []
    if stage_2:
        stage_2_code.append(
            "\n        # Stage 2: Extract independent fields (parallel) - No dependencies")
        for field in stage_2:
            field_key = sanitize_field_key(field['name'])
            stage_2_code.append(
                f"        {field_key}_task = self.{field_key}_extractor(markdown_content)")
            stage_2_tasks.append(field_key)

    # Generate Stage 3 (Dependent fields - parallel with context)
    stage_3_code = []
    stage_3_tasks = []
    if stage_3:
        stage_3_code.append(
            "\n        # Stage 3: Extract dependent fields (parallel with context) - LLM identified dependencies")
        for field in stage_3:
            field_key = sanitize_field_key(field['name'])
            deps = field_dependencies.get(field['name'], [])

            if deps:
                context_args = ', '.join([f"{sanitize_field_key(dep)}_context=json.dumps({stage_1_results.get(dep, sanitize_field_key(dep))})"
                                         for dep in deps])
                stage_3_code.append(
                    f"        {field_key}_task = self.{field_key}_extractor(markdown_content, {context_args})")
            else:
                stage_3_code.append(
                    f"        {field_key}_task = self.{field_key}_extractor(markdown_content)")
            stage_3_tasks.append(field_key)

    # Generate gather statement
    all_tasks = stage_2_tasks + stage_3_tasks
    if all_tasks:
        gather_code = f"\n        # Stage 4: Gather all parallel tasks\n"
        gather_code += f"        {', '.join(all_tasks)} = await asyncio.gather(\n"
        gather_code += ',\n'.join(
            [f"            {task}_task" for task in all_tasks])
        gather_code += "\n        )"
    else:
        gather_code = ""

    # Generate combiner call
    all_field_keys = [sanitize_field_key(f['name']) for f in fields]
    combiner_call = f"\n        # Stage 5: Combine all data intelligently\n"
    combiner_call += f"        complete_{sanitized_form.lower()} = await self.combiner(\n"
    combiner_call += ',\n'.join(
        [f"            {key}" for key in all_field_keys])
    combiner_call += "\n        )"

    pipeline_code = f'''
class {pipeline_class}(dspy.Module):
    """
    Complete async pipeline for extracting {form_name}.
    
    Execution strategy determined by LLM semantic analysis:
    - Stage 1: Context providers (sequential)
    - Stage 2: Independent fields (parallel)
    - Stage 3: Dependent fields (parallel with context)
    - Stage 4: Gather results
    - Stage 5: Intelligent combination
    """
    
    def __init__(self, max_concurrent: int = 5):
        super().__init__()
        
{chr(10).join(extractor_inits)}
        
        self.max_concurrent = max_concurrent
        self._semaphore = None
    
    def _get_semaphore(self):
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent)
        return self._semaphore
    
    async def forward(self, markdown_content: str):
{chr(10).join(stage_1_code)}
{chr(10).join(stage_2_code)}
{chr(10).join(stage_3_code)}
{gather_code}
{combiner_call}
        
        return dspy.Prediction(
            {sanitized_form.lower()}=complete_{sanitized_form.lower()},
            success=True
        )
    
    async def __call__(self, markdown_content: str):
        return await self.forward(markdown_content)
'''

    return pipeline_code


def generate_sync_wrapper(form_name: str, fields: List[Dict[str, Any]]) -> str:
    """Generate synchronous wrapper (TEMPLATE - standard pattern)."""
    sanitized_form = sanitize_form_name(form_name)
    sync_class = f"Sync{sanitized_form}Pipeline"
    async_class = f"Async{sanitized_form}Pipeline"

    extractor_exposures = []
    for field in fields:
        field_key = sanitize_field_key(field['name'])
        extractor_exposures.append(
            f"        self.{field_key}_extractor = self.async_pipeline.{field_key}_extractor"
        )
    extractor_exposures.append(
        "        self.combiner = self.async_pipeline.combiner")

    sync_code = f'''
class {sync_class}(dspy.Module):
    """Synchronous wrapper for async {form_name} pipeline (for DSPy optimizers)."""
    
    def __init__(self):
        super().__init__()
        self.async_pipeline = {async_class}()
        
        # Expose extractors for optimizer access
{chr(10).join(extractor_exposures)}
    
    def forward(self, markdown_content: str):
        """Execute pipeline synchronously."""
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                except ImportError:
                    raise ImportError(
                        "Please install nest_asyncio: pip install nest_asyncio"
                    )
        except RuntimeError:
            pass
        
        self.async_pipeline._semaphore = None
        result = asyncio.run(self.async_pipeline(markdown_content))
        return result
    
    def __deepcopy__(self, memo):
        """Required for DSPy optimization."""
        return {sync_class}()
'''

    return sync_code


# ============================================================================
# MAIN GENERATION ORCHESTRATOR (Step 3: Combine Everything)
# ============================================================================

def generate_code_with_hybrid_approach(form_name: str, form_description: str, fields: List[Dict[str, Any]]) -> Tuple[str, str]:
    """
    Main orchestrator: Use LLM for intelligence, templates for structure.

    Returns:
        (signatures_code, modules_code)
    """
    print("🧠 Step 1: Analyzing form semantics with LLM...")

    # Step 1: Use LLM to analyze form semantics
    semantic_analyzer = dspy.ChainOfThought(AnalyzeFormSemantics)

    fields_json = json.dumps([{
        'name': f['name'],
        'type': f.get('type'),
        'control_type': f.get('control_type'),
        'description': f.get('description'),
        'options': f.get('options', [])
    } for f in fields], indent=2)

    try:
        semantic_result = semantic_analyzer(
            form_name=form_name,
            form_description=form_description,
            fields_json=fields_json
        )
        semantic_analysis = json.loads(semantic_result.semantic_analysis)
        print(f"   ✅ Semantic analysis complete")
        print(
            f"   - Identified {len(semantic_analysis.get('field_dependencies', {}))} dependencies")
        print(
            f"   - Found {len(semantic_analysis.get('semantic_groups', {}))} semantic groups")
    except Exception as e:
        print(f"   ⚠️ Semantic analysis failed: {e}, using fallback")
        # Fallback: basic analysis
        semantic_analysis = {
            'field_dependencies': {f['name']: [] for f in fields},
            'domain_contexts': {f['name']: f.get('description', '') for f in fields},
            'extraction_complexity': {f['name']: 'medium' for f in fields},
            'semantic_groups': {},
            'extraction_order': [f['name'] for f in fields],
            'special_instructions': {}
        }

    print("🎯 Step 2: Generating intelligent prompting strategies for each field...")

    # Step 2: Generate prompting strategy for each field
    strategy_generator = dspy.ChainOfThought(GenerateFieldPromptingStrategy)

    field_strategies = {}
    for field in fields:
        try:
            domain_context = semantic_analysis['domain_contexts'].get(
                field['name'], '')
            complexity = semantic_analysis['extraction_complexity'].get(
                field['name'], 'medium')

            strategy_result = strategy_generator(
                field_name=field['name'],
                field_description=field.get('description', ''),
                field_type=field.get('type', 'text'),
                control_type=field.get('control_type', field.get('type')),
                options=json.dumps(field.get('options', [])),
                domain_context=domain_context,
                complexity=complexity
            )

            field_strategies[field['name']] = json.loads(
                strategy_result.prompting_strategy)
            print(f"   ✅ Strategy generated for {field['name']}")
        except Exception as e:
            print(
                f"   ⚠️ Strategy generation failed for {field['name']}: {e}, using fallback")
            # Fallback: basic strategy
            field_strategies[field['name']] = {
                'extraction_rules': [
                    'Extract the exact value from the document',
                    'Use "NR" if not reported'
                ],
                'examples': [
                    {'scenario': 'Common case', 'output': {
                        sanitize_field_key(field['name']): 'example value'}},
                    {'scenario': 'Not reported', 'output': {
                        sanitize_field_key(field['name']): 'NR'}}
                ],
                'edge_cases': ['Not reported - use NR', 'Ambiguous - choose most specific'],
                'document_hints': ['Search entire document for relevant information']
            }

    print("🏗️  Step 3: Building signatures with template guarantees + LLM intelligence...")

    # Step 3: Generate signatures.py using templates with LLM-informed content
    sanitized_form = sanitize_form_name(form_name)

    signatures_code = f'''"""
DSPy Signatures for {sanitized_form}
Generated with Hybrid Approach: LLM Intelligence + Template Guarantees
"""

import dspy


# ============================================================================
# INDIVIDUAL FIELD SIGNATURES
# ============================================================================

'''

    for field in fields:
        signature_class = generate_signature_class_with_intelligence(
            field,
            form_name,
            form_description,
            semantic_analysis,
            field_strategies[field['name']]
        )
        signatures_code += signature_class + "\n"

    signatures_code += '''
# ============================================================================
# COMBINER SIGNATURE
# ============================================================================

'''
    signatures_code += generate_combiner_signature(
        fields, form_name, semantic_analysis)

    # Generate __all__
    class_names = []
    for field in fields:
        field_name_pascal = sanitize_form_name(field["name"])
        class_names.append(f"Extract{field_name_pascal}")
    class_names.append(f"Combine{sanitized_form}Data")

    signatures_code += f'''

__all__ = [
    {','.join([f'"{name}"' for name in class_names])}
]
'''

    print("🏗️  Step 4: Building modules with dependency-aware execution...")

    # Step 4: Generate modules.py
    modules_code = f'''"""
DSPy Modules for {sanitized_form}
Generated with Hybrid Approach: LLM Intelligence + Template Guarantees
"""

import asyncio
import json
from typing import Dict, Any

import dspy

from utils.json_parser import safe_json_parse
from .signatures import (
'''

    for field in fields:
        field_name_pascal = sanitize_form_name(field["name"])
        modules_code += f"    Extract{field_name_pascal},\n"
    modules_code += f"    Combine{sanitized_form}Data,\n"
    modules_code += ")\n\n"

    modules_code += '''
# ============================================================================
# INDIVIDUAL FIELD EXTRACTORS
# ============================================================================

'''
    for field in fields:
        modules_code += generate_extractor_module(
            field, form_name, semantic_analysis) + "\n"

    modules_code += '''
# ============================================================================
# COMBINER MODULE
# ============================================================================

'''
    modules_code += generate_combiner_module(fields, form_name) + "\n"

    modules_code += '''
# ============================================================================
# ASYNC PIPELINE (with LLM-determined execution order)
# ============================================================================

'''
    modules_code += generate_pipeline_module(fields,
                                             form_name, semantic_analysis) + "\n"

    modules_code += '''
# ============================================================================
# SYNC WRAPPER (for DSPy optimizers)
# ============================================================================

'''
    modules_code += generate_sync_wrapper(form_name, fields) + "\n"

    # Generate __all__
    module_class_names = []
    for field in fields:
        field_name_pascal = sanitize_form_name(field["name"])
        module_class_names.append(f"Async{field_name_pascal}Extractor")
    module_class_names.extend([
        f"Async{sanitized_form}Combiner",
        f"Async{sanitized_form}Pipeline",
        f"Sync{sanitized_form}Pipeline"
    ])

    modules_code += f'''
__all__ = [
    {','.join([f'"{name}"' for name in module_class_names])}
]
'''

    print("✅ Code generation complete!")

    return signatures_code, modules_code


def create_task_directory(project_id: str, form_id: str, form_data: Dict[str, Any]) -> Path:
    """
    Create complete task directory with hybrid-generated code.
    """
    task_name = f"dynamic_{project_id}_{form_id}"
    # Tasks live under the top-level dspy_components/tasks package
    # (sibling of core/), not under core/dspy_components.
    task_dir = (
        Path(__file__).parent.parent
        / "dspy_components"
        / "tasks"
        / task_name
    )

    task_dir.mkdir(parents=True, exist_ok=True)

    form_name = form_data['name']
    form_description = form_data.get(
        'description', f'Extract {form_name} data')
    fields = form_data.get('fields', [])

    print(f"🤖 Generating hybrid DSPy code for {form_name}...")

    # Generate code using hybrid approach
    signatures_code, modules_code = generate_code_with_hybrid_approach(
        form_name,
        form_description,
        fields
    )

    # Write files
    signature_file = task_dir / "signatures.py"
    signature_file.write_text(signatures_code)

    module_file = task_dir / "modules.py"
    module_file.write_text(modules_code)

    init_file = task_dir / "__init__.py"
    init_file.write_text("")

    metadata = {
        "project_id": project_id,
        "form_id": form_id,
        "form_data": form_data
    }
    metadata_file = task_dir / "metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2))

    print(f"✅ Created task directory: {task_dir}")

    return task_dir


def load_dynamic_schemas():
    """Load all dynamic schemas on startup.

    Note:
        The dynamically generated DSPy task packages live under the
        top-level ``dspy_components/tasks`` directory at the project root,
        not inside ``core/``. We therefore resolve the tasks directory
        relative to the project root (parent of ``core``).
    """
    # project_root / "dspy_components" / "tasks"
    tasks_dir = Path(__file__).parent.parent / "dspy_components" / "tasks"
    if not tasks_dir.exists():
        print(f"⚠️ Tasks directory not found: {tasks_dir}")
        return

    print(f"🔄 Loading dynamic schemas from {tasks_dir}...")
    count = 0
    errors = []

    for task_dir in tasks_dir.iterdir():
        if task_dir.is_dir() and task_dir.name.startswith("dynamic_"):
            metadata_file = task_dir / "metadata.json"
            if metadata_file.exists():
                try:
                    metadata = json.loads(metadata_file.read_text())
                    schema_name = register_dynamic_schema(
                        metadata['project_id'],
                        metadata['form_id'],
                        metadata['form_data']
                    )
                    print(f"   ✅ Loaded: {schema_name}")
                    count += 1
                except Exception as e:
                    error_msg = f"Failed to load {task_dir.name}: {str(e)}"
                    print(f"   ❌ {error_msg}")
                    errors.append(error_msg)
            else:
                print(f"   ⚠️ No metadata.json in {task_dir.name}")

    print(f"✅ Loaded {count} dynamic schemas.")
    if errors:
        print(f"⚠️ {len(errors)} schemas failed to load:")
        for err in errors:
            print(f"   - {err}")

    return {"loaded": count, "errors": errors}


def register_dynamic_schema(project_id: str, form_id: str, form_data: Dict[str, Any]) -> str:
    """Register dynamically generated schema."""
    from schemas.configs import SCHEMA_CONFIGS, SchemaConfig

    task_name = f"dynamic_{project_id}_{form_id}"
    form_name = form_data['name']
    sanitized_name = sanitize_form_name(form_name)

    if task_name in SCHEMA_CONFIGS:
        return task_name

    try:
        # Tasks live under project_root / "dspy_components" / "tasks"
        task_dir = (
            Path(__file__).parent.parent
            / "dspy_components"
            / "tasks"
            / task_name
        )
        if str(task_dir.parent) not in sys.path:
            sys.path.insert(0, str(task_dir.parent))

        importlib.invalidate_caches()

        sig_module = importlib.import_module(
            f"dspy_components.tasks.{task_name}.signatures")
        mod_module = importlib.import_module(
            f"dspy_components.tasks.{task_name}.modules")

        importlib.reload(sig_module)
        importlib.reload(mod_module)

        sig_class_name = f"Combine{sanitized_name}Data"
        mod_class_name = f"Sync{sanitized_name}Pipeline"

        if not hasattr(sig_module, sig_class_name):
            print(
                f"⚠️ Could not find exact class {sig_class_name}, searching...")
            for name, obj in vars(sig_module).items():
                if isinstance(obj, type) and issubclass(obj, dspy.Signature) and obj is not dspy.Signature:
                    sig_class_name = name
                    print(f"   Found signature class: {sig_class_name}")
                    break

        sig_class = getattr(sig_module, sig_class_name)
        mod_class = getattr(mod_module, mod_class_name)

        SCHEMA_CONFIGS[task_name] = SchemaConfig(
            name=task_name,
            description=form_data.get(
                'description', f'Dynamically generated: {sanitized_name}'),
            signature_class=sig_class,
            pipeline_class=mod_class,
            output_field_name=f"complete_{sanitized_name.lower()}_json",
            cache_file=f"schemas/generated_fields/{task_name}_fields.json",
        )

        print(f"✅ Registered schema: {task_name}")
        print(f"   - Signature: {sig_class_name}")
        print(f"   - Pipeline: {mod_class_name}")

        try:
            from schemas.registry import refresh_registry
            updated_schemas = refresh_registry()
            print(
                f"   - Registry refreshed: {len(updated_schemas)} total schemas")
        except Exception as e:
            print(f"   - Registry refresh warning: {e}")

        return task_name

    except Exception as e:
        print(f"❌ Error registering schema: {e}")
        raise


def generate_task_from_form(project_id: str, form_id: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete workflow: Generate task directory and register schema.
    """
    try:
        task_dir = create_task_directory(project_id, form_id, form_data)
        schema_name = register_dynamic_schema(project_id, form_id, form_data)

        return {
            'status': 'success',
            'task_dir': str(task_dir),
            'schema_name': schema_name,
            'form_name': form_data['name']
        }

    except Exception as e:
        import traceback
        return {
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }


# Example usage
if __name__ == "__main__":
    # Test with a complex form
    sample_form = {
        'name': 'ClinicalTrialCharacteristics',
        'description': 'Comprehensive trial design and methodology information for systematic reviews of clinical research',
        'fields': [
            {
                'name': 'study_design',
                'type': 'text',
                'control_type': 'dropdown',
                'description': 'Type of study design used (e.g., randomized controlled trial, cohort study, case-control)',
                'required': True,
                'options': ['RCT', 'Cohort Study', 'Case-Control Study', 'Cross-Sectional', 'Other']
            },
            {
                'name': 'randomization_method',
                'type': 'text',
                'control_type': 'text',
                'description': 'Method used for randomization (e.g., computer-generated, block randomization). Depends on study being an RCT.',
                'required': False
            },
            {
                'name': 'sample_size',
                'type': 'number',
                'control_type': 'number',
                'description': 'Total number of participants enrolled at baseline',
                'required': True
            },
            {
                'name': 'baseline_demographics',
                'type': 'object',
                'control_type': 'checkbox_group_with_text',
                'description': 'Baseline demographic characteristics of enrolled participants including gender distribution and age metrics',
                'required': True,
                'options': [
                    'Total participants (N)',
                    'Female (N)',
                    'Female (%)',
                    'Male (N)',
                    'Male (%)',
                    'Mean age (years)',
                    'Age standard deviation (years)',
                    'Age range (years)'
                ]
            },
            {
                'name': 'intervention_description',
                'type': 'text',
                'control_type': 'text',
                'description': 'Detailed description of the intervention being tested, including dosage, frequency, and duration',
                'required': True
            },
            {
                'name': 'primary_outcome',
                'type': 'text',
                'control_type': 'text',
                'description': 'Primary outcome measure as stated by the study authors',
                'required': True
            }
        ]
    }

    print("=" * 80)
    print("HYBRID DSPy CODE GENERATOR TEST")
    print("LLM Intelligence + Template Guarantees")
    print("=" * 80)

    result = generate_task_from_form(
        project_id="test_hybrid",
        form_id="form_001",
        form_data=sample_form
    )

    print("\n" + "=" * 80)
    print("RESULT:")
    print("=" * 80)
    print(json.dumps(result, indent=2))

    if result['status'] == 'success':
        print("\n" + "=" * 80)
        print("GENERATED CODE PREVIEW:")
        print("=" * 80)

        sig_file = Path(result['task_dir']) / "signatures.py"
        if sig_file.exists():
            print("\n📄 signatures.py (first 1500 chars):")
            print(sig_file.read_text()[:1500] + "...\n")

        mod_file = Path(result['task_dir']) / "modules.py"
        if mod_file.exists():
            print("\n📄 modules.py (first 1500 chars):")
            print(mod_file.read_text()[:1500] + "...")


# """
# Dynamic DSPy Code Generator for eviStream
# Uses LLM to intelligently generate DSPy signatures and modules from user-defined forms
# """

# import re
# import json
# from pathlib import Path
# from typing import List, Dict, Any
# import importlib
# import sys
# import dspy
# # Import lm_config to auto-configure DSPy
# import utils.lm_config  # This configures DSPy on import


# """
# Dynamic DSPy Code Generator for eviStream
# Uses LLM to intelligently generate DSPy signatures and modules from user-defined forms
# """

# # Import lm_config to auto-configure DSPy


# def sanitize_form_name(form_name: str) -> str:
#     """
#     Sanitize form name to create valid Python class names.

#     Examples:
#         " TrialCharacteristics" -> "TrialCharacteristics"
#         "Trial Characteristics" -> "TrialCharacteristics"
#         "trial-characteristics" -> "TrialCharacteristics"
#         "Diagnostic_Accuracy_Test" -> "DiagnosticAccuracyTest"
#     """
#     # Strip leading/trailing whitespace
#     name = form_name.strip()

#     # Replace common separators with spaces
#     name = name.replace('_', ' ').replace('-', ' ')

#     # Remove any non-alphanumeric characters except spaces
#     name = re.sub(r'[^a-zA-Z0-9\s]', '', name)

#     # Split into words
#     words = name.split()

#     # Capitalize first letter of each word, keep rest as-is
#     # This preserves things like "TrialCharacteristics" or "DiagnosticTest"
#     sanitized_words = []
#     for word in words:
#         if word:
#             # Only capitalize first letter, preserve rest
#             sanitized_words.append(
#                 word[0].upper() + word[1:] if len(word) > 1 else word.upper())

#     # Join words in PascalCase
#     sanitized = ''.join(sanitized_words)

#     # Ensure it starts with a letter
#     if sanitized and not sanitized[0].isalpha():
#         sanitized = 'Form' + sanitized

#     # Ensure it's not empty
#     if not sanitized:
#         sanitized = 'CustomForm'

#     return sanitized


# class GenerateDSPySignature(dspy.Signature):
#     """Generate a DSPy signature class from form definition."""

#     form_name: str = dspy.InputField(
#         desc="Name of the form (e.g., TrialCharacteristics)")
#     class_name: str = dspy.InputField(
#         desc="Exact class name to use (e.g., CombineTrialCharacteristicsData)")
#     form_description: str = dspy.InputField(
#         desc="Description of what data to extract")
#     fields_json: str = dspy.InputField(
#         desc="JSON string of field definitions with name, type, description")
#     existing_example: str = dspy.InputField(
#         desc="Example of existing DSPy signature for reference")

#     signature_code: str = dspy.OutputField(
#         desc="Complete Python code for signatures.py file. MUST use the specified class_name.")


# # Example signature for reference
# EXAMPLE_SIGNATURE = '''"""
# DSPy Signature for Patient Population
# """

# import dspy


# class CombinePatientPopulationCharacteristics(dspy.Signature):
#     """Extract patient population characteristics from medical research paper."""

#     paper_content: str = dspy.InputField(desc="Full text of the research paper in markdown format")
#     age_mean: str = dspy.OutputField(desc="Mean age of participants")
#     age_range: str = dspy.OutputField(desc="Age range of participants")
#     gender_distribution: str = dspy.OutputField(desc="Gender distribution (e.g., 60% male, 40% female)")
#     sample_size: str = dspy.OutputField(desc="Total number of participants")
# '''


# def clean_code_block(code: str) -> str:
#     """
#     Strip markdown code blocks and whitespace from generated code.
#     """
#     # Remove ```python ... ``` or ``` ... ```
#     pattern = r"```(?:python)?\s*(.*?)```"
#     match = re.search(pattern, code, re.DOTALL)
#     if match:
#         code = match.group(1)
#     return code.strip()


# def generate_signature_with_llm(form_name: str, form_description: str, fields: List[Dict[str, Any]]) -> str:
#     """
#     Use LLM to generate DSPy signature code from form definition.
#     """
#     # Sanitize form name for valid class name
#     sanitized_name = sanitize_form_name(form_name)

#     # Create code generator
#     generator = dspy.ChainOfThought(GenerateDSPySignature)

#     # Convert fields to JSON
#     fields_json = json.dumps(fields, indent=2)

#     # Enforce class name
#     class_name = f"Combine{sanitized_name}Data"

#     # Generate signature code
#     result = generator(
#         form_name=sanitized_name,
#         class_name=class_name,
#         form_description=form_description,
#         fields_json=fields_json,
#         existing_example=EXAMPLE_SIGNATURE
#     )

#     return clean_code_block(result.signature_code)


# def generate_module_template(form_name: str) -> str:
#     """
#     Generate DSPy module code using a robust template (Hybrid Approach).
#     """
#     # Sanitize form name for valid class names
#     sanitized_name = sanitize_form_name(form_name)

#     signature_class = f"Combine{sanitized_name}Data"
#     pipeline_class = f"Async{sanitized_name}Pipeline"

#     return f'''"""
# DSPy Module for {sanitized_name}
# Auto-generated using Hybrid Template
# """

# import dspy
# from .signatures import {signature_class}


# class {pipeline_class}:
#     """Async pipeline for extracting {sanitized_name} data."""

#     def __init__(self):
#         self.extractor = dspy.ChainOfThought({signature_class})

#     async def __call__(self, markdown_content: str):
#         """
#         Extract data from markdown content.
#         """
#         try:
#             result = self.extractor(paper_content=markdown_content)
#             return result
#         except Exception as e:
#             print(f"Error in extraction: {{e}}")
#             return dspy.Prediction()
# '''


# def create_task_directory(project_id: str, form_id: str, form_data: Dict[str, Any]) -> Path:
#     """
#     Create complete task directory with LLM-generated signature and Template module.
#     """
#     # Create task directory name
#     task_name = f"dynamic_{project_id}_{form_id}"
#     task_dir = Path(__file__).parent / "dspy_components" / "tasks" / task_name

#     # Create directory
#     task_dir.mkdir(parents=True, exist_ok=True)

#     # Extract form info
#     form_name = form_data['name']
#     form_description = form_data.get(
#         'description', f'Extract {form_name} data')
#     fields = form_data.get('fields', [])

#     print(f"🤖 Generating DSPy code for {form_name}...")

#     # Generate signatures.py using LLM
#     print("   Generating signatures.py (LLM)...")
#     signature_code = generate_signature_with_llm(
#         form_name, form_description, fields)
#     signature_file = task_dir / "signatures.py"
#     signature_file.write_text(signature_code)

#     # Generate modules.py using Template
#     print("   Generating modules.py (Template)...")
#     module_code = generate_module_template(form_name)
#     module_file = task_dir / "modules.py"
#     module_file.write_text(module_code)

#     # Create __init__.py
#     init_file = task_dir / "__init__.py"
#     init_file.write_text("")

#     # Save metadata.json for persistence
#     metadata = {
#         "project_id": project_id,
#         "form_id": form_id,
#         "form_data": form_data
#     }
#     metadata_file = task_dir / "metadata.json"
#     metadata_file.write_text(json.dumps(metadata, indent=2))

#     print(f"✅ Created task directory: {task_dir}")

#     return task_dir


# def load_dynamic_schemas():
#     """
#     Discover and register all dynamic schemas from dspy_components/tasks.
#     Should be called on application startup.
#     """
#     tasks_dir = Path(__file__).parent / "dspy_components" / "tasks"
#     if not tasks_dir.exists():
#         print(f"⚠️ Tasks directory not found: {tasks_dir}")
#         return

#     print(f"🔄 Loading dynamic schemas from {tasks_dir}...")
#     count = 0
#     errors = []

#     for task_dir in tasks_dir.iterdir():
#         if task_dir.is_dir() and task_dir.name.startswith("dynamic_"):
#             metadata_file = task_dir / "metadata.json"
#             if metadata_file.exists():
#                 try:
#                     metadata = json.loads(metadata_file.read_text())
#                     schema_name = register_dynamic_schema(
#                         metadata['project_id'],
#                         metadata['form_id'],
#                         metadata['form_data']
#                     )
#                     print(f"   ✅ Loaded: {schema_name}")
#                     count += 1
#                 except Exception as e:
#                     error_msg = f"Failed to load {task_dir.name}: {str(e)}"
#                     print(f"   ❌ {error_msg}")
#                     errors.append(error_msg)
#                     import traceback
#                     traceback.print_exc()
#             else:
#                 print(f"   ⚠️ No metadata.json in {task_dir.name}")

#     print(f"✅ Loaded {count} dynamic schemas.")
#     if errors:
#         print(f"⚠️ {len(errors)} schemas failed to load:")
#         for err in errors:
#             print(f"   - {err}")

#     return {"loaded": count, "errors": errors}


# def register_dynamic_schema(project_id: str, form_id: str, form_data: Dict[str, Any]) -> str:
#     """
#     Register dynamically generated schema in the schema registry.
#     """
#     from schemas.configs import SCHEMA_CONFIGS, SchemaConfig

#     task_name = f"dynamic_{project_id}_{form_id}"
#     form_name = form_data['name']

#     # Sanitize form name for class lookups
#     sanitized_name = sanitize_form_name(form_name)

#     # Check if already registered to avoid duplicates/errors on reload
#     if task_name in SCHEMA_CONFIGS:
#         return task_name

#     # Import the generated modules dynamically
#     try:
#         # Add task directory to path if needed
#         task_dir = Path(__file__).parent / \
#             "dspy_components" / "tasks" / task_name
#         if str(task_dir.parent) not in sys.path:
#             sys.path.insert(0, str(task_dir.parent))

#         # Import signature and module classes
#         # We use importlib.invalidate_caches() to ensure we see new files
#         importlib.invalidate_caches()

#         sig_module = importlib.import_module(
#             f"dspy_components.tasks.{task_name}.signatures")
#         mod_module = importlib.import_module(
#             f"dspy_components.tasks.{task_name}.modules")

#         # Reload modules if they were already imported (important for updates)
#         importlib.reload(sig_module)
#         importlib.reload(mod_module)

#         # Get the classes (using sanitized names)
#         sig_class_name = f"Combine{sanitized_name}Data"
#         mod_class_name = f"Async{sanitized_name}Pipeline"

#         if not hasattr(sig_module, sig_class_name):
#             # Fallback: try to find any class inheriting from dspy.Signature
#             print(
#                 f"⚠️ Could not find exact class {sig_class_name}, searching for alternatives...")
#             for name, obj in vars(sig_module).items():
#                 if isinstance(obj, type) and issubclass(obj, dspy.Signature) and obj is not dspy.Signature:
#                     sig_class_name = name
#                     print(f"   Found signature class: {sig_class_name}")
#                     break

#         sig_class = getattr(sig_module, sig_class_name)
#         mod_class = getattr(mod_module, mod_class_name)

#         # Register in SCHEMA_CONFIGS
#         SCHEMA_CONFIGS[task_name] = SchemaConfig(
#             name=task_name,
#             description=form_data.get(
#                 'description', f'Dynamically generated: {sanitized_name}'),
#             signature_class=sig_class,
#             pipeline_class=mod_class,
#             output_field_name=f"complete_{sanitized_name.lower()}_json",
#             cache_file=f"schemas/generated_fields/{task_name}_fields.json",
#         )

#         print(f"✅ Registered schema: {task_name}")
#         print(f"   - Signature: {sig_class_name}")
#         print(f"   - Pipeline: {mod_class_name}")

#         # Refresh the registry so it picks up the new schema
#         try:
#             from schemas.registry import refresh_registry
#             updated_schemas = refresh_registry()
#             print(
#                 f"   - Registry refreshed: {len(updated_schemas)} total schemas")
#         except Exception as e:
#             print(f"   - Registry refresh warning: {e}")

#         return task_name

#     except Exception as e:
#         print(f"❌ Error registering schema: {e}")
#         # import traceback
#         # traceback.print_exc()
#         raise


# def generate_task_from_form(project_id: str, form_id: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Complete workflow: Generate task directory and register schema.
#     """
#     try:
#         # Create task directory with LLM-generated code
#         task_dir = create_task_directory(project_id, form_id, form_data)

#         # Register schema
#         schema_name = register_dynamic_schema(project_id, form_id, form_data)

#         return {
#             'status': 'success',
#             'task_dir': str(task_dir),
#             'schema_name': schema_name,
#             'form_name': form_data['name']
#         }

#     except Exception as e:
#         import traceback
#         return {
#             'status': 'error',
#             'error': str(e),
#             'traceback': traceback.format_exc()
#         }


# # Example usage
# if __name__ == "__main__":
#     # Test with a sample form
#     sample_form = {
#         'name': 'TrialCharacteristics',
#         'description': 'trial design and methodology information',
#         'fields': [
#             {
#                 'name': 'study_design',
#                 'type': 'text',
#                 'description': 'Type of study design (e.g., RCT, cohort study)',
#                 'required': True
#             },
#             {
#                 'name': 'sample_size',
#                 'type': 'number',
#                 'description': 'Total number of participants enrolled',
#                 'required': True
#             }
#         ]
#     }

#     print("Testing Hybrid DSPy Code Generator...")
#     print("=" * 60)

#     result = generate_task_from_form(
#         project_id="test_project",
#         form_id="form_hybrid_001",
#         form_data=sample_form
#     )

#     print("\nResult:")
#     print(json.dumps(result, indent=2))

#     if result['status'] == 'success':
#         print("\n" + "=" * 60)
#         print("Generated Code Preview:")
#         print("=" * 60)

#         # Show generated signatures.py
#         sig_file = Path(result['task_dir']) / "signatures.py"
#         if sig_file.exists():
#             print("\n📄 signatures.py:")
#             print(sig_file.read_text()[:500] + "...")

#         # Show generated modules.py
#         mod_file = Path(result['task_dir']) / "modules.py"
#         if mod_file.exists():
#             print("\n📄 modules.py:")
#             print(mod_file.read_text()[:500] + "...")


# """
# Dynamic DSPy Code Generator for eviStream
# Generates production-grade DSPy signatures and modules following 8 universal patterns
# """

# import re
# import json
# from pathlib import Path
# from typing import List, Dict, Any, Set, Tuple
# import importlib
# import sys
# import dspy
# import utils.lm_config  # Auto-configure DSPy


# def sanitize_form_name(form_name: str) -> str:
#     """
#     Sanitize form name to create valid Python class names.

#     Examples:
#         " TrialCharacteristics" -> "TrialCharacteristics"
#         "Trial Characteristics" -> "TrialCharacteristics"
#         "trial-characteristics" -> "TrialCharacteristics"
#         "Diagnostic_Accuracy_Test" -> "DiagnosticAccuracyTest"
#     """
#     name = form_name.strip()
#     name = name.replace('_', ' ').replace('-', ' ')
#     name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
#     words = name.split()

#     sanitized_words = []
#     for word in words:
#         if word:
#             sanitized_words.append(
#                 word[0].upper() + word[1:] if len(word) > 1 else word.upper())

#     sanitized = ''.join(sanitized_words)

#     if sanitized and not sanitized[0].isalpha():
#         sanitized = 'Form' + sanitized

#     if not sanitized:
#         sanitized = 'CustomForm'

#     return sanitized


# def sanitize_field_key(field_name: str) -> str:
#     """
#     Convert field name to valid Python/JSON key (snake_case).

#     Examples:
#         "Study Design" -> "study_design"
#         "Patient Age (years)" -> "patient_age_years"
#         "Female (%)" -> "female_percent"
#     """
#     # Convert to lowercase
#     name = field_name.lower()

#     # Replace common patterns
#     name = name.replace('(%)', '_percent')
#     name = name.replace('(n)', '_n')
#     name = name.replace('%', '_percent')

#     # Remove parentheses and their contents if still present
#     name = re.sub(r'\([^)]*\)', '', name)

#     # Replace non-alphanumeric with underscores
#     name = re.sub(r'[^a-z0-9]+', '_', name)

#     # Remove leading/trailing underscores
#     name = name.strip('_')

#     # Ensure it starts with a letter
#     if name and not name[0].isalpha():
#         name = 'field_' + name

#     return name or 'field'


# def analyze_field_dependencies(fields: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
#     """
#     Analyze which fields depend on other fields.

#     Returns:
#         Dict mapping field names to set of fields they depend on
#     """
#     dependencies = {}

#     for field in fields:
#         field_name = field['name']
#         field_desc = field.get('description', '').lower()
#         depends_on = set()

#         # Check if description mentions other fields
#         for other_field in fields:
#             if other_field['name'] == field_name:
#                 continue

#             other_name = other_field['name'].lower()
#             # Check if other field is mentioned in this field's description
#             if other_name in field_desc or other_name.replace('_', ' ') in field_desc:
#                 depends_on.add(other_field['name'])

#         # Heuristic: fields with "based on", "given", "for" suggest dependencies
#         if any(keyword in field_desc for keyword in ['based on', 'given', 'for the', 'depending on']):
#             # This field likely depends on context
#             pass

#         dependencies[field_name] = depends_on

#     return dependencies


# def categorize_fields_by_stage(fields: List[Dict[str, Any]],
#                                dependencies: Dict[str, Set[str]]) -> Tuple[List, List, List]:
#     """
#     Categorize fields into execution stages based on dependencies.

#     Returns:
#         (stage_1_context_fields, stage_2_independent_fields, stage_3_dependent_fields)
#     """
#     # Stage 1: Fields that others depend on (context providers)
#     context_field_names = set()
#     for field_name, deps in dependencies.items():
#         for dep in deps:
#             context_field_names.add(dep)

#     stage_1 = [f for f in fields if f['name'] in context_field_names]

#     # Stage 2: Independent fields (no dependencies, not context providers)
#     stage_2 = [f for f in fields
#                if not dependencies[f['name']] and f['name'] not in context_field_names]

#     # Stage 3: Dependent fields (have dependencies, not in stage 1)
#     stage_3 = [f for f in fields
#                if dependencies[f['name']] and f['name'] not in context_field_names]

#     return stage_1, stage_2, stage_3


# def generate_json_schema(field: Dict[str, Any]) -> str:
#     """
#     Generate JSON schema based on control type (PATTERN 3).
#     """
#     control_type = field.get('control_type', field['type'])
#     field_key = sanitize_field_key(field['name'])

#     if control_type == 'text':
#         return f'''{{
#     "{field_key}": "extracted text value or NR if not reported"
# }}'''

#     elif control_type == 'number':
#         return f'''{{
#     "{field_key}": numeric_value_or_"NR"
# }}'''

#     elif control_type == 'dropdown':
#         options = field.get('options', [])
#         opts_str = '", "'.join(options) if options else 'option1", "option2'
#         return f'''{{
#     "{field_key}": "one of: [\\"{opts_str}\\"] or NR"
# }}'''

#     elif control_type == 'checkbox_group_with_text':
#         options = field.get('options', [])
#         schema_lines = []
#         for opt in options:
#             opt_key = sanitize_field_key(opt)
#             schema_lines.append(
#                 f'        "{opt_key}": {{"selected": true/false, "value": "extracted_value"}}')

#         schema = "{\n" + ",\n".join(schema_lines) + "\n    }"
#         return schema

#     return f'{{"{field_key}": "value"}}'


# def generate_extraction_rules(field: Dict[str, Any]) -> str:
#     """
#     Generate extraction rules based on control type (PATTERN 2).
#     """
#     control_type = field.get('control_type', field['type'])

#     rules = []

#     if control_type == 'text':
#         rules.append("- Extract the text exactly as stated in the document")
#         rules.append("- Use 'NR' if not reported or unclear")
#         rules.append("- Preserve exact quotes when available")

#     elif control_type == 'number':
#         rules.append("- Extract numeric values only")
#         rules.append("- Can be integer or decimal")
#         rules.append("- Use 'NR' if not reported")
#         rules.append("- Do not include units in the value")

#     elif control_type == 'dropdown':
#         options = field.get('options', [])
#         if options:
#             opts_str = '", "'.join(options)
#             rules.append(f'- Must be one of: ["{opts_str}"]')
#         rules.append("- Select the most appropriate option")
#         rules.append("- Use 'NR' if none match or not reported")

#     elif control_type == 'checkbox_group_with_text':
#         rules.append("- Set selected=true for each applicable option")
#         rules.append("- Extract the corresponding value in the 'value' field")
#         rules.append("- Multiple options can be selected=true simultaneously")
#         rules.append(
#             "- If an option is not applicable, set selected=false and value=''")
#         rules.append(
#             "- Use 'NR' in value field if the option is mentioned but value not reported")

#     return "\n        ".join(rules)


# def generate_examples(field: Dict[str, Any]) -> str:
#     """
#     Generate diverse examples based on control type (PATTERN 2).
#     """
#     control_type = field.get('control_type', field['type'])
#     field_key = sanitize_field_key(field['name'])

#     examples = []

#     if control_type == 'text':
#         examples.append(f'{{"{field_key}": "Randomized controlled trial"}}')
#         examples.append(f'{{"{field_key}": "NR"}}')
#         examples.append(
#             f'{{"{field_key}": "Prospective cohort study with 12-month follow-up"}}')

#     elif control_type == 'number':
#         examples.append(f'{{"{field_key}": 150}}')
#         examples.append(f'{{"{field_key}": 45.7}}')
#         examples.append(f'{{"{field_key}": "NR"}}')

#     elif control_type == 'dropdown':
#         options = field.get('options', [])
#         if len(options) >= 2:
#             examples.append(f'{{"{field_key}": "{options[0]}"}}')
#             examples.append(f'{{"{field_key}": "{options[1]}"}}')
#         examples.append(f'{{"{field_key}": "NR"}}')

#     elif control_type == 'checkbox_group_with_text':
#         options = field.get('options', [])
#         if len(options) >= 2:
#             opt1_key = sanitize_field_key(options[0])
#             opt2_key = sanitize_field_key(options[1])

#             examples.append(f'''{{
#     "{opt1_key}": {{"selected": true, "value": "150"}},
#     "{opt2_key}": {{"selected": false, "value": ""}}
# }}''')

#             examples.append(f'''{{
#     "{opt1_key}": {{"selected": true, "value": "65.5"}},
#     "{opt2_key}": {{"selected": true, "value": "34.5"}}
# }}''')

#     return "\n        ".join(examples)


# def generate_fallback_structure(field: Dict[str, Any]) -> str:
#     """
#     Generate domain-aware fallback structure (PATTERN 5).
#     """
#     control_type = field.get('control_type', field['type'])
#     field_key = sanitize_field_key(field['name'])

#     if control_type == 'text':
#         return f'{{"{field_key}": "NR"}}'

#     elif control_type == 'number':
#         return f'{{"{field_key}": "NR"}}'

#     elif control_type == 'dropdown':
#         return f'{{"{field_key}": "NR"}}'

#     elif control_type == 'checkbox_group_with_text':
#         options = field.get('options', [])
#         fallback_items = []
#         for opt in options:
#             opt_key = sanitize_field_key(opt)
#             fallback_items.append(
#                 f'                "{opt_key}": {{"selected": False, "value": ""}}')

#         return "{\n" + ",\n".join(fallback_items) + "\n            }"

#     return f'{{"{field_key}": ""}}'


# def generate_signature_class(field: Dict[str, Any], form_name: str, form_description: str) -> str:
#     """
#     Generate individual signature class for one field (PATTERN 1 & 2).
#     """
#     sanitized_form = sanitize_form_name(form_name)
#     field_name_pascal = ''.join(word.capitalize()
#                                 for word in field['name'].split('_'))
#     class_name = f"Extract{field_name_pascal}"

#     field_key = sanitize_field_key(field['name'])
#     control_type = field.get('control_type', field['type'])

#     # PATTERN 1: Rich three-layer documentation
#     layer_1_purpose = f"Extract {field['name']} from the document."

#     layer_2_form_context = f"""Form Context:
#     - Field: "{field['name']}"
#     - Control Type: {control_type}
#     - Part of: {form_name} form
#     - Description: {field.get('description', 'No description provided')}"""

#     if control_type == 'checkbox_group_with_text':
#         options_str = ', '.join(field.get('options', []))
#         layer_2_form_context += f"\n    - Options: {options_str}"
#     elif control_type == 'dropdown':
#         options_str = ', '.join(field.get('options', []))
#         layer_2_form_context += f"\n    - Options: {options_str}"

#     layer_3_domain = f"""Domain Context:
#     This field is part of {form_name.lower()} extraction, which is used for: {form_description}
#     Extract this information accurately from the source document."""

#     docstring = f'''"""
#     {layer_1_purpose}

#     {layer_2_form_context}

#     {layer_3_domain}
#     """'''

#     # PATTERN 2: Hyper-detailed output field description
#     output_desc = f'''"""JSON string with {field['name']} information.

#         Structure:
#         {generate_json_schema(field)}

#         Rules:
#         {generate_extraction_rules(field)}

#         Examples:
#         {generate_examples(field)}

#         Edge Cases:
#         - Always return valid JSON
#         - Use "NR" for not reported or unclear cases
#         - Preserve data types (numbers as numbers, text as strings)
#         - For missing data, use appropriate null representation based on type
#         """'''

#     # Determine if this field needs context
#     has_context = field.get('_depends_on', [])

#     if has_context:
#         context_params = "\n".join([
#             f'    {dep}_context: str = dspy.InputField(desc="Context from {dep} extraction")'
#             for dep in has_context
#         ])

#         signature_code = f'''
# class {class_name}(dspy.Signature):
#     {docstring}

#     markdown_content: str = dspy.InputField(
#         desc="Full markdown content of the source document"
#     )
# {context_params}

#     {field_key}_json: str = dspy.OutputField(
#         desc={output_desc}
#     )
# '''
#     else:
#         signature_code = f'''
# class {class_name}(dspy.Signature):
#     {docstring}

#     markdown_content: str = dspy.InputField(
#         desc="Full markdown content of the source document"
#     )

#     {field_key}_json: str = dspy.OutputField(
#         desc={output_desc}
#     )
# '''

#     return signature_code


# def generate_combiner_signature(fields: List[Dict[str, Any]], form_name: str) -> str:
#     """
#     Generate combiner signature that merges all extracted fields (PATTERN 8).
#     """
#     sanitized_form = sanitize_form_name(form_name)
#     class_name = f"Combine{sanitized_form}Data"

#     # Generate input fields for each extracted component
#     input_fields = []
#     for field in fields:
#         field_key = sanitize_field_key(field['name'])
#         input_fields.append(
#             f'    {field_key}_json: str = dspy.InputField(desc="JSON from Extract{sanitize_form_name(field["name"])}")'
#         )

#     # Generate complete output schema
#     output_schema_items = []
#     for field in fields:
#         field_key = sanitize_field_key(field['name'])
#         control_type = field.get('control_type', field['type'])

#         if control_type == 'checkbox_group_with_text':
#             options = field.get('options', [])
#             for opt in options:
#                 opt_key = sanitize_field_key(opt)
#                 output_schema_items.append(
#                     f'            "{opt_key}": {{"selected": bool, "value": string}}')
#         else:
#             output_schema_items.append(f'            "{field_key}": value')

#     output_schema = "{\n" + ",\n".join(output_schema_items) + "\n        }"

#     combiner_code = f'''
# class {class_name}(dspy.Signature):
#     """Combine all extracted {form_name} components into single comprehensive record."""

# {chr(10).join(input_fields)}

#     complete_{sanitized_form.lower()}_json: str = dspy.OutputField(
#         desc="""Merge all input data into a single JSON object with this structure:
#         {output_schema}

#         Simply merge all fields from the inputs, preserving all nested structures and field names exactly as provided.
#         Parse JSON inputs to extract their fields into the appropriate top-level or nested structures.
#         Ensure all field names match the expected schema exactly."""
#     )
# '''

#     return combiner_code


# def generate_signatures_file(form_name: str, form_description: str, fields: List[Dict[str, Any]]) -> str:
#     """
#     Generate complete signatures.py file with all signature classes.
#     """
#     sanitized_form = sanitize_form_name(form_name)

#     # Add dependency information to fields
#     dependencies = analyze_field_dependencies(fields)
#     for field in fields:
#         field['_depends_on'] = list(dependencies[field['name']])

#     # Generate header
#     code = f'''"""
# DSPy Signatures for {sanitized_form}
# Auto-generated with production-grade patterns
# """

# import dspy


# # ============================================================================
# # INDIVIDUAL FIELD SIGNATURES
# # ============================================================================

# '''

#     # Generate individual signature for each field
#     for field in fields:
#         code += generate_signature_class(field, form_name, form_description)
#         code += "\n"

#     # Generate combiner signature
#     code += '''
# # ============================================================================
# # COMBINER SIGNATURE
# # ============================================================================

# '''
#     code += generate_combiner_signature(fields, form_name)

#     # Generate __all__ export
#     class_names = []
#     for field in fields:
#         field_name_pascal = ''.join(word.capitalize()
#                                     for word in field['name'].split('_'))
#         class_names.append(f"Extract{field_name_pascal}")
#     class_names.append(f"Combine{sanitized_form}Data")

#     code += f'''

# __all__ = [
#     {','.join([f'"{name}"' for name in class_names])}
# ]
# '''

#     return code


# def generate_extractor_module(field: Dict[str, Any], form_name: str) -> str:
#     """
#     Generate async extractor module for one field (PATTERN 5 & 6).
#     """
#     field_name_pascal = ''.join(word.capitalize()
#                                 for word in field['name'].split('_'))
#     class_name = f"Async{field_name_pascal}Extractor"
#     signature_class = f"Extract{field_name_pascal}"
#     field_key = sanitize_field_key(field['name'])
#     control_type = field.get('control_type', field['type'])

#     has_context = field.get('_depends_on', [])

#     # Determine return type based on control type
#     if control_type in ['text', 'dropdown']:
#         return_type = 'str'
#         fallback_value = '"NR"'
#     elif control_type == 'number':
#         return_type = 'Any'  # Can be int, float, or "NR"
#         fallback_value = '"NR"'
#     else:  # checkbox_group_with_text
#         return_type = 'Dict[str, Any]'
#         fallback_value = generate_fallback_structure(field)

#     # Generate __call__ parameters
#     if has_context:
#         call_params = ', '.join(
#             ['markdown_content: str'] + [f'{dep}_context: str' for dep in has_context])
#         extract_params = ', '.join(['markdown_content=markdown_content'] + [
#                                    f'{dep}_context={dep}_context' for dep in has_context])
#     else:
#         call_params = 'markdown_content: str'
#         extract_params = 'markdown_content=markdown_content'

#     extractor_code = f'''
# class {class_name}(dspy.Module):
#     """Async module to extract {field['name']}."""

#     def __init__(self):
#         super().__init__()
#         self.extract = dspy.ChainOfThought({signature_class})

#     async def __call__(self, {call_params}) -> {return_type}:
#         loop = asyncio.get_running_loop()

#         def _extract():
#             return self.extract({extract_params})

#         try:
#             result = await loop.run_in_executor(None, _extract)
#             return safe_json_parse(result.{field_key}_json)
#         except Exception as e:
#             print(f"Error in {field['name']} extraction: {{e}}")
#             return {fallback_value}

#     def forward_sync(self, {call_params}) -> {return_type}:
#         """Synchronous version for DSPy optimizers."""
#         result = self.extract({extract_params})
#         return safe_json_parse(result.{field_key}_json)
# '''

#     return extractor_code


# def generate_combiner_module(fields: List[Dict[str, Any]], form_name: str) -> str:
#     """
#     Generate combiner module (PATTERN 8).
#     """
#     sanitized_form = sanitize_form_name(form_name)
#     class_name = f"Async{sanitized_form}Combiner"
#     signature_class = f"Combine{sanitized_form}Data"

#     # Generate __call__ parameters
#     param_names = [f"{sanitize_field_key(f['name'])}" for f in fields]
#     params = ', '.join([f"{name}: Any" for name in param_names])

#     # Generate combiner call arguments
#     combiner_args = []
#     for field in fields:
#         field_key = sanitize_field_key(field['name'])
#         combiner_args.append(f'{field_key}_json=json.dumps({field_key})')

#     combiner_args_str = ',\n                '.join(combiner_args)

#     # Generate fallback merge
#     fallback_updates = '\n            '.join(
#         [f'combined.update({name})' for name in param_names])

#     combiner_code = f'''
# class {class_name}(dspy.Module):
#     """Async module to combine all {form_name} data."""

#     def __init__(self):
#         super().__init__()
#         self.combiner = dspy.ChainOfThought({signature_class})

#     async def __call__(self, {params}) -> Dict[str, Any]:
#         loop = asyncio.get_running_loop()

#         def _combine():
#             return self.combiner(
#                 {combiner_args_str}
#             )

#         try:
#             result = await loop.run_in_executor(None, _combine)
#             return safe_json_parse(result.complete_{sanitized_form.lower()}_json)
#         except Exception as e:
#             print(f"Error in combining {form_name} data: {{e}}, using fallback merge")
#             combined = {{}}
#             {fallback_updates}
#             return combined

#     def forward_sync(self, {params}) -> Dict[str, Any]:
#         """Synchronous version for DSPy optimizers."""
#         result = self.combiner(
#             {combiner_args_str}
#         )
#         return safe_json_parse(result.complete_{sanitized_form.lower()}_json)
# '''

#     return combiner_code


# def generate_pipeline_module(fields: List[Dict[str, Any]], form_name: str, dependencies: Dict[str, Set[str]]) -> str:
#     """
#     Generate complete async pipeline with dependency-aware execution (PATTERN 4).
#     """
#     sanitized_form = sanitize_form_name(form_name)
#     pipeline_class = f"Async{sanitized_form}Pipeline"

#     stage_1, stage_2, stage_3 = categorize_fields_by_stage(
#         fields, dependencies)

#     # Generate extractor initializations
#     extractor_inits = []
#     for field in fields:
#         field_name_pascal = ''.join(word.capitalize()
#                                     for word in field['name'].split('_'))
#         field_key = sanitize_field_key(field['name'])
#         extractor_inits.append(
#             f"        self.{field_key}_extractor = Async{field_name_pascal}Extractor()"
#         )
#     extractor_inits.append(
#         f"        self.combiner = Async{sanitized_form}Combiner()")

#     # Generate Stage 1 (Context fields - sequential)
#     stage_1_code = []
#     stage_1_results = {}
#     if stage_1:
#         stage_1_code.append(
#             "        # Stage 1: Extract context fields (sequential)")
#         for field in stage_1:
#             field_key = sanitize_field_key(field['name'])
#             stage_1_code.append(
#                 f"        {field_key} = await self.{field_key}_extractor(markdown_content)")
#             stage_1_results[field['name']] = field_key

#     # Generate Stage 2 (Independent fields - parallel)
#     stage_2_code = []
#     stage_2_tasks = []
#     if stage_2:
#         stage_2_code.append(
#             "\n        # Stage 2: Extract independent fields (parallel)")
#         for field in stage_2:
#             field_key = sanitize_field_key(field['name'])
#             stage_2_code.append(
#                 f"        {field_key}_task = self.{field_key}_extractor(markdown_content)")
#             stage_2_tasks.append(field_key)

#     # Generate Stage 3 (Dependent fields - parallel)
#     stage_3_code = []
#     stage_3_tasks = []
#     if stage_3:
#         stage_3_code.append(
#             "\n        # Stage 3: Extract dependent fields (parallel)")
#         for field in stage_3:
#             field_key = sanitize_field_key(field['name'])
#             deps = dependencies[field['name']]
#             context_args = ', '.join([f"{sanitize_field_key(dep)}_context=json.dumps({stage_1_results[dep]})"
#                                      for dep in deps if dep in stage_1_results])
#             if context_args:
#                 stage_3_code.append(
#                     f"        {field_key}_task = self.{field_key}_extractor(markdown_content, {context_args})")
#             else:
#                 stage_3_code.append(
#                     f"        {field_key}_task = self.{field_key}_extractor(markdown_content)")
#             stage_3_tasks.append(field_key)

#     # Generate gather statement
#     all_tasks = stage_2_tasks + stage_3_tasks
#     if all_tasks:
#         gather_code = f"\n        # Stage 4: Gather all parallel tasks\n"
#         gather_code += f"        {', '.join(all_tasks)} = await asyncio.gather(\n"
#         gather_code += ',\n'.join(
#             [f"            {task}_task" for task in all_tasks])
#         gather_code += "\n        )"
#     else:
#         gather_code = ""

#     # Generate combiner call
#     all_field_keys = [sanitize_field_key(f['name']) for f in fields]
#     combiner_call = f"\n        # Stage 5: Combine all data\n"
#     combiner_call += f"        complete_{sanitized_form.lower()} = await self.combiner(\n"
#     combiner_call += ',\n'.join(
#         [f"            {key}" for key in all_field_keys])
#     combiner_call += "\n        )"

#     pipeline_code = f'''
# class {pipeline_class}(dspy.Module):
#     """Complete async pipeline for extracting {form_name} with intelligent dependency handling."""

#     def __init__(self, max_concurrent: int = 5):
#         super().__init__()

# {chr(10).join(extractor_inits)}

#         self.max_concurrent = max_concurrent
#         self._semaphore = None

#     def _get_semaphore(self):
#         if self._semaphore is None:
#             self._semaphore = asyncio.Semaphore(self.max_concurrent)
#         return self._semaphore

#     async def forward(self, markdown_content: str):
# {chr(10).join(stage_1_code)}
# {chr(10).join(stage_2_code)}
# {chr(10).join(stage_3_code)}
# {gather_code}
# {combiner_call}

#         return dspy.Prediction(
#             {sanitized_form.lower()}=complete_{sanitized_form.lower()},
#             success=True
#         )

#     async def __call__(self, markdown_content: str):
#         return await self.forward(markdown_content)
# '''

#     return pipeline_code


# def generate_sync_wrapper(form_name: str, fields: List[Dict[str, Any]]) -> str:
#     """
#     Generate synchronous wrapper for async pipeline (PATTERN 6).
#     """
#     sanitized_form = sanitize_form_name(form_name)
#     sync_class = f"Sync{sanitized_form}Pipeline"
#     async_class = f"Async{sanitized_form}Pipeline"

#     # Generate extractor exposures
#     extractor_exposures = []
#     for field in fields:
#         field_key = sanitize_field_key(field['name'])
#         extractor_exposures.append(
#             f"        self.{field_key}_extractor = self.async_pipeline.{field_key}_extractor"
#         )
#     extractor_exposures.append(
#         "        self.combiner = self.async_pipeline.combiner")

#     sync_code = f'''
# class {sync_class}(dspy.Module):
#     """Synchronous wrapper for async {form_name} pipeline (for DSPy optimizers)."""

#     def __init__(self):
#         super().__init__()
#         self.async_pipeline = {async_class}()

#         # Expose extractors for optimizer access
# {chr(10).join(extractor_exposures)}

#     def forward(self, markdown_content: str):
#         """Execute pipeline synchronously."""
#         try:
#             loop = asyncio.get_running_loop()
#             if loop.is_running():
#                 try:
#                     import nest_asyncio
#                     nest_asyncio.apply()
#                 except ImportError:
#                     raise ImportError(
#                         "Please install nest_asyncio: pip install nest_asyncio"
#                     )
#         except RuntimeError:
#             pass

#         self.async_pipeline._semaphore = None
#         result = asyncio.run(self.async_pipeline(markdown_content))
#         return result

#     def __deepcopy__(self, memo):
#         """Required for DSPy optimization."""
#         return {sync_class}()
# '''

#     return sync_code


# def generate_modules_file(form_name: str, fields: List[Dict[str, Any]]) -> str:
#     """
#     Generate complete modules.py file with all module classes.
#     """
#     sanitized_form = sanitize_form_name(form_name)

#     # Add dependency information
#     dependencies = analyze_field_dependencies(fields)
#     for field in fields:
#         field['_depends_on'] = list(dependencies[field['name']])

#     # Generate header
#     code = f'''"""
# DSPy Modules for {sanitized_form}
# Auto-generated with production-grade async patterns
# """

# import asyncio
# import json
# from typing import Dict, Any

# import dspy

# from utils.json_parser import safe_json_parse
# from .signatures import (
# '''

#     # Import all signatures
#     for field in fields:
#         field_name_pascal = ''.join(word.capitalize()
#                                     for word in field['name'].split('_'))
#         code += f"    Extract{field_name_pascal},\n"
#     code += f"    Combine{sanitized_form}Data,\n"
#     code += ")\n\n"

#     # Generate individual extractors
#     code += '''
# # ============================================================================
# # INDIVIDUAL FIELD EXTRACTORS
# # ============================================================================

# '''
#     for field in fields:
#         code += generate_extractor_module(field, form_name)
#         code += "\n"

#     # Generate combiner
#     code += '''
# # ============================================================================
# # COMBINER MODULE
# # ============================================================================

# '''
#     code += generate_combiner_module(fields, form_name)
#     code += "\n"

#     # Generate async pipeline
#     code += '''
# # ============================================================================
# # ASYNC PIPELINE
# # ============================================================================

# '''
#     code += generate_pipeline_module(fields, form_name, dependencies)
#     code += "\n"

#     # Generate sync wrapper
#     code += '''
# # ============================================================================
# # SYNC WRAPPER (for DSPy optimizers)
# # ============================================================================

# '''
#     code += generate_sync_wrapper(form_name, fields)
#     code += "\n"

#     # Generate __all__ export
#     class_names = []
#     for field in fields:
#         field_name_pascal = ''.join(word.capitalize()
#                                     for word in field['name'].split('_'))
#         class_names.append(f"Async{field_name_pascal}Extractor")
#     class_names.extend([
#         f"Async{sanitized_form}Combiner",
#         f"Async{sanitized_form}Pipeline",
#         f"Sync{sanitized_form}Pipeline"
#     ])

#     code += f'''
# __all__ = [
#     {','.join([f'"{name}"' for name in class_names])}
# ]
# '''

#     return code


# def create_task_directory(project_id: str, form_id: str, form_data: Dict[str, Any]) -> Path:
#     """
#     Create complete task directory with production-grade signatures and modules.
#     """
#     # Create task directory name
#     task_name = f"dynamic_{project_id}_{form_id}"
#     task_dir = Path(__file__).parent / "dspy_components" / "tasks" / task_name

#     # Create directory
#     task_dir.mkdir(parents=True, exist_ok=True)

#     # Extract form info
#     form_name = form_data['name']
#     form_description = form_data.get(
#         'description', f'Extract {form_name} data')
#     fields = form_data.get('fields', [])

#     print(f"🤖 Generating production-grade DSPy code for {form_name}...")

#     # Generate signatures.py
#     print("   Generating signatures.py (Pattern-based)...")
#     signature_code = generate_signatures_file(
#         form_name, form_description, fields)
#     signature_file = task_dir / "signatures.py"
#     signature_file.write_text(signature_code)

#     # Generate modules.py
#     print("   Generating modules.py (Pattern-based)...")
#     module_code = generate_modules_file(form_name, fields)
#     module_file = task_dir / "modules.py"
#     module_file.write_text(module_code)

#     # Create __init__.py
#     init_file = task_dir / "__init__.py"
#     init_file.write_text("")

#     # Save metadata.json for persistence
#     metadata = {
#         "project_id": project_id,
#         "form_id": form_id,
#         "form_data": form_data
#     }
#     metadata_file = task_dir / "metadata.json"
#     metadata_file.write_text(json.dumps(metadata, indent=2))

#     print(f"✅ Created task directory: {task_dir}")

#     return task_dir


# def load_dynamic_schemas():
#     """
#     Discover and register all dynamic schemas from dspy_components/tasks.
#     Should be called on application startup.
#     """
#     tasks_dir = Path(__file__).parent / "dspy_components" / "tasks"
#     if not tasks_dir.exists():
#         print(f"⚠️ Tasks directory not found: {tasks_dir}")
#         return

#     print(f"🔄 Loading dynamic schemas from {tasks_dir}...")
#     count = 0
#     errors = []

#     for task_dir in tasks_dir.iterdir():
#         if task_dir.is_dir() and task_dir.name.startswith("dynamic_"):
#             metadata_file = task_dir / "metadata.json"
#             if metadata_file.exists():
#                 try:
#                     metadata = json.loads(metadata_file.read_text())
#                     schema_name = register_dynamic_schema(
#                         metadata['project_id'],
#                         metadata['form_id'],
#                         metadata['form_data']
#                     )
#                     print(f"   ✅ Loaded: {schema_name}")
#                     count += 1
#                 except Exception as e:
#                     error_msg = f"Failed to load {task_dir.name}: {str(e)}"
#                     print(f"   ❌ {error_msg}")
#                     errors.append(error_msg)
#                     import traceback
#                     traceback.print_exc()
#             else:
#                 print(f"   ⚠️ No metadata.json in {task_dir.name}")

#     print(f"✅ Loaded {count} dynamic schemas.")
#     if errors:
#         print(f"⚠️ {len(errors)} schemas failed to load:")
#         for err in errors:
#             print(f"   - {err}")

#     return {"loaded": count, "errors": errors}


# def register_dynamic_schema(project_id: str, form_id: str, form_data: Dict[str, Any]) -> str:
#     """
#     Register dynamically generated schema in the schema registry.
#     """
#     from schemas.configs import SCHEMA_CONFIGS, SchemaConfig

#     task_name = f"dynamic_{project_id}_{form_id}"
#     form_name = form_data['name']

#     # Sanitize form name for class lookups
#     sanitized_name = sanitize_form_name(form_name)

#     # Check if already registered
#     if task_name in SCHEMA_CONFIGS:
#         return task_name

#     # Import the generated modules dynamically
#     try:
#         task_dir = Path(__file__).parent / \
#             "dspy_components" / "tasks" / task_name
#         if str(task_dir.parent) not in sys.path:
#             sys.path.insert(0, str(task_dir.parent))

#         importlib.invalidate_caches()

#         sig_module = importlib.import_module(
#             f"dspy_components.tasks.{task_name}.signatures"
#         )
#         mod_module = importlib.import_module(
#             f"dspy_components.tasks.{task_name}.modules"
#         )

#         importlib.reload(sig_module)
#         importlib.reload(mod_module)

#         # Get the classes
#         sig_class_name = f"Combine{sanitized_name}Data"
#         mod_class_name = f"Sync{sanitized_name}Pipeline"

#         if not hasattr(sig_module, sig_class_name):
#             print(
#                 f"⚠️ Could not find exact class {sig_class_name}, searching...")
#             for name, obj in vars(sig_module).items():
#                 if isinstance(obj, type) and issubclass(obj, dspy.Signature) and obj is not dspy.Signature:
#                     sig_class_name = name
#                     print(f"   Found signature class: {sig_class_name}")
#                     break

#         sig_class = getattr(sig_module, sig_class_name)
#         mod_class = getattr(mod_module, mod_class_name)

#         # Register in SCHEMA_CONFIGS
#         SCHEMA_CONFIGS[task_name] = SchemaConfig(
#             name=task_name,
#             description=form_data.get(
#                 'description', f'Dynamically generated: {sanitized_name}'),
#             signature_class=sig_class,
#             pipeline_class=mod_class,
#             output_field_name=f"complete_{sanitized_name.lower()}_json",
#             cache_file=f"schemas/generated_fields/{task_name}_fields.json",
#         )

#         print(f"✅ Registered schema: {task_name}")
#         print(f"   - Signature: {sig_class_name}")
#         print(f"   - Pipeline: {mod_class_name}")

#         # Refresh registry
#         try:
#             from schemas.registry import refresh_registry
#             updated_schemas = refresh_registry()
#             print(
#                 f"   - Registry refreshed: {len(updated_schemas)} total schemas")
#         except Exception as e:
#             print(f"   - Registry refresh warning: {e}")

#         return task_name

#     except Exception as e:
#         print(f"❌ Error registering schema: {e}")
#         raise


# def generate_task_from_form(project_id: str, form_id: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Complete workflow: Generate task directory and register schema.
#     """
#     try:
#         # Create task directory with production-grade code
#         task_dir = create_task_directory(project_id, form_id, form_data)

#         # Register schema
#         schema_name = register_dynamic_schema(project_id, form_id, form_data)

#         return {
#             'status': 'success',
#             'task_dir': str(task_dir),
#             'schema_name': schema_name,
#             'form_name': form_data['name']
#         }

#     except Exception as e:
#         import traceback
#         return {
#             'status': 'error',
#             'error': str(e),
#             'traceback': traceback.format_exc()
#         }


# # Example usage
# if __name__ == "__main__":
#     # Test with a complex form showcasing all control types
#     sample_form = {
#         'name': 'TrialCharacteristics',
#         'description': 'Trial design and methodology information for systematic reviews',
#         'fields': [
#             {
#                 'name': 'study_design',
#                 'type': 'text',
#                 'control_type': 'dropdown',
#                 'description': 'Type of study design used in the trial',
#                 'required': True,
#                 'options': ['RCT', 'Cohort Study', 'Case-Control Study', 'Cross-Sectional', 'Other']
#             },
#             {
#                 'name': 'sample_size',
#                 'type': 'number',
#                 'control_type': 'number',
#                 'description': 'Total number of participants enrolled at baseline',
#                 'required': True
#             },
#             {
#                 'name': 'baseline_demographics',
#                 'type': 'object',
#                 'control_type': 'checkbox_group_with_text',
#                 'description': 'Baseline demographic characteristics of enrolled participants',
#                 'required': True,
#                 'options': [
#                     'Total participants (N)',
#                     'Female (N)',
#                     'Female (%)',
#                     'Male (N)',
#                     'Male (%)',
#                     'Mean age (years)',
#                     'Age range (years)'
#                 ]
#             },
#             {
#                 'name': 'intervention_description',
#                 'type': 'text',
#                 'control_type': 'text',
#                 'description': 'Detailed description of the intervention being tested',
#                 'required': True
#             }
#         ]
#     }

#     print("Testing Production-Grade DSPy Code Generator...")
#     print("=" * 80)

#     result = generate_task_from_form(
#         project_id="test_project",
#         form_id="form_prod_001",
#         form_data=sample_form
#     )

#     print("\nResult:")
#     print(json.dumps(result, indent=2))

#     if result['status'] == 'success':
#         print("\n" + "=" * 80)
#         print("Generated Code Preview:")
#         print("=" * 80)

#         # Show generated signatures.py
#         sig_file = Path(result['task_dir']) / "signatures.py"
#         if sig_file.exists():
#             print("\n📄 signatures.py:")
#             print(sig_file.read_text()[:1000] + "...\n")

#         # Show generated modules.py
#         mod_file = Path(result['task_dir']) / "modules.py"
#         if mod_file.exists():
#             print("\n📄 modules.py:")
#             print(mod_file.read_text()[:1000] + "...")
