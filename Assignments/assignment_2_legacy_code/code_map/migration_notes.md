# Migration Notes

## Issues Found in Legacy Code

| Severity | Issue | Line(s) |
|----------|-------|---------|
| CRITICAL | API key hard-coded | 9 |
| CRITICAL | No error handling on HTTP request | 22 |
| HIGH | Python 2 print statement | 4, 16 |
| HIGH | Blocking time.sleep freezes process | 39 |
| HIGH | No input validation on API response | 23-28 |
| MEDIUM | File handle not closed properly (no context manager) | 33-35 |
| MEDIUM | urllib.urlopen deprecated since Python 3 | 22 |
| MEDIUM | No typing — impossible to know expected types | all |
| LOW | Hard-coded polling interval | 38 |
| LOW | Non-standard log format | 34 |
| LOW | No separation of concerns | all |

## Migration Steps

1. Rewrite as async: Replace urllib + time.sleep with httpx + asyncio
2. Add types: Dataclasses for domain models, type hints on all functions
3. Extract modules: Separate fetcher, alerts, logger into own files
4. Add error handling: HTTP timeouts, connection errors, malformed JSON
5. Config via env: API key from environment, not source code
6. Structured logging: JSON log records instead of raw print()
7. Tests: Unit tests for AlertEngine (no HTTP dependency)
