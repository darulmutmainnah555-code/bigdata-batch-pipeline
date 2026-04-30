import os
import shutil
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, hour
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. Inisialisasi Spark
spark = SparkSession.builder.appName("Traffic Monitoring").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# 2. Bersihkan folder output
if os.path.exists("output"):
    shutil.rmtree("output")

os.makedirs("output", exist_ok=True)

# 3. Generate data simulasi
sensor_data = []
start_time = datetime(2026, 1, 1, 8, 0, 0)

for i in range(100):
    for area in ["AreaA", "AreaB", "AreaC"]:
        timestamp = start_time + timedelta(minutes=i)
        vehicle_count = random.randint(50, 200)
        sensor_data.append((timestamp, area, vehicle_count))

# 4. Buat DataFrame
sensor_df = spark.createDataFrame(sensor_data, ["timestamp", "location", "vehicle_count"])

# 5. Total kendaraan per area
traffic = sensor_df.groupBy("location").sum("vehicle_count")

# 6. Data tren waktu
traffic_time = sensor_df

# 7. Data untuk ML
ml_data = sensor_df.withColumn("hour", hour(col("timestamp")))

# 8. Simpan ke Parquet
traffic.write.mode("overwrite").parquet("output/traffic")
traffic_time.write.mode("overwrite").parquet("output/traffic_time")
ml_data.write.mode("overwrite").parquet("output/ml_data")

print("SEMUA DATA BERHASIL DISIMPAN")

# 9. Stop Spark
spark.stop()