# eviStream

**eviStream** is a DSPy-powered medical data extraction pipeline that extracts structured patient population characteristics from medical research papers. It uses large language models with chain-of-thought reasoning to parse markdown-formatted research documents and extract detailed clinical trial information including patient demographics, selection criteria, baseline characteristics, and target conditions.

The pipeline features semantic evaluation capabilities that go beyond exact string matching, using LLM-based comparison to determine if extracted values are semantically equivalent to ground truth. This makes it robust to paraphrasing and formatting variations commonly found in medical literature.

eviStream supports both single-file and batch processing modes, provides comprehensive evaluation metrics with visual dashboards, and logs all LLM interactions for cost tracking and debugging.

## How to Run

### Single File Extraction

```bash
python run.py single --source /path/to/source.json --target /path/to/target.json
```

### Batch Extraction

```bash
python run.py batch --source /path/to/md_directory --target /path/to/target.json --max-examples 10
```

### Optional Flags

- `--clear-cache`: Clear DSPy caches before running
- `--max-examples N`: Limit batch processing to N examples

## Execution Flow

```
1. Initialize DSPy LM (utils/lm_config.py)
   ↓
2. Load markdown source + target JSON (data/loader.py)
   ↓
3. Run Extraction (src/extractor.py)
   → Use DSPy signatures (dspy_components/signatures.py)
   → Execute with modules (dspy_components/modules.py)
   → Parse outputs (utils/json_parser.py)
   ↓
4. Extract Field Schema (src/field_extractor.py)
   → Analyze field structure using ExtractFieldsFromSchema
   ↓
5. Evaluate Results (src/evaluation.py)
   → Compare extracted vs ground truth with SemanticMatcher
   → Calculate metrics (precision, recall, F1, completeness)
   ↓
6. Save Results (src/file_handler.py)
   ↓
7. Display Summary (src/helpers/print_helpers.py)
   ↓
8. Generate Dashboards (src/helpers/visualization.py) [batch only]
   ↓
9. Log LLM History (utils/logging.py)
```
