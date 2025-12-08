# LangGraph Workflow Architecture

## Overview

The DSPy Signature Generator has been redesigned with a **robust LangGraph workflow** featuring:
- ✅ **StateGraph** for workflow orchestration
- ✅ **LangChain Agent** with tools
- ✅ **Human-in-the-Loop** capability
- ✅ **State Persistence** with MemorySaver
- ✅ **Conditional Routing** based on validation results

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    LANGGRAPH WORKFLOW                        │
└─────────────────────────────────────────────────────────────┘

                         ┌──────────┐
                         │  START   │
                         └────┬─────┘
                              │
                              ▼
                      ┌───────────────┐
                      │   ANALYZE     │
                      │  (Blueprint)  │
                      └───────┬───────┘
                              │
                              ▼
                      ┌───────────────┐
                      │   GENERATE    │
                      │ (Agent+Tools) │
                      └───────┬───────┘
                              │
                    ┌─────────┴─────────┐
                    │    Success?       │
                    └─────────┬─────────┘
                         Yes  │  No
                    ┌─────────┴─────────┐
                    ▼                   ▼
            ┌───────────────┐    ┌──────────┐
            │   VALIDATE    │    │ FINALIZE │
            │  (Check Code) │    │  (Fail)  │
            └───────┬───────┘    └────┬─────┘
                    │                 │
          ┌─────────┴─────────┐       │
          │   Valid?          │       │
          └─────────┬─────────┘       │
               Yes  │  No             │
          ┌─────────┴─────────┐       │
          ▼                   ▼       │
  ┌──────────────┐    ┌──────────┐   │
  │ HUMAN_REVIEW │    │  REFINE  │   │
  │ (Optional)   │    │ (Retry)  │   │
  └──────┬───────┘    └────┬─────┘   │
         │                 │          │
         │                 └──────────┤
         │                            │
         ▼                            │
  ┌──────────────┐                   │
  │  FINALIZE    │◄──────────────────┘
  │  (Success)   │
  └──────┬───────┘
         │
         ▼
    ┌────────┐
    │  END   │
    └────────┘
```

---

## Components

### 1. State Definition

```python
class SignatureGenerationState(TypedDict):
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
    status: str
```

### 2. Workflow Nodes

| Node | Purpose | Input | Output |
|------|---------|-------|--------|
| **analyze** | Create blueprint from questionnaire spec | questionnaire_spec | blueprint |
| **generate** | Generate code using LLM + tools | blueprint, validation_feedback | code |
| **validate** | Validate generated code quality | code | is_valid, errors, warnings |
| **human_review** | Optional human checkpoint (interruptible) | code | human_feedback |
| **refine** | Prepare for retry with feedback | validation_feedback, human_feedback | Updated state |
| **finalize** | Package final result | All state | result |

### 3. Tools (LangChain)

```python
@tool
def analyze_field_tool(field_spec: str) -> str:
    """Analyze field specification for extraction patterns"""
    
@tool
def generate_signature_tool(blueprint_json: str, validation_feedback: str) -> str:
    """Generate DSPy Signature class from blueprint"""
    
@tool
def generate_module_tool(signature_class_name: str, ...) -> str:
    """Generate Async DSPy Module wrapper"""
```

### 4. Agent with Structured Output

```python
# Main agent with tools
self.agent = create_agent(
    self.model,  # LLM (Gemini, GPT, etc.)
    tools=self.tools  # Tool list
)

# Specialized agents with structured output (LangChain ToolStrategy)
self.field_analysis_agent = create_agent(
    self.model,
    tools=[],
    response_format=ToolStrategy(
        schema=FieldAnalysisSchema,  # Pydantic model
        handle_errors=True
    )
)

self.signature_generation_agent = create_agent(
    self.model,
    tools=[],
    response_format=ToolStrategy(
        schema=SignatureCodeSchema,  # Pydantic model
        handle_errors=True
    )
)
```

**Structured Output Benefits:**
- ✅ **Type-safe responses**: Pydantic models ensure data validation
- ✅ **Automatic retry**: Handles validation errors with intelligent feedback
- ✅ **Schema enforcement**: Model must return data in exact format
- ✅ **Error recovery**: Built-in error handling with custom messages

Reference: [LangChain Structured Output Documentation](https://docs.langchain.com/oss/python/langchain/structured-output)

### 5. Conditional Routing

```python
def _should_refine_or_finish(state) -> str:
    """Decide whether to refine or finish after validation"""
    if state['is_valid']:
        if enable_human_review and not state.get('human_feedback'):
            return 'human_review'
        return 'finalize'
    elif state['attempt'] >= state['max_attempts']:
        return 'finalize'
    else:
        return 'refine'
```

---

## Features

### ✅ State Persistence

```python
self.checkpointer = MemorySaver()

workflow.compile(
    checkpointer=self.checkpointer,
    interrupt_before=["human_review"]
)
```

- Workflow state is persisted across interruptions
- Can resume from any checkpoint
- Thread-based isolation (multiple workflows in parallel)

### ✅ Human-in-the-Loop

```python
# Enable human review
generator = DSPySignatureGenerator(enable_human_review=True)

# Workflow pauses at human_review node
result = generator.generate_signature(spec, thread_id="task1")

if result.get('paused'):
    # Review code, provide feedback
    final = generator.continue_after_human_review(
        human_feedback="Add more examples",
        thread_id="task1"
    )
```

### ✅ Validation Loop

- Automatic retry up to `max_attempts`
- Validation feedback fed back to generator
- Distinguishes critical errors from warnings

### ✅ Error Recovery

- Comprehensive error handling at each node
- Fallback mechanisms
- Clear error reporting

---

## Usage Examples

### Basic Usage (No Human Review)

```python
from signature_generator import DSPySignatureGenerator

generator = DSPySignatureGenerator(enable_human_review=False)

questionnaire = {
    "class_name": "ExtractIndexTestType",
    "form_question": "Select the index test used",
    "output_structure": {
        "cytology": {"selected": "bool", "comment": "str"},
        "vital_staining": {"selected": "bool", "comment": "str"}
    },
    "output_field_name": "index_test_type_json"
}

result = generator.generate_signature(questionnaire, max_attempts=3)

if result['is_valid']:
    print(result['code'])
```

### With Human-in-the-Loop

```python
generator = DSPySignatureGenerator(enable_human_review=True)

result = generator.generate_signature(questionnaire, thread_id="review1")

if result.get('paused'):
    print("Code for review:")
    print(result['code'])
    
    # Get human feedback (from UI, CLI, etc.)
    feedback = input("Your feedback: ")
    
    # Continue workflow
    final = generator.continue_after_human_review(feedback, thread_id="review1")
    print(final['code'])
```

### Parallel Workflows

```python
import asyncio

async def generate_multiple():
    tasks = []
    for i, spec in enumerate(questionnaires):
        task = generator.generate_signature(spec, thread_id=f"task_{i}")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

---

## Benefits Over Previous Implementation

| Aspect | Before | After |
|--------|--------|-------|
| **Architecture** | Simple for-loop | LangGraph StateGraph |
| **State Management** | Local variables | Persistent TypedDict state |
| **Error Handling** | Try-except in loop | Node-level + workflow-level |
| **Human Review** | Not supported | Built-in interrupt capability |
| **Observability** | Print statements | Event streaming + state inspection |
| **Extensibility** | Hard to modify | Add nodes/edges easily |
| **Agent Support** | No agent | LangChain agent with tools |
| **Parallelization** | Sequential only | Thread-based parallel workflows |

---

## Testing

Run the test suite:

```bash
python test_workflow.py
```

This tests:
1. Basic workflow execution
2. Human-in-the-loop functionality
3. State persistence
4. Error handling

---

## Future Enhancements

- [ ] Add more sophisticated agent reasoning
- [ ] Implement workflow visualization (Mermaid diagrams)
- [ ] Add metrics and monitoring
- [ ] Support for streaming responses
- [ ] Integration with UI for human review
- [ ] Multi-agent collaboration for complex tasks
- [ ] Workflow templates for common patterns

---

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)
- [Human-in-the-Loop Patterns](https://langchain-ai.github.io/langgraph/how-tos/human-in-the-loop/)

