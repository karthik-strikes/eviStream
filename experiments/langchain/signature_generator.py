"""
DSPy Signature & Module Generator with Production-Ready Architecture

Redesigned following best practices from index_test, missing_data_study, 
outcomes_study, patient_population, and reference_standard implementations.

Key Design Principles:
1. Granular Signatures - One signature per extraction task
2. Contextual Inputs - Provide necessary context for accurate extraction
3. Structured Outputs - Mirror domain structure with nested JSON
4. Rich Instructions - Structure + Rules + Examples
5. Async-Ready - Built for parallel execution
6. Error Recovery - Fallbacks at every level
7. Domain-Aware - Medical research domain knowledge embedded
"""

import os
import json
import asyncio
from typing import TypedDict, Annotated, Dict, Any, List, Optional, Literal
from pathlib import Path
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy, ProviderStrategy
from langchain.tools import tool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


# ============================================================================
# STRUCTURED OUTPUT SCHEMAS (Pydantic Models)
# ============================================================================

class FieldAnalysisSchema(BaseModel):
    """Structured output schema for field analysis"""
    field_name: str = Field(description="Original field name")
    sanitized_name: str = Field(description="Snake_case field name")
    field_type: Literal["input", "output"] = Field(
        description="Whether this is an input or output field")
    data_type: str = Field(
        description="Python type hint (str, int, bool, Dict[str, Any], etc.)")
    extraction_pattern: str = Field(
        description="Pattern key from EXTRACTION_PATTERNS")
    requires_context: bool = Field(
        description="Whether this field needs context from other extractions")
    context_fields: List[str] = Field(
        default_factory=list, description="List of context field names if required")
    description: str = Field(
        description="Detailed description for LLM guidance")


class SignatureCodeSchema(BaseModel):
    """Structured output schema for generated signature code"""
    code: str = Field(
        description="Complete Python code for the DSPy signature")
    class_name: str = Field(description="Name of the signature class")
    has_examples: bool = Field(
        description="Whether the code includes example outputs")
    field_count: int = Field(description="Number of fields in the signature")


class ModuleCodeSchema(BaseModel):
    """Structured output schema for generated module code"""
    code: str = Field(
        description="Complete Python code for the async DSPy module")
    class_name: str = Field(description="Name of the module class")
    has_error_handling: bool = Field(
        description="Whether error handling is implemented")
    is_async: bool = Field(description="Whether the module is async")


# ============================================================================
# STATE DEFINITION FOR LANGGRAPH WORKFLOW
# ============================================================================

class SignatureGenerationState(TypedDict):
    """State for the signature generation workflow"""
    # Input
    questionnaire_spec: Dict[str, Any]
    max_attempts: int

    # Workflow state
    blueprint: Optional[Dict[str, Any]]
    code: str
    validation_feedback: str
    attempt: int
    errors: List[str]
    warnings: List[str]
    is_valid: bool

    # Human-in-the-loop
    human_feedback: Optional[str]
    needs_human_review: bool

    # Output
    result: Optional[Dict[str, Any]]
    status: str  # "in_progress", "completed", "failed", "needs_review"


# ============================================================================
# DOMAIN KNOWLEDGE - Medical Research Extraction Patterns
# ============================================================================

EXTRACTION_PATTERNS = {
    "checkbox_group_with_text": {
        "structure": '{"option_name": {"selected": true/false, "comment": "details"}}',
        "example": '{"cytology": {"selected": true, "comment": "Oral brush biopsy"}}',
        "description": "For multiple-choice questions with text boxes for details"
    },
    "simple_text": {
        "structure": '"field_name": "extracted text or NR"',
        "example": '"brand_name": "VELscope"',
        "description": "For simple text extraction fields"
    },
    "numeric_with_ci": {
        "structure": '{"value": number, "confidence_interval": "lower-upper"}',
        "example": '{"reported_sensitivity": 95.08, "reported_sensitivity_ci": "85.2-98.4"}',
        "description": "For metrics with confidence intervals"
    },
    "count_data": {
        "structure": '{"field_name": number_or_"NR"}',
        "example": '{"patients_received_n": 100, "patients_analyzed_n": 95}',
        "description": "For patient/lesion counts"
    },
    "nested_hierarchy": {
        "structure": '{"category": {"subcategory": {"selected": bool, "comment": str}}}',
        "example": '{"population": {"innocuous_lesions": {"selected": true, "comment": "details"}}}',
        "description": "For hierarchical categorizations"
    },
    "confusion_matrix": {
        "structure": '{"true_positives": number, "false_positives": number, ...}',
        "example": '{"true_positives": 58, "false_positives": 7, "false_negatives": 3, "true_negatives": 32}',
        "description": "For diagnostic test performance metrics"
    }
}

MEDICAL_DOMAIN_CONTEXT = {
    "index_test": "The diagnostic test being evaluated (e.g., cytology, vital staining, autofluorescence)",
    "reference_standard": "Gold standard diagnostic test (typically histopathological biopsy)",
    "positivity_threshold": "Criteria defining positive (disease) vs negative (no disease) test results",
    "sensitivity": "Ability to correctly identify disease (TP / (TP + FN))",
    "specificity": "Ability to correctly identify non-disease (TN / (TN + FP))",
    "verification_bias": "When not all patients receive both index test and reference standard",
    "blinding": "Whether examiners are unaware of other test results to prevent bias",
    "OPMD": "Oral Potentially Malignant Disorder (dysplasia, leukoplakia, etc.)",
    "OSCC": "Oral Squamous Cell Carcinoma",
    "NR": "Not Reported - standard convention for missing data"
}

COMMON_FIELD_PATTERNS = {
    "patient_counts": ["patients_received_n", "patients_analyzed_n"],
    "lesion_counts": ["lesions_received_n", "lesions_analyzed_n"],
    "gender_distribution": ["female_n", "female_percent", "male_n", "male_percent"],
    "age_metrics": ["mean", "median", "sd", "range"],
    "diagnostic_metrics": ["sensitivity", "specificity", "ppv", "npv"],
    "confusion_matrix": ["true_positives", "false_positives", "false_negatives", "true_negatives"]
}


# ============================================================================
# STRUCTURED OUTPUTS (Pydantic Models)
# ============================================================================

class FieldAnalysis(BaseModel):
    """Analysis of a single field for signature generation"""
    field_name: str = Field(
        description="Original field name from questionnaire")
    sanitized_name: str = Field(
        description="Python-safe snake_case field name")
    field_type: Literal["input", "output"] = Field(
        description="Whether this is input or output field")
    data_type: str = Field(
        description="Python type hint (str, int, Dict[str, Any], etc.)")
    extraction_pattern: str = Field(
        description="Pattern type from EXTRACTION_PATTERNS")
    requires_context: bool = Field(
        description="Whether extraction needs previous results as context")
    context_fields: List[str] = Field(
        default_factory=list, description="Names of context fields needed")
    description: str = Field(description="Detailed description for the field")


class SignatureBlueprint(BaseModel):
    """Complete blueprint for a DSPy signature"""
    class_name: str = Field(description="PascalCase signature class name")
    docstring: str = Field(
        description="Comprehensive class docstring with domain context")
    input_fields: List[FieldAnalysis] = Field(description="All input fields")
    output_fields: List[FieldAnalysis] = Field(description="All output fields")
    extraction_complexity: Literal["simple", "medium", "complex"] = Field(
        description="Complexity level")
    domain_context: Dict[str, str] = Field(
        default_factory=dict, description="Relevant domain knowledge")


class DSPySignatureCode(BaseModel):
    """Generated DSPy signature code"""
    class_name: str = Field(description="Name of the signature class")
    code: str = Field(description="Complete Python code for the signature")
    imports: List[str] = Field(
        default_factory=list, description="Required imports")
    validation_status: bool = Field(
        default=False, description="Whether code passed validation")


class DSPyModuleCode(BaseModel):
    """Generated DSPy module code"""
    module_class_name: str = Field(
        description="Name of the async module class")
    signature_class_name: str = Field(
        description="Name of the signature it wraps")
    code: str = Field(description="Complete Python code for the async module")
    has_sync_method: bool = Field(
        default=True, description="Whether forward_sync is included")
    error_fallback: Dict[str, Any] = Field(
        description="Default fallback structure")


class PipelineBlueprint(BaseModel):
    """Blueprint for a complete extraction pipeline"""
    pipeline_name: str = Field(description="Name of the pipeline")
    signatures: List[str] = Field(description="List of signature class names")
    modules: List[str] = Field(description="List of module class names")
    dependency_graph: Dict[str, List[str]] = Field(
        description="Which modules depend on which")
    parallel_phases: List[List[str]] = Field(
        description="Groups of modules that can run in parallel")
    combiner_needed: bool = Field(
        default=True, description="Whether a combiner signature is needed")


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

class SignatureValidator:
    """Comprehensive validation for generated DSPy signatures"""

    @staticmethod
    def validate_signature(code: str) -> tuple[bool, List[str]]:
        """
        Validate generated DSPy signature code with detailed checks.
        Returns (is_valid, list_of_errors)
        """
        errors = []

        # Check if code is valid string
        if not isinstance(code, str):
            return False, [f"❌ Invalid code type: expected str, got {type(code).__name__}"]

        if not code or not code.strip():
            return False, ["❌ Empty code generated"]

        # Basic structure checks
        if 'class ' not in code:
            errors.append("❌ Missing class definition")

        if 'dspy.Signature' not in code:
            errors.append("❌ Class must inherit from dspy.Signature")

        if 'dspy.InputField' not in code:
            errors.append("❌ Must have at least one dspy.InputField")

        if 'dspy.OutputField' not in code:
            errors.append("❌ Must have at least one dspy.OutputField")

        # Documentation checks
        if '"""' not in code and "'''" not in code:
            errors.append("❌ Missing class docstring")

        # Import checks
        if 'import dspy' not in code:
            errors.append("❌ Missing 'import dspy' statement")

        # Design pattern checks (based on real implementations)
        if 'dspy.OutputField' in code:
            # Check for detailed output descriptions
            if 'Structure:' not in code and 'structure' not in code.lower():
                errors.append(
                    "⚠️  Output field missing 'Structure:' section (recommended)")

            if 'Rules:' not in code and 'rules' not in code.lower():
                errors.append(
                    "⚠️  Output field missing 'Rules:' section (recommended)")

            if 'Examples:' not in code and 'examples' not in code.lower():
                errors.append(
                    "⚠️  Output field missing 'Examples:' section (recommended)")

        # Type hint checks
        if ': str = dspy.InputField' not in code and ': str = dspy.OutputField' not in code:
            errors.append(
                "⚠️  Missing type hints (recommended: field_name: str = dspy.InputField(...))")

        # Syntax validation
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            errors.append(f"❌ Syntax error: {str(e)}")

        # Advanced checks (based on best practices)
        if '"NR"' not in code and "'NR'" not in code:
            errors.append(
                "⚠️  Consider using 'NR' convention for Not Reported values")

        return len([e for e in errors if e.startswith('❌')]) == 0, errors

    @staticmethod
    def validate_module(code: str) -> tuple[bool, List[str]]:
        """Validate generated DSPy module code"""
        errors = []

        # Check if code is valid string
        if not isinstance(code, str):
            return False, [f"❌ Invalid code type: expected str, got {type(code).__name__}"]

        if not code or not code.strip():
            return False, ["❌ Empty code generated"]

        if 'dspy.Module' not in code:
            errors.append("❌ Class must inherit from dspy.Module")

        if 'async def __call__' not in code and 'def forward' not in code:
            errors.append("❌ Missing __call__ or forward method")

        if 'ChainOfThought' not in code and 'Predict' not in code:
            errors.append("❌ Must use ChainOfThought or Predict wrapper")

        if 'try:' not in code or 'except' not in code:
            errors.append("⚠️  Missing error handling (recommended)")

        if 'asyncio' in code and 'async def' not in code:
            errors.append("❌ Imports asyncio but has no async methods")

        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            errors.append(f"❌ Syntax error: {str(e)}")

        return len([e for e in errors if e.startswith('❌')]) == 0, errors


# ============================================================================
# SIGNATURE GENERATION - LLM-Powered with Domain Knowledge
# ============================================================================

class DSPySignatureGenerator:
    """
    Production-grade DSPy signature generator with LangGraph workflow and agent.

    Architecture:
    - LangGraph StateGraph for workflow orchestration
    - LangChain Agent with tools for generation
    - Human-in-the-loop capability via interrupt_before
    - State persistence with MemorySaver checkpointer

    Workflow Nodes:
    1. analyze_fields: Analyze questionnaire spec and create blueprint
    2. generate_code: Agent generates signature/module code
    3. validate_code: Validate generated code
    4. human_review: Optional human review point (interruptible)
    5. refine_code: Refine based on validation errors or human feedback
    6. finalize: Prepare final result
    """

    def __init__(self, model_name: str = "google_genai:gemini-3-pro-preview",
                 enable_human_review: bool = False):
        """
        Initialize with LLM, validation tools, and workflow graph.

        Args:
            model_name: LLM model identifier
            enable_human_review: Enable human-in-the-loop review step
        """
        self.model = init_chat_model(
            model=model_name,
            temperature=0.3,
            max_tokens=4000,
        )
        self.validator = SignatureValidator()
        self.checkpointer = MemorySaver()
        self.enable_human_review = enable_human_review

        # Create tools and agent
        self._create_tools()
        self._create_agent()

        # Build workflow graph
        self._build_workflow_graph()

    def _create_tools(self):
        """Create LangChain tools for signature generation"""
        model = self.model
        validator = self.validator

        @tool
        def analyze_field_tool(field_spec: str) -> str:
            """
            Analyze a field specification to determine extraction pattern and requirements.

            Args:
                field_spec: JSON spec of the field with name, type, description, options

            Returns:
                JSON with field analysis including pattern, context needs, data type
            """
            field_data = json.loads(field_spec)

            prompt = f"""Analyze this field for DSPy signature generation:

Field Specification:
{json.dumps(field_data, indent=2)}

Available Extraction Patterns:
{json.dumps(EXTRACTION_PATTERNS, indent=2)}

Medical Domain Context:
{json.dumps(MEDICAL_DOMAIN_CONTEXT, indent=2)}

Determine:
1. Which extraction pattern fits best?
2. What Python data type should this be? (str, int, bool, Dict[str, Any], List[str], etc.)
3. Does this need context from previous extractions? (e.g., index test type needed for specimen collection)
4. What detailed description should guide the LLM extraction?

Return JSON matching FieldAnalysis schema:
{{
    "field_name": "original name",
    "sanitized_name": "snake_case_name",
    "field_type": "input" or "output",
    "data_type": "Python type hint",
    "extraction_pattern": "pattern key from EXTRACTION_PATTERNS",
    "requires_context": true/false,
    "context_fields": ["field1", "field2"] if requires_context,
    "description": "Detailed description for LLM"
}}
"""

            result = model.invoke(prompt)
            content = result.content if result and hasattr(
                result, 'content') else None

            # Handle different response types
            if isinstance(content, list):
                # If content is a list, try to extract text from content blocks
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and 'text' in item:
                        text_parts.append(item['text'])
                    elif isinstance(item, str):
                        text_parts.append(item)
                    elif hasattr(item, 'text'):
                        text_parts.append(item.text)
                content = ''.join(text_parts) if text_parts else None

            # Check if content was generated
            if not content or not isinstance(content, str):
                raise ValueError(
                    f"Model returned invalid response: {type(content).__name__ if content else 'None'}")

            return content

        @tool
        def generate_signature_tool(blueprint_json: str, validation_feedback: str = "") -> str:
            """
            Generate a DSPy Signature class from a validated blueprint.

            Args:
                blueprint_json: SignatureBlueprint as JSON
                validation_feedback: Optional feedback from validation failures

            Returns:
                Complete Python code for the DSPy signature
            """
            blueprint = json.loads(blueprint_json)

            # Build examples from real implementations
            real_examples = self._get_real_signature_examples(
                blueprint.get('extraction_complexity', 'medium'))

            prompt = f"""Generate a production-quality DSPy Signature following these patterns:

BLUEPRINT:
{json.dumps(blueprint, indent=2)}

DOMAIN KNOWLEDGE:
{json.dumps(MEDICAL_DOMAIN_CONTEXT, indent=2)}

REAL-WORLD EXAMPLES (from production code):
{real_examples}

REQUIRED FORMAT:
```python
import dspy


class {blueprint['class_name']}(dspy.Signature):
    \"\"\"Extract [what this extracts].
    
    Form Question [N]: "[Original form question]"
    - [Any options or notes from the form]
    
    [Domain context explanation - what this data means in medical research]
    \"\"\"
    
    # INPUT FIELDS (with descriptive comments)
    input_field: str = dspy.InputField(
        desc="Description of what this input provides"
    )
    
    # OUTPUT FIELDS (with comprehensive descriptions)
    output_field: str = dspy.OutputField(
        desc=\"\"\"Description of output format.
        
        Structure:
        {{
            "field1": "value1",
            "field2": {{"nested": "structure"}}
        }}
        
        Rules:
        - Rule 1 about extraction logic
        - Rule 2 about handling edge cases
        - Use "NR" for Not Reported values
        
        Examples:
        {{"field1": "value1", "field2": {{"nested": "structure"}}}}
        {{"field1": "NR", "field2": {{"nested": ""}}}}
        \"\"\"
    )
```

CRITICAL REQUIREMENTS:
1. Class docstring MUST include:
   - What is being extracted
   - Form question context
   - Domain explanation
2. Input fields MUST have clear, concise descriptions
3. Output fields MUST have Structure + Rules + Examples sections
4. Use Type hints (str, int, Dict[str, Any], etc.)
5. Follow snake_case for field names
6. Include "NR" convention for missing data
7. Provide 2-3 realistic examples showing different cases

"""

            if validation_feedback:
                prompt += f"\n\nVALIDATION FEEDBACK (FIX THESE):\n{validation_feedback}\n"

            prompt += """
Generate ONLY the Python code, no explanations.
"""

            result = model.invoke(prompt)
            code = result.content if result and hasattr(
                result, 'content') else None

            # Handle different response types
            if isinstance(code, list):
                # If code is a list, try to extract text from content blocks
                text_parts = []
                for item in code:
                    if isinstance(item, dict) and 'text' in item:
                        text_parts.append(item['text'])
                    elif isinstance(item, str):
                        text_parts.append(item)
                    elif hasattr(item, 'text'):
                        text_parts.append(item.text)
                code = ''.join(text_parts) if text_parts else None

            # Check if code was generated
            if not code or not isinstance(code, str):
                raise ValueError(
                    f"Model returned invalid response: {type(code).__name__ if code else 'None'}")

            # Extract code from markdown if wrapped
            if '```python' in code:
                code = code.split('```python')[1].split('```')[0].strip()
            elif '```' in code:
                code = code.split('```')[1].split('```')[0].strip()

            return code

        @tool
        def generate_module_tool(signature_class_name: str, output_field_name: str,
                                 fallback_structure: str, validation_feedback: str = "") -> str:
            """
            Generate an Async DSPy Module that wraps a signature.

            Args:
                signature_class_name: Name of the signature class to wrap
                output_field_name: Name of the output field in the signature
                fallback_structure: JSON structure for error fallback
                validation_feedback: Optional feedback from validation

            Returns:
                Complete Python code for the async module
            """
            prompt = f"""Generate a production-quality Async DSPy Module following real patterns:

SIGNATURE TO WRAP: {signature_class_name}
OUTPUT FIELD: {output_field_name}
FALLBACK STRUCTURE: {fallback_structure}

REAL-WORLD PATTERN (from production code):
```python
import asyncio
from typing import Dict, Any
import dspy
from utils.json_parser import safe_json_parse


class Async{signature_class_name}Extractor(dspy.Module):
    \"\"\"Async module to extract [description].\"\"\"

    def __init__(self):
        super().__init__()
        # Use ChainOfThought for reasoning (better accuracy for complex medical text)
        self.extract = dspy.ChainOfThought({signature_class_name})

    async def __call__(self, markdown_content: str, **kwargs) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()

        def _extract():
            return self.extract(markdown_content=markdown_content, **kwargs)

        try:
            result = await loop.run_in_executor(None, _extract)
            # Parse JSON output to Python dict
            return safe_json_parse(result.{output_field_name})
        except Exception as e:
            print(f"Error in extraction: {{e}}")
            # Return fallback default structure
            return {fallback_structure}

    def forward_sync(self, markdown_content: str, **kwargs) -> Dict[str, Any]:
        \"\"\"Synchronous method for DSPy optimizers\"\"\"
        result = self.extract(markdown_content=markdown_content, **kwargs)
        return safe_json_parse(result.{output_field_name})
```

REQUIREMENTS:
1. Inherit from dspy.Module
2. Use dspy.ChainOfThought wrapper (better for complex extraction)
3. Async __call__ method with run_in_executor pattern
4. Sync forward_sync method for optimizers
5. Comprehensive error handling with fallback
6. Type hints for all parameters and returns
7. Clear docstring
"""

            if validation_feedback:
                prompt += f"\n\nVALIDATION FEEDBACK:\n{validation_feedback}\n"

            prompt += """
Generate ONLY the Python code.
"""

            result = model.invoke(prompt)
            code = result.content if result and hasattr(
                result, 'content') else None

            # Handle different response types
            if isinstance(code, list):
                # If code is a list, try to extract text from content blocks
                text_parts = []
                for item in code:
                    if isinstance(item, dict) and 'text' in item:
                        text_parts.append(item['text'])
                    elif isinstance(item, str):
                        text_parts.append(item)
                    elif hasattr(item, 'text'):
                        text_parts.append(item.text)
                code = ''.join(text_parts) if text_parts else None

            # Check if code was generated
            if not code or not isinstance(code, str):
                raise ValueError(
                    f"Model returned invalid response: {type(code).__name__ if code else 'None'}")

            if '```python' in code:
                code = code.split('```python')[1].split('```')[0].strip()
            elif '```' in code:
                code = code.split('```')[1].split('```')[0].strip()

            return code

        self.analyze_field_tool = analyze_field_tool
        self.generate_signature_tool = generate_signature_tool
        self.generate_module_tool = generate_module_tool

        # Store tools list for agent
        self.tools = [analyze_field_tool,
                      generate_signature_tool, generate_module_tool]

    def _create_agent(self):
        """Create LangChain agent with structured output support"""
        # Create agent with structured output capability
        # Uses LangChain's ToolStrategy for reliable structured responses
        try:
            self.agent = create_agent(
                self.model,
                tools=self.tools,
                response_format=None  # We'll use tools directly for now
            )
            print("✅ Agent created with tool support")
        except Exception as e:
            # If agent creation fails, we'll use tools directly (which we do anyway)
            print(f"⚠️  Agent creation skipped: {str(e)}")
            self.agent = None

        # Create structured output models for validation
        self.field_analysis_agent = None
        self.signature_generation_agent = None

        # Try to create specialized agents with structured output
        try:
            # Agent for field analysis with structured output
            self.field_analysis_agent = create_agent(
                self.model,
                tools=[],
                response_format=ToolStrategy(
                    schema=FieldAnalysisSchema,
                    handle_errors=True
                )
            )
            print("✅ Field analysis agent created with structured output")
        except Exception as e:
            print(f"⚠️  Field analysis agent creation skipped: {str(e)}")

        try:
            # Agent for signature generation with structured output
            self.signature_generation_agent = create_agent(
                self.model,
                tools=[],
                response_format=ToolStrategy(
                    schema=SignatureCodeSchema,
                    handle_errors=True
                )
            )
            print("✅ Signature generation agent created with structured output")
        except Exception as e:
            print(f"⚠️  Signature generation agent creation skipped: {str(e)}")

    # ========================================================================
    # WORKFLOW GRAPH NODES
    # ========================================================================

    def _node_analyze_fields(self, state: SignatureGenerationState) -> SignatureGenerationState:
        """Node: Analyze questionnaire spec and create blueprint"""
        print(
            f"\n📋 Analyzing fields for {state['questionnaire_spec'].get('class_name', 'Signature')}...")

        try:
            blueprint = self._create_blueprint(state['questionnaire_spec'])
            state['blueprint'] = blueprint
            state['status'] = 'analyzed'
            print("  ✅ Blueprint created")
        except Exception as e:
            state['errors'].append(f"Blueprint creation failed: {str(e)}")
            state['status'] = 'failed'
            print(f"  ❌ Analysis failed: {str(e)}")

        return state

    def _node_generate_code(self, state: SignatureGenerationState) -> SignatureGenerationState:
        """Node: Generate signature code using agent/tools"""
        print(f"  Attempt {state['attempt'] + 1}/{state['max_attempts']}...")

        try:
            # Use the tool directly (agent would be for more complex reasoning)
            code = self.generate_signature_tool.invoke({
                "blueprint_json": json.dumps(state['blueprint']),
                "validation_feedback": state['validation_feedback']
            })

            state['code'] = code
            state['attempt'] += 1
            state['status'] = 'generated'
            print("  ✅ Code generated")
        except Exception as e:
            state['errors'].append(f"Generation failed: {str(e)}")
            state['status'] = 'failed'
            print(f"  ❌ Generation failed: {str(e)}")

        return state

    def _node_validate_code(self, state: SignatureGenerationState) -> SignatureGenerationState:
        """Node: Validate generated code"""
        print("  🔍 Validating code...")

        is_valid, errors = self.validator.validate_signature(state['code'])

        state['is_valid'] = is_valid
        state['errors'] = errors

        # Separate critical errors from warnings
        critical_errors = [e for e in errors if e.startswith('❌')]
        warnings = [e for e in errors if e.startswith('⚠️')]

        state['warnings'] = warnings

        if is_valid:
            state['status'] = 'validated'
            print(f"  ✅ Validation passed")
            if warnings:
                print(f"  ⚠️  {len(warnings)} warnings")
        elif critical_errors:
            state['status'] = 'needs_refinement'
            state['validation_feedback'] = "CRITICAL ERRORS TO FIX:\n" + \
                "\n".join(critical_errors)
            print(
                f"  ❌ Validation failed: {len(critical_errors)} critical errors")
        else:
            # Only warnings, accept it
            state['is_valid'] = True
            state['status'] = 'validated'
            print(f"  ⚠️  Generated with {len(warnings)} warnings (accepted)")

        return state

    def _node_human_review(self, state: SignatureGenerationState) -> SignatureGenerationState:
        """Node: Human review point (interruptible)"""
        print("\n👤 Human review required...")
        print("="*70)
        print(state['code'])
        print("="*70)

        # This node will be interrupted by LangGraph if configured
        # Human can provide feedback via state update
        state['needs_human_review'] = True
        state['status'] = 'awaiting_human_review'

        return state

    def _node_refine_code(self, state: SignatureGenerationState) -> SignatureGenerationState:
        """Node: Refine code based on feedback"""
        print("  🔧 Refining code...")

        # Prepare feedback (from validation or human)
        feedback = state.get('human_feedback') or state.get(
            'validation_feedback', '')

        if feedback:
            state['validation_feedback'] = feedback

        state['status'] = 'refining'
        return state

    def _node_finalize(self, state: SignatureGenerationState) -> SignatureGenerationState:
        """Node: Finalize and prepare result"""
        print("  ✅ Finalizing result...")

        state['result'] = {
            "code": state['code'],
            "is_valid": state['is_valid'],
            "attempts": state['attempt'],
            "errors": state['errors'],
            "warnings": state['warnings'],
            "blueprint": state['blueprint']
        }
        state['status'] = 'completed'

        return state

    # ========================================================================
    # WORKFLOW GRAPH ROUTING
    # ========================================================================

    def _should_continue_generation(self, state: SignatureGenerationState) -> str:
        """Decide next step after generation"""
        if state['status'] == 'failed':
            return 'finalize'
        return 'validate'

    def _should_refine_or_finish(self, state: SignatureGenerationState) -> str:
        """Decide whether to refine or finish after validation"""
        if state['is_valid']:
            if self.enable_human_review and not state.get('human_feedback'):
                return 'human_review'
            return 'finalize'
        elif state['attempt'] >= state['max_attempts']:
            return 'finalize'
        else:
            return 'refine'

    def _after_human_review(self, state: SignatureGenerationState) -> str:
        """Decide next step after human review"""
        if state.get('human_feedback'):
            return 'refine'
        return 'finalize'

    # ========================================================================
    # BUILD WORKFLOW GRAPH
    # ========================================================================

    def _build_workflow_graph(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(SignatureGenerationState)

        # Add nodes
        workflow.add_node("analyze", self._node_analyze_fields)
        workflow.add_node("generate", self._node_generate_code)
        workflow.add_node("validate", self._node_validate_code)
        workflow.add_node("human_review", self._node_human_review)
        workflow.add_node("refine", self._node_refine_code)
        workflow.add_node("finalize", self._node_finalize)

        # Set entry point
        workflow.set_entry_point("analyze")

        # Add edges
        workflow.add_edge("analyze", "generate")
        workflow.add_conditional_edges(
            "generate",
            self._should_continue_generation,
            {
                "validate": "validate",
                "finalize": "finalize"
            }
        )
        workflow.add_conditional_edges(
            "validate",
            self._should_refine_or_finish,
            {
                "human_review": "human_review",
                "refine": "refine",
                "finalize": "finalize"
            }
        )
        workflow.add_conditional_edges(
            "human_review",
            self._after_human_review,
            {
                "refine": "refine",
                "finalize": "finalize"
            }
        )
        workflow.add_edge("refine", "generate")
        workflow.add_edge("finalize", END)

        # Compile with checkpointer and optional interrupt
        interrupt_before = ["human_review"] if self.enable_human_review else []
        self.workflow = workflow.compile(
            checkpointer=self.checkpointer,
            interrupt_before=interrupt_before
        )

        print("✅ Workflow graph compiled successfully")

    def _get_real_signature_examples(self, complexity: str) -> str:
        """Get real examples from production signatures"""
        examples = {
            "simple": """
# SIMPLE EXTRACTION EXAMPLE (from missing_data_study):
class ExtractTimeInterval(dspy.Signature):
    \"\"\"Extract time interval between index test and reference standard.
    
    Form Question 36: "What is the time interval between the index test(s) and reference standard?"
    
    This assesses whether tests were performed close in time, which is important 
    because disease status may change over time (disease progression bias).
    \"\"\"
    
    markdown_content: str = dspy.InputField(
        desc="Full markdown content of the medical research paper"
    )
    
    time_interval: str = dspy.OutputField(
        desc=\"\"\"Description of time interval between index test and reference standard.
        
        Rules:
        - Extract explicit time intervals where stated
        - Use "NR" if not reported
        - Can include qualified descriptions like "assumed same day"
        
        Examples:
        - "The exams were performed in the same day."
        - "not more than 2 weeks between the 3 methods"
        - "NR"
        - "assumed reference standard biopsy immediately followed the index test"
        \"\"\"
    )
""",
            "medium": """
# MEDIUM COMPLEXITY EXAMPLE (from index_test):
class ExtractIndexTestBrandAndSite(dspy.Signature):
    \"\"\"Extract commercial brand name and site selection information.
    
    Form Questions 2-3:
    - Question 2: "Mention the commercial (brand) name of the index test, if stated."
    - Question 3: "How was the site selected for index testing?"
    \"\"\"

    markdown_content: str = dspy.InputField(
        desc="Full markdown content of the medical research paper"
    )

    brand_and_site_json: str = dspy.OutputField(
        desc=\"\"\"JSON string with brand name and site selection information.
        
        Structure:
        {
            "brand_name": "commercial name or NR",
            "site_selection": "description of how sites were selected"
        }
        
        Rules:
        - brand_name: Extract commercial/brand name if mentioned (e.g., "OralCDx", "VELscope")
        - brand_name: Use "NR" if not reported
        - site_selection: Copy description from study about site selection
        
        Examples:
        {"brand_name": "NR", "site_selection": "The dye was applied over the oral lesion identified in clinical examination."}
        {"brand_name": "VELscope", "site_selection": "All clinically visible lesions were examined using the device"}
        \"\"\"
    )
""",
            "complex": """
# COMPLEX EXTRACTION EXAMPLE (from outcomes_study):
class ExtractConfusionMatrixMetrics(dspy.Signature):
    \"\"\"Extract confusion matrix metrics: TP, FP, FN, TN.
    
    Form Questions 3-6:
    - True positives, False positives, False negatives, True negatives
    
    These represent the 2x2 contingency table for diagnostic test performance.
    \"\"\"

    markdown_content: str = dspy.InputField(
        desc="Full markdown content of the medical research paper"
    )
    linking_index_test: str = dspy.InputField(
        desc="The index test name for context"
    )
    outcome_target_condition: str = dspy.InputField(
        desc="The target condition for context"
    )

    confusion_matrix_json: str = dspy.OutputField(
        desc=\"\"\"JSON string with confusion matrix values.
        
        Structure:
        {
            "true_positives": number_or_"NR",
            "false_positives": number_or_"NR",
            "false_negatives": number_or_"NR",
            "true_negatives": number_or_"NR"
        }
        
        Rules:
        - Extract numeric values where reported
        - Use "NR" (not reported) if not explicitly stated
        - TP = Test positive & Disease positive
        - FP = Test positive & Disease negative
        - FN = Test negative & Disease positive
        - TN = Test negative & Disease negative
        
        Examples:
        {"true_positives": 58, "false_positives": 7, "false_negatives": 3, "true_negatives": 32}
        {"true_positives": "NR", "false_positives": "NR", "false_negatives": "NR", "true_negatives": "NR"}
        \"\"\"
    )
"""
        }
        return examples.get(complexity, examples["medium"])

    # ========================================================================
    # MAIN GENERATION METHODS
    # ========================================================================

    def generate_signature(self, questionnaire_spec: Dict[str, Any],
                           max_attempts: int = 3,
                           thread_id: str = "default") -> Dict[str, Any]:
        """
        Generate a single DSPy signature using LangGraph workflow.

        Args:
            questionnaire_spec: Specification with class_name, fields, output_structure, etc.
            max_attempts: Maximum validation retry attempts
            thread_id: Thread ID for workflow state persistence

        Returns:
            dict with 'code', 'is_valid', 'attempts', 'errors', 'blueprint'
        """
        # Initialize state
        initial_state: SignatureGenerationState = {
            "questionnaire_spec": questionnaire_spec,
            "max_attempts": max_attempts,
            "blueprint": None,
            "code": "",
            "validation_feedback": "",
            "attempt": 0,
            "errors": [],
            "warnings": [],
            "is_valid": False,
            "human_feedback": None,
            "needs_human_review": False,
            "result": None,
            "status": "in_progress"
        }

        # Run workflow
        config = {"configurable": {"thread_id": thread_id}}

        try:
            # Execute workflow
            for event in self.workflow.stream(initial_state, config):
                # Stream events for monitoring
                pass

            # Get final state
            final_state = self.workflow.get_state(config)

            # Check if interrupted for human review
            if final_state.next and "human_review" in final_state.next:
                print("\n⏸️  Workflow paused for human review")
                print(
                    "To continue, call: generator.continue_after_human_review(feedback, thread_id)")
                return {
                    "status": "awaiting_human_review",
                    "code": final_state.values.get('code', ''),
                    "thread_id": thread_id,
                    "paused": True
                }

            # Return result
            result = final_state.values.get('result')
            if result:
                return result

            # Fallback if no result
            return {
                "code": final_state.values.get('code', ''),
                "is_valid": final_state.values.get('is_valid', False),
                "attempts": final_state.values.get('attempt', 0),
                "errors": final_state.values.get('errors', []),
                "warnings": final_state.values.get('warnings', []),
                "blueprint": final_state.values.get('blueprint')
            }

        except Exception as e:
            print(f"❌ Workflow execution failed: {str(e)}")
            return {
                "code": "",
                "is_valid": False,
                "attempts": 0,
                "errors": [f"Workflow failed: {str(e)}"],
                "blueprint": None
            }

    def continue_after_human_review(self, human_feedback: str, thread_id: str = "default") -> Dict[str, Any]:
        """
        Continue workflow after human review.

        Args:
            human_feedback: Feedback from human reviewer
            thread_id: Thread ID of the paused workflow

        Returns:
            Final result dict
        """
        config = {"configurable": {"thread_id": thread_id}}

        # Update state with human feedback
        current_state = self.workflow.get_state(config)
        current_state.values['human_feedback'] = human_feedback
        current_state.values['needs_human_review'] = False

        # Continue workflow
        try:
            for event in self.workflow.stream(None, config):
                pass

            final_state = self.workflow.get_state(config)
            result = final_state.values.get('result')

            if result:
                return result

            return {
                "code": final_state.values.get('code', ''),
                "is_valid": final_state.values.get('is_valid', False),
                "attempts": final_state.values.get('attempt', 0),
                "errors": final_state.values.get('errors', []),
                "warnings": final_state.values.get('warnings', []),
                "blueprint": final_state.values.get('blueprint')
            }
        except Exception as e:
            return {
                "code": "",
                "is_valid": False,
                "attempts": 0,
                "errors": [f"Continuation failed: {str(e)}"],
                "blueprint": None
            }

    def generate_signature_legacy(self, questionnaire_spec: Dict[str, Any],
                                  max_attempts: int = 3) -> Dict[str, Any]:
        """
        Legacy method: Generate signature without workflow (for backward compatibility).
        """
        # Step 1: Analyze fields and create blueprint
        print(
            f"\n📋 Analyzing fields for {questionnaire_spec.get('class_name', 'Signature')}...")

        blueprint = self._create_blueprint(questionnaire_spec)

        # Step 2: Generate signature with validation loop
        validation_feedback = ""

        for attempt in range(max_attempts):
            print(f"  Attempt {attempt + 1}/{max_attempts}...")

            try:
                code = self.generate_signature_tool.invoke({
                    "blueprint_json": json.dumps(blueprint.dict() if hasattr(blueprint, 'dict') else blueprint),
                    "validation_feedback": validation_feedback
                })

                is_valid, errors = self.validator.validate_signature(code)

                if is_valid:
                    print(f"  ✅ Valid signature generated!")
                    return {
                        "code": code,
                        "is_valid": True,
                        "attempts": attempt + 1,
                        "errors": [],
                        "blueprint": blueprint,
                        "warnings": [e for e in errors if e.startswith('⚠️')]
                    }

                # Has errors, prepare feedback for next attempt
                critical_errors = [e for e in errors if e.startswith('❌')]
                if critical_errors:
                    validation_feedback = "CRITICAL ERRORS TO FIX:\n" + \
                        "\n".join(critical_errors)
                    print(
                        f"  ❌ Validation failed: {len(critical_errors)} critical errors")
                else:
                    # Only warnings, accept it
                    print(f"  ⚠️  Generated with {len(errors)} warnings")
                    return {
                        "code": code,
                        "is_valid": True,
                        "attempts": attempt + 1,
                        "errors": [],
                        "warnings": errors,
                        "blueprint": blueprint
                    }

            except Exception as e:
                print(f"  ❌ Generation failed: {str(e)}")
                if attempt == max_attempts - 1:
                    return {
                        "code": "",
                        "is_valid": False,
                        "attempts": attempt + 1,
                        "errors": [f"Generation failed: {str(e)}"],
                        "blueprint": blueprint
                    }

        # Max attempts reached
        return {
            "code": code if 'code' in locals() else "",
            "is_valid": False,
            "attempts": max_attempts,
            "errors": errors if 'errors' in locals() else ["Max attempts reached"],
            "blueprint": blueprint
        }

    def generate_module(self, signature_class_name: str, output_field_name: str,
                        fallback_structure: Dict[str, Any], max_attempts: int = 3) -> Dict[str, Any]:
        """
        Generate an async DSPy module that wraps a signature.

        Args:
            signature_class_name: Name of the signature class
            output_field_name: Name of output field in signature
            fallback_structure: Default structure for error recovery
            max_attempts: Maximum validation attempts

        Returns:
            dict with 'code', 'is_valid', 'attempts', 'errors'
        """
        print(f"\n🔧 Generating module for {signature_class_name}...")

        validation_feedback = ""

        for attempt in range(max_attempts):
            print(f"  Attempt {attempt + 1}/{max_attempts}...")

            try:
                code = self.generate_module_tool.invoke({
                    "signature_class_name": signature_class_name,
                    "output_field_name": output_field_name,
                    "fallback_structure": json.dumps(fallback_structure),
                    "validation_feedback": validation_feedback
                })

                is_valid, errors = self.validator.validate_module(code)

                if is_valid:
                    print(f"  ✅ Valid module generated!")
                    return {
                        "code": code,
                        "is_valid": True,
                        "attempts": attempt + 1,
                        "errors": [],
                        "warnings": [e for e in errors if e.startswith('⚠️')]
                    }

                critical_errors = [e for e in errors if e.startswith('❌')]
                if critical_errors:
                    validation_feedback = "\n".join(critical_errors)
                    print(
                        f"  ❌ Validation failed: {len(critical_errors)} errors")
                else:
                    print(f"  ⚠️  Generated with {len(errors)} warnings")
                    return {
                        "code": code,
                        "is_valid": True,
                        "attempts": attempt + 1,
                        "errors": [],
                        "warnings": errors
                    }

            except Exception as e:
                print(f"  ❌ Generation failed: {str(e)}")
                if attempt == max_attempts - 1:
                    return {
                        "code": "",
                        "is_valid": False,
                        "attempts": attempt + 1,
                        "errors": [f"Module generation failed: {str(e)}"]
                    }

        return {
            "code": code if 'code' in locals() else "",
            "is_valid": False,
            "attempts": max_attempts,
            "errors": errors if 'errors' in locals() else ["Max attempts reached"]
        }

    def generate_complete_task(self, task_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete task: multiple signatures + modules + pipeline.

        Args:
            task_spec: Complete task specification with multiple questionnaires

        Returns:
            dict with 'signatures_code', 'modules_code', 'pipeline_code', 'statistics'
        """
        print(
            f"\n🚀 Generating complete task: {task_spec.get('task_name', 'UnnamedTask')}")
        print("="*70)

        questionnaires = task_spec.get('questionnaires', [])

        if not questionnaires:
            return {
                "error": "No questionnaires provided in task_spec",
                "success": False
            }

        # Phase 1: Generate all signatures
        print(f"\n📝 Phase 1: Generating {len(questionnaires)} signatures...")
        signatures = []
        signature_results = []

        for idx, questionnaire in enumerate(questionnaires, 1):
            print(
                f"\n[{idx}/{len(questionnaires)}] {questionnaire.get('class_name', 'Unnamed')}")
            result = self.generate_signature(questionnaire)
            signature_results.append(result)

            if result['is_valid']:
                signatures.append({
                    "class_name": questionnaire.get('class_name'),
                    "code": result['code'],
                    "output_field": questionnaire.get('output_field_name', 'output')
                })

        print(
            f"\n✅ Generated {len(signatures)}/{len(questionnaires)} valid signatures")

        # Phase 2: Generate modules for each signature
        print(f"\n🔧 Phase 2: Generating {len(signatures)} modules...")
        modules = []

        for idx, sig in enumerate(signatures, 1):
            print(f"\n[{idx}/{len(signatures)}] Module for {sig['class_name']}")

            # Determine fallback structure from questionnaire
            questionnaire = questionnaires[idx - 1]
            fallback = self._create_fallback_structure(questionnaire)

            result = self.generate_module(
                sig['class_name'],
                sig['output_field'],
                fallback
            )

            if result['is_valid']:
                modules.append(result['code'])

        print(f"\n✅ Generated {len(modules)}/{len(signatures)} valid modules")

        # Phase 3: Combine into files
        print(f"\n📦 Phase 3: Assembling complete task files...")

        signatures_file = self._assemble_signatures_file(
            signatures, task_spec.get('task_name'))
        modules_file = self._assemble_modules_file(
            modules, task_spec.get('task_name'))

        return {
            "success": True,
            "task_name": task_spec.get('task_name'),
            "signatures_file": signatures_file,
            "modules_file": modules_file,
            "statistics": {
                "total_questionnaires": len(questionnaires),
                "signatures_generated": len(signatures),
                "modules_generated": len(modules),
                "total_attempts": sum(r['attempts'] for r in signature_results)
            },
            "signature_results": signature_results
        }

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _create_blueprint(self, questionnaire_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create signature blueprint from questionnaire spec"""

        # Determine complexity
        output_structure = questionnaire_spec.get('output_structure', {})
        num_fields = len(output_structure) if isinstance(
            output_structure, dict) else 1
        requires_context = questionnaire_spec.get('requires_context', False)

        if num_fields <= 2 and not requires_context:
            complexity = "simple"
        elif num_fields <= 5 and not requires_context:
            complexity = "medium"
        else:
            complexity = "complex"

        # Build blueprint
        blueprint = {
            "class_name": questionnaire_spec.get('class_name', 'ExtractData'),
            "docstring": self._create_docstring(questionnaire_spec),
            "input_fields": self._create_input_fields(questionnaire_spec),
            "output_fields": self._create_output_fields(questionnaire_spec),
            "extraction_complexity": complexity,
            "domain_context": {
                k: v for k, v in MEDICAL_DOMAIN_CONTEXT.items()
                if any(term in str(questionnaire_spec).lower() for term in k.lower().split('_'))
            }
        }

        return blueprint

    def _create_docstring(self, spec: Dict[str, Any]) -> str:
        """Create comprehensive docstring"""
        parts = []

        # Main description
        if 'description' in spec:
            parts.append(spec['description'])
        else:
            parts.append(
                f"Extract {spec.get('class_name', 'data')} from medical research paper.")

        # Form question
        if 'form_question_number' in spec:
            parts.append(
                f"\nForm Question {spec['form_question_number']}: \"{spec.get('form_question', '')}\"")
        elif 'form_question' in spec:
            parts.append(f"\nForm Question: \"{spec['form_question']}\"")

        # Options
        if 'options' in spec:
            parts.append(f"- Options: {', '.join(spec['options'])}")

        # Notes
        if 'note' in spec:
            parts.append(f"- Note: {spec['note']}")

        # Context
        if 'context' in spec:
            parts.append(f"\n{spec['context']}")

        return "\n".join(parts)

    def _create_input_fields(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create input field definitions"""
        fields = [
            {
                "field_name": "markdown_content",
                "sanitized_name": "markdown_content",
                "field_type": "input",
                "data_type": "str",
                "description": "Full markdown content of the medical research paper"
            }
        ]

        # Add context fields if needed
        if spec.get('requires_context'):
            for ctx_field in spec.get('context_fields', []):
                fields.append({
                    "field_name": ctx_field,
                    "sanitized_name": ctx_field,
                    "field_type": "input",
                    "data_type": "str",
                    "description": f"Context from previous extraction: {ctx_field}"
                })

        return fields

    def _create_output_fields(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create output field definitions"""
        output_structure = spec.get('output_structure', {})
        output_field_name = spec.get('output_field_name', 'result_json')

        # Determine data type from structure
        if isinstance(output_structure, dict):
            data_type = "str"  # JSON string
        else:
            data_type = str(output_structure).lower()

        return [
            {
                "field_name": output_field_name,
                "sanitized_name": output_field_name,
                "field_type": "output",
                "data_type": data_type,
                "description": self._create_output_description(spec)
            }
        ]

    def _create_output_description(self, spec: Dict[str, Any]) -> str:
        """Create detailed output field description with Structure + Rules + Examples"""
        parts = ["Description of output format.\n"]

        # Structure
        if 'output_structure' in spec:
            parts.append(
                f"Structure:\n{json.dumps(spec['output_structure'], indent=2)}\n")

        # Rules
        parts.append("Rules:")
        parts.append("- Extract accurately from the paper")
        parts.append('- Use "NR" for Not Reported values')
        if 'rules' in spec:
            for rule in spec['rules']:
                parts.append(f"- {rule}")
        parts.append("")

        # Examples
        if 'examples' in spec and spec['examples']:
            parts.append("Examples:")
            for example in spec['examples']:
                parts.append(json.dumps(example))

        return "\n".join(parts)

    def _create_fallback_structure(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback structure for error recovery"""
        output_structure = spec.get('output_structure', {})

        if isinstance(output_structure, dict):
            # Create fallback with "NR" values
            def create_default(value):
                if isinstance(value, dict):
                    return {k: create_default(v) for k, v in value.items()}
                elif isinstance(value, str) and 'bool' in value:
                    return False
                elif isinstance(value, str) and 'int' in value:
                    return 0
                else:
                    return "NR"

            return create_default(output_structure)
        else:
            return "NR"

    def _assemble_signatures_file(self, signatures: List[Dict[str, Any]], task_name: str) -> str:
        """Assemble complete signatures.py file"""
        lines = [
            "import dspy",
            "",
            "",
            "# " + "=" * 76,
            f"# SIGNATURES - {task_name.upper().replace('_', ' ')}",
            "# " + "=" * 76,
            "",
            ""
        ]

        for sig in signatures:
            lines.append(sig['code'])
            lines.append("\n\n")

        # Add __all__
        class_names = [sig['class_name'] for sig in signatures]
        lines.append("__all__ = [")
        for name in class_names:
            lines.append(f'    "{name}",')
        lines.append("]")

        return "\n".join(lines)

    def _assemble_modules_file(self, modules: List[str], task_name: str) -> str:
        """Assemble complete modules.py file"""
        lines = [
            "import asyncio",
            "import json",
            "from typing import Dict, Any",
            "",
            "import dspy",
            "",
            "from utils.json_parser import safe_json_parse",
            f"from dspy_components.tasks.{task_name}.signatures import (",
            "    # Import signatures here",
            ")",
            "",
            "",
            "# " + "=" * 76,
            f"# MODULES - {task_name.upper().replace('_', ' ')}",
            "# " + "=" * 76,
            "",
            ""
        ]

        for module_code in modules:
            lines.append(module_code)
            lines.append("\n\n")

        return "\n".join(lines)


# ============================================================================
# INTERACTIVE & CLI FUNCTIONS
# ============================================================================

def interactive_signature_generation():
    """Interactive CLI for signature generation"""
    print("\n" + "="*70)
    print("🎯 DSPy Signature Generator - Interactive Mode")
    print("="*70)

    generator = DSPySignatureGenerator()

    # Get user input
    class_name = input(
        "\n📝 Signature class name (e.g., ExtractIndexTestType): ").strip()
    form_question = input("📋 Form question: ").strip()
    description = input("💬 Brief description: ").strip()

    print("\n🔧 Output structure (JSON format):")
    print(
        "Example: {\"field1\": \"str\", \"field2\": {\"selected\": \"bool\", \"comment\": \"str\"}}")
    output_structure_str = input("Structure: ").strip()

    try:
        output_structure = json.loads(output_structure_str)
    except:
        print("⚠️  Invalid JSON, using default structure")
        output_structure = {"result": "str"}

    # Build spec
    spec = {
        "class_name": class_name,
        "form_question": form_question,
        "description": description,
        "output_structure": output_structure,
        "output_field_name": "result_json"
    }

    # Generate
    result = generator.generate_signature(spec, max_attempts=3)

    # Display result
    print("\n" + "="*70)
    if result['is_valid']:
        print("✅ SIGNATURE GENERATED SUCCESSFULLY")
        print("="*70)
        print(result['code'])

        if result.get('warnings'):
            print("\n⚠️  Warnings:")
            for warning in result['warnings']:
                print(f"  {warning}")

        # Save option
        save = input("\n💾 Save to file? (y/n): ").strip().lower()
        if save == 'y':
            filename = input("Filename (e.g., my_signature.py): ").strip()
            with open(filename, 'w') as f:
                f.write(result['code'])
            print(f"✅ Saved to {filename}")
    else:
        print("❌ GENERATION FAILED")
        print("="*70)
        print("Errors:")
        for error in result['errors']:
            print(f"  {error}")


# ============================================================================
# MAIN & EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("🚀 DSPy Signature & Module Generator")
    print("="*70)

    generator = DSPySignatureGenerator()

    # ========================================================================
    # EXAMPLE 1: Generate Single Signature
    # ========================================================================
    print("\n" + "="*70)
    print("EXAMPLE 1: Single Signature Generation")
    print("="*70)

    questionnaire = {
        "class_name": "ExtractReferenceStandardType",
        "form_question_number": 23,
        "form_question": "Mention the reference standard and type of biopsy",
        "description": "Extract the reference standard type and biopsy details",
        "options": ["Biopsy and histopathological assessment", "Other"],
        "note": "Copy and paste the type of biopsy from the study",
        "output_structure": {
            "biopsy_and_histopathological_assessment": {
                "selected": "bool",
                "comment": "str"
            },
            "other": {
                "selected": "bool",
                "comment": "str"
            }
        },
        "output_field_name": "reference_standard_type_json",
        "context": "Reference standard is the gold standard diagnostic test against which the index test is compared. In oral cancer studies, this is typically histopathological examination of biopsy tissue.",
        "examples": [
            {
                "biopsy_and_histopathological_assessment": {"selected": True, "comment": "Punch or wedge biopsy"},
                "other": {"selected": False, "comment": ""}
            },
            {
                "biopsy_and_histopathological_assessment": {"selected": True, "comment": "Incisional biopsy"},
                "other": {"selected": False, "comment": ""}
            }
        ]
    }

    result = generator.generate_signature(questionnaire, max_attempts=3)

    if result['is_valid']:
        print(f"\n✅ Generated in {result['attempts']} attempt(s)")
        print("\n" + result['code'])

        if result.get('warnings'):
            print("\n⚠️  Warnings:")
            for warning in result['warnings']:
                print(f"  {warning}")
    else:
        print(f"\n❌ Failed after {result['attempts']} attempts")
        for error in result['errors']:
            print(f"  {error}")

    # ========================================================================
    # EXAMPLE 2: Generate Signature + Module
    # ========================================================================
    if result['is_valid']:
        print("\n" + "="*70)
        print("EXAMPLE 2: Module Generation for Signature")
        print("="*70)

        fallback = {
            "biopsy_and_histopathological_assessment": {"selected": True, "comment": "NR"},
            "other": {"selected": False, "comment": ""}
        }

        module_result = generator.generate_module(
            "ExtractReferenceStandardType",
            "reference_standard_type_json",
            fallback,
            max_attempts=3
        )

        if module_result['is_valid']:
            print(
                f"\n✅ Module generated in {module_result['attempts']} attempt(s)")
            print("\n" + module_result['code'])
        else:
            print(f"\n❌ Module generation failed")
            for error in module_result['errors']:
                print(f"  {error}")

    # ========================================================================
    # EXAMPLE 3: Complete Task Generation
    # ========================================================================
    print("\n\n" + "="*70)
    print("EXAMPLE 3: Complete Task (Multiple Signatures + Modules)")
    print("="*70)

    task_spec = {
        "task_name": "reference_standard",
        "questionnaires": [
            {
                "class_name": "ExtractReferenceStandardType",
                "form_question_number": 23,
                "form_question": "Mention the reference standard and type of biopsy",
                "output_structure": {
                    "biopsy_and_histopathological_assessment": {"selected": "bool", "comment": "str"},
                    "other": {"selected": "bool", "comment": "str"}
                },
                "output_field_name": "reference_standard_type_json"
            },
            {
                "class_name": "ExtractBiopsySite",
                "form_question_number": 24,
                "form_question": "What is the site of biopsy?",
                "output_structure": {
                    "site_of_biopsy": "str",
                    "site_of_biopsy_full_description": "str"
                },
                "output_field_name": "site_of_biopsy_json"
            }
        ]
    }

    complete_result = generator.generate_complete_task(task_spec)

    if complete_result.get('success'):
        print("\n✅ COMPLETE TASK GENERATED")
        print(f"\nStatistics:")
        stats = complete_result['statistics']
        print(f"  - Total questionnaires: {stats['total_questionnaires']}")
        print(f"  - Signatures generated: {stats['signatures_generated']}")
        print(f"  - Modules generated: {stats['modules_generated']}")
        print(f"  - Total attempts: {stats['total_attempts']}")

        print("\n💾 Save files? (uncomment to save)")
        print(
            "# Path('signatures.py').write_text(complete_result['signatures_file'])")
        print(
            "# Path('modules.py').write_text(complete_result['modules_file'])")
    else:
        print(f"\n❌ Task generation failed: {complete_result.get('error')}")

    # ========================================================================
    # INTERACTIVE MODE
    # ========================================================================
    print("\n\n" + "="*70)
    print("EXAMPLE 4: Interactive Mode (uncomment to run)")
    print("="*70)
    print("# interactive_signature_generation()")
