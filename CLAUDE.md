# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

**eviStream** is an AI-powered medical data extraction platform that automatically generates DSPy code to extract structured information from research papers. It dynamically creates extraction pipelines from custom form definitions, eliminating the need to manually write extraction code for each systematic review questionnaire.

The system uses a three-stage AI code generation workflow:
1. **Cognitive Decomposition** - Breaks forms into atomic extraction tasks
2. **Code Generation** - Creates DSPy signatures and modules automatically
3. **Pipeline Assembly** - Orchestrates multi-stage execution with dependency management

## Commands

### Running Extractions

**Single file extraction:**
```bash
python run.py single --source /path/to/source.json --target /path/to/target.json --schema patient_population
```

**Batch extraction:**
```bash
python run.py batch --source /path/to/md_directory --target /path/to/target.json --schema patient_population --max-examples 10
```

**Available flags:**
- `--schema NAME` - Select schema to run (see `schemas/` directory)
- `--clear-cache` - Clear DSPy caches before running
- `--max-examples N` - Limit batch processing to N examples
- `--save-dashboards` - Save performance dashboards as PNG files

### Streamlit Application

**Launch the interactive web interface:**
```bash
streamlit run app/main.py
```

The Streamlit app provides a complete workflow for:
- Document upload and PDF processing
- Form creation and management
- AI-powered code generation (via core/generators)
- Extraction execution and results review

### Development Commands

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Clear caches:**
```bash
rm -rf .semantic_cache .evaluation_cache cache/
```

## Architecture

### High-Level System Flow

```
User defines form → AI generates DSPy code → Code extracts from papers → Evaluation compares to ground truth
```

### Core Components

**1. Dynamic Schema System** (`schemas/`)

The schema system enables multiple questionnaire types without touching core code. Each schema is defined by a `DynamicSchemaConfig` that specifies:
- Signature class names (extraction tasks)
- Pipeline stages (execution order and dependencies)
- Field definitions (output structure)

Schemas are registered in `schemas/registry.py` and loaded from:
- Static schemas: `schemas/configs.py`
- Dynamic schemas: Generated at runtime and stored in `dspy_components/tasks/`

**2. Code Generation Pipeline** (`core/generators/`)

The generators create production-ready DSPy extraction code using LangGraph workflows:

- `workflow.py` - Orchestrates the complete generation workflow with LangGraph StateGraph
- `decomposition.py` - Analyzes forms and breaks them into atomic extraction tasks
- `signature_gen.py` - Generates DSPy signature classes (defines LLM input/output contracts)
- `module_gen.py` - Generates async extractor modules (implements extraction logic)
- `decomposition_validator.py` - Validates field coverage and pipeline structure
- `human_review.py` - Enables human-in-the-loop review and refinement

The workflow follows this sequence:
```
Form Definition → Decomposition → Parallel (Signature Gen + Module Gen) →
Validation (Coverage, Syntax, Semantic, Flow) → Refinement Loop → File Assembly → Export
```

Generated code is stored in `dspy_components/tasks/task_<hash>/` or `dspy_components/tasks/dynamic_<uuid>/`

**3. DSPy Task Components** (`dspy_components/tasks/`)

Each task directory contains:
- `signatures.py` - DSPy signature classes (LLM contracts)
- `modules.py` - Async extractor modules (execution logic)
- `__init__.py` - Package initialization

Static tasks: `patient_population`, `index_test`, `outcomes_study`, `missing_data_study`, `reference_standard`
Dynamic tasks: Generated at runtime with `task_<hash>` or `dynamic_<uuid>` naming

**4. Extraction Engine** (`core/`)

- `extractor.py` - Main extraction orchestrator that runs pipelines
- `field_extractor.py` - Extracts field metadata from signatures
- `evaluation.py` - Semantic and exact matching evaluation with DSPy
- `file_handler.py` - Saves extraction results to CSV/JSON
- `config.py` - Central configuration (models, paths, concurrency)

**5. Pipeline Execution** (`schemas/runtime.py`)

The `SchemaRuntime` builds pipelines from `DynamicSchemaConfig` that:
- Execute stages in dependency order
- Support parallel or sequential execution within stages
- Accumulate results and pass them to dependent stages
- Handle errors gracefully with fallback values

**6. Utilities** (`utils/`)

- `lm_config.py` - Centralized LLM configuration (DSPy and LangChain models)
- `logging.py` - LLM call history and cost tracking
- `cache_cleaner.py` - Cache management utilities
- `json_parser.py` - Safe JSON parsing with error recovery
- `helpers/visualization.py` - Performance dashboard generation
- `helpers/print_helpers.py` - Console output formatting

### Key Design Patterns

**1. Staged Pipeline Execution**

Pipelines execute in stages defined in `DynamicSchemaConfig.pipeline_stages`:
```python
pipeline_stages = [
    {"stage": 0, "signatures": ["ExtractBasicInfo"], "execution": "parallel"},
    {"stage": 1, "signatures": ["ExtractDetails"], "execution": "sequential"}
]
```

Later stages can depend on outputs from earlier stages. The `StagedPipeline` class in `schemas/config.py` handles accumulation and dependency resolution.

**2. Async Extractor Modules**

All extractors are async and follow this pattern:
```python
class AsyncFieldExtractor(dspy.Module):
    def __init__(self):
        super().__init__()
        self.extract = dspy.ChainOfThought(ExtractFieldSignature)

    async def __call__(self, markdown_content: str, **kwargs) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, lambda: self.extract(markdown_content=markdown_content))
        return safe_json_parse(result.field_json)
```

**3. Semantic Evaluation with Caching**

The `AsyncMedicalExtractionEvaluator` in `core/evaluation.py` uses:
- DSPy-based semantic matching for field comparison
- Persistent disk caching (`.semantic_cache`, `.evaluation_cache`)
- Configurable concurrency with asyncio semaphores
- Field-level analysis (exact vs semantic matching)

**4. Schema Registry Pattern**

Schemas are registered at startup:
```python
from schemas import get_schema, build_runtime, list_schemas

config = get_schema("patient_population")
runtime = build_runtime(config)
result = await runtime.pipeline(markdown_content)
```

### Data Flow

**Extraction Pipeline:**
```
1. Load markdown + target JSON (data/loader.py)
2. Initialize DSPy LM (utils/lm_config.py)
3. Run extraction pipeline (core/extractor.py)
   - Pipeline executes staged extractors (schemas/runtime.py)
   - Each extractor calls DSPy signatures (dspy_components/tasks/*/modules.py)
   - Results parsed and accumulated (utils/json_parser.py)
4. Evaluate results (core/evaluation.py)
   - Semantic matching with caching
   - Field-level metrics (precision, recall, F1)
5. Save results (core/file_handler.py)
6. Log LLM history (utils/logging.py)
7. Generate dashboards (utils/helpers/visualization.py)
```

**Code Generation Pipeline:**
```
1. User creates form in Streamlit (app/main.py)
2. Form definition passed to WorkflowOrchestrator (core/generators/workflow.py)
3. Decomposition creates extraction plan (core/generators/decomposition.py)
4. Parallel generation:
   - Signatures generated (core/generators/signature_gen.py)
   - Modules generated (core/generators/module_gen.py)
5. Multi-stage validation (core/generators/*_validator.py)
6. Optional human review (core/generators/human_review.py)
7. Files written to dspy_components/tasks/ (core/generators/workflow.py)
8. Schema registered (schemas/registry.py)
9. Ready for extraction execution
```

## Configuration

**Environment variables** (`.env`):
- `SUPABASE_URL` - Supabase project URL (metadata storage)
- `SUPABASE_KEY` - Supabase anon/service key
- API keys for LLM providers (loaded by DSPy/LangChain)

**Core configuration** (`core/config.py`):
- `DEFAULT_MODEL` - Primary extraction model (default: `gemini/gemini-3-pro-preview`)
- `EVALUATION_MODEL` - Semantic evaluation model (default: `gemini/gemini-2.5-flash`)
- `BATCH_CONCURRENCY` - Papers processed in parallel (default: 5)
- `EVALUATION_CONCURRENCY` - Concurrent semantic matching calls (default: 20)
- `TEMPERATURE` - Sampling temperature for extraction (default: 1.0)

**Paths** (relative to project root):
- `outputs/logs/` - LLM history CSVs
- `outputs/dashboards/` - Performance visualizations
- `storage/processed/extracted_pdfs/` - Processed PDFs and markdown
- `storage/uploads/pdfs/` - Uploaded PDF files
- `cache/` - DSPy compilation caches
- `.semantic_cache/` - Semantic similarity cache
- `.evaluation_cache/` - Evaluation results cache

## Important Conventions

**1. Field Naming**

DSPy signature output fields should end with `_json` for JSON outputs:
```python
patient_population_json: str = dspy.OutputField(desc="JSON with patient data")
```

Generated modules use `safe_json_parse()` to parse these fields reliably.

**2. Not Reported Convention**

All extractors should use `"NR"` for fields not found in papers:
```python
{"field": "NR"}  # Not Reported
```

This is critical for evaluation metrics.

**3. Source Grounding**

When possible, extraction fields should include source text:
```python
{
    "value": "extracted value",
    "source_text": "quote from paper"
}
```

**4. Task Naming**

Generated tasks use either:
- `task_<short_hash>` - Deterministic hash of form structure
- `dynamic_<uuid>_<hash>` - UUID for uniqueness + hash for versioning

**5. Follow cursor rules**

The `.cursor/rules/instructions.mdc` file specifies:
- Follow user instructions EXACTLY as written
- Do NOT add explanations, comments, or suggestions unless requested
- Do NOT refactor, rename, or optimize code unless asked
- If instructions are ambiguous, ask ONE clarification question and stop
- Output ONLY what is explicitly requested
- Never add emojis unless explicitly mentioned

## Common Workflows

**Adding a new static schema:**

1. Create task directory: `dspy_components/tasks/my_schema/`
2. Write `signatures.py` with DSPy signature classes
3. Write `modules.py` with async extractor modules
4. Define schema config in `schemas/configs.py`
5. Register schema: `register_schema(my_config)`
6. Use with: `python run.py single --schema my_schema ...`

**Generating a dynamic schema:**

1. Use Streamlit app: `streamlit run app/main.py`
2. Create project and upload form
3. AI generates code automatically (via `core/generators/workflow.py`)
4. Review generated code in `dspy_components/tasks/dynamic_*/`
5. Schema auto-registered and ready to use

**Debugging extraction issues:**

1. Check LLM history: `outputs/logs/dspy_history.csv`
2. Review field-level metrics in console output
3. Enable diagnostic mode: Set `run_diagnostic=True` in `run_async_extraction_and_evaluation()`
4. Clear caches if needed: `python run.py ... --clear-cache`
5. Check model configuration in `core/config.py`

**Modifying evaluation logic:**

1. Edit `core/evaluation.py` (semantic matching logic)
2. Adjust field classification (semantic vs exact) in evaluator initialization
3. Clear evaluation cache: `rm -rf .evaluation_cache`
4. Re-run evaluation to see changes

## DSPy Best Practices in this Codebase

**Signatures:**
- Use descriptive docstrings for signature purpose
- Provide detailed output field descriptions with examples
- Include format specifications in output field descriptions
- Use JSON outputs for structured data

**Modules:**
- Always extend `dspy.Module`
- Use `dspy.ChainOfThought` for complex reasoning tasks
- Wrap sync DSPy calls with `loop.run_in_executor()` for async
- Handle errors gracefully with fallback values
- Parse JSON outputs with `safe_json_parse()`

**Pipelines:**
- Define clear stage boundaries based on dependencies
- Use parallel execution when tasks are independent
- Use sequential execution when tasks depend on previous outputs
- Accumulate results across stages for dependent signatures

## Testing Considerations

When adding tests:
- Test semantic evaluation with known ground truth pairs
- Verify pipeline stage execution order
- Test error handling with malformed JSON
- Validate cache hit/miss behavior
- Check concurrency limits under load
- Verify schema registration and lookup

## Performance Notes

**Bottlenecks:**
- Semantic evaluation can be slow on large batches (use higher concurrency)
- DSPy compilation cache misses increase latency (use persistent cache)
- Large markdown files may hit token limits (consider chunking)

**Optimization strategies:**
- Increase `BATCH_CONCURRENCY` for more parallel papers (watch memory)
- Increase `EVALUATION_CONCURRENCY` for faster semantic matching
- Use faster models for evaluation (e.g., `gemini-2.5-flash`)
- Enable cache warming with representative examples
- Use `--max-examples` for development testing

## File Locations Reference

**Core logic:**
- Entry point: `run.py`
- Extraction: `core/extractor.py`
- Evaluation: `core/evaluation.py`
- Generation: `core/generators/workflow.py`

**Configuration:**
- Main config: `core/config.py`
- Schema configs: `schemas/configs.py`, `schemas/config.py`
- LM setup: `utils/lm_config.py`

**Web interface:**
- Main app: `app/main.py`
- Document management: `app/views/documents_tab.py`
- Form creation: `app/views/forms_tab.py`
- Extraction UI: `app/views/extraction_tab.py`
- Results viewer: `app/views/results_tab.py`

**Generated code:**
- Static tasks: `dspy_components/tasks/patient_population/`, etc.
- Dynamic tasks: `dspy_components/tasks/dynamic_*/`

**Data storage:**
- Processed PDFs: `storage/processed/extracted_pdfs/`
- Uploaded PDFs: `storage/uploads/pdfs/`
- Outputs: `outputs/logs/`, `outputs/dashboards/`
