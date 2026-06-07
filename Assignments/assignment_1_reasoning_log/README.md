# Assignment 1: The Reasoning Log

**Weight:** 20% | **Due:** Week 4 | **Domain:** SCS-CN Hydrological Modeling

## Objective

Use **Chain-of-Thought (CoT)** prompting to solve the SCS-CN rainfall-runoff problem, then document the full reasoning trace and human verification steps.

## Deliverable Structure

```
assignment_1_reasoning_log/
├── coT_prompts/
│   ├── prompt_01_initial.md          # First naive prompt
│   ├── prompt_02_refined.md          # CoT-structured prompt
│   └── prompt_03_verification.md     # Prompt asking AI to verify its own work
├── ai_responses/
│   ├── response_01_raw.md            # Raw AI output (with errors)
│   ├── response_02_corrected.md      # Corrected output after CoT
│   └── response_03_verified.md       # AI self-verified output
├── verification/
│   ├── edge_cases.md                 # Documented boundary conditions checked
│   ├── physical_plausibility.md      # Hydrological sanity checks
│   └── final_report.md               # Synthesis: what was learned
└── README.md
```

## The SCS-CN Problem

The Soil Conservation Service Curve Number method estimates surface runoff:

```
Q = (P - Ia)^2 / (P - Ia + S)

where:
  S  = (25400 / CN) - 254
  Ia = 0.2 * S
  P  = precipitation (mm)
  CN = curve number (30-100)
  Q  = runoff (mm)
```

### Physical Constraints You Must Verify

| Rule | Why It Matters |
|------|----------------|
| Q = 0 when P < Ia | No runoff before abstraction satisfied |
| 0 <= Q <= P | Runoff cannot exceed rainfall |
| CN in [30, 100] | Physical range of curve numbers |
| Q increases with CN | Higher CN means more runoff |
| Q increases with P | More rain means more runoff |

## Your Task

**Step 1 — Initial Prompt (Naive)**
Ask an AI to write the SCS-CN function without any structure. Save the prompt and response. Identify at least 2 errors.

**Step 2 — CoT Prompt (Structured)**
Write a Chain-of-Thought prompt that:
- Assigns a role ("Senior Hydrologist")
- States the formula explicitly
- Lists edge cases to handle
- Requests step-by-step reasoning before code

Save the prompt, AI's reasoning trace, and final code.

**Step 3 — Verification Prompt**
Ask the AI to review its own output for physical correctness. Did it catch the same errors you found? Document discrepancies.

**Step 4 — Final Report**
Write a reflection comparing:
- Naive vs. CoT output quality
- AI's self-verification vs. human verification
- What types of errors the AI consistently misses

## Grading Criteria

| Criterion | Weight | What We Look For |
|-----------|--------|------------------|
| CoT Prompt Quality | 30% | Clear role, context, constraints, step-by-step instruction |
| Error Identification | 30% | Correctly identified AI mistakes in naive output |
| Verification Depth | 25% | Physical sanity checks beyond what AI suggested |
| Reflection Quality | 15% | Insightful comparison of human vs. AI verification |
