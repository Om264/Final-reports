# The Reasoning Log — Final Report

## Summary

This assignment compared naive prompting vs. Chain-of-Thought prompting for implementing the SCS-CN rainfall-runoff model. The CoT approach significantly improved code quality but still required human verification for physical correctness.

## Key Findings

### 1. Naive Prompt -> Flawed Code
The unstructured prompt produced code with no input validation, ambiguous variable names, and NaN for P < Ia cases.

### 2. CoT Prompt -> Correct Code (Mostly)
The structured prompt produced complete input validation, clear Ia definition, and all boundary conditions handled. AI still missed floating-point comparison issues.

### 3. AI Self-Verification -> Partial Success
When asked to review its own code, the AI correctly identified the missing edge case for P exactly equal to Ia but failed to notice its original code used regular comparison which fails for P = Ia + 1e-16.

### 4. Human Verification — The Swiss Cheese Layer
Human domain expertise caught the floating-point precision gap, need for monotonicity testing, and physical implausibility of CN > 100.

## Errors Found (Before vs. After CoT)

| Error Type | Naive Prompt | CoT Prompt | Human Catch |
|-----------|-------------|------------|-------------|
| Missing Ia definition | NO | YES | - |
| P < Ia not handled | NO | YES | - |
| No input validation | NO | YES | - |
| No type hints | NO | YES | - |
| Float comparison unsafe | NO | NO | YES |
| No monotonicity test | NO | NO | YES |
| Missing docstring | NO | YES | - |

## Reflection

The CoT prompt dramatically improved output quality, but the AI consistently misses numerical precision issues. The "Jagged Frontier" for this task is clear: AI excels at formula translation and boilerplate but fails at numerical stability and physical edge-case reasoning.
