import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.alert_system import AlertSystem
from app.anomaly_detector import AnomalyDetector
from app.config import CITY_LIST, HISTORY_FILE, REFRESH_INTERVAL
from app.data_storage import DataStorage
from app.notification import NotificationService
from app.predictor import RainfallPredictor
from app.utils import alert_color, city_coordinates, current_timestamp
from app.weather_api import WeatherAPI

logger = logging.getLogger(__name__)


def display_kpi(label: str, value: str, delta: str = "", color: str = "#333") -> None:
    st.markdown(
        f"""
        <div style="
            background: {color}15;
            border: 1px solid {color}40;
            border-radius: 10px;
            padding: 16px;
            margin: 4px 0;
            text-align: center;
        ">
            <div style="font-size: 0.85rem; color: #666; margin-bottom: 4px;">{label}</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {color};">{value}</div>
            {f'<div style="font-size: 0.85rem; color: #888;">{delta}</div>' if delta else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_alert_banner(level: str, city: str, rainfall: float) -> None:
    colors = {"GREEN": "#00cc00", "YELLOW": "#ffcc00", "RED": "#ff3333"}
    bg = colors.get(level, "#999")
    st.markdown(
        f"""
        <div style="
            background: {bg}22;
            border-left: 6px solid {bg};
            border-radius: 6px;
            padding: 12px 16px;
            margin: 8px 0;
        ">
            <strong style="color: {bg};">{level}</strong> Alert for
            <strong>{city}</strong> — Rainfall: {rainfall:.2f} mm/h
        </div>
        """,
        unsafe_allow_html=True,
    )


def _page_setup() -> None:
    st.set_page_config(
        page_title="Rainfall Monitor & Forecasting System",
        page_icon="🌧",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def _sidebar(wapi: WeatherAPI) -> Dict[str, Any]:
    with st.sidebar:
        st.markdown("## ⚙️ Control Panel")

        api_key_input: str = st.text_input(
            "OpenWeatherMap API Key",
            type="password",
            value=wapi.api_key if wapi.api_key else "",
            help="Enter your free API key from openweathermap.org",
        )
        if api_key_input and api_key_input != wapi.api_key:
            wapi.api_key = api_key_input
            wapi.offline_mode = False
            st.success("API key updated!")

        st.divider()
        st.markdown("### 📍 City Selection")
        selected_cities: List[str] = st.multiselect(
            "Select cities to monitor",
            options=["All"] + CITY_LIST,
            default=["All"],
        )

        if "All" in selected_cities or not selected_cities:
            selected_cities = CITY_LIST

        st.divider()
        st.markdown("### 🔄 Refresh")

        col1, col2 = st.columns(2)
        with col1:
            refresh_now: bool = st.button("🔄 Refresh Now", use_container_width=True)
        with col2:
            auto_refresh: bool = st.toggle("Auto-refresh (5 min)", value=True)

        st.divider()
        st.markdown("### 📊 Export")
        data_store = DataStorage()
        csv_data: bytes = data_store.export_to_csv()
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"rainfall_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

        excel_data: Optional[bytes] = data_store.export_to_excel()
        if excel_data:
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name=f"rainfall_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        st.divider()
        st.markdown("### ℹ️ Status")
        st.caption(f"Last update: {current_timestamp()}")
        st.caption(f"Refresh interval: {REFRESH_INTERVAL}s")

        mode: str = "Offline" if wapi.offline_mode else "Live"
        st.caption(f"Mode: {mode}")

    return {
        "selected_cities": selected_cities,
        "refresh_now": refresh_now,
        "auto_refresh": auto_refresh,
    }


def _current_weather_section(
    weather_data: Dict[str, Any],
    alert_level: str,
    alert_status: str,
) -> None:
    st.markdown("## 🌤 Current Weather")
    if weather_data.get("error"):
        st.error(f"⚠ {weather_data['error']}")
        return

    cols = st.columns([2, 1, 1, 1, 1])
    with cols[0]:
        display_kpi(
            "Rainfall Intensity",
            f"{weather_data.get('rainfall', 0):.2f} mm/h",
            color=alert_color(alert_level),
        )
    with cols[1]:
        display_kpi(
            "Temperature",
            f"{weather_data.get('temperature', 0):.1f} °C",
            color="#ff6b35",
        )
    with cols[2]:
        display_kpi(
            "Humidity",
            f"{weather_data.get('humidity', 0):.1f} %",
            color="#0077b6",
        )
    with cols[3]:
        display_kpi(
            "Pressure",
            f"{weather_data.get('pressure', 0):.0f} hPa",
            color="#6c757d",
        )
    with cols[4]:
        display_kpi(
            "Wind Speed",
            f"{weather_data.get('wind_speed', 0):.1f} m/s",
            color="#20c997",
        )

    st.markdown(f"**Description:** {weather_data.get('description', 'N/A').capitalize()} | **City:** {weather_data.get('city', 'N/A')}")


def _alert_center_section(
    alert_system: AlertSystem,
    weather_data: Dict[str, Any],
    alert_level: str,
    alert_status: str,
) -> None:
    st.markdown("## 🚨 Alert Center")
    col1, col2, col3 = st.columns(3)

    summary: Dict[str, int] = alert_system.alert_summary()
    with col1:
        display_kpi("🟢 Normal", str(summary.get("GREEN", 0)), color="#00cc00")
    with col2:
        display_kpi("🟡 Warning", str(summary.get("YELLOW", 0)), color="#ffcc00")
    with col3:
        display_kpi("🔴 Danger", str(summary.get("RED", 0)), color="#ff3333")

    if alert_level == "RED":
        display_alert_banner(alert_level, weather_data.get("city", ""), weather_data.get("rainfall", 0))
        st.warning(f"⚠ **RED ALERT**: {weather_data.get('city', '')} — {weather_data.get('rainfall', 0):.2f} mm/h — Take immediate precautions!")
    elif alert_level == "YELLOW":
        st.info(f"⚠ **Warning**: {weather_data.get('city', '')} — {weather_data.get('rainfall', 0):.2f} mm/h — Monitor conditions.")
    else:
        st.success(f"✅ **Normal**: {weather_data.get('city', '')} — {weather_data.get('rainfall', 0):.2f} mm/h — Conditions are normal.")

    st.divider()
    st.markdown("### 📋 Alert History")
    alerts: List[Dict[str, Any]] = alert_system.load_alert_history(max_lines=20)
    if alerts:
        alert_df: pd.DataFrame = pd.DataFrame(alerts)
        st.dataframe(alert_df, use_container_width=True, hide_index=True)
    else:
        st.caption("No alerts recorded yet.")


def _multi_city_section(
    wapi: WeatherAPI,
    cities: List[str],
    alert_system: AlertSystem,
) -> None:
    st.markdown("## 🏙 Multi-City Monitoring Center")

    all_data: Dict[str, Dict[str, Any]] = wapi.fetch_all_cities(cities)
    rows: List[Dict[str, Any]] = []
    for city, data in all_data.items():
        rainfall: float = data.get("rainfall", 0)
        level, _ = alert_system.evaluate(rainfall, city)
        rows.append({
            "City": city,
            "Rainfall (mm/h)": rainfall,
            "Temperature (°C)": data.get("temperature", 0),
            "Humidity (%)": data.get("humidity", 0),
            "Pressure (hPa)": data.get("pressure", 0),
            "Alert": level,
        })

    if rows:
        df: pd.DataFrame = pd.DataFrame(rows)
        df_sorted: pd.DataFrame = df.sort_values("Rainfall (mm/h)", ascending=False)

        st.markdown("### Rainfall Ranking (Highest First)")
        st.dataframe(
            df_sorted.style.map(
                lambda v: f"background-color: {alert_color(v).lower()}30; color: {alert_color(v)}"
                if v in ("GREEN", "YELLOW", "RED")
                else "",
                subset=["Alert"],
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.divider()
        st.markdown("### Comparison Charts")

        col1, col2 = st.columns(2)
        with col1:
            fig_bar: go.Figure = px.bar(
                df_sorted,
                x="City",
                y="Rainfall (mm/h)",
                color="Alert",
                color_discrete_map={
                    "GREEN": "#00cc00",
                    "YELLOW": "#ffcc00",
                    "RED": "#ff3333",
                },
                title="Rainfall Comparison Across Cities",
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            fig_temp: go.Figure = px.bar(
                df_sorted,
                x="City",
                y="Temperature (°C)",
                color="Temperature (°C)",
                color_continuous_scale="thermal",
                title="Temperature Comparison Across Cities",
            )
            st.plotly_chart(fig_temp, use_container_width=True)
    else:
        st.warning("No data available for the selected cities.")


def _historical_trends_section(data_store: DataStorage) -> None:
    st.markdown("## 📈 Historical Trends")

    df: pd.DataFrame = data_store.load_history(max_records=500)
    if df.empty:
        st.caption("No historical data yet. Data will appear as readings are collected.")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp")

    available_cities: List[str] = df["city"].unique().tolist() if "city" in df.columns else []
    selected_city: str = st.selectbox(
        "Select city for trend view",
        options=["All"] + available_cities,
        index=0,
    )
    if selected_city != "All" and selected_city in df["city"].values:
        df = df[df["city"] == selected_city]

    window: int = st.slider("Moving average window", min_value=1, max_value=20, value=5)

    col1, col2 = st.columns(2)
    with col1:
        fig_line: go.Figure = px.line(
            df,
            x="timestamp",
            y="rainfall",
            color="city" if "city" in df.columns and len(df["city"].unique()) > 1 else None,
            title="Rainfall Over Time",
            labels={"timestamp": "Time", "rainfall": "Rainfall (mm/h)"},
        )
        if len(df) >= window:
            df_sorted: pd.DataFrame = df.sort_values("timestamp")
            ma: pd.Series = df_sorted["rainfall"].rolling(window=window, min_periods=1).mean()
            fig_line.add_trace(
                go.Scatter(
                    x=df_sorted["timestamp"],
                    y=ma,
                    mode="lines",
                    name=f"MA ({window})",
                    line=dict(dash="dash", color="orange"),
                )
            )
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        fig_temp_line: go.Figure = px.line(
            df,
            x="timestamp",
            y="temperature",
            color="city" if "city" in df.columns and len(df["city"].unique()) > 1 else None,
            title="Temperature Over Time",
            labels={"timestamp": "Time", "temperature": "Temperature (°C)"},
        )
        st.plotly_chart(fig_temp_line, use_container_width=True)

    with st.expander("📋 Raw Historical Data", expanded=False):
        st.dataframe(df.tail(100), use_container_width=True, hide_index=True)
        st.caption(f"Total records: {len(df)}")


def _ml_forecast_section(
    predictor: RainfallPredictor,
    weather_data: Dict[str, Any],
) -> None:
    st.markdown("## 🤖 Machine Learning Forecast")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Rainfall Prediction")
        features: Dict[str, float] = {
            "temperature": weather_data.get("temperature", 20.0),
            "humidity": weather_data.get("humidity", 60.0),
            "pressure": weather_data.get("pressure", 1013.0),
            "rainfall": weather_data.get("rainfall", 0.0),
            "rainfall_lag1": weather_data.get("rainfall", 0.0),
            "rainfall_lag2": weather_data.get("rainfall", 0.0),
            "rainfall_lag3": weather_data.get("rainfall", 0.0),
        }
        prediction: Dict[str, Any] = predictor.predict_with_uncertainty(features)

        met_cols = st.columns(3)
        with met_cols[0]:
            display_kpi(
                "Next 1h",
                f"{prediction.get('prediction_1h', 0):.2f} mm/h",
                delta=f"Trend: {prediction.get('trend', 'stable').capitalize()}",
                color="#0077b6",
            )
        with met_cols[1]:
            display_kpi(
                "Next 3h",
                f"{prediction.get('prediction_3h', 0):.2f} mm/h",
                color="#ff6b35",
            )
        with met_cols[2]:
            conf: float = prediction.get("confidence", 0)
            conf_color: str = "#00cc00" if conf > 0.7 else "#ffcc00" if conf > 0.4 else "#ff3333"
            display_kpi(
                "Confidence",
                f"{conf:.1%}",
                delta=f"Source: {prediction.get('source', 'N/A')}",
                color=conf_color,
            )

        st.caption("Predictions use Linear Regression with temperature, humidity, pressure, and lagged rainfall features.")

    with col2:
        st.markdown("### Model Info")
        model_info: Dict[str, Any] = predictor.get_model_info()
        st.metric("Model Status", "Trained" if model_info["is_trained"] else "Not Trained")
        if model_info["metrics"]:
            st.metric("R² Score", f"{model_info['metrics'].get('r2_score', 0):.3f}")
            st.metric("MAE", f"{model_info['metrics'].get('mae', 0):.3f} mm/h")
            st.metric("Samples", str(model_info["metrics"].get("samples", 0)))
        if st.button("🔄 Retrain Model", use_container_width=True):
            with st.spinner("Training model..."):
                metrics = predictor.train_model(force=True)
                if metrics:
                    st.success(f"Model retrained! R² = {metrics.get('r2_score', 0):.3f}")
                else:
                    st.warning("Insufficient data for retraining. Collect more readings.")


def _data_analytics_section(data_store: DataStorage) -> None:
    st.markdown("## 📊 Data Analytics")

    df: pd.DataFrame = data_store.load_history(max_records=1000)
    if df.empty:
        st.caption("Collect data to see analytics.")
        return

    rainfall: pd.Series = pd.to_numeric(df["rainfall"], errors="coerce").dropna()
    if rainfall.empty:
        st.caption("No rainfall data available.")
        return

    stats: Dict[str, float] = {
        "Mean": float(rainfall.mean()),
        "Median": float(rainfall.median()),
        "Max": float(rainfall.max()),
        "Min": float(rainfall.min()),
        "Std Dev": float(rainfall.std()),
        "Latest": float(rainfall.iloc[-1]),
    }

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    metrics_list = [
        ("Mean", stats["Mean"], "#0077b6"),
        ("Median", stats["Median"], "#6c757d"),
        ("Max", stats["Max"], "#ff3333"),
        ("Min", stats["Min"], "#00cc00"),
        ("Std Dev", stats["Std Dev"], "#ffcc00"),
        ("Latest", stats["Latest"], "#ff6b35"),
    ]
    for i, (label, value, color) in enumerate(metrics_list):
        with [col1, col2, col3, col4, col5, col6][i]:
            display_kpi(label, f"{value:.2f}", color=color)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        fig_hist: go.Figure = px.histogram(
            df,
            x="rainfall",
            nbins=30,
            title="Rainfall Distribution",
            labels={"rainfall": "Rainfall (mm/h)", "count": "Frequency"},
            color_discrete_sequence=["#0077b6"],
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        city_avg: pd.DataFrame = df.groupby("city")["rainfall"].mean().reset_index() if "city" in df.columns else pd.DataFrame()
        if not city_avg.empty:
            fig_pie: go.Figure = px.pie(
                city_avg,
                values="rainfall",
                names="city",
                title="Average Rainfall by City",
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with st.expander("📋 Detailed Statistics", expanded=False):
        detailed: pd.DataFrame = df.describe()
        st.dataframe(detailed, use_container_width=True)

        alert_freq: pd.Series = df["alert_level"].value_counts() if "alert_level" in df.columns else pd.Series()
        if not alert_freq.empty:
            st.markdown("**Alert Frequency**")
            st.dataframe(alert_freq.reset_index(), use_container_width=True, hide_index=True)


def _anomaly_detection_section(
    detector: AnomalyDetector,
    weather_data: Dict[str, Any],
    data_store: DataStorage,
) -> None:
    st.markdown("## 🔍 Anomaly Detection")

    rainfall: float = weather_data.get("rainfall", 0)
    city: str = weather_data.get("city", "Unknown")
    anomaly_result: Dict[str, Any] = detector.detect(rainfall, city)

    col1, col2, col3 = st.columns(3)
    with col1:
        status: str = "⚠️ Anomalous" if anomaly_result["is_anomaly"] else "✅ Normal"
        display_kpi("Status", status, color="#ff3333" if anomaly_result["is_anomaly"] else "#00cc00")
    with col2:
        display_kpi(
            "Z-Score",
            f"{anomaly_result['z_score']:.2f}",
            delta=f"Threshold: ±{detector.z_threshold}",
            color="#ff6b35",
        )
    with col3:
        display_kpi(
            "Severity",
            anomaly_result["severity"].capitalize(),
            color={
                "normal": "#00cc00",
                "high": "#ffcc00",
                "extreme": "#ff3333",
            }.get(anomaly_result["severity"], "#999"),
        )

    st.info(f"**Analysis:** {anomaly_result['description']}")
    st.caption(f"Historical baseline: μ={anomaly_result['historical_mean']:.2f}, σ={anomaly_result['historical_std']:.2f}")

    st.divider()
    st.markdown("### 📋 Anomaly History")
    df: pd.DataFrame = data_store.load_history(max_records=200)
    if not df.empty:
        anomaly_df: pd.DataFrame = detector.batch_detect_dataframe(df.tail(100))
        anomalies: pd.DataFrame = anomaly_df[anomaly_df["is_anomaly"]]
        if not anomalies.empty:
            st.dataframe(
                anomalies[["timestamp", "city", "rainfall", "z_score"]].tail(20),
                use_container_width=True,
                hide_index=True,
            )
            st.caption(f"Total anomalies detected: {len(anomalies)}")
        else:
            st.caption("No anomalies detected in recent data.")
    else:
        st.caption("Collect data to enable anomaly detection history.")


def _notification_center_section(
    notification_service: NotificationService,
    weather_data: Dict[str, Any],
    alert_level: str,
    wapi: WeatherAPI,
) -> None:
    st.markdown("## 🔔 Notification Center")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Send Alert")
        if alert_level == "RED":
            if st.button("📨 Send Alert Notification Now", type="primary", use_container_width=True):
                with st.spinner("Sending notifications..."):
                    result: Dict[str, Any] = notification_service.send_alert_notification(
                        city=weather_data.get("city", "Unknown"),
                        rainfall=weather_data.get("rainfall", 0),
                        alert_level=alert_level,
                    )
                    if result["notifications_sent"]:
                        st.success(f"Notifications sent: {', '.join(result['notifications_sent'])}")
                    else:
                        st.info("Simulated: Notifications would be sent (configure email/SMS in .env).")
        else:
            st.info("No RED alert active. Notifications are triggered only for RED alerts.")
            if st.button("📨 Test Notification (Simulate)", use_container_width=True):
                result = notification_service.send_alert_notification(
                    city=weather_data.get("city", "Unknown"),
                    rainfall=weather_data.get("rainfall", 0),
                    alert_level=alert_level,
                )
                st.info(f"Test: {result}")

    with col2:
        st.markdown("### Configuration")
        email_status: str = "✅ Enabled" if notification_service.email_enabled else "❌ Disabled"
        sms_status: str = "✅ Enabled" if notification_service.sms_enabled else "❌ Disabled"
        st.markdown(f"- Email: {email_status}")
        st.markdown(f"- SMS: {sms_status}")
        st.caption("Enable in .env file: ENABLE_EMAIL=true, ENABLE_SMS=true")

        stats: Dict[str, int] = notification_service.get_stats()
        st.metric("Total Notifications Sent", stats["total"])

    st.divider()
    st.markdown("### Notification Log")
    notifications: List[Dict[str, Any]] = notification_service.load_notification_history(max_lines=20)
    if notifications:
        notif_df: pd.DataFrame = pd.DataFrame(notifications)
        st.dataframe(notif_df, use_container_width=True, hide_index=True)
    else:
        st.caption("No notifications sent yet.")


def _interactive_map_section(
    wapi: WeatherAPI,
    cities: List[str],
    alert_system: AlertSystem,
) -> None:
    st.markdown("## 🗺 Interactive Map")
    try:
        import folium
        from streamlit_folium import st_folium

        center_lat: float = 31.5
        center_lon: float = 114.0
        m: folium.Map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=5,
            control_scale=True,
        )

        folium.LayerControl().add_to(m)

        all_data: Dict[str, Dict[str, Any]] = wapi.fetch_all_cities(cities)
        for city, data in all_data.items():
            lat, lon = city_coordinates(city)
            rainfall: float = data.get("rainfall", 0)
            level, _ = alert_system.evaluate(rainfall, city)

            color_map: Dict[str, str] = {
                "GREEN": "green",
                "YELLOW": "orange",
                "RED": "red",
            }
            marker_color: str = color_map.get(level, "blue")

            popup_html: str = f"""
                <div style="min-width: 180px;">
                    <h4 style="margin: 0 0 8px;">{city}</h4>
                    <b>Rainfall:</b> {rainfall:.2f} mm/h<br>
                    <b>Temperature:</b> {data.get('temperature', 0):.1f} °C<br>
                    <b>Humidity:</b> {data.get('humidity', 0):.1f} %<br>
                    <b>Alert Level:</b> <span style="color:{marker_color};">{level}</span><br>
                    <b>Status:</b> {data.get('description', 'N/A').capitalize()}
                </div>
            """

            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=city,
                icon=folium.Icon(color=marker_color, icon="cloud", prefix="fa"),
            ).add_to(m)

        st_folium(m, width=None, height=500)
    except ImportError as e:
        st.warning(f"Folium or streamlit-folium not installed: {e}")
        st.caption("Install with: pip install folium streamlit-folium")


def _forecast_section(wapi: WeatherAPI, city: str) -> None:
    st.markdown("## 📅 24-Hour Forecast")
    forecast_data: Dict[str, Any] = wapi.fetch_forecast(city)
    if forecast_data.get("error"):
        st.caption("Forecast data unavailable.")
        return
    forecasts: List[Dict[str, Any]] = forecast_data.get("forecasts", [])
    if forecasts:
        fdf: pd.DataFrame = pd.DataFrame(forecasts)
        fig: go.Figure = go.Figure()
        fig.add_trace(go.Bar(
            x=fdf["timestamp"],
            y=fdf["rainfall"],
            name="Rainfall",
            marker_color="#0077b6",
        ))
        fig.add_trace(go.Scatter(
            x=fdf["timestamp"],
            y=fdf["temperature"],
            name="Temperature",
            yaxis="y2",
            line=dict(color="#ff6b35", width=2),
        ))
        fig.update_layout(
            title=f"3-Hour Forecast for {city}",
            xaxis=dict(title="Time"),
            yaxis=dict(title="Rainfall (mm/h)", side="left"),
            yaxis2=dict(title="Temperature (°C)", side="right", overlaying="y"),
            legend=dict(x=0.01, y=0.99),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)


def run_dashboard() -> None:
    _page_setup()

    wapi: WeatherAPI = WeatherAPI(offline_mode=False)
    alert_system: AlertSystem = AlertSystem()
    predictor: RainfallPredictor = RainfallPredictor()
    detector: AnomalyDetector = AnomalyDetector()
    notification_service: NotificationService = NotificationService()
    data_store: DataStorage = DataStorage()

    sidebar_state: Dict[str, Any] = _sidebar(wapi)
    selected_cities: List[str] = sidebar_state["selected_cities"]
    auto_refresh: bool = sidebar_state["auto_refresh"]

    if not selected_cities:
        st.warning("Please select at least one city.")
        st.stop()

    primary_city: str = selected_cities[0]
    weather_data: Dict[str, Any] = wapi.fetch_weather(primary_city)
    rainfall: float = weather_data.get("rainfall", 0)
    alert_level, alert_status = alert_system.evaluate(rainfall, primary_city)
    weather_data["alert_level"] = alert_level

    data_store.save_reading(weather_data)

    st.title("🌧 Rainfall Monitor and Forecasting System")
    st.markdown(f"*Real-time rainfall monitoring, alerts, and ML-powered forecasting*")
    st.divider()

    _current_weather_section(weather_data, alert_level, alert_status)

    st.divider()
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🚨 Alerts",
        "🏙 Multi-City",
        "📈 Trends",
        "🤖 Forecast",
        "📊 Analytics",
        "🔍 Anomalies",
        "🔔 Notifications",
        "🗺 Map",
    ])

    with tab1:
        _alert_center_section(alert_system, weather_data, alert_level, alert_status)

    with tab2:
        _multi_city_section(wapi, selected_cities, alert_system)

    with tab3:
        _historical_trends_section(data_store)

    with tab4:
        _ml_forecast_section(predictor, weather_data)
        st.divider()
        _forecast_section(wapi, primary_city)

    with tab5:
        _data_analytics_section(data_store)

    with tab6:
        _anomaly_detection_section(detector, weather_data, data_store)

    with tab7:
        _notification_center_section(notification_service, weather_data, alert_level, wapi)

    with tab8:
        _interactive_map_section(wapi, selected_cities, alert_system)

    st.divider()
    st.caption(
        f"Rainfall Monitor & Forecasting System | "
        f"Last updated: {current_timestamp()} | "
        f"Auto-refresh: {'ON' if auto_refresh else 'OFF'} | "
        f"v1.0"
    )

    if auto_refresh:
        time.sleep(REFRESH_INTERVAL)
        st.rerun()
