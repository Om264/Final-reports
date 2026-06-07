# Prompt Log — Assignment 2: Legacy Code Modernization

## Interaction 1: Code Review
**Prompt:** Review this legacy Python script. List every issue, categorized by severity.

**AI found:** 11 issues (3 critical, 3 high, 3 medium, 2 low)
**Human correction:** AI missed that urllib.urlopen doesnt exist in Python 3. Added.

## Interaction 2: Refactoring Plan
**Prompt:** Generate step-by-step migration plan for async/await, type hints, modular.

**AI output:** 7-step plan, suggested aiohttp instead of httpx.
**Human correction:** Changed to httpx — simpler API, better docs.

## Interaction 3: Async Implementation
**Prompt:** Rewrite data fetching using async/await with httpx.

**AI output:** Correct but typo in __aenter__.
**Human correction:** Fixed typo.

## Interaction 4: Alert Engine
**Prompt:** Design alert system using observer pattern with multiple subscribers.

**AI output:** Clean callback list implementation.
**Human correction:** Added validation to prevent negative threshold.

## Interaction 5: Code Map
**Prompt:** Generate architecture diagram with ASCII art and component responsibilities.

**AI output:** Accurate but labeled WeatherFetcher as synchronous.
**Human correction:** Corrected to note async behavior.
