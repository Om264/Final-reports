# Prompt Log: AI-Assisted Development

## Experiment: Short-Term Rainfall Forecasting & Alert System

---

### Prompt 1: API Integration

**Original Prompt:**
> I am a water resources student building a rainfall monitoring system. Please write Python code to fetch current weather data for Beijing using the OpenWeatherMap API. The code should: 1. Use the requests library to make the API call 2. Extract rainfall intensity from the response 3. Handle API errors gracefully 4. Include comments explaining each step API endpoint: https://api.openweathermap.org/data/2.5/weather

**Generated Solution:**
The AI generated a WeatherAPI class with requests-based API calls, JSON response parsing, rainfall extraction from `rain.1h` and `rain.3h` fields, and basic try-except error handling.

**Issues Found:**
- No retry mechanism for transient failures
- No timeout handling on requests
- No API key validation
- Rainfall extraction did not handle missing rain key gracefully
- No offline fallback mode

**Corrections Made:**
- Added retry mechanism with exponential backoff (3 attempts)
- Added configurable timeout (10s)
- Added API key validation method
- Added safe_float utility for missing keys
- Added offline synthetic data generator

---

### Prompt 2: Alert Logic

**Original Prompt:**
> Implement threshold-based alerting for rainfall monitoring. Use three levels: GREEN (< 10 mm/h), YELLOW (10-20 mm/h), RED (>= 20 mm/h). When RED alert triggers, display warning message, log event to file with timestamp, and show alert in dashboard.

**Generated Solution:**
The AI generated conditional logic for alert levels and a simple file append for logging.

**Issues Found:**
- No persistent alert state tracking
- Log file path was hardcoded
- No alert history loading capability
- No summary statistics

**Corrections Made:**
- Created AlertSystem class with stateful tracking of current alerts per city
- Used configurable log file path from config.py
- Added load_alert_history() method
- Added alert_summary() for dashboard statistics
- Added escalation detection (e.g., GREEN -> RED)

---

### Prompt 3: Dashboard Development

**Original Prompt:**
> Build a Streamlit dashboard to display rainfall data and alerts. Requirements: Title, current rainfall display (large metric), alert status indicator (color-coded), historical data chart, auto-refresh every 5 minutes. Use professional layout with st.metric() and st.dataframe().

**Generated Solution:**
The AI generated a basic Streamlit app with a title, metric display, and a simple line chart.

**Issues Found:**
- Only single-city support
- No sidebar for configuration
- No multi-tab layout
- Charts lacked interactivity (used st.line_chart instead of plotly)
- No export functionality
- Auto-refresh used time.sleep blocking main thread

**Corrections Made:**
- Complete 10-section dashboard with tabs
- Sidebar with API key input, city selection, refresh/export controls
- Used plotly for interactive charts throughout
- Added KPI card components with custom CSS
- Added data export (CSV, Excel) via st.download_button
- Used st.rerun() for auto-refresh instead of blocking sleep
- Added 24-hour forecast section with dual-axis plotly chart

---

### Prompt 4: Machine Learning Module

**Original Prompt:**
> Create a rainfall prediction module using scikit-learn Linear Regression. Use temperature, humidity, pressure, and previous rainfall as features. Predict next 1-hour and 3-hour rainfall. Include model saving/loading with joblib.

**Generated Solution:**
The AI generated a basic regression model with hardcoded feature columns and simple train/predict methods.

**Issues Found:**
- No feature engineering (lag features missing)
- No data validation before training
- Model path was hardcoded
- No confidence scores or uncertainty estimation
- Fallback prediction was not implemented for untrained models

**Corrections Made:**
- Added lag features (1h, 2h, 3h) for time-series context
- Added data validation and cleaning
- Configurable model path from config.py
- Added R²-based confidence scoring
- Added prediction_with_uncertainty() with 95% CI
- Added fallback prediction when model is untrained
- Added automatic retraining when sufficient new data exists

---

### Prompt 5: Anomaly Detection

**Original Prompt:**
> Implement anomaly detection for rainfall data using Z-score method. Flag readings where |z| > 2 as anomalies. Return anomaly flag, score, and description.

**Generated Solution:**
The AI generated a simple Z-score calculation against hardcoded mean/std values.

**Issues Found:**
- Statistics were static, not updated from historical data
- No batch detection for dataframes
- Severity levels not implemented
- Descriptions were generic

**Corrections Made:**
- Added dynamic statistics update from CSV history
- Added batch_detect_dataframe() for analyzing entire history
- Added three severity levels (normal, high, extreme)
- Added detailed contextual descriptions for different anomaly types
- Added summary() method for dashboard display

---

### Prompt 6: Testing and Debugging

**Original Prompt:**
> Write comprehensive tests for the rainfall monitoring system. Test API integration, alert logic, prediction module, and anomaly detection. Use pytest with target of 80%+ code coverage.

**Generated Solution:**
The AI generated basic unit tests with limited edge case coverage.

**Issues Found:**
- No mock tests for API error handling
- Alert tests missed boundary conditions (exactly 10, 20 mm/h)
- Prediction tests did not test model save/load cycle
- Anomaly tests had no coverage for edge cases (zero std, custom thresholds)

**Corrections Made:**
- Added mocked HTTP error tests (401, 404) for WeatherAPI
- Added boundary value tests for alert thresholds (10.0, 20.0 exactly)
- Added model serialization round-trip test
- Added edge case tests (negative rainfall, zero std, empty data)
- Added batch detection tests for anomaly detector
- Added forecast and offline mode validation tests

---

### Summary of AI Interactions

| Module | AI Generation Quality | Issues Identified | Corrections Required |
|---|---|---|---|
| API Integration | Good (basic structure) | Missing retries, timeout, fallback | Added retry, timeout, offline mode |
| Alert Logic | Fair (simple if-else) | No persistence, state tracking | Added AlertSystem class with history |
| Dashboard | Fair (basic layout) | Single city, no plots, no export | Full 10-section dashboard with plotly |
| ML Predictor | Fair (basic model) | No lag features, no confidence | Added features, uncertainty, fallback |
| Anomaly Detection | Fair (basic z-score) | Static stats, no batch | Dynamic stats, batch detection |
| Testing | Fair (basic tests) | Missing mocks, edge cases | Mock tests, boundary cases, coverage |

**Overall Assessment:** AI-generated code provided solid foundations (70% usable) but required significant enhancement (30% corrections) for production quality. Key areas needing human oversight: error handling edge cases, data validation, and architectural decisions.
