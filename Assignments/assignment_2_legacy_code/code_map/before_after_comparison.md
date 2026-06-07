# Before / After Comparison

## Feature Comparison

| Feature | Legacy (v1) | Modernized (v2) |
|---------|------------|-----------------|
| Python version | 2.x style | 3.12+ |
| HTTP library | urllib (blocking) | httpx (async) |
| Sleep mechanism | time.sleep(300) | asyncio.sleep(300) |
| Data model | ad-hoc dict lookups | WeatherData dataclass |
| Error handling | None | timeouts, status checks, typed exceptions |
| Logging | Manual f.open/f.write | logging + JSON FileHandler |
| Configuration | Hard-coded | Constructor parameters + env vars |
| Type safety | None | Full type hints |
| Architecture | Monolithic script | Modular (4 separate files) |
| Extensibility | None | Pub-sub alert callbacks |

## Code Quality Metrics

| Metric | Legacy | Modern |
|--------|--------|--------|
| Cyclomatic complexity | 5 (one big block) | 2-3 per function |
| Number of functions | 0 | 6 |
| Number of classes | 0 | 4 |
| Testability | Impossible | High (AlertEngine is pure logic) |
| Reusability | None | Modules importable independently |

## Key Snippet: Before vs. After

**Legacy:**
```python
url = "http://api.openweathermap.org/data/2.5/weather?lat=" + str(lat) + "&lon=" + str(lon) + "&appid=" + api_key + "&units=metric"
response = urllib.urlopen(url)
data = json.loads(response.read())
```

**Modern:**
```python
url = (
    "https://api.openweathermap.org/data/2.5/weather"
    f"?lat={self.lat}&lon={self.lon}"
    f"&appid={self.api_key}&units=metric"
)
resp = await self._client.get(url, timeout=10.0)
resp.raise_for_status()
data = resp.json()
```
