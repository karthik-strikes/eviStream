# eviStream: Comprehensive Technical Documentation

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Technology Fundamentals](#technology-fundamentals)
3. [Problem Statement](#problem-statement)
4. [System Architecture](#system-architecture)
5. [Core Generators - The Heart of the System](#core-generators)
6. [Complete Workflow](#complete-workflow)
7. [Technology Stack & Rationale](#technology-stack)
8. [Implementation Details](#implementation-details)

---

## Executive Summary

**eviStream** is an intelligent medical data extraction platform that automatically generates code to extract structured information from research papers. It solves the critical bottleneck in systematic reviews and meta-analyses by transforming custom form definitions into production-ready data extraction pipelines.

### Key Innovation
Instead of manually writing extraction code for each form, eviStream uses a **three-stage AI-powered code generation workflow**:
1. **Cognitive Decomposition**: Breaks down complex forms into atomic extraction tasks
2. **Code Generation**: Automatically creates DSPy signatures and modules
3. **Pipeline Assembly**: Orchestrates multi-stage execution with dependency management

---

## Technology Fundamentals

Before diving into the system, let's understand the key technologies used.

### What is DSPy?

**DSPy** (Declarative Self-improving Python) is a framework for programming language models through structured prompts. Think of it as "compile-time for LLMs" - instead of writing prompt strings, you define signatures that describe the input-output behavior.

#### DSPy Core Concepts

**1. Signatures**
A signature defines what an LLM should do, not how to do it.

```python
class ExtractDiagnosis(dspy.Signature):
    """Extract primary diagnosis from medical record."""
    
    # Inputs: What the LLM receives
    markdown_content: str = dspy.InputField(
        desc="Full markdown content of the medical research paper"
    )
    
    # Outputs: What the LLM must produce
    diagnosis: Dict[str, Any] = dspy.OutputField(
        desc="""Primary medical diagnosis with source grounding.
        
        Return format: {"value": "diagnosis text", "source_text": "quote from paper"}
        Use "NR" if not reported."""
    )
```

**Why Signatures?**
- **Type Safety**: Define expected inputs/outputs with Python types
- **Clear Contracts**: Self-documenting interfaces for LLM tasks
- **Composability**: Signatures can be chained in pipelines
- **Optimization**: DSPy can auto-optimize prompts for better performance

**2. Modules**
Modules wrap signatures and add execution logic.

```python
class AsyncDiagnosisExtractor(dspy.Module):
    def __init__(self):
        super().__init__()
        # ChainOfThought adds reasoning steps before extraction
        self.extract = dspy.ChainOfThought(ExtractDiagnosis)
    
    async def __call__(self, markdown_content: str) -> Dict[str, Any]:
        result = self.extract(markdown_content=markdown_content)
        return safe_json_parse(result.diagnosis)
```

**Module Types Used in eviStream:**
- `dspy.ChainOfThought`: Adds step-by-step reasoning before answering
- `dspy.Module`: Base class for custom logic and pipeline orchestration
- `dspy.Prediction`: Standard return type with extracted data

**3. Why DSPy for Medical Extraction?**
- **Structured Output**: Enforces JSON format for extracted data
- **Source Grounding**: Each extraction includes the source text (critical for validation)
- **Fallback Handling**: Built-in error recovery with "NR" (Not Reported) convention
- **Chain of Thought**: Improves accuracy by requiring reasoning steps
- **Pipeline Composition**: Natural fit for multi-stage extraction workflows

---

### What is LangGraph?

**LangGraph** is a framework for building stateful, multi-step workflows with LLMs. It's like a "state machine compiler" that lets you define complex workflows with conditional logic, loops, and human-in-the-loop review.

#### LangGraph Core Concepts

**1. State Graphs**
Define the workflow as a graph of nodes (actions) and edges (transitions).

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(WorkflowState)

# Add nodes (actions)
workflow.add_node("decompose", decompose_form_node)
workflow.add_node("validate", validate_decomposition_node)
workflow.add_node("generate_code", generate_signatures_node)

# Add edges (transitions)
workflow.add_edge("decompose", "validate")
workflow.add_conditional_edges(
    "validate",
    route_after_validation,  # Function decides next step
    {
        "generate_code": "generate_code",  # If valid
        "decompose": "decompose"           # If invalid, retry
    }
)
```

**2. State Management**
State persists across all nodes, enabling complex multi-step workflows.

```python
class WorkflowState(TypedDict):
    # Input
    form_data: Dict[str, Any]
    
    # Workflow state
    decomposition: Optional[Dict[str, Any]]
    decomposition_valid: bool
    signatures_code: List[Dict[str, Any]]
    
    # Control
    attempt: int
    errors: List[str]
    current_stage: str
    
    # Output
    result: Optional[Dict[str, Any]]
```

**3. Checkpointing**
LangGraph can save state and resume later - critical for human-in-the-loop workflows.

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
workflow = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"]  # Pause here for approval
)

# Later, resume from checkpoint
config = {"configurable": {"thread_id": "task_123"}}
workflow.invoke(None, config)  # Continues from where it left off
```

**4. Why LangGraph for eviStream?**
- **Orchestration**: Manages complex 6+ step code generation workflow
- **Validation Loops**: Automatically retries decomposition if validation fails
- **Human-in-the-Loop**: Pauses workflow for manual review and approval
- **Error Recovery**: Tracks errors and provides feedback for refinement
- **State Persistence**: Can resume long-running generation tasks
- **Conditional Routing**: Different paths based on validation results

---

### What is LangChain Structured Output?

**LangChain Structured Output** forces LLMs to return data in a specific Pydantic schema. Think of it as "compile-time type checking for LLM responses."

```python
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel

class Signature(BaseModel):
    """A single atomic signature specification."""
    name: str = Field(description="Descriptive signature name")
    field_names: List[str] = Field(
        min_length=1,
        description="List of fields this signature handles"
    )
    depends_on: List[str] = Field(
        default_factory=list,
        description="Fields needed as input"
    )

# Force LLM to return this exact structure
structured_model = model.with_structured_output(Signature)
result = structured_model.invoke(prompt)  # Returns Signature object

# Pydantic validates:
# - name is a string ✓
# - field_names has at least 1 item ✓
# - depends_on defaults to [] if missing ✓
```

**Why This Matters:**
- **Validation**: Pydantic ensures correct types and required fields
- **Parsing**: No manual JSON parsing - get Python objects directly
- **Error Handling**: Clear error messages when LLM returns invalid data
- **Schema Evolution**: Easy to update models as requirements change

**Used Throughout eviStream:**
- `Stage1Output`: For form decomposition results
- `SignatureSpec`: For DSPy signature specifications
- All workflow state models

---

## Problem Statement

### The Challenge: Medical Data Extraction at Scale

Medical researchers conducting systematic reviews face a critical bottleneck:

**Manual Extraction is Slow and Error-Prone**
- A single systematic review requires extracting data from 50-500+ papers
- Each paper has 10-50 fields to extract (study design, population, interventions, outcomes, risk of bias, etc.)
- Manual extraction takes 15-30 minutes per paper
- Inter-rater reliability requires duplicate extraction (2x the time)
- Different review topics need different extraction forms

**Example Scenario:**
A dental researcher needs to extract intervention outcomes from 200 RCTs. The form has:
- Study identification (3 fields)
- Population classification (5 fields)
- Intervention details (6 fields)
- Outcome measurements (8 fields)
- Event counts per outcome (4 fields per outcome × multiple outcomes)

**Traditional Approaches Fall Short:**
1. **Manual Extraction**: 200 papers × 20 minutes = 67 hours per reviewer
2. **Generic NLP**: Can't handle domain-specific structured forms
3. **Simple Regex/Rules**: Breaks on variation in medical terminology
4. **Hard-coded Scripts**: Need rewriting for each new review form

### What Researchers Actually Need

1. **Form Flexibility**: Define custom extraction forms for each review topic
2. **Automated Extraction**: Let AI extract data from PDFs automatically
3. **Source Grounding**: See the exact text that supports each extraction
4. **Structured Output**: Get clean JSON for meta-analysis tools
5. **Human Oversight**: Review and correct AI extractions before export
6. **No Coding Required**: Clinical researchers shouldn't need to write Python

### eviStream's Solution

**Transform Form → Code → Extraction Pipeline**

Instead of requiring programmers to write extraction code for each form, eviStream:
1. Accepts form definitions through a visual UI (Streamlit)
2. Uses AI to analyze the cognitive workflow of the form
3. Automatically generates production-quality DSPy code
4. Assembles multi-stage pipelines with proper dependencies
5. Executes extraction with source grounding for validation
6. Provides review UI for human oversight

**Result:** From months of manual work to minutes of automated extraction.

---

## System Architecture

eviStream has a three-layer architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER (app/)                     │
│  Streamlit UI for form building, PDF upload, and extraction     │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────┐
│                    CORE PROCESSING LAYER (core/)                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  GENERATORS (core/generators/) - The Intelligence Hub    │   │
│  │  • Workflow Orchestrator (LangGraph)                     │   │
│  │  • Form Decomposer (LLM-powered analysis)               │   │
│  │  • Signature Generator (DSPy code generation)           │   │
│  │  • Module Generator (Pipeline assembly)                 │   │
│  │  • Validators (Comprehensive validation)                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  Supporting Core Components:                                     │
│  • Extractor: Runs generated pipelines                          │
│  • Form Schema Builder: Form definition utilities               │
│  • File Handler: PDF/Markdown processing                        │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────┐
│              EXECUTION LAYER (dspy_components/tasks/)            │
│  Generated DSPy signatures & modules for each form:             │
│  • patient_population/     (hand-crafted example)               │
│  • outcomes_study/          (hand-crafted example)              │
│  • dynamic_<hash>/          (auto-generated for custom forms)   │
│  Each contains:                                                  │
│    - signatures.py: DSPy signature definitions                  │
│    - modules.py: Async extraction modules                       │
│    - metadata.json: Form specification                          │
└─────────────────────────────────────────────────────────────────┘
```

### Directory Structure Explained

**`/app`** - User Interface Layer
```
app/
├── main.py                    # Streamlit entry point
├── components/                # Reusable UI components
│   ├── form_review_ui.py     # Human-in-the-loop review interface
│   ├── pdf_viewer.py         # PDF rendering with highlighting
│   └── sidebar.py            # Navigation and project selector
└── views/                     # Tab-based views
    ├── forms_tab.py          # Form builder UI
    ├── documents_tab.py      # PDF upload management
    ├── extraction_tab.py     # Trigger extraction runs
    └── results_tab.py        # View and edit extracted data
```

**`/core`** - Business Logic Layer
```
core/
├── generators/                # THE INTELLIGENCE CORE ⭐
│   ├── workflow.py           # LangGraph orchestration (550+ lines)
│   ├── decomposition.py      # Form cognitive analysis (400+ lines)
│   ├── signature_gen.py      # DSPy signature code gen (290+ lines)
│   ├── module_gen.py         # Module template assembly (250+ lines)
│   ├── models.py             # Pydantic state definitions (375+ lines)
│   ├── decomposition_validator.py  # Validation engine (430+ lines)
│   ├── signature_validator.py      # Syntax validation
│   ├── module_validator.py         # Module validation
│   ├── human_review.py       # Human-in-the-loop handler
│   ├── form_review_bridge.py # UI bridge for reviews
│   ├── task_utils.py         # File system utilities
│   └── prompts/              # LLM prompt templates
│       ├── decompose_form.md      # 450-line cognitive analysis prompt
│       ├── signature_prompt.md    # 425-line signature generation prompt
│       └── module_prompt.md       # Module generation instructions
│
├── extractor.py              # Pipeline executor
├── form_schema_builder.py    # Form definition helpers
└── file_handler.py           # PDF/Markdown conversion
```

**`/dspy_components/tasks`** - Generated Code Repository
```
dspy_components/tasks/
├── patient_population/       # Hand-crafted reference implementation
│   ├── signatures.py         # 6 signatures (207 lines)
│   └── modules.py           # 6 modules + pipeline (337 lines)
│
└── dynamic_<project>_<form>/ # Auto-generated for each custom form
    ├── metadata.json         # Original form specification
    ├── signatures.py         # Generated DSPy signatures
    └── modules.py           # Generated extraction modules
```

---

## Core Generators - The Heart of the System

The `core/generators/` directory contains the **most critical innovation** in eviStream: automated DSPy code generation through cognitive workflow analysis.

### Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                    WORKFLOW ORCHESTRATOR                        │
│                      (workflow.py)                              │
│              LangGraph-based state machine                      │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Decompose │→ │Validate  │→ │Generate  │→ │Generate  │      │
│  │  Form    │  │Decompose │  │Signature │  │ Modules  │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│       │ retry       │              │              │             │
│       └─────────────┘              │              │             │
└──────────────────────────────────────┬─────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
           ┌────────▼─────────┐  ┌────▼────┐  ┌────────▼────────┐
           │  Decomposition    │  │Signature│  │   Module        │
           │   Generator       │  │Generator│  │  Generator      │
           │(decomposition.py) │  │   (+)   │  │(module_gen.py) │
           └──────────────────┘  │Validator│  └────────┬────────┘
                                 └─────────┘           │
                                                        │
                    ┌───────────────────────────────────┘
                    │
           ┌────────▼─────────┐
           │ Assembly &        │
           │ File Writing      │
           │(task_utils.py)   │
           └───────────────────┘
```

### Component Deep Dive

#### 1. Workflow Orchestrator (`workflow.py`)

**Purpose**: Coordinates the entire code generation process using LangGraph.

**Key Responsibilities:**
- Manages workflow state across all generation stages
- Implements validation loops with retry logic
- Handles human-in-the-loop review checkpoints
- Assembles final output files

**LangGraph Workflow Structure:**
```python
class WorkflowOrchestrator:
    def _build_complete_task_workflow(self):
        workflow = StateGraph(CompleteTaskGenerationState)
        
        # Define nodes (each is a generation/validation step)
        workflow.add_node("decompose", self._node_decompose_form)
        workflow.add_node("validate_decomposition", self._node_validate_decomposition)
        workflow.add_node("human_review", self._node_human_review)
        workflow.add_node("generate_signatures", self._node_generate_signatures)
        workflow.add_node("generate_modules", self._node_generate_modules)
        workflow.add_node("finalize", self._node_finalize_and_assemble)
        
        # Define routing logic
        workflow.add_conditional_edges(
            "validate_decomposition",
            self._route_after_decomposition_validation,
            {
                "generate_signatures": "generate_signatures",  # Valid
                "human_review": "human_review",                # Needs review
                "finalize": "finalize"                         # Failed
            }
        )
        
        # Compile with checkpointing for pause/resume
        self.complete_task_workflow = workflow.compile(
            checkpointer=MemorySaver(),
            interrupt_before=["human_review"]
        )
```

**Why This Design?**
- **Stateful**: Each node reads and updates shared state
- **Resumable**: Can pause for human review and continue later
- **Debuggable**: Clear stage transitions logged throughout
- **Robust**: Automatic retry logic for transient failures

**State Managed Throughout Workflow:**
```python
class CompleteTaskGenerationState(TypedDict):
    # Input
    form_data: Dict[str, Any]           # Original form definition
    task_name: str                       # Unique task identifier
    
    # Decomposition stage
    decomposition: Optional[Dict]        # Cognitive analysis result
    decomposition_valid: bool            # Validation status
    decomposition_feedback: str          # Feedback for retry
    
    # Generation stage
    signatures_code: List[Dict]          # Generated signature code
    modules_code: List[str]              # Generated module code
    
    # Workflow control
    current_stage: str                   # Current workflow position
    attempt: int                         # Retry counter
    errors: List[str]                    # Accumulated errors
    
    # Output
    result: Optional[Dict]               # Final assembled output
    status: str                          # "completed", "failed", "needs_review"
```

#### 2. Decomposition Engine (`decomposition.py`)

**Purpose**: Analyzes form structure and decomposes it into atomic extraction tasks using cognitive workflow analysis.

**The Core Challenge**: Given a form with N fields, how do we group them into M signatures such that:
1. Each field is covered exactly once
2. Related fields are grouped together
3. Dependencies are properly identified
4. The extraction workflow is natural and efficient

**Solution**: LLM-powered cognitive analysis with a 450-line structured prompt.

**Decomposition Process:**
```python
def decompose_form(
    form_data: Dict[str, Any],
    model_name: str = "anthropic:claude-sonnet-4-5",
    feedback: Optional[str] = None
) -> Dict[str, Any]:
    """
    Single-stage decomposition: LLM groups fields, code handles the rest.
    
    Returns:
        {
            "reasoning_trace": "Step-by-step decomposition logic",
            "signatures": [
                {
                    "name": "IdentifyStudySource",
                    "field_names": ["reference_id", "first_author"],
                    "depends_on": []
                },
                {
                    "name": "ExtractOutcomes",
                    "field_names": ["outcome_code", "events_count"],
                    "depends_on": ["reference_id"]  # Needs context
                }
            ],
            "pipeline": [...],      # Auto-generated from dependencies
            "field_coverage": {...} # Field-to-signature mapping
        }
    """
```

**Cognitive Workflow Analysis Prompt Strategy:**

The prompt teaches the LLM to think like a human completing the form:

```markdown
# Prompt Structure (decompose_form.md)

1. Understanding Workflow Stages (150 lines)
   - Context Establishment: What needs to be known first?
   - Classification: What categories exist?
   - Data Extraction: What facts to collect?
   - Synthesis: What summaries needed?

2. Grouping Rules (100 lines)
   - Rule 1: Context fields always go first
   - Rule 2: Group by information source
   - Rule 3: Group fields sharing "lookup coordinates"
   - Rule 4: Separate dependent syntheses
   - Rule 5: Handle special fields (comments, specifications)

3. Identifying Dependencies (80 lines)
   - True dependencies: Need value X to find value Y
   - Not dependencies: Conditional fields (only filled sometimes)

4. Complete Examples (120 lines)
   - Full worked examples with reasoning traces
   - Common patterns for medical forms
```

**Example Decomposition:**

Input form (Dental Outcomes):
```json
{
  "form_name": "Dental Analgesia Outcomes",
  "fields": [
    {"field_name": "reference_id", "field_type": "text"},
    {"field_name": "population_code", "field_type": "number"},
    {"field_name": "outcome_code", "field_type": "number"},
    {"field_name": "follow_up_time", "field_type": "text"},
    {"field_name": "events_count", "field_type": "number"}
  ]
}
```

LLM produces:
```json
{
  "reasoning_trace": "Step 1: Context establishment needs reference_id first. Step 2: Classification of population and outcome can happen in parallel. Step 3: Events extraction depends on outcome_code as lookup coordinate.",
  
  "signatures": [
    {
      "name": "IdentifyStudySource",
      "field_names": ["reference_id"],
      "depends_on": []
    },
    {
      "name": "ClassifyClinicalContext",
      "field_names": ["population_code", "outcome_code"],
      "depends_on": []
    },
    {
      "name": "DefineTimepoint",
      "field_names": ["follow_up_time"],
      "depends_on": []
    },
    {
      "name": "ExtractEvents",
      "field_names": ["events_count"],
      "depends_on": ["outcome_code", "follow_up_time"]
    }
  ]
}
```

**Post-LLM Processing (Pure Python):**

1. **Enrich Signatures with Metadata**: Merge field metadata from form_data
```python
enriched_signatures = _enrich_signatures_with_metadata(
    llm_signatures, form_data
)
# Each signature now has full field definitions:
# {"name": "...", "fields": {"field_name": {full_metadata}}, "depends_on": [...]}
```

2. **Build Field Coverage Map**: Track which signature handles which field
```python
field_coverage = _build_field_coverage(enriched_signatures)
# {"reference_id": "IdentifyStudySource", "outcome_code": "ClassifyClinicalContext"}
```

3. **Auto-Generate Pipeline**: Create execution stages from dependencies
```python
pipeline = _auto_generate_pipeline(enriched_signatures)
# [
#   {"stage": 1, "signatures": ["IdentifyStudySource", "ClassifyClinicalContext"], "execution": "parallel"},
#   {"stage": 2, "signatures": ["ExtractEvents"], "execution": "sequential", "depends_on": stage 1}
# ]
```

**Why This Approach Works:**
- **LLM Handles Semantics**: Understanding form intent and grouping logic
- **Code Handles Structure**: Deterministic metadata merging and pipeline generation
- **Validation**: Comprehensive checks before proceeding
- **Retry Logic**: Feedback loop if validation fails

#### 3. Signature Generator (`signature_gen.py`)

**Purpose**: Converts enriched signature specifications into production-ready DSPy signature code.

**Input**: Enriched signature from decomposition
```python
enriched_sig = {
    "name": "ExtractDiagnosis",
    "fields": {
        "diagnosis": {
            "field_name": "diagnosis",
            "field_type": "text",
            "field_description": "Primary diagnosis",
            "extraction_hints": ["Look in assessment section"]
        }
    },
    "depends_on": []
}
```

**Output**: Python code string
```python
import dspy

class ExtractDiagnosis(dspy.Signature):
    """Extract primary diagnosis from medical record."""
    
    markdown_content: str = dspy.InputField(
        desc="Full markdown content of the medical research paper"
    )
    
    diagnosis: Dict[str, Any] = dspy.OutputField(
        desc="""Primary diagnosis.
        
        Description: Primary diagnosis
        
        Extraction Hints:
        - Look in assessment section
        
        Rules:
        - Extract verbatim from document
        - Use "NR" if not reported
        
        Source Grounding:
        - Return: {"value": <diagnosis>, "source_text": <quote>}
        
        Examples:
        {"value": "Type 2 Diabetes", "source_text": "Patient diagnosed with..."}
        {"value": "NR", "source_text": "NR"}
        """
    )
```

**Generation Strategy: Structured Output + Templates**

Unlike asking the LLM to generate Python code directly (error-prone), we use a two-step process:

**Step 1: LLM generates JSON specification**
```python
def _generate_spec_from_enriched_sig(
    self, enriched_sig: Dict, validation_feedback: str = ""
) -> SignatureSpec:
    # Load 425-line prompt template
    prompt = load_prompt("signature_prompt.md")
    prompt = prompt.replace("[[ENRICHED_SIGNATURE_JSON]]", json.dumps(enriched_sig))
    
    # Use structured output to get validated JSON
    structured_model = self.model.with_structured_output(SignatureSpec)
    spec = structured_model.invoke(prompt)
    
    # Pydantic validates structure automatically
    return spec
```

**Step 2: Python template generates code from spec**
```python
def _generate_code_from_spec(self, spec: SignatureSpec) -> str:
    """Convert validated spec to Python code using deterministic templates."""
    
    code_lines = ["import dspy"]
    
    # Add class definition
    code_lines.extend([
        f"class {spec.class_name}(dspy.Signature):",
        f'    """{spec.class_docstring}"""'
    ])
    
    # Add input fields
    for field in spec.input_fields:
        code_lines.extend([
            f"    {field.field_name}: {field.field_type} = dspy.InputField(",
            f'        desc="""{field.description}"""',
            "    )"
        ])
    
    # Add output fields
    for field in spec.output_fields:
        code_lines.extend([
            f"    {field.field_name}: {field.field_type} = dspy.OutputField(",
            f'        desc="""{field.description}"""',
            "    )"
        ])
    
    return "\n".join(code_lines)
```

**Why This Split Approach?**
- **Validation**: Pydantic catches structural errors before code generation
- **Determinism**: Template ensures syntactically correct Python
- **Debugging**: JSON spec is human-readable
- **Retry**: Can regenerate code from same spec with tweaks

**Signature Prompt Strategy (signature_prompt.md):**

The 425-line prompt teaches the LLM to design signatures with:

1. **One Output Field Per Extracted Value** (not composite objects)
2. **Source Grounding**: Every field returns `{"value": <data>, "source_text": <quote>}`
3. **Complete Descriptions**: Include extraction rules, options, hints, examples
4. **Type Mapping**: text→str, number→int, enum→str with options listed
5. **Context Fields**: Add input fields for dependencies

**Validation and Retry:**
```python
def generate_signature(
    self, enriched_sig: Dict, max_attempts: int = 3
) -> Dict[str, Any]:
    validation_feedback = ""
    
    for attempt in range(max_attempts):
        # Generate spec from enriched signature
        spec = self._generate_spec_from_enriched_sig(
            enriched_sig, validation_feedback
        )
        code = self._generate_code_from_spec(spec)
        
        # Validate syntax and structure
        is_valid, errors = self.validator.validate_signature(code)
        
        if is_valid:
            return {"code": code, "is_valid": True}
        
        # Retry with feedback
        validation_feedback = "\n".join(errors)
    
    return {"code": code, "is_valid": False, "errors": errors}
```

#### 4. Module Generator (`module_gen.py`)

**Purpose**: Wraps generated signatures in async DSPy modules with error handling.

**Key Innovation**: Modules are **pure templates** - no LLM needed!

**Generation Strategy:**
```python
def generate_module_code(
    self,
    signature_class_name: str,
    fallback_structure: Dict[str, Any]
) -> str:
    """Generate async module using deterministic template."""
    
    module_class_name = f"Async{signature_class_name}Extractor"
    
    # Extract field names for result building
    field_names = list(fallback_structure.keys())
    
    # Build field extraction code
    field_extraction = "{\n"
    for field in field_names:
        field_extraction += f'            "{field}": getattr(result, "{field}", {{"value": "NR", "source_text": "NR"}}),\n'
    field_extraction += "        }"
    
    # Generate module code
    return f'''
class {module_class_name}(dspy.Module):
    """Async module to extract data using {signature_class_name} signature."""

    def __init__(self):
        super().__init__()
        self.extract = dspy.ChainOfThought({signature_class_name})

    async def __call__(self, markdown_content: str, **kwargs) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        
        def _extract():
            return self.extract(markdown_content=markdown_content, **kwargs)
        
        try:
            result = await loop.run_in_executor(None, _extract)
            return {field_extraction}
        except Exception as e:
            print(f"Error in {module_class_name}: {{e}}")
            return {json.dumps(fallback_structure, indent=12)}
'''
```

**Module Template Features:**
- **Async Execution**: Uses `asyncio.run_in_executor` for non-blocking LLM calls
- **Chain of Thought**: Wraps signature in `dspy.ChainOfThought` for reasoning
- **Error Recovery**: Returns fallback structure with "NR" values on failure
- **Context Support**: Accepts `**kwargs` for dependency fields

**Why Templates Instead of LLM?**
- **Speed**: Instant generation (no API call)
- **Reliability**: Always syntactically correct
- **Cost**: Zero tokens used
- **Consistency**: All modules follow same pattern

#### 5. Decomposition Validator (`decomposition_validator.py`)

**Purpose**: Comprehensive validation of decomposition results before code generation.

**Four Validation Checks:**

**1. Field Coverage Validation**
```python
# Check: Every form field covered exactly once
form_fields = {"reference_id", "diagnosis", "treatment"}
covered_fields = {"reference_id", "diagnosis"}  # From signatures

missing_fields = form_fields - covered_fields
# ["treatment"] ← FAIL

extra_fields = covered_fields - form_fields
# [] ← OK
```

**2. Duplicate Assignment Detection**
```python
# Check: No field assigned to multiple signatures
def detect_duplicate_field_assignments(signatures):
    field_assignments = {}
    for sig in signatures:
        for field_name in sig["fields"]:
            field_assignments[field_name].append(sig["name"])
    
    duplicates = {field: sigs for field, sigs in field_assignments.items() if len(sigs) > 1}
    # {"diagnosis": ["Sig1", "Sig2"]} ← FAIL if duplicates exist
```

**3. DAG Dependency Validation**
```python
# Check: No circular dependencies
def validate_dag_dependencies(signatures):
    # Build dependency graph
    dependency_graph = {}  # sig_name -> list of required fields
    output_providers = {}  # field_name -> sig_name that produces it
    
    for sig in signatures:
        dependency_graph[sig["name"]] = sig["depends_on"]
        for field in sig["fields"]:
            output_providers[field] = sig["name"]
    
    # Detect cycles using DFS
    visited = set()
    rec_stack = set()
    
    def has_cycle(sig_name, path):
        if sig_name in rec_stack:
            return path + [sig_name]  # Cycle found!
        # ... DFS logic
    
    # Also verify topological sort is possible
    execution_order = topological_sort(dependency_graph, output_providers)
```

**4. Pipeline Stage Validation**
```python
# Check: Pipeline structure is valid
def validate_pipeline_stages(pipeline, signatures):
    issues = []
    
    # Check all signatures are assigned to stages
    # Check no signature appears in multiple stages
    # Check waits_for_stage references exist
    # Check stage numbers are unique
    
    return is_valid, issues
```

**Validation in Workflow:**
```python
def _node_validate_decomposition(self, state):
    validator = DecompositionValidator()
    is_valid, validation_results = validator.validate_complete_decomposition(
        state["decomposition"],
        state["form_data"]
    )
    
    if not is_valid:
        # Build feedback for retry
        issues = validation_results["issues"]
        state["decomposition_feedback"] = "\n".join(issues)
        
        # Retry decomposition with feedback
        return route_to("decompose")
    else:
        # Proceed to code generation
        return route_to("generate_signatures")
```

**Why Comprehensive Validation?**
- **Prevents Invalid Code**: Catch issues before generation
- **Retry with Feedback**: Specific error messages help LLM fix issues
- **Quality Assurance**: Multiple validation layers ensure correctness
- **Debugging**: Clear validation results for troubleshooting

#### 6. Prompt Engineering (`prompts/`)

**Purpose**: Carefully crafted prompts that guide LLMs through code generation.

**Three Key Prompts:**

**decompose_form.md** (450 lines)
- Teaches cognitive workflow analysis
- Provides grouping heuristics
- Includes worked examples
- Defines dependency identification rules

**signature_prompt.md** (425 lines)
- Explains DSPy signature concepts
- Details source grounding requirements
- Provides complete examples with context fields
- Specifies field description structure

**module_prompt.md** (Not used - templates instead)
- Originally for LLM-based module generation
- Deprecated in favor of deterministic templates

**Prompt Engineering Techniques:**

1. **Few-Shot Learning**: Complete worked examples
```markdown
Example 1: Meta-analysis Outcomes Form
Input: {...form data...}
Output: {...complete decomposition...}
Reasoning: Step 1: ..., Step 2: ..., Step 3: ...
```

2. **Structured Thinking**: Step-by-step frameworks
```markdown
Step 1: Understand the form's purpose
Step 2: Identify natural workflow sequence
Step 3: Group fields by workflow stage
Step 4: Name signatures descriptively
Step 5: Identify dependencies
Step 6: Verify coverage
```

3. **Constraint Specification**: Clear requirements
```markdown
CRITICAL REQUIREMENTS:
1. ✅ Every field must appear exactly once
2. ✅ Use descriptive names, not generic ones
3. ✅ depends_on lists field names, not signature names
```

4. **Common Mistake Prevention**:
```markdown
❌ WRONG: Group by field type
✓ RIGHT: Group by workflow stage

❌ WRONG: "depends_on": ["SignatureName"]
✓ RIGHT: "depends_on": ["field_name"]
```

---

## Complete Workflow

### End-to-End Process

```
┌──────────────────────────────────────────────────────────────────┐
│  1. USER: Define Form in Streamlit UI                            │
│     • Add fields (text, number, enum, subform)                   │
│     • Describe each field's purpose                              │
│     • Optionally add extraction hints                            │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  2. SYSTEM: Trigger DSPy Code Generation                         │
│     generate_task_from_form(form_data, project_id, form_id)     │
│     • Validates form structure                                   │
│     • Generates unique task name                                 │
│     • Calls WorkflowOrchestrator                                 │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  3. ORCHESTRATOR: Start LangGraph Workflow                       │
│     orchestrator.generate_complete_task(form_data)               │
│     • Initializes workflow state                                 │
│     • Enters decomposition stage                                 │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  4. DECOMPOSITION: Cognitive Form Analysis                       │
│     decompose_form(form_data)                                    │
│     ┌──────────────────────────────────────────────────────────┐│
│     │ LLM analyzes form with 450-line prompt:                  ││
│     │ • Identifies workflow stages                             ││
│     │ • Groups related fields                                  ││
│     │ • Detects dependencies                                   ││
│     │ • Returns: signatures with field groupings              ││
│     └──────────────────────────────────────────────────────────┘│
│     ┌──────────────────────────────────────────────────────────┐│
│     │ Python enriches and processes:                           ││
│     │ • Merges field metadata from form_data                   ││
│     │ • Builds field coverage map                              ││
│     │ • Auto-generates pipeline stages from dependencies       ││
│     └──────────────────────────────────────────────────────────┘│
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  5. VALIDATION: Comprehensive Checks                             │
│     validator.validate_complete_decomposition()                  │
│     • Field coverage: All fields covered exactly once?           │
│     • Duplicate detection: No field in multiple signatures?      │
│     • DAG validation: No circular dependencies?                  │
│     • Pipeline validation: Stages properly structured?           │
│                                                                   │
│     If FAIL: Retry decomposition with feedback ──┐              │
│     If PASS: Proceed to code generation ──────────┼───────────┐ │
└───────────────────────────────────────────────────┘           │ │
                                                                │ │
       ┌────────────────────────────────────────────────────────┘ │
       │                                                            │
       ▼                                                            │
┌──────────────────────────────────────────────────────────────────┐
│  6. SIGNATURE GENERATION: Create DSPy Signatures                 │
│     For each signature in decomposition:                         │
│     signature_gen.generate_signature(enriched_sig)               │
│     ┌──────────────────────────────────────────────────────────┐│
│     │ LLM generates JSON spec with 425-line prompt:            ││
│     │ • class_name, class_docstring                            ││
│     │ • input_fields (document + context fields)               ││
│     │ • output_fields (one per extracted value)                ││
│     │ Returns: SignatureSpec (Pydantic model)                  ││
│     └──────────────────────────────────────────────────────────┘│
│     ┌──────────────────────────────────────────────────────────┐│
│     │ Python template generates code:                          ││
│     │ • Deterministic code generation from spec                ││
│     │ • Validates syntax                                       ││
│     │ • Retries if invalid (with feedback)                     ││
│     └──────────────────────────────────────────────────────────┘│
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  7. MODULE GENERATION: Wrap Signatures                           │
│     For each signature:                                          │
│     module_gen.generate_module(class_name, fallback)             │
│     • Uses deterministic template (no LLM)                       │
│     • Creates async module with error handling                   │
│     • Adds Chain of Thought reasoning                            │
│     • Includes fallback structure                                │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  8. ASSEMBLY: Create Complete Files                              │
│     • Assemble signatures.py:                                    │
│       - Unified imports (dspy, typing)                           │
│       - All signature classes                                    │
│       - __all__ export list                                      │
│     • Assemble modules.py:                                       │
│       - Imports (asyncio, dspy, signatures)                      │
│       - All module classes                                       │
│       - Pipeline class (orchestrates execution)                  │
│       - __all__ export list                                      │
│     • Create metadata.json:                                      │
│       - Original form specification                              │
│       - Project and form IDs                                     │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  9. FILE WRITING: Save to Disk                                   │
│     task_dir = dspy_components/tasks/dynamic_<project>_<form>/   │
│     • Write signatures.py                                        │
│     • Write modules.py                                           │
│     • Write metadata.json                                        │
│     • Write __init__.py                                          │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  10. REGISTRATION: Load Dynamic Schema                           │
│      load_dynamic_schemas()                                      │
│      • Scans dspy_components/tasks/ for dynamic_* folders        │
│      • Imports generated modules dynamically                     │
│      • Registers schema in runtime registry                      │
│      • Makes available for extraction UI                         │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  11. USER: Upload PDFs & Run Extraction                          │
│      • Upload research papers via documents tab                  │
│      • Select form and document in extraction tab                │
│      • Click "Run Extraction"                                    │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  12. EXTRACTION: Execute Pipeline                                │
│      extractor.run_async_extraction(markdown, schema_runtime)    │
│      ┌──────────────────────────────────────────────────────────┐│
│      │ Load generated pipeline from dynamic task folder         ││
│      │ pipeline = AsyncPipeline()                               ││
│      └──────────────────────────────────────────────────────────┘│
│      ┌──────────────────────────────────────────────────────────┐│
│      │ Execute pipeline stages in order:                        ││
│      │ Stage 1: Independent signatures run in parallel          ││
│      │   → Each calls LLM with DSPy ChainOfThought             ││
│      │   → Returns {field: {"value": X, "source_text": Y}}     ││
│      │ Stage 2: Dependent signatures run sequentially           ││
│      │   → Receive context from Stage 1 outputs                 ││
│      │   → Extract dependent fields                             ││
│      └──────────────────────────────────────────────────────────┘│
│      ┌──────────────────────────────────────────────────────────┐│
│      │ Aggregate results:                                       ││
│      │ • Flatten nested dictionaries                            ││
│      │ • Preserve source grounding for each field               ││
│      │ • Handle "NR" values gracefully                          ││
│      └──────────────────────────────────────────────────────────┘│
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  13. RESULTS: Display & Edit                                     │
│      • Show extracted values with source text                    │
│      • Highlight source locations in PDF                         │
│      • Allow manual corrections                                  │
│      • Export to JSON                                            │
└──────────────────────────────────────────────────────────────────┘
```

### Workflow Timeline

**Initial Form Setup** (One-time per form type)
- User defines form: 5-10 minutes
- Code generation: 2-3 minutes (LLM calls)
- Testing: 5-10 minutes

**Per-Document Extraction** (Repeatable)
- Upload PDF: 10 seconds
- Run extraction: 30-120 seconds (depending on form complexity)
- Review results: 2-5 minutes
- Export: instant

### Error Handling at Each Stage

**Decomposition Failures:**
- Missing field coverage → Retry with feedback
- Circular dependencies → Retry with dependency hints
- Invalid groupings → Retry with workflow clarification

**Generation Failures:**
- Syntax errors in signatures → Retry with validation feedback
- Missing fields → Retry with field requirements
- Type mismatches → Retry with type specifications

**Extraction Failures:**
- LLM timeout → Return fallback with "NR" values
- Malformed output → Safe JSON parsing with defaults
- Missing context → Log error, continue with available fields

---

## Technology Stack & Rationale

### Core Technologies

#### 1. DSPy (Structured LLM Programming)

**What**: Framework for programming language models declaratively  
**Version**: Latest (pip install dspy)  
**License**: Apache 2.0

**Why We Use It:**
- **Type-Safe Prompting**: Define input/output schemas instead of string templates
- **Composability**: Chain signatures into complex pipelines
- **Source Grounding**: Natural fit for value + source_text pairs
- **ChainOfThought**: Built-in reasoning improves extraction accuracy
- **Optimization**: Can auto-tune prompts (future capability)

**Alternative Considered:**
- **LangChain**: More general-purpose, less focused on structured extraction
- **Plain OpenAI API**: Would require extensive prompt engineering and parsing
- **Guidance**: Less mature ecosystem

**Why DSPy Won:**
DSPy's signature abstraction perfectly matches our use case: structured data extraction with source grounding.

#### 2. LangGraph (Workflow Orchestration)

**What**: Framework for building stateful LLM workflows  
**Version**: Latest (pip install langgraph)  
**License**: MIT

**Why We Use It:**
- **State Management**: Persistent state across multi-step workflow
- **Conditional Routing**: Different paths based on validation results
- **Checkpointing**: Pause for human review, resume later
- **Retry Logic**: Automatic retry with feedback
- **Debuggability**: Clear visibility into workflow stages

**Alternative Considered:**
- **Apache Airflow**: Too heavy for LLM workflows, designed for data pipelines
- **Prefect**: Similar issues, not LLM-aware
- **Plain Python**: Would require extensive boilerplate for state management

**Why LangGraph Won:**
Purpose-built for LLM workflows with built-in checkpointing and conditional logic.

#### 3. Streamlit (User Interface)

**What**: Python library for building data apps  
**Version**: Latest (pip install streamlit)  
**License**: Apache 2.0

**Why We Use It:**
- **Rapid Development**: UI in pure Python, no frontend expertise needed
- **Interactive**: Built-in state management and reactivity
- **Rich Components**: File upload, tabs, forms out of the box
- **Deployment**: Easy deployment with Streamlit Cloud

**Alternative Considered:**
- **Flask + React**: More flexible but much slower development
- **Gradio**: Simpler but less customizable
- **Django**: Overkill for this use case

**Why Streamlit Won:**
Fastest path to a functional UI with minimal code.

#### 4. Anthropic Claude (Primary LLM)

**Model**: claude-sonnet-4-5-20250929  
**Why**: Best instruction-following for code generation tasks

**Usage:**
- Decomposition: Cognitive workflow analysis
- Signature Generation: DSPy specification creation

**Fallback**: Google Gemini 2.0 Flash (faster, cheaper for simple tasks)

#### 5. LangChain (LLM Abstraction)

**What**: Unified interface for calling different LLMs  
**Version**: Latest (pip install langchain)

**Why We Use It:**
- **Structured Output**: `with_structured_output(PydanticModel)`
- **Provider Abstraction**: Switch between Claude, GPT-4, Gemini easily
- **Retry Logic**: Built-in retry with exponential backoff

#### 6. Pydantic (Data Validation)

**What**: Data validation using Python type annotations  
**Version**: v2.x (pip install pydantic)

**Why We Use It:**
- **Structured Output Validation**: Ensures LLM returns correct schema
- **Type Safety**: Catch errors at generation time, not runtime
- **Documentation**: Auto-generates JSON schemas
- **Serialization**: Easy conversion to/from JSON

### Supporting Technologies

#### PDF Processing

**Libraries:**
- `pdf2image`: PDF to image conversion
- `PyMuPDF` (fitz): PDF text extraction
- `marker`: PDF to markdown conversion (for extraction)

**Why Multiple Tools:**
- Viewing: pdf2image for high-quality rendering
- Extraction: marker for markdown (preserves structure)
- Highlighting: PyMuPDF for coordinate-based annotations

#### Storage

**Supabase** (optional): PostgreSQL database for project storage  
**JSON Files** (fallback): Local storage for development

#### Python Environment

**Requirements:**
```
dspy                    # Structured LLM programming
streamlit               # UI framework
langgraph               # Workflow orchestration
langchain              # LLM abstraction
pydantic               # Data validation
anthropic              # Claude API
google-generativeai    # Gemini API
pandas                 # Data manipulation
tiktoken               # Token counting
sentence-transformers  # Semantic similarity
python-dotenv          # Environment variables
aiofiles               # Async file I/O
diskcache              # LLM response caching
```

### Technology Decision Matrix

| **Requirement** | **Solution** | **Why** |
|----------------|--------------|---------|
| Structured LLM prompting | DSPy | Type-safe signatures, composability |
| Multi-step code generation | LangGraph | State management, checkpointing |
| LLM selection | Claude Sonnet 4.5 | Best instruction-following |
| Structured output | LangChain + Pydantic | Guaranteed valid JSON |
| User interface | Streamlit | Rapid development in Python |
| PDF processing | Marker + PyMuPDF | Quality markdown extraction |
| Storage | Supabase / JSON | Flexible, scalable |
| Async execution | asyncio | Non-blocking LLM calls |
| Caching | diskcache | Avoid redundant LLM calls |

---

## Implementation Details

### DSPy Signatures in Practice

#### Source Grounding Convention

Every output field uses this structure:
```python
field_name: Dict[str, Any] = dspy.OutputField(
    desc="""Description...
    
    Source Grounding:
    - Return: {"value": <extracted_value>, "source_text": <quote>}
    - value: The actual extracted data
    - source_text: Verbatim quote from document (1-3 sentences)
    - If not found: {"value": "NR", "source_text": "NR"}
    """
)
```

**Why This Pattern:**
- **Validation**: Users can verify extraction accuracy
- **Error Detection**: Spot hallucinations by checking source
- **Annotation**: Source text can be highlighted in PDF
- **Consistency**: "NR" convention prevents confusion between missing data and empty strings

#### Example Generated Signature

From eviStream's auto-generated code:
```python
class IdentifyStudySource(dspy.Signature):
    """Extract study identification details from research paper.
    
    Form Questions:
    - reference_id: "What is the reference ID or citation key?"
    - first_author: "Who is the first author?"
    - trial_name: "What is the trial name (if applicable)?"
    """
    
    markdown_content: str = dspy.InputField(
        desc="Full markdown content of the medical research paper"
    )
    
    reference_id: Dict[str, Any] = dspy.OutputField(
        desc="""Reference ID or citation key.
        
        Description: Unique identifier for this study
        
        Rules:
        - Extract from author year format if present
        - Use DOI if no other identifier available
        - Use "NR" if not reported
        
        Source Grounding:
        - Return: {"value": "Smith_2024", "source_text": "Smith et al. (2024)..."}
        
        Examples:
        {"value": "Jones_2023", "source_text": "Jones et al. (2023) conducted a randomized trial..."}
        {"value": "NR", "source_text": "NR"}
        """
    )
    
    first_author: Dict[str, Any] = dspy.OutputField(
        desc="""First author name.
        
        Rules:
        - Extract last name only
        - Standardize format: "Smith" not "Smith, J."
        - Use "NR" if not reported
        
        Source Grounding:
        - Return: {"value": "Smith", "source_text": "Smith et al. (2024)..."}
        """
    )
    
    trial_name: Dict[str, Any] = dspy.OutputField(
        desc="""Trial name if applicable.
        
        Rules:
        - Extract acronym if present (e.g., "ASCOT")
        - Use full name if no acronym
        - Use "NR" if not a registered trial
        
        Source Grounding:
        - Return: {"value": "ASCOT", "source_text": "The ASCOT trial (Anglo-Scandinavian Cardiac Outcomes Trial)..."}
        """
    )
```

### DSPy Modules in Practice

#### Async Module Pattern

Every generated module follows this pattern:
```python
class AsyncIdentifyStudySourceExtractor(dspy.Module):
    """Async module to extract study source using IdentifyStudySource signature."""
    
    def __init__(self):
        super().__init__()
        # Chain of Thought adds reasoning steps
        self.extract = dspy.ChainOfThought(IdentifyStudySource)
    
    async def __call__(self, markdown_content: str, **kwargs) -> Dict[str, Any]:
        """
        Extract data from markdown content.
        
        Args:
            markdown_content: Full markdown text
            **kwargs: Additional context fields if needed
        
        Returns:
            Dict with extracted values
        """
        # Get event loop for async execution
        loop = asyncio.get_running_loop()
        
        # Define sync extraction function
        def _extract():
            return self.extract(markdown_content=markdown_content, **kwargs)
        
        try:
            # Run in executor (DSPy is sync, we wrap in async)
            result = await loop.run_in_executor(None, _extract)
            
            # Extract fields from result
            return {
                "reference_id": getattr(result, "reference_id", {"value": "NR", "source_text": "NR"}),
                "first_author": getattr(result, "first_author", {"value": "NR", "source_text": "NR"}),
                "trial_name": getattr(result, "trial_name", {"value": "NR", "source_text": "NR"})
            }
        except Exception as e:
            print(f"Error in AsyncIdentifyStudySourceExtractor: {e}")
            # Return fallback structure
            return {
                "reference_id": {"value": "NR", "source_text": "NR"},
                "first_author": {"value": "NR", "source_text": "NR"},
                "trial_name": {"value": "NR", "source_text": "NR"}
            }
```

#### Pipeline Assembly

Generated pipelines orchestrate signature execution:
```python
class AsyncOutcomesPipeline(dspy.Module):
    """Complete async pipeline for outcomes extraction."""
    
    def __init__(self, max_concurrent: int = 5):
        super().__init__()
        
        # Initialize all extractors
        self.study_source_extractor = AsyncIdentifyStudySourceExtractor()
        self.classification_extractor = AsyncClassifyClinicalContextExtractor()
        self.outcome_extractor = AsyncDefineOutcomeMeasurementExtractor()
        self.events_extractor = AsyncExtractEventDataExtractor()
        
        # Semaphore for rate limiting
        self.max_concurrent = max_concurrent
        self._semaphore = None
    
    async def forward(self, markdown_content: str):
        """Execute multi-stage pipeline."""
        
        # Stage 1: Independent signatures run in parallel
        stage1_tasks = [
            self.study_source_extractor(markdown_content),
            self.classification_extractor(markdown_content),
            self.outcome_extractor(markdown_content)
        ]
        
        study_source, classification, outcome = await asyncio.gather(*stage1_tasks)
        
        # Stage 2: Dependent signature receives context
        # events_extractor needs outcome_code and follow_up_time
        events = await self.events_extractor(
            markdown_content,
            outcome_code=outcome["outcome_code"],
            follow_up_time=outcome["follow_up_time"]
        )
        
        # Combine all results
        complete_data = {
            **study_source,
            **classification,
            **outcome,
            **events
        }
        
        return dspy.Prediction(
            extracted_data=complete_data,
            success=True
        )
```

### LangGraph Workflow in Practice

#### State Definition

```python
from typing import TypedDict, Dict, Any, List, Optional

class CompleteTaskGenerationState(TypedDict):
    # Input
    form_data: Dict[str, Any]           # Form specification
    task_name: str                       # Unique identifier
    thread_id: str                       # For checkpointing
    max_attempts: int                    # Retry limit
    
    # Decomposition stage
    decomposition: Optional[Dict]        # Cognitive analysis result
    decomposition_valid: bool            # Validation status
    decomposition_feedback: str          # Retry feedback
    field_coverage: Dict[str, str]       # Field→signature mapping
    
    # Generation stage
    signatures_code: List[Dict]          # Generated signatures
    modules_code: List[str]              # Generated modules
    field_to_signature_map: Dict         # Complete mapping
    
    # Control flow
    current_stage: str                   # Current workflow position
    attempt: int                         # Retry counter
    errors: List[str]                    # Error accumulation
    warnings: List[str]                  # Warning accumulation
    
    # Human-in-the-loop
    human_review_enabled: bool           # Enable HITL?
    human_feedback: Optional[str]        # Feedback from reviewer
    human_approved: bool                 # Approval status
    decomposition_summary: Optional[str] # Summary for review
    
    # Output
    result: Optional[Dict]               # Final output
    status: str                          # "completed" | "failed" | "needs_review"
```

#### Workflow Nodes

Each node is a pure function that reads and updates state:
```python
def _node_decompose_form(
    self, state: CompleteTaskGenerationState
) -> CompleteTaskGenerationState:
    """Node 1: Decompose form using cognitive behavior analysis."""
    
    print(f"\n{'='*70}")
    print(f"STAGE: Cognitive Decomposition")
    print(f"{'='*70}")
    print(f"Attempt {state['attempt'] + 1}/{state['max_attempts']}")
    
    try:
        # Call decomposition engine
        decomposition = decompose_form(
            state["form_data"],
            model_name=self.model_name,
            feedback=state.get("decomposition_feedback") or None
        )
        
        # Update state
        state["decomposition"] = decomposition
        state["field_coverage"] = decomposition.get("field_coverage", {})
        state["current_stage"] = "decomposition_complete"
        
        num_signatures = len(decomposition.get('signatures', []))
        num_stages = len(decomposition.get('pipeline', []))
        
        print(f"✓ Decomposed into {num_signatures} signatures across {num_stages} stages")
        
    except Exception as e:
        state["errors"].append(f"Decomposition failed: {str(e)}")
        state["current_stage"] = "decomposition_failed"
        print(f"✗ Decomposition failed: {str(e)}")
    
    return state
```

#### Conditional Routing

Route based on state:
```python
def _route_after_decomposition_validation(
    self, state: CompleteTaskGenerationState
) -> str:
    """Decide next step after validation."""
    
    if state["decomposition_valid"]:
        # Check if human review is enabled
        if state.get("human_review_enabled", False):
            return "human_review"
        else:
            return "generate_signatures"
    else:
        # Validation failed
        if state["attempt"] >= state["max_attempts"]:
            return "finalize"  # Give up
        else:
            return "decompose"  # Retry with feedback
```

#### Workflow Compilation

```python
def _build_complete_task_workflow(self):
    """Build and compile the LangGraph workflow."""
    
    workflow = StateGraph(CompleteTaskGenerationState)
    
    # Add nodes
    workflow.add_node("decompose", self._node_decompose_form)
    workflow.add_node("validate_decomposition", self._node_validate_decomposition)
    workflow.add_node("human_review", self._node_human_review)
    workflow.add_node("generate_signatures", self._node_generate_signatures)
    workflow.add_node("generate_modules", self._node_generate_modules)
    workflow.add_node("finalize", self._node_finalize_and_assemble)
    
    # Set entry point
    workflow.set_entry_point("decompose")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "decompose",
        self._route_after_decompose,
        {
            "validate_decomposition": "validate_decomposition",
            "finalize": "finalize"
        }
    )
    
    workflow.add_conditional_edges(
        "validate_decomposition",
        self._route_after_decomposition_validation,
        {
            "generate_signatures": "generate_signatures",
            "human_review": "human_review",
            "finalize": "finalize"
        }
    )
    
    workflow.add_conditional_edges(
        "human_review",
        self._route_after_human_review,
        {"generate_signatures": "generate_signatures"}
    )
    
    workflow.add_conditional_edges(
        "generate_signatures",
        self._route_after_signatures,
        {
            "generate_modules": "generate_modules",
            "finalize": "finalize"
        }
    )
    
    workflow.add_edge("generate_modules", "finalize")
    workflow.add_edge("finalize", END)
    
    # Compile with checkpointing
    interrupt_before = ["human_review"] if self.human_review_enabled else []
    self.complete_task_workflow = workflow.compile(
        checkpointer=MemorySaver(),
        interrupt_before=interrupt_before
    )
```

### Human-in-the-Loop Implementation

#### Pause for Review

```python
def generate_complete_task(
    self,
    form_data: Dict[str, Any],
    task_name: Optional[str] = None,
    thread_id: str = "default"
) -> Dict[str, Any]:
    """Generate complete task with optional human review."""
    
    initial_state = {
        "form_data": form_data,
        "task_name": task_name,
        "thread_id": thread_id,
        "human_review_enabled": self.human_review_enabled,
        # ... other initial state
    }
    
    config = {"configurable": {"thread_id": thread_id}}
    
    # Execute workflow
    for event in self.complete_task_workflow.stream(initial_state, config):
        pass  # Stream events for monitoring
    
    # Get final state
    final_state = self.complete_task_workflow.get_state(config)
    
    # Check if paused for review
    if final_state.next and "human_review" in final_state.next:
        return {
            "status": "awaiting_human_review",
            "thread_id": thread_id,
            "paused": True,
            "decomposition_summary": final_state.values.get("decomposition_summary"),
            "decomposition": final_state.values.get("decomposition"),
            "validation_results": final_state.values.get("validation_results")
        }
    
    # Otherwise, return completed result
    return final_state.values.get("result")
```

#### Resume After Approval

```python
def approve_decomposition(self, thread_id: str = "default") -> Dict[str, Any]:
    """Approve decomposition and continue workflow."""
    
    config = {"configurable": {"thread_id": thread_id}}
    
    # Update state with approval
    self.complete_task_workflow.update_state(
        config,
        {
            "human_approved": True,
            "human_feedback": None
        }
    )
    
    # Resume workflow from checkpoint
    for event in self.complete_task_workflow.stream(None, config):
        pass
    
    final_state = self.complete_task_workflow.get_state(config)
    return final_state.values.get("result")
```

### Extraction Execution

#### Loading Generated Pipelines

```python
def load_dynamic_schemas():
    """Dynamically import generated DSPy components."""
    
    tasks_dir = Path("dspy_components/tasks")
    
    # Find all dynamic task folders
    for task_folder in tasks_dir.glob("dynamic_*"):
        try:
            # Import modules
            task_name = task_folder.name
            modules_path = f"dspy_components.tasks.{task_name}.modules"
            
            # Dynamic import
            modules_module = importlib.import_module(modules_path)
            
            # Get pipeline class
            pipeline_class = getattr(modules_module, f"Async{task_name.title()}Pipeline")
            
            # Register in schema registry
            register_dynamic_schema(task_name, pipeline_class)
            
            print(f"✓ Loaded dynamic schema: {task_name}")
            
        except Exception as e:
            print(f"✗ Failed to load {task_folder.name}: {e}")
```

#### Running Extraction

```python
async def run_async_extraction(
    markdown_content: str,
    schema_runtime: SchemaRuntime
):
    """Execute extraction pipeline on markdown content."""
    
    try:
        # Get pipeline from schema runtime
        async_pipeline = schema_runtime.pipeline
        
        # Execute pipeline (handles multi-stage execution internally)
        pipeline_result = await async_pipeline(markdown_content)
        
        # Extract results
        if isinstance(pipeline_result, dspy.Prediction):
            extracted_data = pipeline_result.extracted_data
        else:
            extracted_data = pipeline_result
        
        # Flatten nested structures
        flattened_results = flatten_json(extracted_data)
        
        return {
            "baseline_results": flattened_results,
            "success": True
        }
        
    except Exception as e:
        print(f"❌ Error in extraction: {e}")
        traceback.print_exc()
        return {
            "baseline_results": [],
            "success": False,
            "error": str(e)
        }
```

---

## Appendix: Key Files Reference

### Core Generation Files

| **File** | **Lines** | **Purpose** |
|----------|-----------|-------------|
| `core/generators/workflow.py` | 787 | LangGraph orchestration |
| `core/generators/decomposition.py` | 397 | Cognitive form analysis |
| `core/generators/signature_gen.py` | 292 | DSPy signature generation |
| `core/generators/module_gen.py` | 249 | Module template assembly |
| `core/generators/models.py` | 375 | Pydantic state models |
| `core/generators/decomposition_validator.py` | 428 | Validation engine |
| `core/generators/prompts/decompose_form.md` | 454 | Decomposition prompt |
| `core/generators/prompts/signature_prompt.md` | 426 | Signature generation prompt |

### Application Files

| **File** | **Lines** | **Purpose** |
|----------|-----------|-------------|
| `app/main.py` | 216 | Streamlit application entry |
| `app/views/forms_tab.py` | ~300 | Form builder UI |
| `app/views/extraction_tab.py` | ~250 | Extraction execution UI |
| `app/views/results_tab.py` | ~200 | Results viewer |
| `core/extractor.py` | 76 | Pipeline executor |

---

## Conclusion

**eviStream** represents a paradigm shift in medical data extraction: from manual coding to AI-powered code generation. By combining DSPy's structured prompting, LangGraph's workflow orchestration, and sophisticated prompt engineering, it transforms custom form definitions into production-ready extraction pipelines in minutes instead of weeks.

**Key Innovations:**
1. **Cognitive Decomposition**: Understanding forms as workflows, not just field lists
2. **Structured Code Generation**: LLM generates specs, templates generate code
3. **Comprehensive Validation**: Multiple validation layers ensure correctness
4. **Source Grounding**: Every extraction includes supporting evidence
5. **Human-in-the-Loop**: Pause workflow for review and approval

**Impact:**
- **Speed**: 67 hours of manual extraction → 10 minutes automated
- **Accuracy**: Source grounding enables verification
- **Flexibility**: New form types in minutes, not weeks
- **Accessibility**: No coding required for clinical researchers

**Future Directions:**
- DSPy prompt optimization for improved accuracy
- Multi-modal extraction (tables, figures)
- Active learning from user corrections
- Batch processing optimization



