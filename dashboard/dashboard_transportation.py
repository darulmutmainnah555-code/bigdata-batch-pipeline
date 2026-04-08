import streamlit as st
import time
import sys
import os

# ===========================
# FIX MODULE PATH (WAJIB)
# ===========================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# ===========================
# IMPORT MODULE
# ===========================
from analytics import transportation_analytics as ta
from alerts import transportation_alert as alert

# ===========================
# CONFIG (LANGKAH 5: OPTIMASI)
# ===========================
DATA_PATH = "data/serving/transportation"
REFRESH_INTERVAL = 5 # Jeda 5 detik agar performa stabil

st.set_page_config(
    page_title="Smart Transportation Dashboard",
    layout="wide"
)

st.title("🚗 Smart Transportation - Real-Time Analytics")

# ===========================
# AUTO REFRESH
# ===========================
placeholder = st.empty()

# ===========================
# MAIN LOOP
# ===========================
while True:
    with placeholder.container():

        # ===========================
        # LOAD DATA
        # ===========================
        df = ta.load_data(DATA_PATH)

        if df.empty:
            st.warning("⏳ Waiting for streaming transportation data...")
            time.sleep(REFRESH_INTERVAL)
            continue

        # ===========================
        # PREPROCESS
        # ===========================
        df = ta.preprocess(df)

        # ===========================
        # METRICS
        # ===========================
        try:
            metrics = ta.compute_metrics(df)
        except Exception as e:
            st.error(f"Error computing metrics: {e}")
            time.sleep(REFRESH_INTERVAL)
            continue

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Trips", metrics["total_trips"])
        col2.metric("Total Fare", int(metrics["total_fare"]))
        col3.metric("Top Location", metrics["top_location"])

        st.divider()

        # ===========================
        # PEAK HOUR
        # ===========================
        try:
            peak_hour = ta.detect_peak_hour(df)
            st.info(f"🚦 Peak traffic hour: {peak_hour}:00")
        except Exception:
            st.warning("Tidak dapat menghitung peak hour")

        # ===========================
        # ALERTS
        # ===========================
        try:
            alerts = alert.generate_alert(df)
            if alerts:
                st.subheader("🚨 Traffic Alerts")
                for a in alerts:
                    st.error(a)
        except Exception as e:
            st.warning(f"Alert error: {e}")

        st.divider()

        # ===========================
        # VISUALISASI (LANGKAH 4 & 5)
        # ===========================
        try:
            col1, col2 = st.columns(2)

            with col1:
                # 1. Traffic Density
                st.subheader("🚗 Fare per Location (Traffic Density)")
                st.bar_chart(ta.fare_per_location(df)) 

            with col2:
                # 3. Vehicle Distribution
                st.subheader("🛵 Vehicle Distribution")
                st.bar_chart(ta.vehicle_distribution(df)) 

            # Traffic Volume (Windowing / Resample)
            st.subheader("📊 Traffic Volume per Minute")
            st.line_chart(ta.traffic_per_window(df))

            # 2. Mobility Trend (Sampling / Downsampled)
            st.subheader("📈 Mobility Trend (Downsampled)")
            df_sample = df.tail(1000) # Hanya ambil 1000 data terakhir agar ringan
            st.line_chart(df_sample['fare']) 

        except Exception as e:
            st.warning(f"Visualization error: {e}")

        st.divider()

        # ===========================
        # ANOMALY
        # ===========================
        try:
            st.subheader("⚠️ Abnormal Trips")
            anomaly_df = ta.detect_anomaly(df)

            if not anomaly_df.empty:
                st.dataframe(anomaly_df.tail(20)) # Batasi baris yang tampil
            else:
                st.success("No anomalies detected")
        except Exception as e:
            st.warning(f"Anomaly error: {e}")

        st.divider()

        # ===========================
        # LIVE DATA (LANGKAH 4: LIMITED ROW)
        # ===========================
        st.subheader("📋 Live Trip Data (Limited 50 Rows)")
        # 4. Real-Time Table (LIMITED ROW)
        # Penting: Jangan tampilkan seluruh data -> akan crash
        st.dataframe(df.tail(50)) 

    # Jeda Refresh (Langkah 5)
    time.sleep(REFRESH_INTERVAL)