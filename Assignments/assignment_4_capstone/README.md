# Assignment 4: Final Capstone Project

**Weight:** 40% | **Due:** Week 16 | **Domain:** Reservoir Optimization

## Objective

Build a complete, functional mini-application for reservoir dispatch optimization during drought. Integrates everything from the course: AI-assisted development, prompt engineering, testing, validation, and reflection.

## Deliverable Structure

```
assignment_4_capstone/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── reservoir.py          # Reservoir state model
│   │   ├── optimizer.py          # scipy.optimize formulation
│   │   ├── constraints.py        # Physical & operational constraints
│   │   └── objectives.py         # Multi-objective functions
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── io_utils.py           # Data loading/saving
│   │   └── validation.py         # Swiss Cheese validation layer
│   └── tests/
│       ├── test_reservoir.py
│       ├── test_optimizer.py
│       ├── test_constraints.py
│       └── test_validation.py
├── docs/
│   ├── AGENTS.md                 # Persistent project context
│   ├── prompt_log.md             # Complete AI interaction log
│   ├── jagged_frontier_report.md # Reflection on AI strengths/weaknesses
│   └── presentation_outline.md   # 5-minute demo script
├── outputs/
│   └── schedule.csv              # Optimal 7-day release schedule
└── README.md
```

## Problem

A reservoir must balance ecological flow (10 m3/s minimum) vs. hydropower revenue during a 7-day drought.

**Constraints:** V_min <= Storage <= V_max, Q_release >= Q_ecology, mass balance.

## How This Differs

| Aspect | Assignments 1-3 | Assignment 4 |
|--------|----------------|--------------|
| Scope | Single skill | All skills integrated |
| Deliverable | Report or module | Complete runnable app |
| Reflection | Brief | Systematic Jagged Frontier analysis |
