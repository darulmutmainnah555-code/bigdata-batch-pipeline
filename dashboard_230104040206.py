import streamlit as st
from pyspark.sql import SparkSession
import plotly.express as px
from sklearn.linear_model import LinearRegression
import pandas as pd
import os

# 1. Konfigurasi halaman
st.set_page_config(page_title="Smart Traffic Dashboard")
st.title("🚦 Smart City Traffic Monitoring")

# 2. Inisialisasi Spark
@st.cache_resource
def init_spark():
    return SparkSession.builder.appName("Dashboard").getOrCreate()

spark = init_spark()

# 3. SET PATH (INI YANG PALING PENTING 🔥)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "output")

# 4. Load data
try:
    traffic = spark.read.parquet(os.path.join(OUTPUT_PATH, "traffic")).toPandas()
    traffic_time = spark.read.parquet(os.path.join(OUTPUT_PATH, "traffic_time")).toPandas()
    ml_data = spark.read.parquet(os.path.join(OUTPUT_PATH, "ml_data")).toPandas()
except Exception as e:
    st.error("Data belum tersedia! Jalankan engine dulu.")
    st.write(f"Detail error: {e}")  # biar kelihatan kalau ada error lain
    st.stop()

# 5. Sidebar filter
area = st.sidebar.selectbox("Pilih Area", ["AreaA", "AreaB", "AreaC"])

# 6. KPI
if "sum(vehicle_count)" in traffic.columns:
    total = traffic["sum(vehicle_count)"].sum()
else:
    total = traffic["vehicle_count"].sum()

st.metric("Total Kendaraan", int(total))

# 7. Filter data
filtered = traffic_time[traffic_time["location"] == area]

# 8. Grafik
if not filtered.empty:
    fig = px.line(filtered, x="timestamp", y="vehicle_count", title="Tren Kendaraan")
    st.plotly_chart(fig)
else:
    st.warning("Data tidak tersedia untuk area ini")

# 9. Prediksi AI
st.subheader("🔮 Prediksi Kendaraan")

ml_filtered = ml_data[ml_data["location"] == area]

if not ml_filtered.empty:
    X = ml_filtered[["hour"]]
    y = ml_filtered["vehicle_count"]

    model = LinearRegression()
    model.fit(X, y)

    jam = st.slider("Pilih Jam", 0, 23, 8)
    prediksi = model.predict([[jam]])

    st.write(f"Prediksi jumlah kendaraan pada jam {jam}: {int(prediksi[0])}")
else:
    st.warning("Data ML tidak tersedia untuk area ini")
    