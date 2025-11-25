# eviStream

**eviStream** is a DSPy-powered medical data extraction pipeline that extracts structured data from medical research papers. It now supports multiple *schemas* (questionnaires) so you can run different systematic-review forms—patient population, ROB, index test, etc.—without touching core code. Each schema declares its own DSPy pipeline, required fields, and evaluation outputs.

The pipeline features semantic evaluation capabilities that go beyond exact string matching, using LLM-based comparison to determine if extracted values are semantically equivalent to ground truth. This makes it robust to paraphrasing and formatting variations commonly found in medical literature.

eviStream supports both single-file and batch processing modes, provides comprehensive evaluation metrics with visual dashboards, and logs all LLM interactions for cost tracking and debugging.

## How to Run

### Single File Extraction

```bash
python run.py single --source /path/to/source.json --target /path/to/target.json --schema patient_population
```

### Batch Extraction

```bash
python run.py batch --source /path/to/md_directory --target /path/to/target.json --schema patient_population --max-examples 10
```

### Optional Flags

- `--schema NAME`: Select which schema to run (see `eviStream/schemas/`)
- `--clear-cache`: Clear DSPy caches before running
- `--max-examples N`: Limit batch processing to N examples

## Execution Flow

```
1. Initialize DSPy LM (utils/lm_config.py)
   ↓
2. Load markdown source + target JSON (data/loader.py)
   ↓
3. Run Extraction (src/extractor.py)
   → Use DSPy signatures (dspy_components/tasks/<task>/signatures.py)
   → Execute with modules (dspy_components/tasks/<task>/modules.py)
   → Parse outputs (utils/json_parser.py)
   ↓
4. Evaluate Results (src/evaluation.py)
   → Compare extracted vs ground truth with SemanticMatcher
   → Calculate metrics (precision, recall, F1, completeness)
   ↓
5. Save Results (src/file_handler.py)
   ↓
6. Display Summary (src/helpers/print_helpers.py)
   ↓
7. Generate Dashboards (src/helpers/visualization.py) [batch only]
   ↓
8. Log LLM History (utils/logging.py)

Each schema lives under `eviStream/schemas/` and registers itself in `schemas/registry.py`. To add a new systematic-review form, create a schema module that lists its required fields, declares the DSPy pipeline factory, and assigns unique CSV/JSON filenames, then point the CLI at it with `--schema <name>`.
```
