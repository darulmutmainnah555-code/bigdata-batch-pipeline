# =====================================
# ANALYTICS + SERVING LAYER
# =====================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import sum as _sum, avg, desc, col
import os
import time

# ============================
# START TIMER
# ============================

start_time = time.time()

print("========================================")
print("        ANALYTICS LAYER STARTED        ")
print("========================================")

# ============================
# INIT SPARK
# ============================

spark = SparkSession.builder \
    .appName("AnalyticsLayer") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# ============================
# CREATE SERVING FOLDER
# ============================

if not os.path.exists("data/serving"):
    os.makedirs("data/serving")

# ============================
# LOAD CLEAN DATA (SILVER)
# ============================

print("Loading Clean Parquet Data...")

df_clean = spark.read.parquet("data/clean/parquet/")

# ubah tipe supaya tidak scientific notation
df_clean = df_clean.withColumn(
    "total_amount",
    col("total_amount").cast("long")
)

total_records = df_clean.count()

print(f"Total Records: {total_records}")
print("----------------------------------------")

# ============================
# KPI 1: TOTAL REVENUE
# ============================

print("Calculating Total Revenue...")

total_revenue = df_clean.agg(
    _sum("total_amount").alias("total_revenue")
)

# ubah tipe hasil agregasi
total_revenue = total_revenue.withColumn(
    "total_revenue",
    col("total_revenue").cast("long")
)

total_revenue.show()

# Save as CSV
total_revenue.write.mode("overwrite") \
    .option("header", True) \
    .csv("data/serving/total_revenue")

print("Total Revenue saved to data/serving/total_revenue")
print("----------------------------------------")

# ============================
# KPI 2: TOP 10 PRODUCTS
# ============================

print("Calculating Top 10 Products...")

top_products = df_clean.groupBy("product") \
    .agg(_sum("quantity").alias("total_quantity")) \
    .orderBy(desc("total_quantity")) \
    .limit(10)

top_products.show()

top_products.write.mode("overwrite") \
    .option("header", True) \
    .csv("data/serving/top_products")

print("Top Products saved to data/serving/top_products")
print("----------------------------------------")

# ============================
# KPI 3: REVENUE PER CATEGORY
# ============================

print("Calculating Revenue per Category...")

category_revenue = df_clean.groupBy("category") \
    .agg(_sum("total_amount").alias("category_revenue"))

# ubah tipe supaya tidak scientific notation
category_revenue = category_revenue.withColumn(
    "category_revenue",
    col("category_revenue").cast("long")
)

category_revenue = category_revenue.orderBy(desc("category_revenue"))

category_revenue.show()

category_revenue.write.mode("overwrite") \
    .option("header", True) \
    .csv("data/serving/category_revenue")

print("Category Revenue saved to data/serving/category_revenue")
print("----------------------------------------")

# ============================
# KPI 4: AVERAGE TRANSACTION VALUE
# ============================

print("Calculating Average Transaction Value per Customer...")

avg_transaction = df_clean.groupBy("customer_id") \
    .agg(avg("total_amount").alias("avg_transaction_value"))

avg_transaction.show(5)

avg_transaction.write.mode("overwrite") \
    .option("header", True) \
    .csv("data/serving/avg_transaction")

print("Average Transaction saved to data/serving/avg_transaction")
print("----------------------------------------")

# ============================
# STOP SPARK
# ============================

spark.stop()

end_time = time.time()
execution_time = round(end_time - start_time, 2)

print("========================================")
print("   ANALYTICS LAYER COMPLETED SUCCESS   ")
print(f"   Execution Time: {execution_time} sec")
print("========================================")