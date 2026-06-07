# AI-Generated Code Map — Rainfall Monitor v2

## Architecture Overview

```
+-----------------------------------------------------------+
|                    RainfallDashboard                       |
|   (orchestrator — poll loop + event wiring)               |
+-----------------------------------------------------------+
|                                                           |
|  +---------------+   +---------------+   +---------------+ |
|  | WeatherFetcher|-->| AlertEngine   |-->| AlertLogger   | |
|  | (async HTTP)  |   | (threshold)   |   | (JSON file)   | |
|  +---------------+   +---------------+   +---------------+ |
|         |                   |                               |
|         v                   v                               |
|  +---------------+   +---------------+                     |
|  | WeatherData   |   | AlertEvent    |                     |
|  | (dataclass)   |   | (dataclass)   |                     |
|  +---------------+   +---------------+                     |
+-----------------------------------------------------------+
```

## Component Responsibilities

### WeatherFetcher
- Manages a single httpx.AsyncClient session
- fetch_current(): GETs OpenWeather API, returns typed WeatherData
- Safe for concurrent use via async context manager

### AlertEngine
- Pure logic: compares rainfall against threshold
- Publish-subscribe pattern for extensibility
- Returns AlertEvent when threshold exceeded, None otherwise

### AlertLogger
- Writes structured JSON records to alerts.log
- Separate file handler with timestamps
- Extensible to email/SMS via additional callbacks

## Data Flow

1. RainfallDashboard.run_forever() loops every poll_seconds
2. Calls WeatherFetcher.fetch_current() -> WeatherData
3. Passes data to AlertEngine.evaluate()
4. If threshold exceeded -> AlertEvent -> all subscribers notified
5. Subscribers: log to file + print to console
6. Sleeps poll_seconds, repeats

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Async context manager | Ensures HTTP connections closed on exit |
| Pub-sub for alerts | Extensible without modifying AlertEngine |
| Dataclasses over dicts | Type safety, IDE autocomplete |
| JSON log format | Machine-parseable, ELK compatible |
