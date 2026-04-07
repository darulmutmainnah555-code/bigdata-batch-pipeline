import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(
    page_title="Real-Time E-Commerce Dashboard",
    layout="wide"
)

st.title("Real-Time E-Commerce Analytics Dashboard")

DATA_PATH = "data/serving/stream"
placeholder = st.empty()

def load_stream_data():

    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()

    files = [f for f in os.listdir(DATA_PATH) if f.endswith(".parquet")]

    if len(files) == 0:
        return pd.DataFrame()

    df = pd.concat(
        [pd.read_parquet(os.path.join(DATA_PATH, f)) for f in files],
        ignore_index=True
    )

    return df

while True:
    with placeholder.container():
        try:
            df = load_stream_data()

            if df.empty:
                st.info("Waiting for streaming data...")
                time.sleep(5)
                continue

            # convert timestamp
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])

            # =========================
            # KPI METRICS
            # =========================

            st.subheader("Key Metrics")

            col1, col2, col3, col4 = st.columns(4)

            total_transactions = len(df)
            total_revenue = df["price"].sum()
            avg_transaction = df["price"].mean()
            unique_cities = df["city"].nunique()

            col1.metric("Total Transactions", total_transactions)
            col2.metric("Total Revenue", f"${int(total_revenue)}")
            col3.metric("Avg Transaction", f"${int(avg_transaction)}")
            col4.metric("Cities", unique_cities)

            st.divider()

            # =========================
            # CHART SECTION
            # =========================

            colA, colB = st.columns(2)

            # Revenue per City
            with colA:
                st.subheader("Revenue by City")
                city_sales = (
                    df.groupby("city")["price"]
                    .sum()
                    .sort_values(ascending=False)
                )
                st.bar_chart(city_sales)

            # Top Products
            with colB:
                st.subheader("Top Products")
                product_sales = (
                    df.groupby("product")["price"]
                    .sum()
                    .sort_values(ascending=False)
                )
                st.bar_chart(product_sales)

            st.divider()

            # =========================
            # REVENUE TREND
            # =========================

            st.subheader("Revenue Trend")

            if "timestamp" in df.columns:
                df["minute"] = df["timestamp"].dt.floor("min")

                revenue_trend = (
                    df.groupby("minute")["price"]
                    .sum()
                    .reset_index()
                )

                st.line_chart(revenue_trend.set_index("minute"))

            # =========================
            # LIVE TRANSACTIONS
            # =========================

            st.subheader("Live Transactions")

            if "timestamp" in df.columns:
                latest_data = df.sort_values("timestamp", ascending=False).head(10)
                st.dataframe(latest_data)

        except Exception as e:
            st.error(f"Error: {e}")
            time.sleep(5)