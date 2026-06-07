# Assignment 2: Legacy Code Modernization

**Weight:** 20% | **Due:** Week 8 | **Domain:** Rainfall Alert System

## Objective

Take an old, undocumented research script and modernize it using AI assistance. Deliver a Python 3.12 codebase with type hints, async patterns, and an AI-generated Code Map.

## Deliverable Structure

```
assignment_2_legacy_code/
├── legacy/
│   ├── rainfall_monitor_v1.py        # Original script (Python 2 style)
│   └── data.csv                      # Sample rainfall data
├── modernized/
│   └── src/
│       ├── __init__.py
│       ├── fetcher.py                # Async API fetcher
│       ├── alerts.py                 # Alert engine with threshold logic
│       ├── logger.py                 # Structured logging module
│       └── dashboard.py              # Streamlit dashboard
├── code_map/
│   ├── ai_generated_map.md           # AI-produced architecture explanation
│   ├── migration_notes.md            # What changed and why
│   └── before_after_comparison.md    # Side-by-side improvement log
└── prompt_log.md                     # Record of AI interactions
```

## The Legacy Script

The file `legacy/rainfall_monitor_v1.py` uses Python 2 style, has no functions, hard-codes values, uses blocking calls, no error handling, no type hints, and no tests.

## Your Task

1. Analyze the legacy code using AI. Identify all issues.
2. Plan a migration strategy using AI.
3. Modernize each component: add types, async, proper error handling.
4. Generate an AI-created Code Map explaining the architecture.
5. Document AI interactions in `prompt_log.md`.

## Grading Criteria

| Criterion | Weight | What We Look For |
|-----------|--------|------------------|
| Code Modernization | 35% | Type hints, async/await, error handling, structured logging |
| AI Collaboration | 25% | Quality of prompts used; how you corrected AI suggestions |
| Code Map Quality | 25% | AI-generated architecture explanation must be accurate |
| Migration Documentation | 15% | Clear before/after comparison with rationale |
